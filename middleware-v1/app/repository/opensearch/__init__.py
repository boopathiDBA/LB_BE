import os
import json
import uuid

import requests
from typing import List, Any, Union

import marshmallow_dataclass

from app.helpers import updated_searched_offer
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support


class OpensearchOffers(IOffer):

    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self.secrets = sconfig.app_settings()
        self.sqs_client = sconfig.sqs_client()

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        offer = None
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        open_search_url = f"{open_search_host}/{client_index}/_search/template"
        headers = {'Content-type': 'application/json'}

        if wildcard_search:
            aquery = Support.wildcard_search_query_v2(link)
        else:
            aquery = Support.product_url_search_query(link)

        if not aquery:
            return offer

        try:
            logger.info(dict(correlation_id=SConfig.correlation_id, message="OpenSearch link search",
                             url=open_search_url, query=aquery, headers=headers))
            document = requests.get(url=open_search_url, data=aquery, headers=headers)
            output = document.json()
            result = json.dumps(output, separators=(',', ':'))
            if json.loads(result)['hits']['hits']:
                data = json.loads(result)['hits']['hits'][0]
            else:
                return offer

            offer_schema = marshmallow_dataclass.class_schema(Offer)()
            offer = self.offer_object(offer_schema, data['_source'], data['_score'])
        except Exception as err:
            result = f"Error fetching data from OpenSearch with message:{err}"
            logger.error(dict(correlation_id=SConfig.correlation_id, message=result))
        return offer

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        offer = None
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        open_search_url = f"{open_search_host}/{client_index}/_search/template"
        headers = {'Content-type': 'application/json'}
        aquery = Support.search_by_title_query(title)

        if not aquery:
            return offer

        try:
            logger.info(dict(correlation_id=SConfig.correlation_id, message="OpenSearch title search",
                             url=open_search_url, query=aquery, headers=headers))
            document = requests.get(url=open_search_url, data=aquery, headers=headers)
            output = document.json()
            result = json.dumps(output, separators=(',', ':'))
            data = None
            if json.loads(result)['hits']['hits']:
                for each_hit in json.loads(result)['hits']['hits']:
                    input_title = Support.clean_text(title)
                    target_title = Support.clean_text(each_hit["_source"]["name"])
                    text_score = Support.get_cosine(input_title, target_title)
                    if text_score >= 0.9:
                        data = each_hit
                        break
            if not data:
                return offer

            offer_schema = marshmallow_dataclass.class_schema(Offer)()
            offer = self.offer_object(offer_schema, data['_source'], data['_score'])
            offer.url_match = False
        except Exception as err:
            result = f"Error fetching data from OpenSearch with message:{err}"
            logger.error(dict(correlation_id=SConfig.correlation_id, message=result))
        return offer


    def search_attributes_by_id(
                self, id: str
        ) -> Union[OfferAttributes, bool]:
            pass

    def search_by_attributes(self, offer_attr: AttributeSearchInput) -> List[Offer]:
        data = self._get_opensearch_data(offer_attr, self)
        scored_result = []

        try:
            hits_data = json.loads(data['results'])['hits']['hits']
            if not hits_data:
                return scored_result
        except Exception as e:
            logger.error(dict(correlation_id=SConfig.correlation_id, error=e, object=json.loads(hits_data),
                              message="Error occurred getting response from Opensearch"))
        result_list = []
        log_result_list = []
        offer_url_list = []
        offer_schema = marshmallow_dataclass.class_schema(Offer)()
        for result in hits_data:
            try:
                offer_object = self.offer_object(offer_schema, result['_source'], result['_score'])
                if offer_object.offer_url == offer_attr.get('viewing_url'):
                    offer_object = updated_searched_offer(offer_object)
                if offer_object.offer_url not in offer_url_list:
                    result_list.append(offer_object)
                    offer_url_list.append(offer_object.offer_url)

                log_result_list.append(Support.offer_required_fields(offer_object))
            except Exception as e:
                logger.error(dict(correlation_id=SConfig.correlation_id, errors=e,
                                  source='OpensearchOffers', object=result))
        logger.debug(dict(correlation_id=SConfig.correlation_id, source="Opensearch Api",
                          length=len(log_result_list), result=log_result_list))
        viewing_offer = next((item for item in result_list if item.searched), None)
        if viewing_offer:
            # ToDo: Fix logic issue here - "viewing_offer" is being calculated against the "link" parsed in from
            # cleaned and parsed browser URL and will not match the "offer_url" in OpenSearch
            index = result_list.index(viewing_offer)
            result_list.insert(0, result_list.pop(index))

        logger.info(dict(correlation_id=SConfig.correlation_id, message="OpenSearch API Execution Completed"))
        # todo Can this be moved to usecase implementation?
        #      The final scored result including img scores and google scores if any will be included
        #      Needs to be run async
        self.__publish_sqs_topic_on_demand_requests(self, scored_result)

        return result_list

    @staticmethod
    def _get_opensearch_data(offer_attr, self) -> Any:
        # Open search variables
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        open_search_url = f"{open_search_host}/{client_index}/_search/template"
        headers = {'Content-type': 'application/json'}
        logger.debug(dict(correlation_id=SConfig.correlation_id, message=f"Searching in opensearch", offer=offer_attr))

        # TODO : remove old function
        """
        aquery = self.__search_template(
            offer_attr.get('title'), offer_attr.get('product_id'), offer_attr.get('raw_brand_name'),
            offer_attr.get('openai_attributes'), offer_attr.get('google_pid'), offer_attr.get('department_name'),
            offer_attr.get('category_name'), offer_attr.get('subcategory_name'), offer_attr.get('id')
        )
        """
        # New changes for BE-925
        aquery = self.__search_template_v3(offer_attr)

        # logger.debug(dict(correlation_id=SConfig.correlation_id, message=f"Query params: {aquery['query']}"))

        try:
            logger.info(dict(correlation_id=SConfig.correlation_id, message="OpenSearch query",
                             url=open_search_url, data=aquery, headers=headers))
            document = requests.get(url=open_search_url, data=aquery['query'], headers=headers)
            output = document.json()

            body = json.dumps(output, separators=(',', ':'))
        except Exception as err:
            body = f"Error fetching data from OpenSearch with message:{err}"
            logger.error(dict(correlation_id=SConfig.correlation_id, message=body))

        return dict(results=body, aquery=aquery)

    @staticmethod
    def __search_template(to_search, product_id, raw_brand_name, openai_attributes, google_pid,
                          department_name, category_name, subcategory_name, offer_id) -> dict:
        attribute_threshold = 0
        params_pm_combined_attributes, params_negative_attributes = [], []

        params = {
            "id": "browser_extension_search_v2",
            "params": {
                "query_string": f"{to_search} ",
                "from": 0,
                "size": 50
            }
        }

        if department_name:
            params["params"]["p_department_name"] = department_name

        if product_id and department_name.lower() != 'fashion':
            params["params"]["p_product_id"] = product_id

        if raw_brand_name:
            params["params"]["p_raw_brand_name"] = raw_brand_name

        if google_pid:
            params["params"]["p_google_pid"] = google_pid

        if category_name:
            params["params"]["p_category_name"] = category_name

        if subcategory_name:
            params["params"]["p_subcategory_name"] = subcategory_name

        if offer_id:
            params["params"]["p_offer_id"] = offer_id

        if openai_attributes:
            pm_attributes, other_attributes, param_pm_attributes, param_subcategories = [], [], [], []
            param_other_attributes, params_positive_attributes = [], []

            boost_value = 25 if department_name and department_name.lower() == 'fashion' else 40

            positive_attributes = [
                {"positive_attributes": [{"name": "model"}, {"name": "brand"}], "boost": boost_value}
            ]

            negative_attributes = [
                {"negative_attributes": [{"name": "color"}, {"name": "storage"}, {"name": "size"}]}
            ]
            # param_subcategories = [
            #     each
            #     for each in openai_attributes
            #     if each["name"] == "sub-category" and each["value"] is not None
            # ]
            if len(pm_attributes) > 0:
                param_pm_attributes = [
                    each
                    for each in openai_attributes
                    if each["name"] in pm_attributes and each["value"] is not None
                ]

            if len(other_attributes) > 0:
                param_other_attributes = [
                    each
                    for each in openai_attributes
                    if each["name"] in other_attributes and each["value"] is not None
                ]

            openai_attributes_transform = {
                each["name"]: each["value"] for each in openai_attributes
            }

            for each in zip(positive_attributes, negative_attributes):
                boost = each[0]["boost"]
                attribute_threshold += boost

                for each1 in each[0]["positive_attributes"]:
                    attr = {}
                    key = each1["name"]
                    value = openai_attributes_transform[key]
                    if key == "model" and value is None:
                        break
                    if value is not None:
                        attr["name"] = key
                        attr["value"] = value
                    if len(attr) > 0:
                        params_positive_attributes.append(attr)
                if len(params_positive_attributes) > 0:
                    positive_attribute_dict = {
                        "positive_attributes": params_positive_attributes,
                        "boost": boost,
                    }
                    for neg_each in each[1]["negative_attributes"]:
                        attr = {}
                        key = neg_each["name"]
                        value = openai_attributes_transform[key]
                        if value is not None:
                            attr["name"] = key
                            attr["value"] = value
                        if len(attr) > 0:
                            params_negative_attributes.append(attr)
                    # if len(params_negative_attributes) > 0:
                    #     positive_attribute_dict['negative_attribute_dict'] = params_negative_attributes
                    params_pm_combined_attributes.append(positive_attribute_dict)

            # if len(param_subcategories) > 0:
            #     params["params"]["openai_subcategory"] = param_subcategories
            if len(param_pm_attributes) > 0:
                params["params"]["pm_attributes"] = param_pm_attributes
            if len(param_other_attributes) > 0:
                params["params"]["other_attributes"] = param_other_attributes
            if len(params_pm_combined_attributes) > 0:
                params["params"]["pm_combined_attributes"] = params_pm_combined_attributes

        return dict(query=json.dumps(params), attribute_threshold=attribute_threshold,
                    params_pm_combined_attributes=params_pm_combined_attributes,
                    params_negative_attributes=params_negative_attributes)

    @staticmethod
    def __search_template_v3(offer_atts) -> dict:
        p_attrs = []
        search_query = {
            "id": "browser_extension_search_v3",
            "params": {
                "from": 0,
                "size": 100
            }
        }
        search_query["params"]["query_string"] = offer_atts.get("title")
        search_query["params"]["p_department_name"] = offer_atts.get("department_name")
        search_query["params"]["p_category_name"] = offer_atts.get("category_name")
        search_query["params"]["p_subcategory_name"] = offer_atts.get("subcategory_name")
        search_query["params"]["p_offer_id"] = offer_atts.get("id")
        search_query["params"]["p_product_id"] = offer_atts.get("product_id")
        search_query["params"]["p_gtin"] = offer_atts.get("gtin")
        search_query["params"]["p_mpn"] = offer_atts.get("mpn")
        search_query["params"]["p_upc"] = offer_atts.get("upc")
        search_query["params"]["p_isbn"] = offer_atts.get("isbn")
        search_query["params"]["p_ean"] = offer_atts.get("ean")
        search_query["params"]["p_asin"] = offer_atts.get("asin")
        search_query["params"]["p_gpid"] = offer_atts.get("gpid")
        search_query["params"]["p_product_codes"] = offer_atts.get("product_codes")
        search_query["params"]["p_brand"] = offer_atts.get("brand")
        search_query["params"]["p_brand_name"] = offer_atts.get("brand_name")
        search_query["params"]["p_expiry_date"] = offer_atts.get("expiry_date")
        attrs = offer_atts.get("attrs")
        pos_attrs = offer_atts.get("pos_attrs")
        neg_attrs = offer_atts.get("neg_attrs")
        if pos_attrs:
            for attr_key, attr_value in pos_attrs.items():
                attr_value["boost"] = 0.5
                p_attrs.append(attr_value)
        if neg_attrs:
            for attr_key, attr_value in neg_attrs.items():
                p_attrs.append(attr_value)
        search_query["params"]["p_attrs"] = p_attrs
        if attrs.get("model_name") and attrs.get("size") and attrs.get("colour"):
            search_query["params"]["p_model_name"] = attrs.get("model_name")

        return dict(query=json.dumps(search_query))

    @staticmethod
    def offer_object(schema, attributes, score):
        in_stock = attributes.get('stock') == '1'
        store_name = attributes.get('store_name') if attributes.get('store_name') is not None else "Not Given"
        price = Support.format_price(attributes.get('price'))
        product_url = attributes.get('product_url').replace(' ', '%20')
        if attributes.get('affiliate_url') is not None and len(attributes.get('affiliate_url')) != 0:
            affiliate_url = attributes.get('affiliate_url')
        else:
            affiliate_url = product_url
        origin_store_id = str(attributes.get("source_store_id")) if attributes.get("source_store_id") else None
        vendor_id = str(attributes.get("vendor_id")) if attributes.get("vendor_id") else None
        source_id = str(attributes.get("source_id")) if attributes.get("source_id") else None
        department = attributes.get('department_name') or ''
        category_name = attributes.get('category_name') or ''
        subcategory_name = attributes.get('subcategory_name') or ''
        attrs = attributes.get('attrs')
        cleaned_data = Support.cleanup_offer_data(attributes)
        pos_attrs, neg_attrs = Support.get_attrs(attrs, department)
        attrs_transform = Support.transform_attrs(attrs=attrs, target_attr=None, key_value_pair=True)

        offer = schema.load(
            {
                "id": attributes.get('id'),
                "title": attributes.get('name'),
                "offer_url": product_url,
                "link": affiliate_url,
                "slug": attributes.get('slug'),
                "image_url": attributes.get('image_url'),
                "price": price,
                "in_stock": in_stock,
                "store_name": Support.store_name_mapping(store_name),
                "ops_score": float(score),
                "source": "lb",
                "product_id": attributes.get('product_id'),
                # "openai_attributes": attributes.get("openai_attributes"),
                "department_name": department or '',
                "category_name": category_name or '',
                "subcategory_name": subcategory_name or '',
                # "google_pid": attributes.get("google_pid"),
                "af": affiliate_url is not product_url,
                "origin_store_id": origin_store_id,
                "vendor_id": vendor_id,
                "source_id": source_id,
                "xpath_obj": Support.dummy_x_paths(attributes),
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
                "expiry_date": attributes.get("expiry_date")
            }
        )
        return offer

    @staticmethod
    def __publish_sqs_topic_on_demand_updates(self, offer: object) -> None:
        queue_url = os.getenv('SQS_UPDATE_QUEUE',
                              'https://sqs.ap-southeast-2.amazonaws.com/710613906184/uat-lb-deal-update')
        if offer.origin_store_id and offer.vendor_id and offer.source_id and \
                offer.offer_url and offer.price and offer.in_stock:
            payload = {
                "store_id": int(offer.origin_store_id),
                "vendor_id": offer.vendor_id,
                "sale_id": int(offer.source_id),
                "url": offer.offer_url,
                "price": offer.price * 100,
                "stock": int(offer.in_stock),
            }
            try:
                self.sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
                logger.debug(dict(correlation_id=SConfig.correlation_id, queue_url=queue_url,
                                  message="Publishing to sqs topic - on-demand-updates", payload=payload))
            except Exception as err:
                logger.error(dict(correlation_id=SConfig.correlation_id, error=err,
                                  message="Error Publishing to sqs topic - on-demand-updates", payload=offer))
        else:
            logger.info(dict(correlation_id=SConfig.correlation_id, queue_url=queue_url,
                             message="missing field for publishing sqs topic - on-demand-updates", offer=offer))

    @staticmethod
    def __publish_sqs_topic_on_demand_requests(self, entries):
        queue_url = os.getenv('SQS_REQUESTS_QUEUE',
                              'https://sqs.ap-southeast-2.amazonaws.com/710613906184/uat-ondemand-scrape')
        batch_size = 10
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            offer_entries = []
            for offer in batch:
                if offer.origin_store_id and offer.vendor_id and offer.source_id and offer.offer_url:
                    payload = {
                        "store_id": int(offer.origin_store_id),
                        "vendor_id": offer.vendor_id,
                        "sale_id": int(offer.source_id),
                        "url": offer.offer_url,
                    }
                    # TODO: Check correct Id val & format
                    entry = {
                        'Id': f'{offer.id}',
                        'MessageBody': json.dumps(payload)
                    }
                    offer_entries.append(entry)
            if offer_entries:
                try:
                    self.sqs_client.send_message_batch(QueueUrl=queue_url, Entries=offer_entries)
                    logger.debug(dict(correlation_id=SConfig.correlation_id,
                                      message="Publishing to sqs topic - on-demand-requests", payload=offer_entries))
                except Exception as err:
                    logger.error(dict(correlation_id=SConfig.correlation_id, error=err,
                                      message="Error Publishing to sqs topic - on-demand-requests", payload=entries))
