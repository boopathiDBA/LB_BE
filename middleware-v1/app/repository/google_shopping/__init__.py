from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs

import marshmallow_dataclass
from serpapi import GoogleSearch
# from serpapi.serp_api_client_exception import SerpApiClientException
# import sentry_sdk

from typing import List, Union
import validators
from urllib.parse import urlparse, parse_qs
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support

import validators


class GoogleOffers(IOffer):

    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self.secrets = sconfig.secrets_manager()

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(
            self, id: str
    ) -> Union[OfferAttributes, bool]:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        params = dict(product_id=attr['gpid'], location="Sydney CBD, New South Wales, Australia",
                      engine="google_product", hl="en", gl="au", api_key=self.secrets['SERP_API_KEY'], timeout=15000)

        result_list, product_results = [], []
        try:
            logger.info("SERP Product API Execution Started")
            search = GoogleSearch(params)
            results = search.get_dict()
            product_results = results["sellers_results"]["online_sellers"]
        except JSONDecodeError:
            logger.info("Internal Error in SERP Product API")
        except KeyError:
            logger.info("No sellers_results or online_sellers in SERP Product API")
        except Exception as e:
            logger.exception(e)

        offer_schema = marshmallow_dataclass.class_schema(Offer)()
        for result in product_results:
            if self.__clean_offer_url(result.get('link'), True) and self.__permitted_store(result.get("source")):
                try:
                    if result.get('base_price') is not None:
                        result['title'] = attr.get('title')
                        result['price'] = result.get('base_price').replace("$", "")
                        result['source'] = result.get('name')
                        result['thumbnail'] = results.get('product_results').get('media')[0].get('link')
                        offer_object = self.__offer_object(self, offer_schema, result)
                        offer_object.source = 'gp'
                        result_list.append(offer_object)
                except Exception as e:
                    logger.info(dict(correlation_id=SConfig.correlation_id,
                                     errors=e, source='Google Product API Offers', object=result,
                                     message="Error occurred getting shopping_results from GoogleProduct"))
        logger.info(dict(message="SERP Product API results before scoring",
                         length=len(result_list), results=result_list))

        logger.info("SERP Product API Execution Completed")
        return result_list

    def search_by_title(self, title: str) -> List[Offer]:
        api_key = self.secrets['SERP_API_KEY']
        result_list = []
        log_result_list = []
        shopping_results = []
        results = {}

        # Reducing the scrape count from 200 to 100
        # Keeping the loop, if required in future
        range_count = 1
        for index in range(range_count):
            start = index*100
            try:
                logger.info("SERP Shopping API Execution Started")
                search = GoogleSearch(self.__search_params(title, api_key, start))
                results = search.get_dict()
                # logger.info("Google Results:", results.keys())
                # Usual Business logic moved under child transaction
                # if not results.get("inline_shopping_results"):
                #     logger.debug({'error': results.get('error'), 'message': 'SERP API Exception', 'title': title})
                #     return []
            except JSONDecodeError:
                logger.info("Internal Error in SERP Shopping API")
            except KeyError:
                logger.info("No sellers_results or online_sellers in SERP Shopping API")
            except Exception as e:
                logger.exception(e)

            if index == 0:
                if "inline_shopping_results" in results.keys():
                    shopping_results += results.get("inline_shopping_results")

                if "shopping_results" in results.keys():
                    shopping_results += results.get("shopping_results")

                if shopping_results:
                    logger.info(
                        dict(
                            debug="No Shopping or Inline Results available",
                            source='Google Offer', title=title,
                            correlation_id=SConfig.correlation_id
                        )
                    )
            else:
                if "shopping_results" in results.keys():
                    shopping_results += results.get("shopping_results")

        offer_schema = marshmallow_dataclass.class_schema(Offer)()
        image_list = []

        for result in shopping_results:
            if self.__clean_offer_url(result.get('link'), True):
                try:
                    offer_object = self.__offer_object(self, offer_schema, result)
                    if offer_object and offer_object.image_url not in image_list:
                        result_list.append(offer_object)
                        image_list.append(offer_object.image_url)
                except Exception as e:
                    logger.info(dict(correlation_id=SConfig.correlation_id,
                                     errors=e, source='Google Shopping API Offers', object=result,
                                     message="Error occurred getting shopping_results from GoogleShopping"))
        logger.info(dict(message="SERP Shopping API results before scoring",
                         length=len(result_list), results=result_list))

        logger.info("SERP Shopping API Execution Completed")
        return result_list

    @staticmethod
    def __search_params(title, api_key, start):
        params = dict(q=title, api_key=api_key, location="Sydney CBD, New South Wales, Australia", hl="en", gl="au",
                      engine="google_shopping", google_domain="google.com.au", start=start, num="100", timeout=15000)
        return params

    @staticmethod
    def __clean_offer_url(link, check):
        parsed_url = urlparse(link)
        queries = parse_qs(parsed_url.query)
        if queries and queries.get('q'):
            clean_url = queries.get('q')[0]
            if clean_url and validators.url(clean_url):
                return True if check else clean_url
            else:
                return False if check else link
        else:
            return True if check else link

    @staticmethod
    def __permitted_store(source):
        blacklisted_stores = ["Oz Hair and Beauty", "Westfield Australia"]
        return source and source not in blacklisted_stores

    @staticmethod
    def __offer_object(self, schema, attributes):
        in_stock = attributes.get('stock') == 'in_stock'
        store_name = Support.store_name_mapping(attributes.get("source"))
        if attributes.get('price') is not None and "tax" not in attributes.get('price').lower() and\
                not self.__blacklisted_store(store_name):
            price = Support.format_price(attributes.get('price'))
            offer = schema.load(
                {
                    "id": attributes.get('product_id', 0),
                    "title": attributes.get('title'),
                    "offer_url": self.__clean_offer_url(attributes.get('link'), False),
                    "slug": attributes.get("slug", "test_slug"),
                    "image_url": attributes.get('thumbnail'),
                    "price": price,
                    "in_stock": in_stock,
                    "store_name": store_name,
                    "source": "gs"
                }
            )
            return offer

    @staticmethod
    def __blacklisted_store(store_name):
        blacklist_stores = ['techinn', 'tradeinn']
        return any(blacklist_store in store_name.lower() for blacklist_store in blacklist_stores)
