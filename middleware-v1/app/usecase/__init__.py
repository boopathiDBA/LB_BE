import abc
import re
import os
from typing import Dict
from urllib import parse

from fastapi import HTTPException
from operator import attrgetter

from app.helpers import whitelist_from_csv, updated_searched_offer, search_image_vector_by_id, search_offer_by_image_v2, \
    cleanup_input_title, cleanup_input_url
from app.helpers.log import logger

import validators
import concurrent.futures

from app.helpers.error import *
from app.repository.google_shopping import *
from app.repository import SearchOffersInput
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urlencode, quote

from app.repository.helpers.calculate_confidence import CalculateScore
from app.settings import SConfig


class IUseCase(abc.ABC):
    @abc.abstractmethod
    def find_offers(
            self, search_input: SearchOffersInput
    ) -> List[Offer]:
        pass

    @abc.abstractmethod
    def merge_results(
            self, google_offers: List[Offer], lb_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        pass

    @abc.abstractmethod
    def get_offers_extras(
            self, searched_offers: List[Offer]
    ) -> dict:
        pass


def get_sanitised_link(link: str) -> str:
    whitelist_params = dict()
    whitelist = ['variant', 'variation', 'id', 'pid', 'product', 'product_id']
    whitelist.extend(whitelist_from_csv())

    search_url = link.split('?')[0]
    # converting query_params string to dictionary
    query_params = dict(parse.parse_qsl(parse.urlsplit(link).query))
    query_params_keys = query_params.keys()
    for x in query_params_keys:
        if x in whitelist:
            whitelist_params[x] = query_params[x]

    regex = re.compile(r'^dwvar_')
    special_list = [s for s in query_params_keys if re.search(regex, s)]
    for x in special_list:
        whitelist_params[x] = query_params[x]
    return search_url + '?' + urlencode(whitelist_params) if whitelist_params else search_url


def get_short_slug(link: str) -> str:
    parsed_link = urlparse(link)
    try:
        arr = [x for x in parsed_link.path.split("/") if x.strip()]
        end_path = arr[-1] if arr else ''
        if len(end_path) > 5:
            domain = parsed_link.netloc.strip('www.')
            return f"{domain}/{end_path}"
        else:
            return link
    except Exception as e:
        logger.error(
            dict(correlation_id=SConfig.correlation_id, error=e, link=link, message="Error creating short_slug"))
    return link


@dataclass
class SearchUseCase(IUseCase):
    _google_repo: IOffer
    _opensearch_repo: IOffer
    _scraping_repo: IOffer
    _brand_repo: IOffer
    _aladdin_repo: IOffer
    _allow_google_search: bool
    _is_test: bool = False

    RESTRICTED_PARAMS = ["#lb-gs=0"]
    RESTRICTED_TITLE_KEYWORDS = ["Refurb", "Refurbished", "As New", "Open Box", "Remanufactured",
                                 "Second Hand", "Second-hand", "Pre-owned", "Pre Owned", "Pre Loved",
                                 "Pre-loved", "Factory Second", "Excellent Grade", "Like New",
                                 "Renewed", "Re-newed", "Used", "Restored", "Re-stored", "Ex Demo", "Ex-Demo",
                                 "Floor Stock", "Floor-stock", "Excellent", "Very Good", "Good", "Fair",
                                 "Factory Seconds", "Unlocked", "Grade A", "Grade B", "Grade C", "Pristine Ex Demo"]
    # PD-778 Added word boundry to fix incorrect matches
    RESTRICTED_TITLE_KEYWORDS = [rf'\b{re.escape(keyword)}\b' for keyword in RESTRICTED_TITLE_KEYWORDS]
    PATTERN = re.compile('|'.join(RESTRICTED_TITLE_KEYWORDS), re.IGNORECASE)

    def find_offers(
            self, search_input: SearchOffersInput
    ) -> List[Offer]:
        image_search_departments = ["fashion", "health & beauty"]
        link = search_input.get("url")
        search_input_price = Support.format_price(search_input.get('price')) if search_input.get('price') else None
        if not link:
            raise UnprocessableEntityException
        if self.__is_base_url(link):
            raise HTTPException(status_code=404, detail="Expected url should be a product url")

        # replacing RESTRICTED_PARAMS from Link if present
        # And avoiding Google SERP API call.
        if any(item in link for item in self.RESTRICTED_PARAMS):
            self._allow_google_search = False
            for item in self.RESTRICTED_PARAMS:
                link = link.replace(item, '')

        # Find offer details from LB API
        offer = self.__get_offer(search_input)
        if not offer:
            logger.info(dict(correlation_id=SConfig.correlation_id, message="Title not found",
                             search_input=search_input))
            raise TitleNotFoundException

        # Call SERP API and OpenSearch API parallely
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # New changes for BE-925
            offer_attributes = self.__get_offer_attributes_v2(offer, link)
            department = offer_attributes.get("department_name")

            if self._allow_google_search and len(offer.title.split()) > 2 and not self.__blacklisted_store(offer):
                # New changes for BE-925
                # If google product id is set, get all search results for it for all departments
                # Else we dont have a gpid, perform google shopping search except for fashion
                if offer_attributes.get('gpid'):
                    google_results = executor.submit(self._google_repo.search_by_attributes, offer_attributes).result()
                elif department.lower() == "fashion":
                    google_results = []
                else:
                    google_results = executor.submit(self._google_repo.search_by_title, offer.title).result()
            else:
                logger.info(dict(correlation_id=SConfig.correlation_id, source="SearchUseCase#find_offers",
                                 message="Google search not allowed", link=link, offer=offer))
                google_results = []
            opensearch_results = executor.submit(self._opensearch_repo.search_by_attributes, offer_attributes).result()

            image_results = []
            if offer_attributes.get("department_name") and \
                    offer_attributes.get("department_name").lower() in image_search_departments:
                image_vector, knn_index = search_image_vector_by_id(offer.id, offer_attributes.get("department_name").lower())

                if image_vector:
                    image_results = executor.submit(search_offer_by_image_v2, image_vector, offer_attributes,
                                                    knn_index).result()

            executor.shutdown(wait=True)

        opensearch_results = self.merge_image_results(opensearch_results, image_results)

        # SCORE RESULTS
        c = CalculateScore(apply_threshold=True)
        if not self._is_test:
            google_results = Support.calculate_confidence_v4(google_results, offer_attributes.get('title'), None, {})
            opensearch_results = c.calculate_confidence_v2(offer_attrs=offer_attributes, offers=opensearch_results)

        #  MERGE RESULTS
        if google_results:
            merged_results = self.merge_results(google_results, opensearch_results, offer)
        else:
            merged_results = opensearch_results

        # matched_web_results = self.__get_web_offers(merged_results, offer)
        updated_matched_results = self.__update_merged_results(merged_results, offer)
        final_results = self.__check_searched_present(updated_matched_results, offer)
        results_with_savings = self.__calculate_savings_filtering(final_results, offer, search_input.get("url"))
        updated_confidence = self.__final_confidence_update(results_with_savings, offer)
        sorted_result = self.__conditional_sorting(updated_confidence, search_input_price)
        sorted_result = self.__update_affiliate_urls(sorted_result)

        return sorted_result

    def merge_image_results(self, text_results: List[Offer], image_results: List[Offer]) -> List[Offer]:
        if len(image_results) == 0:
            return text_results
        text_results_hash: Dict[int, Offer] = {each.id: each for each in text_results}
        image_results_hash: Dict[int, Offer] = {each.id: each for each in image_results}
        for text_result_id, text_result in text_results_hash.items():
            if text_result_id in image_results_hash:
                text_result.image_score = image_results_hash[text_result_id].image_score
                image_results_hash.pop(text_result_id)
        for _, image_result in image_results_hash.items():
            if image_result.image_score > 0.85:
                image_result.is_only_img_match = True
                text_results_hash[image_result.id] = image_result
        return list(text_results_hash.values())

    def merge_results(
            self, google_offers: List[Offer], lb_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        merged_offers = []
        offer_url_list = []
        offer_slug_list = []
        offers_details_list = []
        offer_short_slug_list = []
        google_offer_url_list = [get_sanitised_link(x.offer_url.lower()) for x in google_offers]

        for lb_offer in lb_offers[:]:
            lb_sanitised_link = get_sanitised_link(lb_offer.offer_url)
            lb_slug = lb_offer.slug
            lb_short_slug = get_short_slug(lb_offer.offer_url)
            lb_offer_other_details = self.__offer_other_details(lb_offer)

            if lb_sanitised_link in offer_url_list or lb_slug in offer_slug_list or \
                    lb_short_slug in offer_short_slug_list or lb_offer_other_details in offers_details_list:
                lb_offers.remove(lb_offer)

            else:
                offer_url_list.append(lb_sanitised_link)
                offer_slug_list.append(lb_slug)
                offer_short_slug_list.append(lb_short_slug)
                offers_details_list.append(lb_offer_other_details)

                if get_sanitised_link(lb_offer.offer_url.lower()) in google_offer_url_list:
                    g_offer = next((g_offer for g_offer in google_offers if
                                    get_sanitised_link(g_offer.offer_url.lower()) == get_sanitised_link(
                                        lb_offer.offer_url.lower())), None)

                    compared_offer = self.__compare_offer_price(lb_offer, g_offer)
                    merged_offers.append(compared_offer)
                    if compared_offer.source == 'gs' and compared_offer in google_offers:
                        google_offers.remove(compared_offer)
                    google_offer_url_list.remove(get_sanitised_link(lb_offer.offer_url.lower()))
                else:
                    merged_offers.append(lb_offer)
        merged_offers += self.__remaining_google_offers(
            google_offers, offer_slug_list, offers_details_list, offer_url_list, offer_short_slug_list
        )
        logger.info(dict(correlation_id=SConfig.correlation_id, message="Merged offers list", length=len(merged_offers),
                         results=merged_offers))
        return merged_offers

    def get_offers_extras(
            self, searched_offers: List[Offer]
    ) -> dict:
        if searched_offers:
            max_savings_item = max(searched_offers, key=lambda x: float(x.savings) and x.confidence == "high")
            max_savings_amount = float(max_savings_item.savings)
            total_offers = len(searched_offers)
            price_alert = True if (total_offers == 1 and searched_offers[0].searched) or total_offers == 0 else False

            if max_savings_amount > 0:
                converted_savings = Support.convert_to_int(max_savings_amount)
                savings = converted_savings if type(converted_savings) is int else "%0.2f" % converted_savings
                savings = f"${savings}"
            else:
                savings = None
            extras = dict(price_alert=price_alert, savings=savings, product=max_savings_item.title)
            return extras

    # Private Methods from here
    def __get_offer(self, search_input: SearchOffersInput) -> Offer:
        link = cleanup_input_url(search_input.get("url").split('#lb-gs')[0])
        title = cleanup_input_title(search_input.get("name"))
        self.__validate_link(link)
        sanitised_link = get_sanitised_link(link)
        wildcard_search = self.__check_wildcard_search(link)
        link_without_query = sanitised_link.split('?')[0]
        if link_without_query[-1] != '/':
            link_without_query_with_slash = link_without_query + '/'
        else:
            link_without_query_with_slash = link_without_query
        #
        try:
            offer = self._opensearch_repo.search_by_link(sanitised_link, False)
            if not offer and "www." in sanitised_link:
                offer = self._opensearch_repo.search_by_link(sanitised_link.replace("www.", "", 1), False)
            if not offer:
                offer = self._opensearch_repo.search_by_link(link_without_query, False)
            if not offer and "www." in link_without_query:
                offer = self._opensearch_repo.search_by_link(link_without_query.replace("www.", "", 1), False)
            if not offer:
                offer = self._opensearch_repo.search_by_link(link_without_query_with_slash, False)
            if not offer and "www." in link_without_query_with_slash:
                offer = self._opensearch_repo.search_by_link(link_without_query_with_slash.replace("www.", "", 1),
                                                             False)
            if wildcard_search:
                if not offer:
                    offer = self._opensearch_repo.search_by_link(sanitised_link)
                if not offer and "www." in sanitised_link:
                    offer = self._opensearch_repo.search_by_link(sanitised_link.replace("www.", "", 1))
                if not offer:
                    offer = self._opensearch_repo.search_by_link(link_without_query)
                if not offer and "www." in link_without_query:
                    offer = self._opensearch_repo.search_by_link(link_without_query.replace("www.", "", 1))
                if not offer:
                    offer = self._opensearch_repo.search_by_link(link_without_query_with_slash)
                if not offer and "www." in link_without_query_with_slash:
                    offer = self._opensearch_repo.search_by_link(link_without_query_with_slash.replace("www.", "", 1))
            if not offer:
                # utilize browser extension scrapped data to get offer result
                offer = self._scraping_repo.get_offer_info(search_input)
            if not offer:
                offer = self._scraping_repo.search_by_link(link)
            if not offer:
                offer = self._aladdin_repo.search_by_link(link, False)
            if not offer and title:
                offer = self._opensearch_repo.search_by_title(title=title)
        except Exception as e:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             source="SearchUseCase#__get_offer",
                             link=link, sanitised_link=link,
                             message=f"Product not found in Opensearch or Scrapping: {e}"))
            offer = self._scraping_repo.search_by_link(link_without_query)
        return offer

    @staticmethod
    def __is_base_url(url) -> bool:
        parsed_url = urlparse(url)
        if parsed_url.params == '' and parsed_url.query == '' and (parsed_url.path == '/' or parsed_url.path == ''):
            return True
        else:
            return False

    # def __get_web_offers(self, merged_results, offer) -> List[Offer]:
    #     return self._web_repo.search_by_links(merged_results, offer)

    def __get_offer_attributes(self, offer, link) -> dict:
        # Getting Brand Value and attributes from Opensearch
        raw_data = self._brand_repo.search_attributes_by_id(offer.id)
        if raw_data:
            offer_attributes = dict(title=raw_data.title)
            offer_attributes['raw_brand_name'] = raw_data.raw_brand_name if raw_data.raw_brand_name else None
            offer_attributes['product_id'] = raw_data.product_id if raw_data.product_id else None
            offer_attributes['google_pid'] = raw_data.google_pid if raw_data.google_pid else None
            offer_attributes['openai_attributes'] = raw_data.openai_attributes if raw_data.openai_attributes else None
            offer_attributes['department_name'] = raw_data.department_name if raw_data.department_name else ""
            offer_attributes['category_name'] = raw_data.category_name if raw_data.category_name else None
            offer_attributes['subcategory_name'] = raw_data.subcategory_name if raw_data.subcategory_name else None
            offer_attributes['id'] = raw_data.id if raw_data.id else None
            # if department is Fashion
            # Query Pinecone
            # elif department is Electronics
            # Make Opensearch Queries

        else:
            offer_attributes = dict(title=offer.title, product_id=offer.product_id,
                                    department_name=offer.department_name, google_pid=offer.google_pid, id=offer.id)

        if offer_attributes.get('product_id') and int(offer_attributes.get('product_id')) == 866450367:
            offer_attributes['product_id'] = None

        offer_attributes['viewing_url'] = link
        return offer_attributes

    def __get_offer_attributes_v2(self, offer, link) -> dict:
        # Getting Brand Value and attributes from Opensearch
        raw_data = self._brand_repo.search_attributes_by_id(offer.id)
        if raw_data:
            # TODO: convert these block to code in a single line
            # new_offer_attributes = asdict(raw_data)
            offer_attributes = dict(title=raw_data.title)
            # TODO: remove old fields
            # offer_attributes['raw_brand_name'] = raw_data.raw_brand_name if raw_data.raw_brand_name else None
            offer_attributes['product_id'] = raw_data.product_id if raw_data.product_id else None
            # TODO: remove old fields
            # offer_attributes['google_pid'] = raw_data.google_pid if raw_data.google_pid else None
            # offer_attributes['openai_attributes'] = raw_data.openai_attributes if raw_data.openai_attributes else None
            offer_attributes['department_name'] = raw_data.department_name if raw_data.department_name else ""
            offer_attributes['category_name'] = raw_data.category_name if raw_data.category_name else ""
            offer_attributes['subcategory_name'] = raw_data.subcategory_name if raw_data.subcategory_name else ""
            offer_attributes['id'] = raw_data.id if raw_data.id else None
            offer_attributes['gtin'] = raw_data.gtin
            offer_attributes['mpn'] = raw_data.mpn
            offer_attributes['upc'] = raw_data.upc
            offer_attributes['isbn'] = raw_data.isbn
            offer_attributes['ean'] = raw_data.ean
            offer_attributes['asin'] = raw_data.asin
            offer_attributes['gpid'] = raw_data.gpid
            offer_attributes['attrs'] = raw_data.attrs
            offer_attributes['pos_attrs'] = raw_data.pos_attrs
            offer_attributes['neg_attrs'] = raw_data.neg_attrs
            offer_attributes['brand'] = raw_data.brand
            offer_attributes['brand_name'] = raw_data.brand_name
            offer_attributes['product_codes'] = raw_data.product_codes
            offer_attributes[
                'expiry_date'] = raw_data.expiry_date if raw_data.expiry_date and raw_data.expiry_date == "pytest" else None

        else:
            offer_attributes = dict(title=offer.title, product_id=offer.product_id,
                                    department_name=offer.department_name, gpid=offer.gpid, id=offer.id,
                                    product_codes=[], pos_attrs={}, neg_attrs={}, attrs={})

        if offer_attributes.get('product_id') and int(offer_attributes.get('product_id')) == 866450367:
            offer_attributes['product_id'] = None

        if offer.url_match:
            offer_attributes['viewing_url'] = link
        else:
            offer_attributes['viewing_url'] = None

        return offer_attributes

    def __get_offer_attributes_v3(self, offer: Offer, link) -> dict:
        raw_data = offer
        if raw_data.id:
            offer_attributes = asdict(raw_data)
        else:
            offer_attributes = dict(title=offer.title, product_id=offer.product_id,
                                    department_name=offer.department_name, gpid=offer.gpid, id=offer.id,
                                    product_codes=[], pos_attrs={}, neg_attrs={}, attrs={})

        if offer_attributes.get('product_id') and int(offer_attributes.get('product_id')) == 866450367:
            offer_attributes['product_id'] = None

        offer_attributes['viewing_url'] = link
        return offer_attributes

    @staticmethod
    def __blacklisted_store(offer):
        blacklist_stores = ['techinn', 'tradeinn']
        return any(blacklist_store in offer.store_name.lower() for blacklist_store in blacklist_stores)

    @staticmethod
    def __conditional_sorting(results_with_savings, search_input_price) -> List[Offer]:
        best_match, similar = [], []
        for item in results_with_savings:
            # Boost score if offer has affiliate url
            item.ops_score = item.ops_score + 0.001 if item.af else item.ops_score
            try:
                # Update price if offer is viewing offer
                if search_input_price and item.price and item.price != search_input_price and item.searched:
                    item.price = search_input_price
            except Exception as err:
                logger.info(dict(correlation_id=SConfig.correlation_id, message="Price not updating",
                                 search_input_price=search_input_price, error=err))
            best_match.append(item) if item.confidence == "high" else similar.append(item)
        """ Sorting top match with respect to price and score in ascending order """
        sorted_top_offers = sorted(best_match, key=lambda o: (float(o.price), o.ops_score))
        """ If other offers have the same price as viewing offer, then viewing should show at top. """
        if sorted_top_offers:
            """ Find viewing offer in the list """
            viewing_offer = list(filter(lambda elem: elem.searched, sorted_top_offers))[0]
            for top_offer in sorted_top_offers:
                if top_offer is not viewing_offer and float(top_offer.price) == float(viewing_offer.price):
                    viewing_offer_index = sorted_top_offers.index(viewing_offer)
                    same_price_offer_index = sorted_top_offers.index(top_offer)
                    """ Swap viewing offer with same price offer """
                    if viewing_offer_index > same_price_offer_index:
                        sorted_top_offers[same_price_offer_index] = viewing_offer
                        sorted_top_offers[viewing_offer_index] = top_offer

        """ Sorting similar match with respect to ops_score in descending order """
        sorted_similar_offers = sorted(similar, key=lambda o: o.ops_score, reverse=True)
        final_result = sorted_top_offers + sorted_similar_offers
        logger.info(dict(correlation_id=SConfig.correlation_id, message="Final result", length=len(final_result),
                         result=final_result))
        return final_result

    @staticmethod
    def __final_confidence_update(results, offer) -> List[Offer]:
        if not offer.url_match:
            for each_result in results:
                if each_result.searched:
                    each_result.searched = False
                if each_result.confidence == "high":
                    each_result.confidence = "medium"
        return results

    @staticmethod
    def __calculate_savings_filtering(results, offer, link) -> List[Offer]:
        price_list = []
        for result in results:
            result_price = Support.convert_to_int(result.price)
            offer_price = Support.convert_to_int(offer.price)
            price_list.append(float(result_price))
            result.savings = float(offer_price) - float(result_price)
            result_price = Support.convert_to_int(result.price)
            result_savings = Support.convert_to_int(float(result.savings))
            result.price = result_price if type(result_price) is int else "%0.2f" % float(result.price)
            result.savings = result_savings if type(result_savings) is int else "%0.2f" % float(result.savings)
            if os.getenv('FRAGMENT_FOR_REFRESH_FLAG', '#lb-gs=0') in link and result.xpath_obj:
                xpath_obj = result.xpath_obj
                xpath_obj['refresh'] = False
                result.xpath_obj = xpath_obj
        average_price = sum(price_list) / len(price_list)
        for result in results[:]:
            results.remove(result) if float(result.price) < (average_price * 0.34) and not result.searched else None
        return results

    @staticmethod
    def __compare_offer_price(lb_offer, google_offer):
        confidence_priority = {
            "high": 1,
            "medium": 0,
            "low": -1
        }

        lb_offer_confidence = confidence_priority[lb_offer.confidence]
        google_offer_confidence = confidence_priority[google_offer.confidence]

        if lb_offer_confidence > google_offer_confidence:
            return lb_offer
        elif lb_offer_confidence == google_offer_confidence:
            if float(lb_offer.price) <= float(google_offer.price) != 0.0:
                return lb_offer
            else:
                return google_offer
        else:
            return google_offer

    @staticmethod
    def __match_google_link(link, web_results):
        for web_offer in web_results:
            if web_offer.offer_url == link:
                return web_offer
        return False

    @staticmethod
    def __validate_link(link):
        if not validators.url(link) and not validators.url(link.split('?')[0]):
            logger.info(dict(correlation_id=SConfig.correlation_id, source="SearchUseCase#__validate_link",
                             message="Url validation failed", link=link))
            raise UnprocessableEntityException()

    @staticmethod
    def __check_wildcard_search(link):
        restricted_rules = [
            {"domains": ["petbarn.com.au"], "queries": ["sku"]}
        ]
        wildcard_search = True
        domain = parse.urlsplit(link).netloc
        query = parse.urlsplit(link).query
        for rule in restricted_rules:
            allowed_domains, allowed_queries = rule["domains"], rule["queries"]
            if any(each_domain in domain for each_domain in allowed_domains) and any(
                    each_query in query for each_query in allowed_queries):
                wildcard_search = False
                break
        return wildcard_search

    def __update_merged_results(self, merged_offers, offer) -> List[Offer]:
        offer_price = Support.convert_to_int(offer.price)
        search_offer_found = False
        for m_offer in merged_offers[:]:
            m_price = Support.convert_to_int(m_offer.price)

            # Remove offer if restricted keywords are in title or restricted store name present in offer
            if (
                    re.search(self.PATTERN, m_offer.title) or
                    m_offer.store_name.strip().lower() == "reebelo" or
                    m_offer.store_name.strip().lower() == "reebelo au" or
                    m_offer.store_name.strip().lower() == "aladdin"
            ):
                merged_offers.remove(m_offer)
                continue

            # checking if m_offer is viewing offer
            if m_offer.slug == offer.slug or \
                    m_offer.offer_url == offer.offer_url or \
                    self.__offer_other_details(m_offer) == self.__offer_other_details(offer):

                # To fix issue: BE-785
                if m_offer.source == 'lb' and m_offer.id != offer.id:
                    continue
                if not search_offer_found:
                    logger.info(dict(message="Adding viewed offer", source="__update_matched_web_results",
                                     merged_offer=m_offer))
                    m_offer = updated_searched_offer(m_offer)
                    search_offer_found = True
                else:
                    merged_offers.remove(m_offer)
                    continue

            # Calculating savings
            m_offer.savings = offer_price - m_price
        return merged_offers

    def __update_affiliate_urls(self, offers: List[Offer]) -> List[Offer]:
        lb_web_base_url = os.getenv('LB_WEB_BASE_URL', "https://s.web.littlebirdie.dev")
        for offer in offers:
            # updating offer_url with affiliate_url redirect link
            if offer.searched is False:
                offer.offer_url = f"{lb_web_base_url}/affiliate/redirect?offer_url={quote(offer.offer_url)}"
        return offers

    @staticmethod
    def __check_searched_present(merged_offers, offer) -> list:
        offer = updated_searched_offer(offer)
        if not merged_offers:
            merged_offers = [offer]
        if not any(obj.searched for obj in merged_offers):
            merged_offers.insert(0, offer)
        return merged_offers

    def __remaining_google_offers(
            self, google_offers, offer_slug_list, offers_details_list, offer_url_list, offer_short_slug_list
    ) -> list:
        for result in google_offers[:]:
            offer_other_details = self.__offer_other_details(result)
            if get_sanitised_link(result.offer_url.lower()) in offer_url_list or \
                    get_short_slug(result.offer_url.lower()) in offer_short_slug_list or \
                    offer_other_details in offers_details_list:
                google_offers.remove(result)

            offer_url_list.append(get_sanitised_link(result.offer_url.lower()))
            offer_slug_list.append(result.slug)
            offers_details_list.append(offer_other_details)
        return google_offers

    @staticmethod
    def __offer_other_details(offer) -> dict:
        title = offer.title.lower()
        details = {
            "title": re.sub('[^A-Za-z0-9]+', '', title),
            "store": offer.store_name.strip().lower()
        }
        return details
