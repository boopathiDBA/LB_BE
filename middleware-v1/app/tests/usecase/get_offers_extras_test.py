import json

import pytest
from dataclasses import dataclass

from app.repository import SearchOffersInput
from app.repository.brand_search.mock import MockBrandSearch
from app.repository.google_shopping.mock import *
from app.repository.opensearch.mock import *
from app.repository.scraping_api.mock import *
from app.repository.web_offer.mock import *
from app.usecase.mock import *
from app.usecase import SearchUseCase


def toJSON(i):
    return json.dumps(i, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class TestCase:
    __test__ = False  # False since @dataclass
    name: str
    search_input: SearchOffersInput
    _google_repo: IOffer
    _web_repo: IOffer
    _opensearch_repo: IOffer
    _scraping_repo: IOffer
    _brand_repo: IOffer
    _aladdin_repo: IOffer
    expected: any
    _allow_google_search: bool


class TestGetExtrasUseCase:
    test_cases = [
        # TestCase(name="Test when savings of all the offers <= 0 ",
        #          search_input=dict(url="http://mocksite.com/TC2A"),
        #          _google_repo=MockGoogleSearch(), _web_repo=MockWebOffer(), _opensearch_repo=MockOpenSearch(),
        #          _scraping_repo=MockScrapingAPI(), _brand_repo=MockBrandSearch(),
        #          expected=MockSearchUseCaseTC2A(), _allow_google_search=True),
        # This Test case is not possible as of now, because viewing offer will always be present
        # TestCase(name="Test when savings are > 0 but no high confidence score ",
        #          link="http://mocksite.com/TC2B",
        #          _google_repo=MockGoogleSearch(), _web_repo=MockWebOffer(), _opensearch_repo=MockOpenSearch(),
        #          _scraping_repo=MockScrapingAPI(), _brand_repo=MockBrandSearch(),
        #          expected=MockSearchUseCaseTC2B()),
        # TestCase(name="Test when savings present with high confidence ",
        #          search_input=dict(url="http://mocksite.com/TC2C"),
        #          _google_repo=MockGoogleSearch(), _web_repo=MockWebOfferTC2C(), _opensearch_repo=MockOpenSearch(),
        #          _scraping_repo=MockScrapingAPI(), _brand_repo=MockBrandSearch(),
        #          expected=MockSearchUseCaseTC2C(), _allow_google_search=True),
    ]

    @pytest.mark.parametrize(
        "search_input,_google_repo,_web_repo,_opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo, expected, _allow_google_search",
        map(lambda x: (
                x.search_input, x._google_repo, x._web_repo, x._opensearch_repo, x._scraping_repo, x._brand_repo,
                x._aladdin_repo, x.expected, x._allow_google_search),
            test_cases),
        ids=map(lambda x: x.name, test_cases),
    )
    def test_get_offers_extras(self, search_input, _google_repo, _web_repo, _opensearch_repo, _scraping_repo, _brand_repo,
                               _aladdin_repo, expected, _allow_google_search):
        search = SearchUseCase(_google_repo, _opensearch_repo, _scraping_repo, _brand_repo, _aladdin_repo,
                               _allow_google_search)
        link = search_input.get("url")
        searched_offers = search.find_offers(search_input)
        actual = search.get_offers_extras(searched_offers)
        expected = expected.get_offers_extras(link)
        assert toJSON(actual) == toJSON(expected)


if __name__ == "__main__":
    pytest.main()
