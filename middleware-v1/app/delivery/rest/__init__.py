# import string, secrets
# import sys
# import traceback
#
# from typing import List, Dict
# from fastapi import FastAPI, HTTPException, Body, APIRouter
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZipMiddleware
# from fastapi.responses import JSONResponse
# from mangum import Mangum
# from serpapi.serp_api_client_exception import SerpApiClientException
# from starlette.requests import Request
#
# from datetime import datetime
#
# import sentry_sdk
# from pydantic import BaseModel
#
# from app.app import get_app_and_handler
# from app.helpers.error import *
# from app.repository.google_shopping import *
# from app.repository.web_offer import *
# from app.repository.opensearch import *
# from app.repository.scraping_api import *
# from app.repository.aladdin import *
# from app.usecase import SearchUseCase
# from app.model.entities import *
# from app.settings import SConfig
# from app.helpers.log import logger
# from app.helpers.error import handle_http_error
# from app.helpers import make_api_call, generate_correlation_id
# from app.repository.brand_search import BrandSearch
#
# # Using single object creation here for AWS Secrets(SConfig),
# # so that object is called only one time in whole application
# sconfig = SConfig()
#
# router = APIRouter(
#     prefix="/offer",
# )
#
#
# class URLRequest(BaseModel):
#     url: str
#     vendor_id: str
#     store_id: int
#
#
# class DataPoint(BaseModel):
#     x: str
#     y: float
#
#
# class PriceHistoryResponse(BaseModel):
#     label: str
#     data: List[DataPoint]
#     fill: bool = False
#     lineTension: float = 0.1
#     spanGaps: bool = True
#     steppedLine: str = "before"
#
#
# def updated_search_input(search_input):
#     url = search_input['url']
#     search_input['url'] = url.replace("//", "/").replace("https:/", "https://").replace("http:/", "http://")
#     return search_input
#
#
# def get_offer_api_schema(offers):
#     offers_api_schema = []
#     for offer in offers:
#         schema = OfferAPISchema()
#         offer = schema.dump(offer)
#         offers_api_schema.append(offer)
#     return offers_api_schema
#
#
# @router.get('/ext')
# async def search_offers(request: Request):
#     correlation_id = request.headers.get('x-transaction-id')
#     # Generating Correlation_id if not provided
#     if correlation_id is None:
#         alphabet = string.ascii_letters + string.digits
#         correlation_id = ''.join(secrets.choice(alphabet) for i in range(6))
#
#     sentry_sdk.set_tag("transaction_id", correlation_id)
#     SConfig.correlation_id = correlation_id
#
#     """
#     Search for matching products by title.
#     Primarily used by browser extension.
#     """
#     search = SearchUseCase(
#         GoogleOffers(sconfig), OpensearchOffers(sconfig), ScrapingAPI(sconfig),
#         BrandSearch(), Aladdin(sconfig), _allow_google_search=True
#     )
#     # e.g. for reference "https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/"
#     try:
#         search_input = dict(request.query_params)
#         logger.info(dict(correlation_id=SConfig.correlation_id, object=search_input, message="Searching offers"))
#         offers = search.find_offers(updated_search_input(search_input))
#     except TitleNotFoundException as te:
#         raise HTTPException(status_code=404, detail="Title not found from Scraping API")
#     except NotFoundException as ue:
#         raise HTTPException(status_code=404, detail="Offer(s) not found")
#     except UnprocessableEntityException as ne:
#         raise HTTPException(status_code=422, detail="Error(s) with required fields")
#     except SerpApiClientException as se:
#         raise HTTPException(status_code=422, detail="SERP Un-processable Entity Error")
#     except Exception as e:
#         if e.__class__.__name__ == "ValidationError":
#             raise HTTPException(status_code=422, detail="Offer entity Validation Error")
#         else:
#             ex_type, ex_value, ex_traceback = sys.exc_info()
#             stack_trace = [f"correlation_id: {correlation_id}"]
#
#             for trace in traceback.extract_tb(ex_traceback):
#                 stack_trace.append(
#                     "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
#             logger.info(stack_trace)
#
#             raise e
#
#     extras = search.get_offers_extras(offers)
#     return SuccessResponse(ResponseWithExtras(offers=get_offer_api_schema(offers), extras=extras))
#
#
# @router.get('/price_history')
# async def get_deal_price_history(request: Request):
#     """
#         Get the price history for a deal based on its offer ID.
#
#         Returns:
#             JSONResponse: The JSON response containing the price history data.
#
#         Raises:
#             HTTPException: If 'offer_id' is not provided or if there is an HTTP error.
#     """
#     query_params = dict(request.query_params)
#     offer_id = query_params.get('id')
#
#     if offer_id is None:
#         raise HTTPException(status_code=400, detail="id is required")
#
#     correlation_id = request.headers.get('x-transaction-id')
#     if correlation_id is None:
#         correlation_id = generate_correlation_id()
#     genie_base_url = sconfig.app_settings().get("GENIE_BASE_URL")
#     headers = {"X-Correlation-ID": correlation_id}
#     try:
#         response = await make_api_call('GET',
#                                        f"{genie_base_url}/offer/price_history/?id={offer_id}",
#                                        headers=headers)
#         price_history_response = PriceHistoryResponse(**response)
#         return JSONResponse(content=price_history_response.dict(), headers=headers)
#     except httpx.HTTPError as err:
#         err_response = getattr(err, 'response', None)
#         err_response_code = err_response and getattr(err_response, 'status_code', 200)
#
#         if err_response_code == 404:
#             return JSONResponse(content={}, headers=headers, status_code=404)
#
#         err_details = err_response and err_response.json()
#         logger.exception(err, extra=dict(correlation_id=correlation_id, details=err_details))
#         return JSONResponse(content={}, headers=headers, status_code=err_response_code)
#
#
# @router.post('/update')
# async def update(request: dict = Body(...)):
#     queue_url = os.getenv('SQS_UPDATE_QUEUE',
#                           'https://sqs.ap-southeast-2.amazonaws.com/710613906184/uat-lb-deal-update')
#     if request.get("origin_store_id") and request.get("vendor_id") and request.get("source_id") and \
#             request.get("request_url") and request.get("price") and request.get("in_stock"):
#         payload = {
#             "store_id": int(request.get("origin_store_id")),
#             "vendor_id": request.get("vendor_id"),
#             "sale_id": int(request.get("source_id")),
#             "url": request.get("request_url"),
#             "price": int(float(request.get("price")) * 100),
#             "stock": int(request.get("in_stock")),
#             "xpath": request.get("xpath_obj"),
#             "last_update": datetime.utcnow().isoformat()
#         }
#         try:
#             sconfig = SConfig()
#             sconfig.sqs_client().send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
#             logger.info(dict(correlation_id=SConfig.correlation_id, queue_url=queue_url,
#                              message="Publishing to sqs topic - on-demand-updates (xpath_obj)", payload=payload))
#         except Exception as err:
#             logger.error(dict(correlation_id=SConfig.correlation_id, error=err,
#                               message="Error Publishing to sqs topic - on-demand-updates(xpath_obj)", payload=request))
#             ex_type, ex_value, ex_traceback = sys.exc_info()
#             stack_trace = []
#
#             for trace in traceback.extract_tb(ex_traceback):
#                 stack_trace.append(
#                     "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
#             return {"Success": False, "error": stack_trace}
#         return {"Success": True}
#     else:
#         logger.info(dict(correlation_id=SConfig.correlation_id, message="Missing field values - SQS", request=request))
#         return {"Success": False, "message": "Missing field values"}
#
#
# @router.post("/parse-detail")
# async def on_demand_scraping(url_request: URLRequest, request: Request):
#     correlation_id = request.headers.get('x-transaction-id')
#     if correlation_id is None:
#         correlation_id = generate_correlation_id()
#     scraping_url = sconfig.app_settings().get("SCRAPING_URL")
#     headers = {"X-Correlation-ID": correlation_id}
#     response_for_unsuccessful_scraping = {
#         "deal": None,
#         "error": {
#             "message": 'No updates available'
#         }
#     }
#     logger.append_keys(correlation_id=correlation_id)
#     try:
#         data = {"url": url_request.url,
#                 "vendor_id": url_request.vendor_id,
#                 "store_id": url_request.store_id
#                 }
#         response = await make_api_call('POST',
#                                        f"{scraping_url}",
#                                        data=data,
#                                        headers=headers,
#                                        raise_on_invalid_status=False
#                                        )
#         logger.append_keys(status_code=response.status_code)
#         result = response.json()
#         deal = result.get('deal')
#         if deal:
#             deal_price = deal.get('price')
#             if deal_price:
#                 # convert cents to dollars with 2 decimal places
#                 dollars = deal_price / 100
#                 formatted_dollars = float("{:.2f}".format(dollars).rstrip('0').rstrip('.'))
#                 deal.update({'price': formatted_dollars})
#             return JSONResponse(content=result, headers=headers)
#         return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)
#     except (httpx.HTTPError, json.JSONDecodeError) as err:
#         # Do not log error in sentry if no action can be taken
#         logger.info(err)
#         return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)
#     except Exception as err:
#         logger.error(err)
#         return JSONResponse(content=response_for_unsuccessful_scraping, headers=headers)
#
# App, handler = get_app_and_handler(router)
