from datetime import datetime
from urllib.parse import unquote
import urllib.parse

from fastapi import HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.requests import Request
import starlette.status as status

import sentry_sdk
import boto3

from app.helpers.error import NotFoundException
from app.settings import SConfig
from app.helpers.log import logger
from app.helpers import generate_correlation_id
from app.delivery.app import get_app_and_handler
from app.repository.web_affiliate import WebAffiliate
from . import router

METRIC_NAMESPACE = "lb-middleware"
METRIC_NAME = "affiliate_redirect_api"
METRIC_SERVICE = "affiliate-service"
CloudWatch = boto3.client('cloudwatch')

# Using single object creation here for AWS Secrets(SConfig),
# so that object is called only one time in whole application
sconfig = SConfig()

web_affiliate = WebAffiliate()

IGNORE_REFERERS = ["goodguys.com.au"]


def record_metric(val):
    response = CloudWatch.put_metric_data(
        Namespace=METRIC_NAMESPACE,
        MetricData=[
            {
                'MetricName': METRIC_NAME,
                'Dimensions': [
                    {
                        'Name': 'status',
                        'Value': val
                    },
                ],
                'Timestamp': datetime.now(),
                'Value': 1,
                'Unit': 'Count'
            },
        ]
    )
    # logger.info(response)


@router.get('/redirect')
async def redirect_handler(request: Request):
    correlation_id = request.headers.get('x-transaction-id')
    # Generating Correlation_id if not provided
    if correlation_id is None:
        correlation_id = generate_correlation_id()

    sentry_sdk.set_tag("transaction_id", correlation_id)
    SConfig.correlation_id = correlation_id
    logger.set_correlation_id(correlation_id)

    product_url = dict(request.query_params).get("offer_url")
    if not product_url:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Required param: offer_url, not found")

    product_url = unquote(product_url)
    referer = request.headers.get('Referer')
    if referer:
        referer_netloc = urllib.parse.urlparse(referer).netloc
        product_netloc = urllib.parse.urlparse(product_url).netloc
        for ignore_referer in IGNORE_REFERERS:
            if ((referer_netloc in ignore_referer or ignore_referer in referer_netloc)
                    and (referer_netloc in product_netloc or product_netloc in referer_netloc)):
                record_metric("fallback")
                return RedirectResponse(url=product_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    try:
        affiliate_url = web_affiliate.get_by_product_url(product_url)
        # return JSONResponse(content={"affiliate_url": affiliate_url})
        record_metric("success")
        return RedirectResponse(url=affiliate_url, status_code=status.HTTP_302_FOUND)
    except NotFoundException as nfe:
        logger.warning(f"Affiliate url not found for product_url: {product_url}. Error: {str(nfe)} => {logger.get_correlation_id()}")
        record_metric("fallback")
        return RedirectResponse(url=product_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except Exception as e:
        logger.warning(f"Error getting Affiliate url for product_url: {product_url} - {str(e)} => {logger.get_correlation_id()}")
        record_metric("fallback")
        return RedirectResponse(url=product_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

App, handler = get_app_and_handler(router)
