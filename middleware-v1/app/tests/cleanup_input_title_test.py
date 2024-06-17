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


class TestCleanupTitle:
    test_cases = [
        TestCase(test_case_name="Test title without encoding",
                 name="Apple iphone 15 256GB Red", expected_name="Apple iphone 15 256GB Red",
                 link=None, expected_link=None),
        TestCase(test_case_name="Test title with encoding",
                 name="Hello%20World&lang=en%20US", expected_name="Hello World&lang=en US",
                 link=None, expected_link=None),
        TestCase(test_case_name="Test Amazon title ",
                 name="Dyson%20V11%20Absolute%20Cordless%20Vacuum%20:%20Amazon.com.au:%20Home", expected_name="Dyson V11 Absolute Cordless Vacuum ",
                 link=None, expected_link=None),
        TestCase(test_case_name="Test Empty title ",
                 name=None,
                 expected_name=None,
                 link=None, expected_link=None)
    ]

    @pytest.mark.parametrize(
        "name, expect_name, link, expected_link,test_case_name, ",
        map(lambda x: (x.name, x.expected_name, x.link, x.expected_link, x.test_case_name), test_cases),
        ids=map(lambda x: x.test_case_name, test_cases),
    )
    def test_cleanup_input_title(self, name, expect_name, link, expected_link, test_case_name):
        actual_name = cleanup_input_title(name)
        assert actual_name == expect_name


if __name__ == "__main__":
    pytest.main()
