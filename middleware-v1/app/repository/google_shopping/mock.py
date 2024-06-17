from typing import List, Union
from serpapi.serp_api_client_exception import SerpApiClientException

from app.repository import IOffer, AttributeSearchInput, SearchOffersInput
from app.model.entities import Offer, OfferAttributes


def get_mock_data() -> dict:
    data = {
            "TC1G - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                                '?param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=True,
                      source='gs', ops_score=0.7)
            ],
            "TC1H - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                                '?param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy'
                                '?param=true',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7)
            ],
            "TC1I - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                                '?param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=1545,
                      in_stock=False, source='gs', store_name="Samsung"),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy'
                                '?param=true',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs')
            ],
            "TC1J - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', store_name='TV Store')
            ],
            "TC1L - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                                '?param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='/https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7)
            ],
            "TC1L1 - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                            '?blacklist_param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='/https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7)
            ],
            "TC1L2 - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/full'
                                '-slug'
                                '?blacklist_param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full'
                           '-slug',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy'
                                '/full-slug',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='/https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full'
                           '-slug',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy'
                                '/full-slug',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', ops_score=0.7)
            ],
            "TC1L3 - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', store_name='TV Store')
            ],
            "TC1L4 - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='TC1L4 - Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', store_name='TV Store')
            ],
            "TC2B - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020'
                                '?param=true',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', ops_score=0.9),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='/goto/deal/75-q60b-qled-4k-smart-tv-2022-517422396',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy'
                                '?param=true',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=499.00, in_stock=False,
                      source='gs', ops_score=0.5)
            ],
            "TC1R - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs')
            ],
            "TC1S - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015/', image_url='N/A', price=545.0,
                      in_stock=False, source='gs'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=True,
                      source='gs')
            ],
            "TC1U - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015/', image_url='N/A', price=45.0,
                      in_stock=False, source='gs'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=True,
                      source='gs')
            ],
            "TC2C - Samsung T5300 32 Full HD HDR Smart TV": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='/goto/deal/samsung-t5300-32-full-hd-smart-led-tv-2020-296499015',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='/goto/deal/75-q60b-qled-4k-smart-tv-2022-517422396',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=500, in_stock=False,
                      source='gs', store_name='TV Store', confidence='high')
            ],
            "default": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gs', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gs', store_name='TV Store')
            ],
            "GOOGLE/PID/TC1X": [
                Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                      link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                      slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                      in_stock=False, source='gp', store_name='Samsung'),
                Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                      link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                      slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                      source='gp', store_name='TV Store')
            ]
        }
    return data


class MockGoogleSearch(IOffer):
    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        pass

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    def search_by_attributes(self, attr: AttributeSearchInput) -> List[Offer]:
        if attr.get('gpid') == "GOOGLE/PID/TC1X":
            return get_mock_data().get('GOOGLE/PID/TC1X')
        elif attr.get('gpid') == "GOOGLE/PID/Default":
            return get_mock_data().get('default')
        else:
            pass

    def search_by_title(self, title: str) -> List[Offer]:
        if title == "TC1D - Samsung T5300 32 Full HD HDR Smart TV":
            return []
        elif title == "EXC3 - Samsung T5300 32 Full HD HDR Smart TV":
            raise SerpApiClientException
        else:
            mock_data = get_mock_data()
            return mock_data.get(title) if title in mock_data.keys() else mock_data.get('default')
