from typing import List, Union

from app.helpers.error import NotFoundException
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
                  in_stock=False, gpid="GOOGLE/PID/Default"),
        "http://mocksite.com/TC1F":
            Offer(title='TC1F - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, gpid="GOOGLE/PID/Default"),
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
            Offer(title='TC1L - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1L1":
            Offer(title='TC1L1 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1L2":
            Offer(title='TC1L2 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1L3":
            Offer(title='TC1L3 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1L4":
            Offer(title='TC1L4 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, store_name="Samsung", source='lb', id="TC1L4"),
        "http://mocksite.com/TC1R":
            Offer(title='TC1R - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False),
        "http://mocksite.com/TC1RA":
            Offer(title='TC1RA - Samsung T5300 32 Full HD HDR Smart TV',
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
        "http://mocksite.com/TC1X":
            Offer(title='TC1X - Samsung T5300 32 Full HD HDR Smart TV', id="GOOGLE/PID/TC1X",
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
                  in_stock=False, store_name='Samsung', gpid="GOOGLE/PID/Default")
    }
    return data


def get_mock_data() -> dict:
    data = {
        "TC1J - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, source='lb', store_name="Samsung"),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=499.0, in_stock=False,
                  source='lb')
        ],
        "TC1G - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1H - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.85),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1I - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=1545,
                  in_stock=False, source="lb", store_name='Samsung'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.9, in_stock=True,
                  source="lb", store_name='TV Store')
        ],
        "TC1L - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1L1 - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1L2 - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                  offer_url='https://www.jbhifi.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full-slug',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full-slug',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1L3 - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.myer.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.myer.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8, store_name='Samsung'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1L4 - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='TC1L4 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, store_name="Samsung", source='lb', id='TC1L4'),
            Offer(title='TC1L4 - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/2',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/2',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, store_name="Samsung", source='lb'),
        ],
        "TC1R - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.00, in_stock=False,
                  source='lb', ops_score=0.85)
        ],
        "TC1RA - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=545.00, in_stock=False,
                  source='lb', ops_score=0.85),
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545.0,
                  in_stock=False, source='lb', ops_score=0.8)
        ],
        "TC1S - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015/affiliate', image_url='N/A', price=545,
                  in_stock=False, source="lb", searched=True),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=499.9, in_stock=True,
                  source="lb", af=True, ops_score=0.85)
        ],
        "TC1U - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=45,
                  in_stock=False, source="lb", store_name='Samsung'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.9, in_stock=True,
                  source="lb", store_name='TV Store')
        ],
        "TC1W - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='TC1W - Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, source="lb", store_name='Samsung', id='TC1W'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.9, in_stock=True,
                  source="lb", store_name='TV Store')
        ],
        "TC1X - Samsung T5300 32 Full HD HDR Smart TV": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV', id="GOOGLE/PID/TC1X",
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, source="lb", store_name='Samsung'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.9, in_stock=True,
                  source="lb", store_name='TV Store')
        ],
        "default": [
            Offer(title='Samsung T5300 32 Full HD HDR Smart TV',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='samsung-t5300-32-full-hd-smart-led-tv-2020-296499015', image_url='N/A', price=545,
                  in_stock=False, source="lb", store_name='Samsung'),
            Offer(title='75" Q60B QLED 4K Smart TV (2022)',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='75-q60b-qled-4k-smart-tv-2022-517422396', image_url='N/A', price=2499.9, in_stock=True,
                  source="lb", store_name='TV Store')
        ]
    }
    return data


class MockOpenSearch(IOffer):
    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
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

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_attributes_by_link(self, link: str) -> OfferAttributes:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_by_attributes(self, offer_attr: AttributeSearchInput) -> List[Offer]:
        title = offer_attr.get('title')
        mock_data = get_mock_data()
        return mock_data.get(title) if title in mock_data.keys() else mock_data.get('default')
