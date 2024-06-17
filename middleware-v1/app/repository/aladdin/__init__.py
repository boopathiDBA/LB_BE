import json
import os
from typing import List, Union

import httpx
import marshmallow_dataclass
import requests

from app.model.entities import Offer, OfferAttributes
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.repository.opensearch import OpensearchOffers
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support


class Aladdin(IOffer):
    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self._aladdin_host = os.getenv('GENIE_BASE_URL', 'https://cass.ingest.littlebirdie.dev')
        self._aladdin_url_meta_endpoint = f"{self._aladdin_host}/url-meta"
        self._aladdin_api_timeout = os.getenv('ALADDIN_API_TIMEOUT', 30)
        self._json_headers = {'Content-type': 'application/json'}
        self._open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        self._client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        self._open_search_url = f"{self._open_search_host}/{self._client_index}/_search/template"

    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        offer = None

        try:
            aladdin_res = httpx.get(self._aladdin_url_meta_endpoint, params={"url": link}, headers=self._json_headers, timeout=self._aladdin_api_timeout)
            aladdin_res.raise_for_status()

            url_meta = aladdin_res.json().get("meta")

            source_store_id = url_meta.get("store_id")
            vendor_id = url_meta.get("vendor_id")
            is_canonical = url_meta.get("is_canonical")

            if not source_store_id or not vendor_id or not is_canonical:
                logger.info(dict(correlation_id=SConfig.correlation_id, link=link,
                                 source="Aladdin Repo",
                                 message=f"Found invalid source_store_id, vendor_id and is_canonical from aladdin API: {source_store_id}, {vendor_id}, {is_canonical}"))
                return offer

            offer = self._search_by_source_store_id_and_vendor_id(source_store_id, vendor_id)
            logger.debug(dict(correlation_id=SConfig.correlation_id, link=link,
                              source="Aladdin Repo",
                              message=f"Found offer using source_store_id: {source_store_id} and vendor_id: {vendor_id}"))
            return offer
            # todo should the below be added?
            # self.__publish_sqs_topic_on_demand_updates(self, offer)
        except Exception as e:
            logger.warning(dict(correlation_id=SConfig.correlation_id, link=link,
                              source="Aladdin Repo",
                              message=f"Error occurred getting offer from aladdin repo with message: {e}"))

        return offer

    def _search_by_source_store_id_and_vendor_id(self, source_store_id: int, vendor_id: str):
        query = Support.source_store_id_and_vendor_id_query(source_store_id, vendor_id)

        document = requests.get(url=self._open_search_url, data=query, headers=self._json_headers)
        output = document.json()
        result = json.dumps(output, separators=(',', ':'))
        if json.loads(result)['hits']['hits']:
            data = json.loads(result)['hits']['hits'][0]
        else:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             source="Aladdin Repo",
                             message=f"Offer not found for source_store_id: {source_store_id}, vendor_id: {vendor_id}"))
            return None

        offer_schema = marshmallow_dataclass.class_schema(Offer)()
        return OpensearchOffers.offer_object(offer_schema, data['_source'], data['_score'])

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(self, link: str) -> Union[OfferAttributes, bool]:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass
