import json
import marshmallow_dataclass
import httpx
from typing import List, Union

from app.helpers.error import *
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support


class WebOffers(IOffer):
    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self.base_url = sconfig.app_settings().get("LB_BASE_URL")

    def search_by_title(
            self, title: str
    ) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    def search_by_link(
            self, link: str
    ) -> Offer:
        logger.info("Web API (search_by_link) Execution Started")
        params = {
            "product_url": link
        }
        url = f"{self.base_url}/api/deals/link_search"

        result = httpx.get(url, params=params)
        result = self.__result_without_errors(result, link)

        if result:
            offer_schema = marshmallow_dataclass.class_schema(Offer)()
            offer = Support.create_web_offer_object(
                offer_schema,
                result.get('deal')
            )
            logger.info("Web API (search_by_link) Execution Completed")
            return offer

    def search_by_links(
            self, merged_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        logger.info("Web API (search_by_links) Execution Started")

        url = f"{self.base_url}/api/deals/offers_by_url"
        product_urls = []
        for m_offer in merged_offers:
            product_urls.append(m_offer.offer_url)

        data = json.dumps({'product_urls': product_urls})
        result = httpx.post(url, data=data, headers={'Content-Type': 'application/json'})
        logger.info("Web API (search_by_links) Execution Completed")
        return result.json().get('deals')

    @staticmethod
    def __result_without_errors(result, link):
        if result.json().get('errors'):
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             link=link, message="Product not found in web database",
                             error=result.json().get('errors')))
        else:
            return result.json()
