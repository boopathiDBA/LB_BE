from typing import List

import marshmallow_dataclass

from app.helpers.error import TitleNotFoundException, NotFoundException
from app.model.entities import Offer, OfferAttributes
from app.repository import IOffer, AttributeSearchInput, SearchOffersInput


def get_mock_offer_data():
    data = {
        "http://mocksite.com/TC1D":
            Offer(title='TC1D - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1E":
            Offer(title='TC1E - Samsung T5300 32 Full HD HDR Smart TV',
                  link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1F":
            Offer(title='TC1F - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1G":
            Offer(title='TC1G - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1H":
            Offer(title='TC1H - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1I":
            Offer(title='TC1I - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1J":
            Offer(title='TC1J - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1L":
            Offer(title='TC1H - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1R":
            Offer(title='TC1R - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1S":
            Offer(title='TC1S - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1U":
            Offer(title='TC1U - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/EXC3":
            Offer(title='EXC3 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC2B":
            Offer(title='TC2B - Samsung T5300 32 Full HD HDR Smart TV',
                  link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC2C":
            Offer(title='TC2C - Samsung T5300 32 Full HD HDR Smart TV',
                  link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "default":
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, store_name='Samsung')
    }
    return data


def get_mock_web_offers():
    data = {
        'MockWebOffer': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', 'image': 'N/A',
                 'price': 545, 'store_name': 'Samsung',
                 'in_stock': False, 'source': "lb"}
             },
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                 'in_stock': True, 'store_name': 'TV Store',
                 'source': "lb"}
             }
        ],
        'MockWebOfferTC1E': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', 'image': 'N/A',
                 'price': 545, 'store_name': 'Samsung',
                 'in_stock': False, 'source': "gs"}},
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                 'in_stock': True, 'store_name': 'TV Store',
                 'source': "gs"}}
        ],
        'MockWebOfferTC1F': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                 'image': 'http://image_url.com/update',
                 'price': 545, 'store_name': 'Samsung',
                 'in_stock': False, 'source': "gs"}},
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396',
                 'image': 'http://image_url.com/update', 'price': 399.9,
                 'in_stock': True, 'store_name': 'TV Store',
                 'source': "gs"}}
        ],
        'MockWebOfferTC1I': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', 'image': 'N/A',
                 'price': 545, 'store_name': 'Samsung',
                 'in_stock': False, 'source': "gs"}},
            {
                'id': 0,
                'attributes': {
                    'name': '75" Q60B QLED 4K Smart TV (2022)',
                    'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                    'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                    'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                    'in_stock': True, 'store_name': 'TV Store',
                    'source': "gs"}}
        ],
        'MockWebOfferTC1J': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', 'image': 'N/A',
                 'price': 545,
                 'in_stock': False, 'source': "lb"}},
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                 'in_stock': True,
                 'source': "lb"}}
        ],
        'MockWebOfferTC1S': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/affiliate',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/affiliate',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015/affiliate', 'image': 'N/A',
                 'price': 545,
                 'in_stock': False, 'source': "lb"}},
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                 'in_stock': True,
                 'source': "lb"}}
        ],
        'MockWebOfferTC1U': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/affiliate',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/affiliate',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015/affiliate', 'image': 'N/A',
                 'price': 545,
                 'in_stock': False, 'source': "lb"}},
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 2499.9,
                 'in_stock': True,
                 'source': "lb"}}
        ],
        'MockWebOfferTC2C': [
            {'id': 0,
             'attributes': {
                 'name': 'Samsung T5300 32 Full HD HDR Smart TV',
                 'affiliate_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'product_url': 'https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 'slug': 'samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', 'image': 'N/A',
                 'price': 545, 'store_name': 'Samsung',
                 'in_stock': False, 'source': "lb"}
             },
            {'id': 0,
             'attributes': {
                 'name': '75" Q60B QLED 4K Smart TV (2022)',
                 'affiliate_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'product_url': 'https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                 'slug': '75-q60b-qled-4k-smart-tv-2022-517422396', 'image': 'N/A', 'price': 500,
                 'in_stock': True, 'store_name': 'TV Store',
                 'source': "lb"}
             }
        ]

    }
    return data


class MockWebOffer(IOffer):
    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_link(self, link: str) -> Offer:
        if link in ["http://mocksite.com/TC1B", "http://mocksite.com/TC1W", "http://mocksite.com/TC1W/"]:
            return []
        elif link == "http://mocksite.com/TC1C":
            raise NotImplemented
        elif link == "http://mocksite.com/EXC1":
            raise NotFoundException
        elif link == "http://mocksite.com/EXC4":
            raise NotFoundException
        else:
            mock_data = get_mock_offer_data()
            return mock_data.get(link) if link in mock_data.keys() else mock_data.get('default')

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> List[dict]:
        return get_mock_web_offers().get(self.__class__.__name__)


class MockWebOfferTC1E(MockWebOffer):
    pass


class MockWebOfferTC1F(MockWebOffer):
    pass


class MockWebOfferTC1I(MockWebOffer):
    pass


class MockWebOfferTC1J(MockWebOffer):
    pass


class MockWebOfferTC1S(MockWebOffer):
    pass


class MockWebOfferTC1U(MockWebOffer):
    pass


class MockWebOfferTC2C(MockWebOffer):
    pass
