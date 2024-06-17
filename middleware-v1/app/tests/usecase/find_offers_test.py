import json

import marshmallow
import pytest
from dataclasses import dataclass

from serpapi.serp_api_client_exception import SerpApiClientException

from app.helpers.error import TitleNotFoundException, UnprocessableEntityException
from app.repository import IOffer, SearchOffersInput
from app.repository.aladdin.mock import MockAladdin
from app.repository.brand_search.mock import MockBrandSearch, MockBrandSearchTC1T
from app.repository.google_shopping.mock import MockGoogleSearch
from app.repository.opensearch.mock import MockOpenSearch
from app.repository.scraping_api.mock import MockScrapingAPI
from app.repository.web_offer.mock import MockWebOffer, MockWebOfferTC1E, MockWebOfferTC1I, MockWebOfferTC1F, \
    MockWebOfferTC1S, MockWebOfferTC1U
from app.usecase.mock import MockSearchUseCase
from app.usecase import SearchUseCase


def say_hello(name: str) -> str:
    return f"Hello {name}"


def toJSON(i):
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
        TestCase(name="Test find_offers getting returned correctly",
                 search_input=dict(url="http://mocksite.com/TC1A"),
                 _google_repo=MockGoogleSearch(), _opensearch_repo=MockOpenSearch(),
                 _scraping_repo=MockScrapingAPI(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="When no title from WebOffer#search_by_link but ScrapingAPI#search_by_link return "
                      "correctly",
                 search_input=dict(url="http://mocksite.com/TC1B"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="When error from WebOffer#search_by_link but ScrapingAPI#search_by_link returns correctly",
                 search_input=dict(url="http://mocksite.com/TC1C"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="When no data returned from Google",
                 search_input=dict(url="http://mocksite.com/TC1D"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="When no data returned from Opensearch",
                 search_input=dict(url="http://mocksite.com/TC1E"),
                 _google_repo=MockGoogleSearch(),
                 _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test results matching with web results getting updated",
                 search_input=dict(url="http://mocksite.com/TC1F"),
                 _google_repo=MockGoogleSearch(),
                 _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test best results are coming as sorted based on ops_score and price",
                 search_input=dict(url="http://mocksite.com/TC1G"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test similar results are coming as sorted based on ops_score",
                 search_input=dict(url="http://mocksite.com/TC1H"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test sanitised google offer urls",
                 search_input=dict(url="http://mocksite.com/TC1I"),
                 _google_repo=MockGoogleSearch(),
                 _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test sanitised lb offer urls",
                 search_input=dict(url="http://mocksite.com/TC1J"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test offers are not duplicated based on offer_url",
                 search_input=dict(url="http://mocksite.com/TC1L"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test de duplication based on slug",
                 search_input=dict(url="http://mocksite.com/TC1L1"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test de duplication based on short slug",
                 search_input=dict(url="http://mocksite.com/TC1L2"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test de duplication based on title and store name",
                 search_input=dict(url="http://mocksite.com/TC1L3"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test viewing offer is not during from de-dup",
                 search_input=dict(url="http://mocksite.com/TC1L4"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test savings getting calculated properly",
                 search_input=dict(url="http://mocksite.com/TC1N"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test after merge offers matching with web offers getting updated when price is less",
                 search_input=dict(url="http://mocksite.com/TC1O"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test after merge offers matching with web offers getting updated when price is more",
                 search_input=dict(url="http://mocksite.com/TC1P"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                  expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test searched flag",
                 search_input=dict(url="http://mocksite.com/TC1Q"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test when searched flag is not best match",
                 search_input=dict(url="http://mocksite.com/TC1R"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Sort order when searched offer has same price as other products",
                 search_input=dict(url="http://mocksite.com/TC1RA"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test affiliate url getting updated if present in DB",
                 search_input=dict(url="http://mocksite.com/TC1S"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test result when raw_data is present for offer",
                 search_input=dict(url="http://mocksite.com/TC1T"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearchTC1T(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test offers with value less than 66% of average should be removed",
                 search_input=dict(url="http://mocksite.com/TC1U"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test when search url has restricted params",
                 search_input=dict(url="http://mocksite.com/TC1V#lb-gs=0"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test offer to be returned using browser scrapped data",
                 search_input=dict(url="http://mocksite.com/TC1W", name="TC1W - Samsung T5300 32 Full HD HDR Smart TV"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),
        TestCase(name="Test when google_pid present",
                 search_input=dict(url="http://mocksite.com/TC1X"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=MockSearchUseCase(), _test_exception=False, _allow_google_search=True),

        TestCase(name="URL not present in query parameters",
                 search_input=dict(name="Samsung T5300 32 Full HD HDR Smart TV"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=UnprocessableEntityException, _test_exception=True, _allow_google_search=True),

        TestCase(name="Test Not found Title",
                 search_input=dict(url="http://mocksite.com/EXC1"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=TitleNotFoundException, _test_exception=True, _allow_google_search=True),
        TestCase(name="Test url validation working",
                 search_input=dict(url="wrong/url/http://mocksite.com/EXC2"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=UnprocessableEntityException, _test_exception=True, _allow_google_search=True),
        TestCase(name="Test when SERP API throws error",
                 search_input=dict(url="http://mocksite.com/EXC3"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=SerpApiClientException, _test_exception=True, _allow_google_search=True),
        TestCase(name="Test when other ValidationError in entity",
                 search_input=dict(url="http://mocksite.com/EXC4"),
                 _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
                 _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(), _aladdin_repo=MockAladdin(),
                 expected=marshmallow.exceptions.ValidationError, _test_exception=True, _allow_google_search=True),
        # Add test case for when we have restricted params in Link
        # TestCase(name="Test when other ValidationError in entity",
        #        link="http://mocksite.com/EXC4",
        #        _google_repo=MockGoogleSearch(), _scraping_repo=MockScrapingAPI(),
        #        _opensearch_repo=MockOpenSearch(), _brand_repo=MockBrandSearch(),
        #        expected=marshmallow.exceptions.ValidationError, _test_exception=True, ALLOW_GOOGLE_SEARCH=True,
        #        RESTRICTED_PARAMS=["lb-gs=0"])

    ]

    @pytest.mark.parametrize(
        "search_input,_google_repo,_opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo, expected, _test_exception, "
        "_allow_google_search",
        map(lambda x: (
                x.search_input, x._google_repo, x._opensearch_repo, x._scraping_repo,
                x._brand_repo, x._aladdin_repo, x.expected, x._test_exception, x._allow_google_search),
            test_cases),
        ids=map(lambda x: x.name, test_cases),
    )
    def test_find_offers(self, search_input, _google_repo, _opensearch_repo, _scraping_repo,
                         _brand_repo, _aladdin_repo, expected, _test_exception, _allow_google_search):
        search = SearchUseCase(_google_repo, _opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo,
                               _allow_google_search, True)
        if _test_exception:
            # Reference: https://docs.pytest.org/en/stable/reference/reference.html#pytest.raises
            with pytest.raises(expected) as expected_exc:
                actual_exc_type = search.find_offers(search_input)
                assert expected_exc.type == actual_exc_type
        else:
            actual = search.find_offers(search_input)
            expected = expected.find_offers(search_input)
            assert toJSON(actual) == toJSON(expected)


if __name__ == "__main__":
    pytest.main()
