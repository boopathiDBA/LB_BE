import sys
import path
# directory reach
directory = path.Path(__file__).abspath()
# setting path
sys.path.append(directory.parent.parent)

from typing import List
from repository import IOffer
from repository.web_offer import SearchWebOffers
# from app.usecase import *


class TestWebOffer:
    def __init__(self, offers: IOffer) -> None:
        self._offers = offers

    def test_search_by_link(self) -> None:
        sample_list = self._offers.search_by_link(
            "https://www.camgo.com.au/store/p13/monopod-gopro.html")
        print("sample_list", sample_list)

    def test_search_by_links(self) -> None:
        sample_list = self._offers.search_by_links(
            [
                "https://www.appliancecentral.com.au/qa32ls03bbwxxy-samsung-32-inch-the-frame-qled-smart-tv",
                "https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/",
                "https://www.jbhifi.com.au/products/samsung-t5300-32-full-hd-smart-led-tv-2020"
            ]
        )
        print("sample_list", sample_list)

    def test_match_price(self) -> None:
        sample_list = self._offers.find_offers(
            "https://www.samsung.com/au/tvs/qled-tv/q60b-75-inch-qled-4k-smart-tv-qa75q60bawxxy/"
        )
        print("sample_list", sample_list)




test = TestWebOffer(SearchWebOffers())
# test.test_search_by_link()
test.test_search_by_links()

# testusecase = TestWebOffer(SearchUseCase())
# testusecase.test_match_price()
