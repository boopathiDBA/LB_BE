from typing import List, Union

import httpx
import json
import marshmallow_dataclass

from app.model.entities import Offer, OfferAttributes
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.helpers.log import logger
from app.repository.helpers import Support
from app.settings import SConfig


class ScrapingAPI(IOffer):
    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self.secrets = sconfig.app_settings()
        # Temporarily ignoring Kafka
        # self.producer = sconfig.kafka_producer()

    def search_by_title(self, title: str) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        # Convert browser extension scrapped data to offer dataclass
        try:
            deal: dict = search_input
            deal["product_page"] = deal.get("url")

            if deal.get('price'):
                # convert to cents, due to __offer_object method implementation
                deal["price"] = float(deal.get('price', 0)) * 100

            if deal.get('stock'):
                deal["stock"] = int(deal.get('stock'))

            if deal.get('seller'):
                deal["store_name"] = deal.get('seller')

            # Map received scrapped data as per scrapping api response
            search_offer_json = {
                "page_title": deal.get('name'),
                "source": "be",
                "deal": deal
            }

            offer_schema = marshmallow_dataclass.class_schema(Offer)()

            result = self.__offer_object(self, offer_schema, search_offer_json, deal.get('url'), True)
            return result
        except Exception as e:
            logger.info(dict(correlation_id=SConfig.correlation_id, search_input=search_input,
                             source="Browser Extension Scrapping",
                             message=f"Error occurred for Browser Scrapped offer info with message: {e}"))

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        try:
            result = self.__get_scraped_data(link, self.secrets)
            offer_schema = marshmallow_dataclass.class_schema(Offer)()
            json_result = result.json()

            offer = self.__offer_object(self, offer_schema, json_result, link, False)

            return offer
        except Exception as e:
            logger.info(dict(correlation_id=SConfig.correlation_id, link=link, source="Scraping API",
                             message=f"Error occurred getting results from Scraping API with message: {e}"))

    @staticmethod
    def __get_scraped_data(link: str, secrets: dict):
        logger.info(dict(correlation_id=SConfig.correlation_id, message="Scraping API Execution Started"))
        data = json.dumps({'url': link})
        scraping_url = secrets.get('SCRAPING_URL')
        result = httpx.post(scraping_url, data=data, timeout=60.0, headers={"Content-Type": "application/json"})
        logger.info(dict(correlation_id=SConfig.correlation_id, source="Scraping API Response: ",
                         response=result.text, status_code=result.status_code))
        logger.info(dict(correlation_id=SConfig.correlation_id, message="Scraping API Execution Completed"))
        return result

    @staticmethod
    def __offer_object(self, offer_schema, result, link, publish_kafka):
        deal = result.get('deal')
        price_in_dollars = deal.get('price') / 100
        price = Support.format_price(price_in_dollars)
        if price <= 0:
            raise
        store_name = deal.get("store_name", 'NA')

        if store_name == "NA":
            store_name = Support.get_store_name(link)
        white_list_urls = ["cygnett.com"]
        if result.get('page_title') and any(item in link for item in white_list_urls):
            title = result.get('page_title')
        else:
            title = deal.get('name')

        # Temporarily ignoring Kafka
        # if publish_kafka:
        #     self.__publish_kafka_topic(self, deal, title)

        offer = offer_schema.load(
            {
                "title": title,
                "offer_url": deal.get('product_page'),
                "slug": deal.get("slug", "test_slug"),
                "image_url": deal.get('image_url'),
                "price": price,
                "in_stock": deal.get("true", "true"),
                "store_name": Support.store_name_mapping(store_name)
            }
        )
        return offer
    # Temporarily ignoring Kafka
    # @staticmethod
    # def __publish_kafka_topic(self, offer, title):
    #
    #     if title and offer.get('product_page') and offer.get('price'):
    #         payload = {
    #             "name": title,
    #             "url": offer.get('product_page'),
    #             "image_url": offer.get("image_url"),
    #             "brand": offer.get("brand"),
    #             "price": float(offer.get('price', 0)),
    #             "currency": offer.get("currency"),
    #             "stock": offer.get("stock"),
    #             "mpc": offer.get("mpn"),
    #             "upc": offer.get("gtin"),
    #             "seller": offer.get("seller"),
    #             "category": offer.get("category")
    #         }
    #         self.producer.send('on-demand-ingestion-non-lb-offers', payload)
    #         logger.info(dict(correlation_id=SConfig.correlation_id,
    #                          message="Publishing to on-demand-ingestion-non-lb-offers", payload=payload))
    #     else:
    #         logger.info(dict(correlation_id=SConfig.correlation_id,
    #                          message="missing field for publishing on-demand-ingestion-non-lb-offers", offer=offer))

# ScrapingAPI().search_by_link("https://www.jbhifi.com.au/products/lenovo-ideapad-slim-3-14-hd-chromebook-64gb")
