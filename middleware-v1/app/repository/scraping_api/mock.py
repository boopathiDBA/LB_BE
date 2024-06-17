from typing import List, Union

import marshmallow_dataclass

from app.helpers.error import TitleNotFoundException
from app.model.entities import Offer, OfferAttributes
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput


def get_mock_data() -> dict:
    data = {
            "http://mocksite.com/TC1B": dict(
                title='TC1B - Samsung T5300 32 Full HD HDR Smart TV',
                link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                in_stock=False
            ),
            "http://mocksite.com/TC1C": dict(
                title='TC1C - Samsung T5300 32 Full HD HDR Smart TV',
                link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                in_stock=False, gpid='GOOGLE/PID/Default'
            ),
            "http://mocksite.com/TC1W": dict(
                title='TC1W - Samsung T5300 32 Full HD HDR Smart TV',
                link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                in_stock=False
            ),
            "default": dict(
                title='Samsung T5300 32 Full HD HDR Smart TV',
                link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                in_stock=False
            )
        }
    return data


class MockScrapingAPI(IOffer):
    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        if search_input.get("url") == "http://mocksite.com/TC1B":
            return []
        elif search_input.get("url") == "http://mocksite.com/TC1W":
            mock_data = get_mock_data()
            offer = Offer(**mock_data["http://mocksite.com/TC1W"])
            offer.id = "TC1W"
            return offer
        else:
            pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        if link == "http://mocksite.com/EXC1":
            raise TitleNotFoundException
        elif link == "http://mocksite.com/EXC4":
            schema = marshmallow_dataclass.class_schema(Offer)()
            return schema.load(dict(title=None, in_stock=100))
        else:
            mock_data = get_mock_data()
            return Offer(**mock_data[link]) if link in mock_data.keys() else Offer(**mock_data["default"])