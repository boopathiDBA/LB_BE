import urllib.parse
from pathlib import Path
from typing import Union

from cachetools import TTLCache, cached

from app.repository import IAffiliate
from app.helpers.db import WebDBHelper
from app.helpers.log import logger
from app.repository.web_affiliate.constants import unwantedUrls
from app.helpers.error import NotFoundException


class WebAffiliate(IAffiliate):
    def __init__(self) -> None:
        self._webdb_helper = WebDBHelper()

        suffix_list = open(Path.cwd() / "app" / "repository" / "web_affiliate" / "suffix_list.txt", "r", encoding="utf-8")
        self._suffixes = suffix_list.read().splitlines()
        self._suffixes.sort(key=len, reverse=True)

    @cached(cache=TTLCache(maxsize=10000, ttl=900))
    def _check_affiliate_status(self, tld, domain):
        sql_select = ("select * from affiliate_links.affiliate_parameters where"
                      " (affiliate_domain ilike %s or affiliate_domain ilike %s) and enabled = true")
        select_values = (tld, domain)

        select_result, webdb_error, webdb_error_message = self._webdb_helper.select_one(
            query=sql_select, values=select_values
        )
        # payload validation
        if webdb_error:
            logger.error(f"Error checking affiliate status: {webdb_error_message} => {logger.get_correlation_id()}")
            select_result = None

        return select_result

    def _match_suffix(self, domain):
        logger.debug(f"Matching domain suffix - {domain} => {logger.get_correlation_id()}")

        try:
            for suffix in self._suffixes:
                if domain.endswith(suffix):
                    return suffix
        except Exception as e:
            logger.warning(
                f"Failed to match suffix. Error: {e}, Domain: {domain}"
            )
        return None

    def _extract_domain(self, domain, suffix):
        logger.debug(f"Extracting domain: {domain} => {logger.get_correlation_id()}")
        domain = domain.replace(suffix, "")
        dot_position = domain.rfind(".")
        character_count = len(domain) - dot_position - 1
        return domain[-character_count:]

    def get_by_product_url(self, product_url: str) -> Union[str, None]:
        affiliate_url = product_url
        domain = urllib.parse.urlparse(product_url).netloc

        suffix = self._match_suffix(domain)
        if suffix is None:
            raise NotFoundException("Suffix did not match")

        tld = self._extract_domain(domain, suffix) + suffix

        # checks if it is already an affiliate link
        # We don't update these for time being
        for url in unwantedUrls:
            if url in product_url:
                raise NotFoundException("Unwanted url found")

        store_details = self._check_affiliate_status(tld, domain)
        if store_details is None:
            raise NotFoundException(f"Store Details not found for product_url: {product_url}")

        network = store_details[2].lower()
        merchant_id = store_details[3]

        if network == "ebay":
            if "?" in product_url:
                join_char = "&"
            else:
                join_char = "?"

            affiliate_url = (
                    product_url
                    + join_char
                    + "mkcid=1&mkrid=705-53470-19255-0&siteid=15&campid=5338753876&customid=&toolid=10001&mkevt=1"
            )

        if network == "amazon":
            if "?" in product_url:
                join_char = "&"
            else:
                join_char = "?"

            affiliate_url = product_url + join_char + "tag=littlebirdie-22"
            affiliate_url.replace("tag=AssocId&", "")

        if network == "cf" or network == "commission factory":
            affiliate_url = (
                    "https://t.cfjump.com/70775/t/"
                    + merchant_id
                    + "?Url="
                    + urllib.parse.quote(product_url)
            )

        if network == "awin":
            affiliate_url = (
                    "https://awin1.com/cread.php?awinaffid=779937&awinmid="
                    + merchant_id
                    + "&ued="
                    + urllib.parse.quote(product_url)
            )

        if network == "rakuten":
            affiliate_url = (
                    "https://click.linksynergy.com/deeplink?id=v6k2tRUjNjc&mid="
                    + merchant_id
                    + "&murl="
                    + urllib.parse.quote(product_url)
            )

        if network == "impact":
            affiliate_url = (
                    "https://" + merchant_id + "?u=" + urllib.parse.quote(product_url)
            )

        if network == "partnerize":
            affiliate_url = (
                    "https://"
                    + merchant_id
                    + "/destination:"
                    + urllib.parse.quote(product_url)
            )

        if network == "cj":
            affiliate_url = (
                    "https://www.dpbolvw.net/click-100259730-"
                    + merchant_id
                    + "?url="
                    + urllib.parse.quote(product_url)
            )

        # Catch edge case where gets here but no network
        # Logging out to work out how / why
        try:
            affiliate_url
        except NameError:
            logger.debug(
                f"product_url didn't work: {product_url} => {logger.get_correlation_id()}"
            )
            raise NotFoundException("Created affiliate url is corrupt")

        if affiliate_url is None:
            raise NotFoundException("Affiliate url could not be evaluated")

        return affiliate_url
