from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.requests import Request

from app.delivery.app import get_app_and_handler
from app.helpers import make_api_call, generate_correlation_id
from app.repository.web_offer import *
from app.settings import SConfig
from . import router

# Using single object creation here for AWS Secrets(SConfig),
# so that object is called only one time in whole application
sconfig = SConfig()


class DataPoint(BaseModel):
    x: str
    y: float


class PriceHistoryResponse(BaseModel):
    label: str
    data: List[DataPoint]
    fill: bool = False
    lineTension: float = 0.1
    spanGaps: bool = True
    steppedLine: str = "before"


@router.get('/price_history')
async def get_deal_price_history(request: Request):
    """
        Get the price history for a deal based on its offer ID.

        Returns:
            JSONResponse: The JSON response containing the price history data.

        Raises:
            HTTPException: If 'offer_id' is not provided or if there is an HTTP error.
    """
    query_params = dict(request.query_params)
    offer_id = query_params.get('id')

    if offer_id is None:
        raise HTTPException(status_code=400, detail="id is required")

    correlation_id = request.headers.get('x-transaction-id')
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    genie_base_url = sconfig.app_settings().get("GENIE_BASE_URL")
    headers = {"X-Correlation-ID": correlation_id}
    try:
        response = await make_api_call('GET',
                                       f"{genie_base_url}/offer/price_history/?id={offer_id}",
                                       headers=headers)
        price_history_response = PriceHistoryResponse(**response)
        return JSONResponse(content=price_history_response.dict(), headers=headers)
    except httpx.HTTPError as err:
        err_response = getattr(err, 'response', None)
        err_response_code = err_response and getattr(err_response, 'status_code', 200)

        if err_response_code == 404:
            return JSONResponse(content={}, headers=headers, status_code=404)

        err_details = err_response and err_response.json()
        logger.exception(err, extra=dict(correlation_id=correlation_id, details=err_details))
        return JSONResponse(content={}, headers=headers, status_code=err_response_code)


App, handler = get_app_and_handler(router)
