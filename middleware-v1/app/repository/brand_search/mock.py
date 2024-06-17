from typing import List, Union
from serpapi.serp_api_client_exception import SerpApiClientException

from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes


def get_mock_offer_attributes():
    data = {
        'default':
            OfferAttributes(title="Samsung T5300 32 Full HD HDR Smart TV", gpid="GOOGLE/PID/Default"),
        'TC1E':
            OfferAttributes(title="Samsung T5300 32 Full HD HDR Smart TV", gpid="GOOGLE/PID/Default"),
        'TC1L4':
            OfferAttributes(title="TC1L4 - Samsung T5300 32 Full HD HDR Smart TV"),
        'http://mocksite.com/TC1T':
            OfferAttributes(title="Samsung T5300 32 Full HD HDR Smart TV", brand='Samsung'),
        'GOOGLE/PID/TC1X':
            OfferAttributes(title="Samsung T5300 32 Full HD HDR Smart TV", brand='Samsung',
                            gpid="GOOGLE/PID/TC1X")
    }
    return data


class MockBrandSearch(IOffer):
    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        mock_data = get_mock_offer_attributes()
        if id in mock_data.keys():
            return mock_data.get(id)
        else:
            pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        pass


class MockBrandSearchTC1T(MockBrandSearch):
    pass
