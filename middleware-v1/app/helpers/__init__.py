import csv
import json
import math
import os
import uuid

import inflect
import httpx

import marshmallow_dataclass
import requests
import re
import tldextract
from typing import Union
from pathlib import Path
from functools import lru_cache
from urllib.parse import urlparse
from urllib import parse

from app.helpers.log import logger
from app.model.entities import Offer
from app.repository.helpers import Support
from app.repository.helpers.calculate_confidence import CalculateScore
from aws_lambda_powertools import Tracer

no_cache_tld_extract = tldextract.TLDExtract(cache_dir=None)
tracer = Tracer()

def whitelist_from_csv() -> list:
    results = []
    path = (Path(__file__).parent / "../usecase/whitelist_params.csv").resolve()
    with open(path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            results.extend(row)
        return list(set(results))


def updated_searched_offer(offer):
    offer.confidence = "high"
    offer.searched = True
    pattern = r"https://www\.ebay\..+?/p/\w+"
    is_ebay = bool(re.search(pattern, offer.offer_url))
    if is_ebay:
        query = urlparse(offer.link).query
        offer.offer_url = offer.offer_url + '?' + query
    if offer.source == 'lb':
        offer.ops_score = 2
    return offer


def cleanup_input_title(input_value: str) -> str:
    cleaned_value = None
    try:
        if input_value:
            cleaned_value = parse.unquote(input_value)
            cleaned_value = re.sub(":\\s*Amazon.com.au:\\s*Home", "", cleaned_value, flags=re.IGNORECASE)
    except Exception as e:
        logger.error(dict(message=e, source="cleanup_input_title", input_title=input_value))
        cleaned_value = input_value
    return cleaned_value


def cleanup_input_url(input_value: str) -> str:
    cleaned_value = None
    try:
        if input_value:
            cleaned_value = parse.unquote(input_value)
            if "m.catch" in cleaned_value:
                cleaned_value = cleaned_value.replace("m.catch", "www.catch")
    except Exception as e:
        logger.error(dict(message=e, source="cleanup_input_url", input_url=input_value))
        cleaned_value = input_value
    return cleaned_value


def search_image_vector_by_id(offer_id, department_name):
    knn_index_config = {"fashion": dict(knn_index="a_knn_fashion_deals"), "health & beauty": dict(knn_index="a_knn_health_beauty_deals")}
    open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
    headers = {'Content-type': 'application/json'}
    # TODO: Add Logger
    input_vector = None
    knn_index = None
    try:
        knn_index = knn_index_config[department_name].get("knn_index")
        search_url = f"{open_search_host}/{knn_index}/_search/template"
        query_extract_vector = {
            "id": "browser_extension_get_product_image_vector",
            "params": {"id": offer_id},
        }
        logger.info(dict(offer_id=offer_id, query_extract_vector=json.dumps(query_extract_vector)))
        input_vector_response = json.loads(
            requests.get(search_url, headers=headers, data=json.dumps(query_extract_vector)).text
        )
        logger.info(dict(offer_id=offer_id, input_vector_response=len(input_vector_response)))
        if input_vector_response["hits"]["hits"]:
            input_vector = input_vector_response["hits"]["hits"][0]["_source"]["image_vector"]
        else:
            return input_vector, knn_index
    except Exception as e:
        # TODO: Update Logger
        logger.error(dict(message=e, source="search_image_vector_by_id", offer_id=offer_id))
    return input_vector, knn_index


def search_offer_by_image(image_vector, lb_text_offers, input_offer, input_offer_attrs):
    knn_index = "a_knn_fashion_deals"
    open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
    search_url = f"{open_search_host}/{knn_index}/_search"
    body = {
        "size": 100,
        "_source": {"excludes": "image_vector"},
        "query": {"knn": {"image_vector": {"vector": image_vector, "k": 4}}},
    }
    headers = {'Content-type': 'application/json'}
    text_match_offers_dict = get_matching_offer(lb_text_offers)
    try:
        image_search_response = json.loads(
            requests.get(search_url, headers=headers, data=json.dumps(body)).text
        )
        image_hits = image_search_response["hits"]["hits"]
        deal_ids = [each_image_hit["_id"] for each_image_hit in image_hits]
        body = {
            "size": 100,
            "query": {
                "bool": {
                    "filter": [{"terms": {"id": deal_ids}}],
                    "must_not": [{"term": {"hide": {"value": "true"}}}],
                }
            },
        }
        search_url = f"{open_search_host}/a_deals/_search"
        deal_info_response = json.loads(
            requests.get(search_url, headers=headers, data=json.dumps(body)).text
        )
        deal_info_hits = deal_info_response["hits"]["hits"]
        deal_info_dict = {each["_id"]: each for each in deal_info_hits}
        offer_schema = marshmallow_dataclass.class_schema(Offer)()
        # BE-632 negatively boost text match offers if no associated image set
        for text_match_offer_id, text_match_offer in text_match_offers_dict.items():
            if str(text_match_offer_id) not in deal_ids and text_match_offer.ops_score < 1.5:
                # TODO : Remove the commented block
                """
                ops_score = get_cosine_score(text_match_offer, input_offer.title)
                if attr_match(text_match_offer, input_offer):
                    attr_score = ops_score * 25 / 100
                else:
                    attr_score = 0

                ops_score = ops_score + attr_score
                if attr_match(text_match_offer, input_offer, negative_boost=True):
                    attr_score = ops_score * 25 / 100
                else:
                    attr_score = 0
                ops_score = ops_score - attr_score
                """
                # Code refactoring
                ops_score = text_match_offer.ops_score
                image_boost = get_boosting_factor(0.7) * ops_score
                boosted_score = ops_score + image_boost
                text_match_offers_dict[int(text_match_offer_id)].ops_score = boosted_score
                if boosted_score > 0.95:
                    text_match_offers_dict[int(text_match_offer_id)].confidence = "high"
                else:
                    text_match_offers_dict[int(text_match_offer_id)].confidence = "medium"

        # BE-362 boost/de-boost based on knn and text matching score
        c = CalculateScore(apply_threshold=False)
        for each_image_hit in image_hits:
            img_match_offer_id = each_image_hit["_id"]
            deal_info = deal_info_dict.get(img_match_offer_id)

            if not deal_info:
                continue

            knn_score = float(each_image_hit["_score"])
            img_match_score = math.ceil((knn_score * 100)) / 100
            text_match_offer = text_match_offers_dict.get(int(img_match_offer_id))

            if text_match_offer:
                text_match_offer_id = text_match_offer.id
                text_match_score = text_match_offer.text_score
                ops_score = text_match_offer.ops_score
                if ops_score < 1.5:
                    # TODO : Remove the commented block
                    """ 
                    ops_score = get_cosine_score(text_match_offer, input_offer.title)

                    if attr_match(text_match_offer, input_offer):
                        attr_score = ops_score * 25 / 100
                    else:
                        attr_score = 0
                    ops_score = ops_score + attr_score
                    if attr_match(text_match_offer, input_offer, negative_boost=True):
                        attr_score = ops_score * 25 / 100
                    else:
                        attr_score = 0
                    ops_score = ops_score - attr_score
                   """
                    # Code Refactoring
                    image_boost = get_boosting_factor(img_match_score) * ops_score
                    boosted_score = ops_score + image_boost
                    text_match_offers_dict[int(text_match_offer_id)].ops_score = boosted_score

            else:
                # Code Refactoring
                result_list = []
                if deal_info and img_match_score > 0.85:
                    each_image_hit["_source"]["price"] = deal_info["_source"].get("price")
                    each_image_hit["_source"]["product_id"] = deal_info["_source"].get("product_id")
                    each_image_hit["_source"]["affiliate_url"] = deal_info["_source"].get("affiliate_url")
                    each_image_hit["_source"]["store_name"] = deal_info["_source"].get("store_name")
                    each_image_hit["_source"]["attrs"] = deal_info["_source"].get("attrs")
                    each_image_hit["_source"]["gtin"] = deal_info["_source"].get("gtin")
                    each_image_hit["_source"]["mpn"] = deal_info["_source"].get("mpn")
                    each_image_hit["_source"]["upc"] = deal_info["_source"].get("upc")
                    each_image_hit["_source"]["isbn"] = deal_info["_source"].get("isbn")
                    each_image_hit["_source"]["ean"] = deal_info["_source"].get("ean")
                    each_image_hit["_source"]["gpid"] = deal_info["_source"].get("gpid")
                    each_image_hit["_source"]["asin"] = deal_info["_source"].get("asin")
                    each_image_hit["_source"]["source_store_id"] = deal_info["_source"].get("source_store_id")
                    each_image_hit["_source"]["vendor_id"] = deal_info["_source"].get("vendor_id")
                    each_image_hit["_source"]["source_id"] = deal_info["_source"].get("source_id")
                    each_image_hit["_source"]["department_name"] = deal_info["_source"].get("department_name") or ""
                    each_image_hit["_source"]["category_name"] = deal_info["_source"].get("category_name") or ""
                    each_image_hit["_source"]["subcategory_name"] = deal_info["_source"].get("subcategory_name") or ""

                    img_match_offer = offer_object(offer_schema, each_image_hit["_source"], img_match_score)
                    result_list.append(img_match_offer)
                    scored_result = c.calculate_confidence(offer_attrs=input_offer_attrs, offers=result_list)
                    ops_score = scored_result[0].ops_score
                    # Todo : Remove the commented block
                    """
                    if attr_match(img_match_offer, input_offer):
                        attr_score = ops_score * 25 / 100
                    else:
                        attr_score = 0
                    ops_score = ops_score + attr_score
                    if attr_match(img_match_offer, input_offer, negative_boost=True):
                        attr_score = ops_score * 25 / 100
                    else:
                        attr_score = 0
                    ops_score = ops_score - attr_score
                    """
                    image_boost = get_boosting_factor(img_match_score) * ops_score
                    boosted_score = ops_score + image_boost
                    img_match_offer.ops_score = boosted_score
                    text_match_offers_dict[int(img_match_offer_id)] = img_match_offer
            # rewrite the confidence based on ops_score
            if text_match_offers_dict.get(int(img_match_offer_id)) \
                    and text_match_offers_dict.get(int(img_match_offer_id)).ops_score > 0.95:
                text_match_offers_dict[int(img_match_offer_id)].confidence = "high"
            elif text_match_offers_dict.get(int(img_match_offer_id)):
                text_match_offers_dict[int(img_match_offer_id)].confidence = "medium"

        return list(text_match_offers_dict.values())
    except Exception as err:
        # TODO: Update Logger
        logger.error(dict(message=err, source="image_search", input_offer=input_offer))
        return lb_text_offers


def search_offer_by_image_v2(image_vector, input_offer_attrs, knn_index):
    knn_index = knn_index
    open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
    search_url = f"{open_search_host}/{knn_index}/_search"
    body = {
        "size": 100,
        "_source": {"excludes": "image_vector"},
        "query": {"knn": {"image_vector": {"vector": image_vector, "k": 4}}},
    }
    headers = {'Content-type': 'application/json'}
    try:
        image_search_response = json.loads(
            requests.get(search_url, headers=headers, data=json.dumps(body)).text
        )
        image_hits = image_search_response["hits"]["hits"]
        deal_ids = [each_image_hit["_id"] for each_image_hit in image_hits]
        body = {
            "size": 100,
            "query": {
                "bool": {
                    "filter": [{"terms": {"id": deal_ids}}],
                    "must_not": [{"term": {"hide": {"value": "true"}}}],
                }
            },
        }
        search_url = f"{open_search_host}/a_deals/_search"
        deal_info_response = json.loads(
            requests.get(search_url, headers=headers, data=json.dumps(body)).text
        )
        deal_info_hits = deal_info_response["hits"]["hits"]
        deal_info_dict = {each["_id"]: each for each in deal_info_hits}
        offer_schema = marshmallow_dataclass.class_schema(Offer)()

        result_list = []
        for each_image_hit in image_hits:
            img_match_offer_id = each_image_hit["_id"]
            deal_info = deal_info_dict.get(img_match_offer_id)

            if not deal_info:
                continue

            knn_score = float(each_image_hit["_score"])
            img_match_score = math.ceil((knn_score * 100)) / 100

            img_match_offer = offer_object(offer_schema, deal_info["_source"], img_match_score)
            if img_match_offer is None:
                continue
            img_match_offer.image_score = img_match_score
            result_list.append(img_match_offer)

        return result_list
    except Exception as err:
        # TODO: Update Logger
        logger.error(dict(message=err, source="image_search", input_offer=input_offer_attrs))
        return []


def get_matching_offer(lb_text_offers):
    matched_dict = {each.id: each for each in lb_text_offers}
    # {{"id": {"offer object"}}}
    return matched_dict


def offer_object(schema, attributes, score) -> Offer:
    offer = None
    try:
        in_stock = attributes.get('stock') == '1'
        store_name = attributes.get('store_name') if attributes.get('store_name') is not None else "Not Given"
        price = Support.format_price(attributes.get('price'))
        product_url = attributes.get('be_product_url').replace(' ', '%20')
        if attributes.get('affiliate_url') is not None and len(attributes.get('affiliate_url')) != 0:
            affiliate_url = attributes.get('affiliate_url')
        else:
            affiliate_url = product_url
        origin_store_id = str(attributes.get("source_store_id")) if attributes.get("source_store_id") else None
        vendor_id = str(attributes.get("vendor_id")) if attributes.get("vendor_id") else None
        source_id = str(attributes.get("source_id")) if attributes.get("source_id") else None
        department = attributes.get('department_name') or ""
        attrs = attributes.get('attrs')
        cleaned_data = Support.cleanup_offer_data(attributes)
        pos_attrs, neg_attrs = Support.get_attrs(attrs, department)
        attrs_transform = Support.transform_attrs(attrs=attrs, target_attr=None, key_value_pair=True)
        # Code Refactoring
        offer = schema.load(
            {
                "id": attributes.get('id'),
                "title": attributes.get('name'),
                "offer_url": product_url,
                "link": affiliate_url,
                "slug": attributes.get('slug', 'anonymous-slug'),
                "image_url": attributes.get('image_url'),
                "price": price,
                "in_stock": in_stock,
                "store_name": Support.store_name_mapping(store_name),
                "ops_score": float(score),
                "source": "lb",
                "product_id": attributes.get('product_id'),
                "department_name": department,
                "category_name": attributes.get('category_name'),
                "subcategory_name": attributes.get('subcategory_name'),
                # "openai_attributes": attributes.get("openai_attributes"),
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
                "brand_name": attributes.get('brand_name')
            }
        )
    except Exception as err:
        # TODO: Update Logger
        logger.error(dict(message=err, source="offer_object helper", image_vector=attributes))
    return offer


def get_cosine_score(offer, name):
    title = offer.title
    title = clean_text(title)
    name = clean_text(name)
    score = Support.get_cosine(title, name)
    return score


def clean_text(text):
    # TODO: Refactor for reuseability
    txt = text.lower()
    txt = re.sub(' +', ' ', txt)
    # txt = re.sub(r"[^a-zA-Z0-9]+", ' ', txt)
    return txt


def attr_match(offer, input_offer, negative_boost=False):
    offer_attr = transform_offer_to_match(offer)
    input_offer_attr = transform_offer_to_match(input_offer)
    p = inflect.engine()
    if negative_boost:
        matched = False
        if offer_attr.get('color') and offer_attr.get('color') != input_offer_attr.get('color'):
            matched = True
    else:
        matched = offer_attr.get('color') and input_offer_attr.get('color') \
                  and offer_attr.get('color') == input_offer_attr.get('color') \
                  and offer_attr.get('brand') and input_offer_attr.get('brand') \
                  and p.compare(offer_attr.get('brand'), input_offer_attr.get('brand'))
    return matched


def transform_offer_to_match(offer):
    target_attr = ["color", "brand"]
    attr_transform = {}
    openai_attrs = offer.openai_attributes
    if offer and openai_attrs:
        attr_transform = {
            openai_attr["name"]: (openai_attr["value"] or "").lower() for openai_attr in openai_attrs
            if openai_attr["name"] in target_attr
        }
    return attr_transform


def get_boosting_factor(knn_score):
    if 0 < knn_score <= 0.70:
        factor = -0.5
    elif 0.70 < knn_score <= 0.80:
        factor = -0.35
    elif 0.81 < knn_score <= 0.85:
        factor = -0.25
    elif 0.85 < knn_score <= 0.90:
        factor = -0.15
    elif 0.90 < knn_score < 0.93:
        factor = 0.2
    elif 0.93 < knn_score < 0.95:
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


@tracer.capture_method
async def make_api_call(
        method: str,
        url: str,
        data=None,
        headers=None,
        params=None,
        timeout=None,
        raise_on_invalid_status=True
):
    """
    Perform an HTTP request and handle the response.

    Args:
        method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        url (str): The URL to send the HTTP request to.
        data: The request data, typically a dictionary for POST or PUT requests.
        headers (dict): Optional headers to include in the request.
        params (dict): Optional query parameters to include in the request.

    Returns:
        union[dict, Response]: If validate_status_code is true and response is success then return
        parsed JSON response data.
    """
    async with httpx.AsyncClient(timeout=timeout or 60) as client:
        response = await client.request(
            method,
            url,
            json=data,
            headers=headers,
            params=params,
        )
        if raise_on_invalid_status:
            response.raise_for_status()
            return response.json()
        else:
            return response


def generate_correlation_id():
    return str(uuid.uuid4())


@lru_cache(maxsize=10000)
def get_domain_from_fully_qualified_domain_name(fqdn: str) -> Union[str, None]:
    domain_name = no_cache_tld_extract(fqdn).registered_domain
    if domain_name:
        return domain_name
