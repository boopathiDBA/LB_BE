# TODO: Update unittest to pytest
import unittest
from app.repository import IOffer
from app.repository.google_shopping import MockGoogleSearch


class SetupGoogleMockup:

    def __init__(self, offers: IOffer) -> None:
        self._offers = offers

    def test(self) -> IOffer:
        sample_list = self._offers.search_by_title("Iphone 12")
        print("sample_list", sample_list)
        return sample_list


class GoogleUnitTest(unittest.TestCase):

    def test_google(self):
        # Arrange / Setup
        test = SetupGoogleMockup(MockGoogleSearch())
        # Act
        test.test()
        # Assert
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
