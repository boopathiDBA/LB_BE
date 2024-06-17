import abc
import sys
from datetime import datetime

from app.model.entities import Offer, OfferAttributes
from typing import List, Union

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import TypedDict
else:  # pragma: no cover
    from typing_extensions import TypedDict


class AttributeSearchInput(TypedDict):
    title: str
    product_id: int
    brand: str
    gpid: str
    viewing_url: str
    # raw_department: str


class _SearchOffersInput(TypedDict):
    # required parameters in offer
    # URL is the only required attribute for backward compatibility
    url: str


class SearchOffersInput(_SearchOffersInput, total=False):
    # required parameters in offer.
    # To make below attributes required, move attribute to ReqFindOfferInput class above
    name: str
    image: str
    stock: int
    price: float
    brand: str
    last_update: datetime
    sku: str
    gtin: str
    currency: str
    seller: str
    description: str
    department_name: str
    attrs: list


class IOffer(abc.ABC):
    @abc.abstractmethod
    def search_by_title(
            self, title: str
    ) -> List[Offer]:
        pass

    @abc.abstractmethod
    def search_by_link(
            self, link: str, wildcard_search: bool = True
    ) -> Offer:
        pass

    @abc.abstractmethod
    def get_offer_info(
            self, search_input: SearchOffersInput
    ) -> Offer:
        pass

    @abc.abstractmethod
    def search_by_links(
            self, google_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        pass

    @abc.abstractmethod
    def search_attributes_by_link(
            self, link: str
    ) -> OfferAttributes:
        pass

    @abc.abstractmethod
    def search_attributes_by_id(
            self, link: str
    ) -> Union[OfferAttributes, bool]:
        pass

    @abc.abstractmethod
    def search_by_attributes(
            self, attr: AttributeSearchInput
    ) -> List[Offer]:
        pass


class IAffiliate(abc.ABC):
    @abc.abstractmethod
    def get_by_product_url(
            self, product_url: str
    ) -> str:
        pass
    