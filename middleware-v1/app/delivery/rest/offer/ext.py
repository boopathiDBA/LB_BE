import secrets
import string
import sys
import traceback

import sentry_sdk
from serpapi.serp_api_client_exception import SerpApiClientException
from starlette.requests import Request

from app.delivery.app import get_app_and_handler
from app.model.entities import *
from app.repository.aladdin import *
from app.repository.brand_search import BrandSearch
from app.repository.google_shopping import *
from app.repository.scraping_api import *
from app.repository.web_offer import *
from app.settings import SConfig
from app.usecase import SearchUseCase
from . import router

# Using single object creation here for AWS Secrets(SConfig),
# so that object is called only one time in whole application
sconfig = SConfig()


def updated_search_input(search_input):
    url = search_input['url']
    search_input['url'] = url.replace("//", "/").replace("https:/", "https://").replace("http:/", "http://")
    return search_input


def get_offer_api_schema(offers):
    offers_api_schema = []
    for offer in offers:
        schema = OfferAPISchema()
        offer = schema.dump(offer)
        offers_api_schema.append(offer)
    return offers_api_schema


@router.get('/ext')
async def search_offers(request: Request):
    correlation_id = request.headers.get('x-transaction-id')
    # Generating Correlation_id if not provided
    if correlation_id is None:
        alphabet = string.ascii_letters + string.digits
        correlation_id = ''.join(secrets.choice(alphabet) for i in range(6))

    sentry_sdk.set_tag("transaction_id", correlation_id)
    SConfig.correlation_id = correlation_id

    """
    Search for matching products by title.
    Primarily used by browser extension.
    """
    search = SearchUseCase(
        GoogleOffers(sconfig), OpensearchOffers(sconfig), ScrapingAPI(sconfig),
        BrandSearch(), Aladdin(sconfig), _allow_google_search=True
    )
    # e.g. for reference "https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/"
    try:
        search_input = dict(request.query_params)
        logger.info(dict(correlation_id=SConfig.correlation_id, object=search_input, message="Searching offers"))
        offers = search.find_offers(updated_search_input(search_input))
    except TitleNotFoundException as te:
        raise HTTPException(status_code=404, detail="Title not found from Scraping API")
    except NotFoundException as ue:
        raise HTTPException(status_code=404, detail="Offer(s) not found")
    except UnprocessableEntityException as ne:
        raise HTTPException(status_code=422, detail="Error(s) with required fields")
    except SerpApiClientException as se:
        raise HTTPException(status_code=422, detail="SERP Un-processable Entity Error")
    except Exception as e:
        if e.__class__.__name__ == "ValidationError":
            raise HTTPException(status_code=422, detail="Offer entity Validation Error")
        else:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            stack_trace = [f"correlation_id: {correlation_id}"]

            for trace in traceback.extract_tb(ex_traceback):
                stack_trace.append(
                    "File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
            logger.info(stack_trace)

            raise e

    extras = search.get_offers_extras(offers)
    return SuccessResponse(ResponseWithExtras(offers=get_offer_api_schema(offers), extras=extras))

App, handler = get_app_and_handler(router)
