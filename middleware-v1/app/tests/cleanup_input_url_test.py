import pytest
from dataclasses import dataclass
from app.helpers import cleanup_input_url, cleanup_input_title


@dataclass
class TestCase:
    __test__ = False  # False since @dataclass
    test_case_name: str
    name: str
    expected_name: any
    link: str
    expected_link: any


class TestCleanupURL:
    test_cases = [
        TestCase(test_case_name="Test URL without encoding", name=None, expected_name=None,
                 link="http://mocksite.com/TC3A", expected_link="http://mocksite.com/TC3A"),
        TestCase(test_case_name="Test URL with encoding", name=None, expected_name=None,
                 link="https://www.example.com/search?q=Hello%20World&lang=en%20US",
                 expected_link="https://www.example.com/search?q=Hello World&lang=en US"),
        TestCase(test_case_name="Test CATCH store mobile url", name=None, expected_name=None,
                 link="https://m.catch.com.au/product/sony-wh-1000xm4-wireless-noise-cancelling-headphones-black-6546945",
                 expected_link="https://www.catch.com.au/product/sony-wh-1000xm4-wireless-noise-cancelling-headphones-black-6546945"),
    ]

    @pytest.mark.parametrize(
        "name, expect_name, link, expected_link,test_case_name, ",
        map(lambda x: (x.name, x.expected_name, x.link, x.expected_link, x.test_case_name), test_cases),
        ids=map(lambda x: x.test_case_name, test_cases),
    )
    def test_cleanup_input_url(self, name, expect_name, link, expected_link, test_case_name):
        actual_link = cleanup_input_url(link)
        assert actual_link == expected_link


if __name__ == "__main__":
    pytest.main()
