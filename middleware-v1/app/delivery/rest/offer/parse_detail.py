from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request

from app.delivery.app import get_app_and_handler
from app.helpers import make_api_call, generate_correlation_id
from app.repository.aladdin import *
from app.settings import SConfig
from . import router

# Using single object creation here for AWS Secrets(SConfig),
# so that object is called only one time in whole application
sconfig = SConfig()


class URLRequest(BaseModel):
    url: str
    vendor_id: str
    store_id: int


@router.post("/parse-detail")
async def on_demand_scraping(url_request: URLRequest, request: Request):
    correlation_id = request.headers.get('x-transaction-id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    scraping_url = sconfig.app_settings().get("SCRAPING_URL")
    headers = {"X-Correlation-ID": correlation_id}
    response_for_unsuccessful_scraping = {
        "deal": None,
        "error": {
            "message": 'No updates available'
        }
    }
    logger.append_keys(correlation_id=correlation_id)
    try:
        data = {"url": url_request.url,
                "vendor_id": url_request.vendor_id,
                "store_id": url_request.store_id
                }
        response = await make_api_call('POST',
                                       f"{scraping_url}",
                                       data=data,
                                       headers=headers,
                                       raise_on_invalid_status=False
                                       )
        logger.append_keys(status_code=response.status_code)
        result = response.json()
        deal = result.get('deal')
        if deal:
            deal_price = deal.get('price')
            if deal_price:
                # convert cents to dollars with 2 decimal places
                dollars = deal_price / 100
                formatted_dollars = float("{:.2f}".format(dollars).rstrip('0').rstrip('.'))
                deal.update({'price': formatted_dollars})
            return JSONResponse(content=result, headers=headers)
        return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)
    except (httpx.HTTPError, json.JSONDecodeError) as err:
        # Do not log error in sentry if no action can be taken
        logger.info(err)
        return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)
    except Exception as err:
        logger.error(err)
        return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)

App, handler = get_app_and_handler(router)
