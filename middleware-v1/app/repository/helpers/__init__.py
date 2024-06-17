import math
import re
import os
import requests
import json
import tldextract

from typing import Union, Any
from fuzzywuzzy import fuzz
from app.helpers.log import logger
from collections import Counter
from difflib import SequenceMatcher
from urllib.parse import urlparse
from datetime import datetime

from app.settings import SConfig


class Support:
    micro_tag_black_list_domains = None

    @classmethod
    def get_micro_tags_blacklist_domains(cls):
        if cls.micro_tag_black_list_domains is None:
            with open(SConfig.MICRO_TAGS_BLACKLIST_DOMAINS_PATH) as file_obj:
                data = json.load(file_obj)
                cls.micro_tag_black_list_domains = data
        return cls.micro_tag_black_list_domains

    @staticmethod
    def format_price(price) -> float:
        try:
            price = str(price).replace('$', '').replace(',', '').replace(" + tax", '')
            return float(price)
        except Exception as e:
            message = f"Cannot format price, type of {price} might be incorrect."
            logger.debug(dict(correlation_id=SConfig.correlation_id, errors=e, source='Format_price', message=message))
            return 0.0

    @staticmethod
    def convert_to_int(price) -> Union[float, int]:
        try:
            frac, whole = math.modf(float(price))
            if frac == 0:
                return int(whole)
            else:
                return price
        except Exception as e:
            message = f"Cannot convert to integer, incoming value {price} might be incorrect."
            logger.debug(dict(correlation_id=SConfig.correlation_id, errors=e, source='Format_price', message=message))
            return 0.0

    @staticmethod
    def calculate_confidence(search_ds, title, op_limit=40, sort=True) -> list:
        offer_list_processed_new = []
        total_score = 200.0000

        v_title = title.lower()
        for hits in search_ds:
            v_ratio = fuzz.ratio(v_title, hits.title.lower())
            v_token_sort_ratio = fuzz.token_sort_ratio(v_title, hits.title.lower())
            score = (float(v_ratio) + float(v_token_sort_ratio)) / total_score

            if score >= 0.88:
                hits.confidence = "high"
                offer_list_processed_new.append(hits)
            elif 0.88 > score >= 0.79 and hits.source == "lb":
                hits.confidence = "medium"
                offer_list_processed_new.append(hits)
            else:
                hits.confidence = "low"

        return offer_list_processed_new

    @staticmethod
    def __clean_text(text):
        txt = text.lower()
        txt = re.sub(' +', ' ', txt)
        # txt = re.sub(r"[^a-zA-Z0-9]+", ' ', txt)
        return txt

    @staticmethod
    def clean_text(text):
        txt = text.lower()
        txt = re.sub(' +', ' ', txt)
        # txt = re.sub(r"[^a-zA-Z0-9]+", ' ', txt)
        return txt

    @staticmethod
    def score_classification(score, hits):
        if score >= 0.95:
            hits.confidence = "high"
        elif 0.95 > score >= 0.79:
            hits.confidence = "medium"
        else:
            hits.confidence = "low"
        return hits

    @staticmethod
    def transform_attrs(attrs, target_attr, key_value_pair = False):
        attr_transform = {}
        if attrs and not key_value_pair:
            for each_attr in attrs:
                if each_attr["name"] in target_attr:
                    key = each_attr["name"]
                    attr_transform[key] = {"value": (each_attr["value"] or "").lower(), "name": key.lower()}
        elif attrs:
            for each_attr in attrs:
                key = each_attr["name"]
                attr_transform[key] = (each_attr["value"] or "").lower()

        if target_attr and "brand" in target_attr:
            attr_transform["brand"] = {"name": "brand"}

        return attr_transform

    @staticmethod
    def get_attrs(attrs, department):
        pos_attrs = dict()
        neg_attrs = dict()
        if not attrs:
            return pos_attrs, neg_attrs
        pos_attrs_config = ["model_name", "capacity", "size", "colour"]
        neg_attrs_config = ["capacity", "size", "colour", "condition", "gender"]

        pos_attrs = Support.transform_attrs(attrs, pos_attrs_config)
        neg_attrs = Support.transform_attrs(attrs, neg_attrs_config)
        return pos_attrs, neg_attrs

    @staticmethod
    def cleanup_offer_data(offer_data):
        cleaned_data = dict()
        product_codes = []
        cleanup_fields_config = ["gtin", "mpn", "ean", "isbn", "upc", "asin", "gpid", "brand"]
        product_codes_fields_config = ["gtin", "ean", "isbn", "upc"]
        # converting fields to lowercase
        for each_fields in cleanup_fields_config:
            cleaned_data[each_fields] = (offer_data.get(each_fields) or "").lower()
        # constructing product codes list
        for each_id in product_codes_fields_config:
            if cleaned_data[each_id]:
                product_codes.append(cleaned_data[each_id])
        cleaned_data["product_codes"] = product_codes
        return cleaned_data

    @staticmethod
    def __score_classification(score, hits):
        if score >= 0.95:
            hits.confidence = "high"
        elif 0.95 > score >= 0.79:
            hits.confidence = "medium"
        else:
            hits.confidence = "low"
        return hits

    @staticmethod
    def calculate_confidence_v2(search_ds, title, op_limit=40, sort=True) -> list:
        offer_list_processed_new = []
        max_ops_score = search_ds[0].ops_score
        v_title = Support.__clean_text(title)

        for hits in search_ds:
            name = Support.__clean_text(hits.title)

            if hits.source == 'lb':
                v_ratio = (hits.ops_score / max_ops_score)
                v_token_ratio = fuzz.token_set_ratio(v_title, name) / 100.00
                score = v_ratio * v_token_ratio
            else:
                v_ratio = fuzz.token_sort_ratio(v_title, name) / 100.00
                v_token_ratio = fuzz.token_set_ratio(v_title, name) / 100.00
                score = v_ratio * v_token_ratio

            hits = Support.__score_classification(score, hits)
            offer_list_processed_new.append(hits)

        return offer_list_processed_new

    @staticmethod
    def calculate_confidence_v3(search_ds, title, op_limit=40, sort=True) -> list:
        offer_list_processed_new = []
        title = Support.__clean_text(title)

        for hits in search_ds:
            name = Support.__clean_text(hits.title)
            score = SequenceMatcher(lambda x: x == " ", title, name).ratio()

            hits = Support.__score_classification(score, hits)
            hits.ops_score = score

            message = f"Score: {score}, Name: {name}, Title: {title}, Hits confidence: {hits.ops_score}," \
                      f"Hits source: {hits.source}"
            logger.info(dict(correlation_id=SConfig.correlation_id, source='calculate_confidence_v3',
                             message=message))

            offer_list_processed_new.append(hits)

        return offer_list_processed_new

    @staticmethod
    def calculate_confidence_v4(search_ds, title, raw_brand_name, attribute_params) -> list:
        attribute_threshold = attribute_params.get('attribute_threshold') or -1
        params_negative_attributes = attribute_params.get('params_negative_attributes') or ''
        len_params_pm_combined_attributes = len(attribute_params.get('params_pm_combined_attributes') or '')

        offer_list_processed_new = []
        title = Support.__clean_text(title)
        raw_brand_name = Support.__clean_text(str(raw_brand_name or ''))

        title = f"{raw_brand_name} {title}" if raw_brand_name not in title else title

        for hits in search_ds:
            name = Support.__clean_text(hits.title)
            score = Support.get_cosine(title, name)

            # f_score = fuzz.token_set_ratio(title, name) / 100.00
            if hits.ops_score >= 10000:
                score = 2
            elif 5000 <= hits.ops_score < 10000:
                score = 1.5
            elif 2000 <= hits.ops_score < 2600:
                if hits.ops_score >= 2500:
                    attr_boost = ((hits.ops_score - 2500) - (hits.ops_score % 10))
                else:
                    attr_boost = ((hits.ops_score - 2000) - (hits.ops_score % 10))

                unmatch_count = 0
                negative_boost = 0
                params_negative_attributes_transform = {}
                openai_attributes_transform = {}
                if len(params_negative_attributes) > 0:
                    params_negative_attributes_transform = {
                        each["name"]: each["value"] for each in params_negative_attributes
                    }
                if hits.openai_attributes:
                    openai_attributes = hits.openai_attributes

                    openai_attributes_transform = {
                        each["name"]: each["value"] for each in openai_attributes
                    }
                if len(params_negative_attributes_transform) > 0 and len(openai_attributes_transform) > 0:
                    for key, value in params_negative_attributes_transform.items():
                        if openai_attributes_transform[key] is not None and openai_attributes_transform[key] != value:
                            unmatch_count += 1
                if unmatch_count == 1:
                    negative_boost = 35

                if unmatch_count > 1:
                    score = 0.9
                else:
                    score_attrb = score + (score * (attr_boost / 100))
                    score_negb = score_attrb * (negative_boost / 100)
                    score = score_attrb - score_negb

            elif 500 <= hits.ops_score < 2000:
                score = score + 0.05 if raw_brand_name not in name else score

            if score > 0.6:  # Restricting the offers with less score, as per BE-632
                hits = Support.__score_classification(score, hits)
                hits.ops_score = score
                message = dict(score=score, name=name, title=title, hits_confidence=hits.ops_score, source=hits.source,
                               id=hits.id, product_id=hits.product_id, store=hits.store_name, price=hits.price)
                logger.debug(dict(correlation_id=SConfig.correlation_id,
                                  source='calculate_confidence_v4', message=message))

                if hits.source == "gs" or hits.source == 'gp':
                    if score > 0.95:
                        offer_list_processed_new.append(hits)
                else:
                    offer_list_processed_new.append(hits)

        return offer_list_processed_new

    @staticmethod
    def get_raw_data_from_opensearch(id: str) -> Any:
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        open_search_url = f"{open_search_host}/{client_index}/_search/template"
        headers = {'Content-type': 'application/json'}

        aquery = Support.search_id_query(id)
        logger.info(f"Query params: {aquery}")

        try:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             message="BrandSearch API Execution Started",
                             url=open_search_url, headers=headers))
            document = requests.get(url=open_search_url, data=aquery, headers=headers)
            output = document.json()

            body = json.dumps(output, separators=(',', ':'))
        except Exception as err:
            body = f"Error fetching data from OpenSearch with message:{err}"
            logger.info(body)

        return body

    @staticmethod
    def wildcard_search_query(link):
        parsed_link = Support.incorrect_domain(urlparse(link), link)
        netloc = parsed_link.netloc

        if "m.catch" in netloc:
            netloc = netloc.replace("m.catch", "www.catch")

        slug = [x for x in parsed_link.path.split("/") if x.strip()][-1]
        if len(slug) < 4:
            return None
        if link[-1] == '/':
            slug = slug + '/'
        if parsed_link.query:
            slug = f"{slug}?{parsed_link.query}"
        else:
            if slug.lower() in ['product', 'product/', 'detail', 'detail/']:
                logger.info(
                    dict(correlation_id=SConfig.correlation_id, link=link, message="Ignoring blacklisted slugs"))
                return False

        params = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                "domain": netloc,
                "slug": slug
            }
        }
        return json.dumps(params)
##TODO - merge it with sanitized link method
    @staticmethod
    def split_query_params(parsed_link_query):
        black_list_array = [
            "utm_term=",
            "cgid=",
            "facetTokenValue=",
            "utm_source=",
            "redirect=",
            "adId=",
            "seoNameToken=",
            "affid=",
            "utm_campaign=",
            "utm_content=",
            "utm_medium=",
            "click_id=",
            "pk_campaign=",
            "source=",
        ]
        try:
            parts_query = parsed_link_query.split("&")
            query_params = ""
            for item in parts_query:
                temp_item = item.split("=")[0]
                if temp_item + "=" in black_list_array:
                    continue
                else:
                    query_params += item + "&"
            query_params = query_params[:-1]
        except Exception as e:
            body = f"The exception is raised for url query params:{e}"
            logger.error(body)
            query_params = None

        return query_params

    @staticmethod
    def wildcard_search_query_v2(link):
        parsed_link = Support.incorrect_domain(urlparse(link), link)
        product_url_domain = parsed_link.netloc
        product_url_slug = [x for x in parsed_link.path.split("/") if x.strip()][-1]
        if parsed_link.query:
            parsed_link_query = Support.split_query_params(parsed_link.query) or ""
        else:
            parsed_link_query = ""
        if parsed_link.fragment:
            parsed_link_fragment = f"#{parsed_link.fragment}"
        else:
            parsed_link_fragment = ""

        if parsed_link_query or parsed_link_fragment:
            product_url_params = f"{parsed_link_query}{parsed_link_fragment}"
        else:
            product_url_params = None

        query = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                    "product_url_domain": product_url_domain,
                    "product_url_slug": product_url_slug,
                    "product_url_params": product_url_params
            }
        }
        return json.dumps(query)
    @staticmethod
    def incorrect_domain(parsed_link, link):
        if "www.amazon" in parsed_link.netloc:
            try:
                # Filtering AMAZON url with specific pattern for Opensearch
                pattern = r"https://www\.amazon\..+?/(dp|gp/offer-listing|gp/product)/\w+"
                matched_str = re.search(pattern, link)
                if matched_str:
                    link = matched_str.group(0)
                parsed_link = urlparse(link)
            except Exception as e:
                body = f"The exception is raised for incorrect_domain function used for Amazon link:{e}"
                logger.error(body)
                parsed_link = urlparse(link)
        return parsed_link

    @staticmethod
    def search_id_query(id) -> str:
        params = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                "id": id
            }
        }
        return json.dumps(params)

    @staticmethod
    def search_by_title_query(title) -> str:
        params = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                "name": title
            }
        }
        return json.dumps(params)

    @staticmethod
    def text_to_vector(text):
        words = re.compile(r"\w+").findall(text.lower())
        return Counter(words)

    @staticmethod
    def get_cosine(text1, text2):
        vec1 = Support.text_to_vector(text1)
        vec2 = Support.text_to_vector(text2)

        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
        sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    @staticmethod
    def offer_required_fields(offer):
        return dict(title=offer.title, offer_url=offer.offer_url, price=offer.price)

    @staticmethod
    def create_web_offer_object(schema, w_offer):
        attributes = w_offer.get('attributes')
        if attributes.get('name'):
            in_stock = attributes.get('stock') == 'in_stock'
            price = Support.format_price(attributes.get('price'))
            offer = schema.load(
                dict(id=w_offer.get('id'), title=attributes.get('name'), link=attributes.get('affiliate_url'),
                     slug=attributes.get('slug'), image_url=attributes.get('image'), price=price,
                     in_stock=in_stock, offer_url=attributes.get('product_url'), source="lb",
                     product_id=attributes.get('product_id'),
                     store_name=Support.store_name_mapping(attributes.get('store_name')))
            )
            return offer
        else:
            logger.info(dict(correlation_id=SConfig.correlation_id, offer=w_offer,
                             message="Product Name not present in DB"))

    @staticmethod
    def get_store_name(link):
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        open_search_url = f"{open_search_host}/a_stores/_search"
        headers = {'Content-type': 'application/json'}
        logger.info(f"Search link: {link}")

        aquery = Support.search_query(link)

        try:
            logger.info(dict(message="OpenSearch Store Name Search API Execution Started",
                             url=open_search_url, headers=headers))
            document = requests.get(url=open_search_url, data=aquery, headers=headers)
            output = document.json()
            body = json.dumps(output, separators=(',', ':'))
            # body = json.loads(body)['hits']['hits'][0]['_source']['name']
            json_data = json.loads(body)
            if json_data and json_data['hits']['hits'] and \
                    json_data['hits']['hits'][0] and \
                    json_data['hits']['hits'][0]['_source']:
                return json_data['hits']['hits'][0]['_source']['name']
            else:
                logger.info(dict(correlation_id=SConfig.correlation_id, link=link,
                                 message="Store info not available in Opensearch"))
                return []
        except Exception as err:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             message="Error fetching store name from OpenSearch", error=err))
            return "NA"

    @staticmethod
    def search_query(store_url) -> str:
        params = {
            "query": {
                "match": {
                    "website_url": {
                        "operator": "and"
                    }
                }
            }
        }
        params["query"]["match"]["website_url"]["query"] = store_url

        return json.dumps(params)

    @staticmethod
    def store_name_mapping(store_name):
        mapping = {
            'Amazon.com.au': 'Amazon Australia',
            'Appliances Online Australia': 'Appliances Online',
            'Betta Home Living': 'Betta',
            'big w': 'Big W',
            'Big W': 'Big W',
            'BIG W': 'Big W',
            'Bing Lee Electronics': 'Bing Lee',
            'Bing Lee Electrics': 'Bing Lee',
            'Bunnings Warehouse': 'Bunnings',
            'ebay': 'eBay Australia',
            'eBay.com.au': 'eBay Australia',
            'ebay.com.au': 'eBay Australia',
            'harvey norman australia': 'Harvey Norman',
            'harvey norman': 'Harvey Norman',
            'mightyape.com.au': 'Mighty Ape',
            'rebel': 'Rebel Sport',
            'toys r us': 'Toys R Us',
            'target australia': 'Target',
            'Target Australia': 'Target',
            'kogan.com': 'Kogan'
        }

        store_name = mapping.get(store_name.lower()) if store_name.lower() in mapping else store_name
        return store_name

    @staticmethod
    def product_url_search_query(url):
        query = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                "product_url": url
            }
        }
        return json.dumps(query)

    @staticmethod
    def source_store_id_and_vendor_id_query(source_store_id: int, vendor_id: str):
        query = {
            "id": "browser_extension_get_product_details_v2",
            "params": {
                "source_store_id": source_store_id,
                "vendor_id": vendor_id
            }
        }
        return json.dumps(query)

    @classmethod
    def dummy_x_paths(cls, attr):
        from app.helpers import get_domain_from_fully_qualified_domain_name
        product_url = attr.get("be_product_url")
        # micro tags supported
        mode = 1
        if not attr.get("vendor_id"):
            refresh = False
        else:
            domain_name = get_domain_from_fully_qualified_domain_name(product_url)
            if domain_name in cls.get_micro_tags_blacklist_domains():
                # micro tags not supported
                mode = 0
            if attr.get("last_price_date"):
                refresh = True
                try:
                    last_price_update = datetime.strptime(attr.get("last_price_date"), "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    if "." in attr.get("last_price_date"):
                        last_price_update = datetime.strptime(attr.get("last_price_date"), "%Y-%m-%dT%H:%M:%S.%fZ")
                    elif "Z" in attr.get("last_price_date") or "z" in attr.get("last_price_date"):
                        last_price_update = datetime.strptime(attr.get("last_price_date"), "%Y-%m-%dT%H:%M:%S%fZ")
                    else:
                        last_price_update = datetime.strptime(attr.get("last_price_date"), "%Y-%m-%dT%H:%M:%S")
                except Exception as err:
                    last_price_update = None
                    logger.info(dict(correlation_id=SConfig.correlation_id,
                                     message="Error in formatting last_price date", error=err))

                if last_price_update:
                    refresh = (datetime.utcnow() - last_price_update).total_seconds() > 1800
            else:
                refresh = True

        return {
            "url": product_url,
            "refresh": refresh,
            "mode": mode,
            "x-paths": None
        }

    @staticmethod
    def health_beauty_boosting_factor(knn_score):
        if 0.90 < knn_score <= 0.92:
            factor = 0.1
        elif 0.92 < knn_score <= 0.94:
            factor = 0.15
        elif 0.94 < knn_score <= 0.96:
            factor = 0.5
        elif 0.97 < knn_score <= 1.0:
            factor = 0.95
        else:
            factor = 0
        return factor

    @staticmethod
    def get_boosting_factor(knn_score):
        if 0 < knn_score <= 0.70:
            factor = -0.5
        elif 0.70 < knn_score <= 0.80:
            factor = -0.35
        elif 0.80 < knn_score <= 0.85:
            factor = -0.25
        elif 0.85 < knn_score <= 0.90:
            factor = -0.15
        elif 0.90 < knn_score <= 0.93:
            factor = 0.2
        elif 0.93 < knn_score <= 0.95:
            factor = 0.3
        elif 0.95 < knn_score <= 0.96:
            factor = 0.5
        elif 0.96 < knn_score <= 0.97:
            factor = 0.5
        elif 0.97 < knn_score <= 0.98:
            factor = 1
        elif 0.98 < knn_score <= 0.99:
            factor = 1
        elif 0.99 < knn_score <= 0.9999:
            factor = 1
        elif 0.9999 < knn_score <= 1:
            factor = 1
        else:
            factor = 0
        return factor
