import os
import re
import json
import requests
import marshmallow_dataclass
from typing import List, Union
from urllib.parse import urlparse


from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support


class BrandSearch(IOffer):
    def search_by_link(self, link: str, wildcard_search: bool = True) -> str:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> Union[OfferAttributes, bool]:
        pass

    def search_attributes_by_id(self, offer_id: str) -> Union[OfferAttributes, bool]:
        data = Support.get_raw_data_from_opensearch(offer_id)

        try:
            json_data = json.loads(data)
            if json_data and json_data['hits']['hits']:
                data = json_data['hits']['hits'][0]['_source']
                offer_schema = marshmallow_dataclass.class_schema(OfferAttributes)()
                return self.__offer_details_object(offer_schema, data)
        except Exception as e:
            logger.error(dict(correlation_id=SConfig.correlation_id, error=e, object=data,
                              message="Error occurred while search_attributes_by_id"))
        return False

    @staticmethod
    def __offer_details_object(schema, attributes):
        # TODO: To remove old fields
        # raw_color = attributes.get('raw_color')
        # if isinstance(raw_color, list):
        # raw_color = ",".join(raw_color)
        # pos_attrs_config = ["model","brand"]
        department = attributes.get('department_name') or ''
        attrs = attributes.get('attrs')
        cleaned_data = Support.cleanup_offer_data(attributes)
        pos_attrs, neg_attrs = Support.get_attrs(attrs, department)
        attrs_transform = Support.transform_attrs(attrs=attrs, target_attr=None, key_value_pair=True)

        offer = schema.load(
            {
                "id": attributes.get('id'),
                "title": attributes.get('name'),
                "product_id": attributes.get('product_id'),
                # TODO: To remove old fields
                # "raw_brand_name": attributes.get('raw_brand_name'),
                # "raw_size": attributes.get('raw_size'),
                # "raw_color": raw_color,
                # "google_pid": attributes.get('google_pid'),
                # "openai_attributes": attributes.get('openai_attributes'),
                "department_name": department,
                "category_name": attributes.get('category_name') or "",
                "subcategory_name": attributes.get('subcategory_name') or "",
                "gtin": cleaned_data.get("gtin"),
                "mpn": cleaned_data.get("mpn"),
                "upc": cleaned_data.get("upc"),
                "isbn": cleaned_data.get("isbn"),
                "ean": cleaned_data.get("ean"),
                "asin": cleaned_data.get("asin"),
                "gpid": cleaned_data.get("gpid"),
                "attrs": attrs_transform,
                "pos_attrs": pos_attrs,
                "neg_attrs": neg_attrs,
                "brand": cleaned_data.get("brand"),
                "brand_name": attributes.get('brand_name'),
                "product_codes": cleaned_data.get("product_codes"),
                "expiry_date": attributes.get('expiry_date')
            }
        )
        return offer
