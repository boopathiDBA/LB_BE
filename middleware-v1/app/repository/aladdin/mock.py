from typing import List, Union

from app.model.entities import Offer, OfferAttributes
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput


class MockAladdin(IOffer):
    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(self, link: str) -> Union[OfferAttributes, bool]:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass
