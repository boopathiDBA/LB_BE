from urllib.parse import quote

from app.helpers.error import UnprocessableEntityException
from app.repository.google_shopping import *
from app.usecase import IUseCase
from typing import List
import json
import requests
import os
import uuid
from app.helpers import offer_object
from pathlib import Path
from app.repository.helpers import Support


def get_mock_offers():
    data = {
        'http://mocksite.com/TC1D': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price="2499.90", in_stock=True, confidence='low',
                  searched=False, source='lb', ops_score=0.0, savings="-1954.90")
        ],
        'http://mocksite.com/TC1E': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ],
        'http://mocksite.com/TC1F': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False,
                  confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ],
        'http://mocksite.com/TC1G': [
            Offer(confidence="high", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  offer_url="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  ops_score=2, price=545, savings=0, searched=True,
                  slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020", source="lb",
                  store_name="anonymous-link", title="Samsung T5300 32 Full HD HDR Smart TV"),
            Offer(confidence="low", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  offer_url="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  ops_score=0.85, price=2499, savings=-1954, searched=False,
                  slug="samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy", source="lb",
                  store_name="anonymous-link", title="75\" Q60B QLED 4K Smart TV (2022)")
        ],
        'http://mocksite.com/TC1H': [
            Offer(confidence="high", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  offer_url="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  ops_score=2, price=545, savings=0, searched=True,
                  slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020", source="lb",
                  store_name="anonymous-link", title="Samsung T5300 32 Full HD HDR Smart TV"),
            Offer(confidence="low", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  offer_url="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  ops_score=0.85, price=2499, savings=-1954, searched=False,
                  slug="samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy", source="lb",
                  store_name="anonymous-link", title="75\" Q60B QLED 4K Smart TV (2022)")
        ],
        'http://mocksite.com/TC1I': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=1545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=-1000),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price='2499.90', in_stock=True, confidence='low',
                  searched=False, source='lb', ops_score=0.0, savings='-1954.90')
        ],
        'http://mocksite.com/TC1J': [
            Offer(confidence="high", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  offer_url="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  ops_score=2, price=545, savings=0, searched=True,
                  slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020", source="lb",
                  store_name="Samsung", title="Samsung T5300 32 Full HD HDR Smart TV"),
            Offer(confidence="low", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  offer_url="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  ops_score=0.0, price=499, savings=46, searched=False,
                  slug="samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy", source="lb",
                  store_name="anonymous-link", title="75\" Q60B QLED 4K Smart TV (2022)")
        ],
        'http://mocksite.com/TC1L': [
            Offer(confidence="high", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  offer_url="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  ops_score=2,
                  price=545, savings=0, searched=True,
                  slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  source="lb", store_name="anonymous-link", title="Samsung T5300 32 Full HD HDR Smart TV"),
            Offer(confidence="low", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  offer_url="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy",
                  ops_score=0.85,
                  price=2499, savings=-1954, searched=False,
                  slug="samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy", source="lb",
                  store_name="anonymous-link", title="75\" Q60B QLED 4K Smart TV (2022)"),
        ],
        'http://mocksite.com/TC1L1': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  image_url='N/A', store_name='anonymous-link', price=2499, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.85, savings=-1954)
        ],
        'http://mocksite.com/TC1L2': [
            Offer(id=0, title='TC1L2 - Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='gs', ops_score=0.0, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full-slug',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full-slug',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/full-slug',
                  image_url='N/A', store_name='anonymous-link', price=2499, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.85, savings=-1954),
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                  offer_url='https://www.jbhifi.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020/full-slug',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.8, savings=0),
        ],
        'http://mocksite.com/TC1L3': [
            Offer(id=0, title='TC1L3 - Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='gs', ops_score=0.0, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  image_url='N/A', store_name='anonymous-link', price=2499, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.85, savings=-1954),
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.myer.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='myer.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.myer.com.au/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.8, savings=0),
        ],
        "http://mocksite.com/TC1L4": [
            Offer(id='TC1L4', title='TC1L4 - Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020/1',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ],
        'http://mocksite.com/TC1Q': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ],
        'http://mocksite.com/TC1R': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  image_url='N/A', store_name='anonymous-link', price=2499, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.85, savings=-1954)
        ],
        'http://mocksite.com/TC1RA': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.85, savings=0)
        ],
        'http://mocksite.com/TC1S': [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                 link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                 slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                 offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020', xpath_obj=None,
                 image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                 searched=True, source='lb', ops_score=2, savings=0, product_id=None, attrs=None,
                 gpid=None, department_name="", origin_store_id=None, vendor_id=None, source_id=None, af=False),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                 link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy',
                 offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy', xpath_obj=None,
                 image_url='N/A', store_name='anonymous-link', price="499.90", in_stock=True, confidence='low',
                 searched=False, source='lb', ops_score=0.851, savings="45.10", product_id=None, attrs=None,
                 gpid=None, department_name="", origin_store_id=None, vendor_id=None, source_id=None, af=True)
        ],
        'http://mocksite.com/TC1U': [
            Offer(confidence="high", description="anonymous-description", id=0, image_url="N/A", in_stock=False,
                  link="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  offer_url="https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020",
                  ops_score=2, price=45, product_id=None, savings=500, searched=True,
                  slug="jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020", source="lb",
                  store_name="Samsung", title="Samsung T5300 32 Full HD HDR Smart TV"),
            Offer(confidence="low", description="anonymous-description", id=0, image_url="N/A", in_stock=True,
                  link="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/",
                  offer_url="https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/",
                  ops_score=0.0, price="2499.90", product_id=None, savings="-1954.90", searched=False,
                  slug="samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/", source="lb",
                  store_name="TV Store", title="75\" Q60B QLED 4K Smart TV (2022)")
        ],
        "http://mocksite.com/TC1V#lb-gs=0": [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price="2499.90", in_stock=True, confidence='low',
                  searched=False, source='lb', ops_score=0.0, savings="-1954.90")
        ],
        "http://mocksite.com/TC1W": [
            Offer(id='TC1W', title='TC1W - Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ],
        "http://mocksite.com/TC1X": [
            Offer(id='GOOGLE/PID/TC1X', title='TC1X - Samsung T5300 32 Full HD HDR Smart TV',
                  description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='anonymous-link', price=545, in_stock=False, confidence='high',
                  searched=True, source='gs', ops_score=0.0, savings=0),
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV',
                  description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='low',
                  searched=False, source='lb', ops_score=0.0, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gp', ops_score=0.0, savings=-1954)
        ],
        "default": [
            Offer(id=0, title='Samsung T5300 32 Full HD HDR Smart TV', description='anonymous-description',
                  link='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  slug='jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  offer_url='https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020',
                  image_url='N/A', store_name='Samsung', price=545, in_stock=False, confidence='high',
                  searched=True, source='lb', ops_score=2, savings=0),
            Offer(id=0, title='75" Q60B QLED 4K Smart TV (2022)', description='anonymous-description',
                  link='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  slug='samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  offer_url='https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/',
                  image_url='N/A', store_name='TV Store', price=2499, in_stock=False, confidence='low',
                  searched=False, source='gs', ops_score=0.0, savings=-1954)
        ]
    }
    return data


class MockSearchUseCase(IUseCase):
    def __init__(self):
        self._google_repo = IOffer
        self._web_repo = IOffer
        self._opensearch_repo = IOffer
        self._scraping_repo = IOffer

    def merge_results(
            self, google_offers: List[Offer], lb_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        pass

    def get_offers_extras(
            self, searched_offers: List[Offer]
    ) -> dict:
        pass

    def find_offers(
            self, search_input: SearchOffersInput
    ) -> List[Offer]:
        link = search_input.get("url")
        mock_data = get_mock_offers()
        if not link:
            raise UnprocessableEntityException
        # elif link == 'http://mocksite.com/TC1S':
        #     offers = mock_data.get(link)
        #     schema = marshmallow_dataclass.class_schema(Offer)()
        #     results = []
        #     for offer in offers:
        #         offer = schema.load(offer)
        #         result_price = Support.convert_to_int(offer.price)
        #         result_savings = Support.convert_to_int(float(offer.savings))
        #         offer.price = result_price if type(result_price) is int else "%0.2f" % offer.price
        #         offer.savings = result_savings if type(result_savings) is int else "%0.2f" % offer.savings
        #         results.append(offer)
        #     return results
        else:
            lb_web_base_url = os.getenv('LB_WEB_BASE_URL', "https://s.web.littlebirdie.dev")
            res = mock_data.get(link) if link in mock_data.keys() else mock_data.get('default')
            for x in res:
                if not x.searched:
                    x.offer_url = f"{lb_web_base_url}/affiliate/redirect?offer_url={quote(x.offer_url)}"
            return res


def get_searched_offers_extras():
    data = {
        'MockSearchUseCaseTC2A': dict(price_alert=False, savings=None, product="Samsung T5300 32 Full HD HDR Smart TV"),
        'MockSearchUseCaseTC2B': dict(price_alert=False, savings=None, product="Samsung T5300 32 Full HD HDR Smart TV"),
        'MockSearchUseCaseTC2C': dict(price_alert=False, savings="$45", product='75" Q60B QLED 4K Smart TV (2022)')
    }
    return data


class MockSearchUseCaseExtra(IUseCase):
    def __init__(self):
        self._google_repo = IOffer
        self._web_repo = IOffer
        self._opensearch_repo = IOffer
        self._scraping_repo = IOffer

    def merge_results(
            self, google_offers: List[Offer], lb_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        pass

    def get_offers_extras(
            self, searched_offers: List[Offer]
    ) -> dict:
        return get_searched_offers_extras().get(self.__class__.__name__)

    def find_offers(
            self, search_input: SearchOffersInput
    ) -> List[Offer]:
        pass


class MockSearchUseCaseTC2A(MockSearchUseCaseExtra):
    pass


class MockSearchUseCaseTC2B(MockSearchUseCaseExtra):
    pass


class MockSearchUseCaseTC2C(MockSearchUseCaseExtra):
    pass


json_file_path = (Path(__file__).parent / "../tests/usecase/ops_deals_sample.json").resolve()

with open(json_file_path, 'r') as json_file:
    json_data = json.load(json_file)
def create_ops_doc(input_doc):
    json_template = json_data.copy()
    for key, value in input_doc.items():
        json_template[key] = value
        if key == "id" and not input_doc.get("store_name"):
            json_template["store_name"] = str(value)
    json_template["expiry_date"] = "pytest"
    return json_template

def index_fixtures(ops_ingest : bool =False):
    opensearch_test_deals=[]
    deals_index = "a_deals"
    open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
    headers = {'Content-type': 'application/json'}
    # id,name,description,gtin,department_name,price,brand,brand_name,brand_id,product_url,be_product_url
    input_docs = [
        {"gtin_match": dict(id=1, source_id=1, name=f"GTIN ONLY MATCH {uuid.uuid4()}", product_url="http://mocksite.com/tc1a",
                            image_url="http://mocksite.com/tc1a",
                            be_product_url="http://mocksite.com/tc1a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", gtin="1GTIN",condition=True)
        },
        {"gtin_match": dict(id=2, source_id=2, name=f"GTIN ONLY MATCH {uuid.uuid4()}", product_url="http://mocksite.com/tc2a",
                            image_url="http://mocksite.com/tc2a",
                            be_product_url="http://mocksite.com/tc2a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", gtin="1GTIN",condition=True)
         },
        {"gtin_match": dict(id=3, source_id=3, name=f"GTIN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc3a",
                            image_url="http://mocksite.com/tc3a",
                            be_product_url="http://mocksite.com/tc3a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", gtin="2GTIN",condition=False)
         },
        {"gtin_match": dict(id=4, source_id=4, name=f"GTIN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc4a",
                            image_url="http://mocksite.com/tc4a",
                            be_product_url="http://mocksite.com/tc4a", department_name="Appliances",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", gtin="1GTIN",
                            condition=False)
         },
        {"gtin_match": dict(id=5, source_id=5, name=f"GTIN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc5a",
                            image_url="http://mocksite.com/tc5a",
                            be_product_url="http://mocksite.com/tc5a", department_name=None,
                            category_name=None,
                            subcategory_name=None, gtin="1GTIN",
                            condition=False)
         },
        # mpn
        {"mpn_match": dict(id=6, source_id=6, name=f"MPN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc6a",
                            image_url="http://mocksite.com/tc6a",
                            be_product_url="http://mocksite.com/tc6a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",brand="nike",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", mpn="1MPN",
                            condition=True)
         },
        {"mpn_match": dict(id=7, source_id=7, name=f"MPN ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc7a",
                           image_url="http://mocksite.com/tc7a",
                           be_product_url="http://mocksite.com/tc7a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware", brand="Nike",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", mpn="1MPN",
                           condition=True)
         },
        {"mpn_match": dict(id=8, source_id=8, name=f"MPN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc8a",
                            image_url="http://mocksite.com/tc8a",
                            be_product_url="http://mocksite.com/tc8a", department_name=None,
                            category_name=None,brand="Adidas",
                            subcategory_name=None, mpn="1MPN",
                            condition=False)
         },
        {"mpn_match": dict(id=9, source_id=9, name=f"MPN ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc9a",
                           image_url="http://mocksite.com/tc9a",
                           be_product_url="http://mocksite.com/tc9a", department_name=None,
                           category_name=None, brand=None,
                           subcategory_name=None, mpn="1MPN",
                           condition=False)
         },
        {"mpn_match": dict(id=10, source_id=10, name=f"MPN ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc10a",
                           image_url="http://mocksite.com/tc10a",
                           be_product_url="http://mocksite.com/tc10a", department_name=None,
                           category_name=None, brand="nike",
                           subcategory_name=None, mpn="2MPN",
                           condition=False)
         },
        {"product_id_match": dict(id=11, source_id=11, name=f"Product ID ONLY MATCH - 11",
                           product_url="http://mocksite.com/tc11a",
                           image_url="http://mocksite.com/tc11a",
                           be_product_url="http://mocksite.com/tc11a", department_name="Electronics",
                           category_name=None, brand=None,
                           subcategory_name=None,product_id= "123",
                           condition=True)
         },
        {"product_id_match": dict(id=12, source_id=12, name=f"Product ID ONLY MATCH {uuid.uuid4()}",
                                  product_url="http://mocksite.com/tc12a",
                                  image_url="http://mocksite.com/tc12a",
                                  be_product_url="http://mocksite.com/tc12a", department_name=None,
                                  category_name=None, brand=None,
                                  subcategory_name=None, product_id="123",
                                  condition=True)
         },
        {"product_id_match": dict(id=13, source_id=13, name=f"Product ID ONLY MATCH {uuid.uuid4()}",
                                  product_url="http://mocksite.com/tc13a",
                                  image_url="http://mocksite.com/tc13a",
                                  be_product_url="http://mocksite.com/tc13a", department_name=None,
                                  category_name=None, brand=None,
                                  subcategory_name=None, product_id=None,
                                  condition=False)
         },
        # UPC
        {"upc_match": dict(id=14, source_id=14, name=f"UPC ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc14a",
                           image_url="http://mocksite.com/tc14a",
                           be_product_url="http://mocksite.com/tc14a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", upc="1UPC",
                           condition=True)
         },
        {"upc_match": dict(id=15, source_id=15, name=f"UPC ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc15a",
                           image_url="http://mocksite.com/tc15a",
                           be_product_url="http://mocksite.com/tc15a", department_name=None,
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", upc="1UPC",
                           condition=False)
         },
        {"upc_match": dict(id=16, source_id=16, name=f"UPC ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc16a",
                           image_url="http://mocksite.com/tc16a",
                           be_product_url="http://mocksite.com/tc16a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", upc=None,
                           condition=False)
         },
        {"isbn_match": dict(id=17, source_id=17, name=f"ISBN ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc17a",
                           image_url="http://mocksite.com/tc17a",
                           be_product_url="http://mocksite.com/tc17a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", isbn="1ISBN",
                           condition=True)
         },
        {"isbn_match": dict(id=18, source_id=18, name=f"ISBN ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc18a",
                           image_url="http://mocksite.com/tc18a",
                           be_product_url="http://mocksite.com/tc18a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", isbn="1ISBN",
                           condition=True)
         },
        {"isbn_match": dict(id=19, source_id=19, name=f"ISBN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc19a",
                            image_url="http://mocksite.com/tc19a",
                            be_product_url="http://mocksite.com/tc19a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", isbn="1isbn",
                            condition=True)
         },
        {"ean_match": dict(id=20, source_id=20, name=f"EAN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc20a",
                            image_url="http://mocksite.com/tc20a",
                            be_product_url="http://mocksite.com/tc20a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", ean="1EAN",
                            condition=True)
         },
        {"ean_match": dict(id=21, source_id=21, name=f"EAN ONLY MATCH {uuid.uuid4()}",
                            product_url="http://mocksite.com/tc21a",
                            image_url="http://mocksite.com/tc21a",
                            be_product_url="http://mocksite.com/tc21a", department_name="Electronics",
                            category_name="Computer Accessories & Network Hardware",
                            subcategory_name="Computer Components & Parts - Graphics/Video Cards", ean="1ean",
                            condition=True)
         },
        {"gpid_match": dict(id=22, source_id=22, name=f"GPID ONLY MATCH {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc22a",
                           image_url="http://mocksite.com/tc22a",
                           be_product_url="http://mocksite.com/tc22a", department_name="Electronics",
                           category_name="Computer Accessories & Network Hardware",
                           subcategory_name="Computer Components & Parts - Graphics/Video Cards", gpid="1GPID",
                           condition=True)
         },
        {"gpid_match": dict(id=23, source_id=23, name=f"GPID {uuid.uuid4()}",
                           product_url="http://mocksite.com/tc23a",
                           image_url="http://mocksite.com/tc23a",
                           be_product_url="http://mocksite.com/tc23a", department_name=None,
                           category_name=None,
                           subcategory_name=None, gpid="1gpid",
                           condition=True)
         },
        {"mpn_model_match": dict(id=24, source_id=24, name=f"MPN Model MATCH {uuid.uuid4()}",
                                 product_url="http://mocksite.com/tc24a",
                                 image_url="http://mocksite.com/tc24a",
                                 be_product_url="http://mocksite.com/tc24a", department_name=None,
                                 category_name=None, brand="nike",
                                 subcategory_name=None, mpn="3MPN",
                                 attrs=[{"name":"colour","value":"red"},{"name":"size","value":"10"}],
                                 condition=True)
         },
        {"mpn_model_match": dict(id=25, source_id=25, name=f"MPN Model MATCH {uuid.uuid4()}",
                                 product_url="http://mocksite.com/tc25a",
                                 image_url="http://mocksite.com/tc25a",
                                 be_product_url="http://mocksite.com/tc25a", department_name=None,
                                 category_name=None, brand="nike",
                                 subcategory_name=None, mpn=None,
                                 attrs=[{"name": "model_name", "value": "3MPN"}, {"name": "colour", "value": "red"}, {"name": "size", "value": "10"}],
                                 condition=True)
         },
        {"model_mpn_match": dict(id=26, source_id=26, name=f"Model MPN MATCH {uuid.uuid4()}",
                                 product_url="http://mocksite.com/tc26a",
                                 image_url="http://mocksite.com/tc26a",
                                 be_product_url="http://mocksite.com/tc26a", department_name=None,
                                 category_name=None, brand="nike",
                                 subcategory_name=None, mpn=None,
                                 attrs=[{"name": "model_name", "value": "4MPN"}, {"name": "colour", "value": "red"},
                                        {"name": "size", "value": "10"}],
                                 condition=True)
         },
        {"model_mpn_match": dict(id=27, source_id=27, name=f"Model MPN MATCH {uuid.uuid4()}",
                                 product_url="http://mocksite.com/tc27a",
                                 image_url="http://mocksite.com/tc27a",
                                 be_product_url="http://mocksite.com/tc27a", department_name=None,
                                 category_name=None, brand="nike",
                                 subcategory_name=None, mpn="4mpn",
                                 attrs=[{"name": "colour", "value": "red"},
                                        {"name": "size", "value": "10"}],
                                 condition=True)
         },
        {"market_place": dict(id=28, source_id=28, name=f"Market Place Match",
                                 product_url="http://mocksite.com/tc28a",
                                 image_url="http://mocksite.com/tc28a",
                                 be_product_url="http://mocksite.com/tc28a",
                                 store_name= "test_store",
                                 condition=True)
         },
        {"market_place": dict(id=29, source_id=29, name=f"Market Place Match",
                              product_url="http://mocksite.com/tc29a",
                              image_url="http://mocksite.com/tc29a",
                              be_product_url="http://mocksite.com/tc29a",
                              store_name="test_store",
                              condition=True)
         }


    ]

    for each_dict in input_docs:
        test_deals_dict = dict()
        for key, value in each_dict.items():
            test_deals_dict[key] = create_ops_doc(input_doc=value)
            deal_id = test_deals_dict[key]["id"]
            index_url = f"{open_search_host}/{deals_index}/_doc/{deal_id}"
            if ops_ingest:
                create_response = json.loads(
                    requests.post(index_url, headers=headers, data=json.dumps(test_deals_dict[key])).text
                )
            opensearch_test_deals.append(test_deals_dict)
    # Insert the documents into the index

    return opensearch_test_deals  # Provide the Elasticsearch client to the test functions

class MockSearchUseCase_V2(IUseCase):
    def __init__(self,doc_key:str = None,ops_ingest:bool = False,condition:bool = True):
        self._google_repo = IOffer
        self._web_repo = IOffer
        self._opensearch_repo = IOffer
        self._scraping_repo = IOffer
        self.input_doc = index_fixtures(ops_ingest=ops_ingest)
        self.doc_key = doc_key
        self.offer_schema = marshmallow_dataclass.class_schema(Offer)()
        self.condition = condition
        self.support = Support()


    def merge_results(
            self, google_offers: List[Offer], lb_offers: List[Offer], offer: Offer
    ) -> List[Offer]:
        pass

    def get_offers_extras(
            self, searched_offers: List[Offer]
    ) -> dict:
        pass

    def find_offers(
            self, search_input: SearchOffersInput
    ) -> List[Offer]:
        result_set = []
        link = search_input.get("url")
        title = search_input.get("name")
        if not link:
            raise UnprocessableEntityException
        else:
            for each_offer in self.input_doc:
                offer_dict= each_offer.get(self.doc_key)
                if offer_dict:
                    target_condition = offer_dict.get("condition")
                    if self.condition != target_condition:
                        continue
                    offer = offer_object(self.offer_schema,offer_dict,0.0)

                    if offer.link == link:
                        offer.ops_score = 2.00
                        result_set.append(offer)
                    elif self.doc_key == "gtin_match" and target_condition:
                        offer.ops_score = 1.88
                        result_set.append(offer)
                    elif self.doc_key == "mpn_match" and target_condition:
                        offer.ops_score = 1.87
                        result_set.append(offer)
                    elif self.doc_key == "upc_match" and target_condition:
                        offer.ops_score = 1.85
                        result_set.append(offer)
                    elif self.doc_key == "isbn_match" and target_condition:
                        offer.ops_score = 1.82
                        result_set.append(offer)
                    elif self.doc_key == "ean_match" and target_condition:
                        offer.ops_score = 1.79
                        result_set.append(offer)
                    elif self.doc_key == "gpid_match" and target_condition:
                        offer.ops_score = 1.5
                        result_set.append(offer)
                    elif self.doc_key == "product_id_match" and target_condition:
                        offer.ops_score = 2.0
                        result_set.append(offer)
                    elif self.doc_key == "mpn_model_match" and target_condition:
                        offer.ops_score = 1.87
                        result_set.append(offer)
                    elif self.doc_key == "model_mpn_match" and target_condition:
                        offer.ops_score = 1.87
                        result_set.append(offer)
                    elif self.doc_key == "market_place" and target_condition:
                        offer.ops_score = 0.89
                        result_set.append(offer)
                    """elif self.doc_key == "product_id_match" and target_condition:
                        input_title = self.support.clean_text(title)
                        name = self.support.clean_text(offer.title)
                        text_score = self.support.get_cosine(input_title, name)
                        offer.ops_score = text_score+ (text_score*0.3)
                        result_set.append(offer)"""

        return result_set
