import json
import pytest
import os
import requests
import uuid
import marshmallow
from dataclasses import dataclass
from serpapi.serp_api_client_exception import SerpApiClientException
from app.helpers.error import TitleNotFoundException, UnprocessableEntityException
from app.repository import IOffer, SearchOffersInput
from app.repository.brand_search.mock import MockBrandSearch, MockBrandSearchTC1T
from app.repository.brand_search import BrandSearch
from app.repository.google_shopping.mock import MockGoogleSearch
from app.repository.opensearch.mock import MockOpenSearch
from app.repository.opensearch import OpensearchOffers
from app.repository.scraping_api.mock import MockScrapingAPI
from app.repository.web_offer.mock import MockWebOffer, MockWebOfferTC1E, MockWebOfferTC1I, MockWebOfferTC1F, \
    MockWebOfferTC1S, MockWebOfferTC1U
from app.usecase.mock import MockSearchUseCase_V2
from app.repository.aladdin.mock import MockAladdin
from app.usecase import SearchUseCase
from app.settings import SConfig

sconfig = SConfig()


def say_hello(name: str) -> str:
    return f"Hello {name}"


def tojson(i):
    return json.dumps(i, default=lambda o: o.__dict__, sort_keys=True, indent=4)


# ------------------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------------------
@dataclass
class TestCase:
    __test__ = False  # False since @dataclass
    name: str
    search_input: SearchOffersInput
    _google_repo: IOffer
    _opensearch_repo: IOffer
    _scraping_repo: IOffer
    _brand_repo: IOffer
    _aladdin_repo: IOffer
    expected: any
    _test_exception: bool
    _allow_google_search: bool


class TestFindOffersUseCase:
    test_cases = [
        TestCase(name="Test when GTIN matched",
                 search_input=dict(url="http://mocksite.com/tc1a"),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase_V2("gtin_match", ops_ingest=True, condition=True), _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when GTIN without department matched",
                 search_input=dict(url="http://mocksite.com/tc5a"),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase_V2("gtin_match", ops_ingest=False, condition=False), _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when MPN matched",
                 search_input=dict(url="http://mocksite.com/tc6a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("mpn_match", ops_ingest=False, condition=True), _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when ProductID matched",
                 search_input=dict(url="http://mocksite.com/tc11a",name="Product ID ONLY MATCH - 11"),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase_V2("product_id_match", ops_ingest=False, condition=True), _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when UPC matched",
                 search_input=dict(url="http://mocksite.com/tc14a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("upc_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when ISBN matched",
                 search_input=dict(url="http://mocksite.com/tc17a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("isbn_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when EAN matched",
                 search_input=dict(url="http://mocksite.com/tc20a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("ean_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when GPID matched",
                 search_input=dict(url="http://mocksite.com/tc22a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("gpid_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when MPN and Model matched",
                 search_input=dict(url="http://mocksite.com/tc24a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("mpn_model_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test when Model and MPN matched",
                 search_input=dict(url="http://mocksite.com/tc26a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("model_mpn_match", ops_ingest=False, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),
        TestCase(name="Test market place rules",
                 search_input=dict(url="http://mocksite.com/tc28a"), _aladdin_repo=MockAladdin(),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=OpensearchOffers(sconfig),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=BrandSearch(),
                 expected=MockSearchUseCase_V2("market_place", ops_ingest=True, condition=True),
                 _test_exception=False,
                 _allow_google_search=False),

    ]

    @pytest.mark.parametrize(
        "search_input,_google_repo,_opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo, expected, _test_exception, "
        "_allow_google_search,test_case_name",
        map(lambda x: (
                x.search_input, x._google_repo, x._opensearch_repo, x._scraping_repo,
                x._brand_repo, x._aladdin_repo, x.expected, x._test_exception, x._allow_google_search,x.name),
            test_cases),
        ids=map(lambda x: x.name, test_cases),
    )
    def test_find_offers(self, search_input, _google_repo, _opensearch_repo, _scraping_repo,
                         _brand_repo, _aladdin_repo, expected, _test_exception, _allow_google_search, test_case_name):
        search = SearchUseCase(_google_repo, _opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo,
                               _allow_google_search)
        if test_case_name == "Test market place rules":
            print("yay")
        if _test_exception:
            # Reference: https://docs.pytest.org/en/stable/reference/reference.html#pytest.raises
            with pytest.raises(expected) as expected_exc:
                actual_exc_type = search.find_offers(search_input)
                assert expected_exc.type == actual_exc_type
        else:
            expected = expected.find_offers(search_input)
            actual = search.find_offers(search_input)
            expected_list = json.loads(tojson(expected))
            actual_list = json.loads(tojson(actual))

            expected_dict = {each["id"]: each for each in expected_list}
            actual_dict = {each["id"]: each for each in actual_list}

            # assert len(expected_dict) == len(actual_dict)

            for expected_key, expected_value in expected_dict.items():
                actual_value = actual_dict.get(expected_key)
                assert actual_dict.get(expected_key)
                if actual_value:
                    assert expected_value.get("ops_score") == actual_value.get("ops_score")


if __name__ == "__main__":
    pytest.main()
