import json

import pytest
from dataclasses import dataclass

from app.usecase import get_sanitised_link


def toJSON(i):
    return json.dumps(i, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class TestCase:
    __test__ = False  # False since @dataclass
    name: str
    link: str
    expected: any


class TestSanitiseLink:
    test_cases = [
        TestCase(name="Example 1 with no params",
                 link="http://mocksite.com/TC3A", expected="http://mocksite.com/TC3A"),
        TestCase(name="Example 2 with params not in whitelist",
                 link="http://mocksite.com/TC3C?pid=1&abc=2", expected="http://mocksite.com/TC3C?pid=1"),
        TestCase(name="Example 3-A with params starting with dwvar_",
                 link="http://mocksite.com/TC3C?dwvar_123=3",
                 expected="http://mocksite.com/TC3C?dwvar_123=3"),
        TestCase(name="Example 3-B with params not starting with dwvar_",
                 link="http://mocksite.com/TC3C?xxdwvar_123=3",
                 expected="http://mocksite.com/TC3C"),
        TestCase(name="Example 4 - real example",
                 link="https://www.theiconic.com.au/morena-sports-bag-1706299.html?utm_source=google&utm_medium"
                      "=au_sem_nonbrand&utm_campaign=AU_NC_Designer_PG_ICONIC"
                      "&utm_term=PRODUCT_GROUP&gclsrc=aw.ds",
                 expected='https://www.theiconic.com.au/morena-sports-bag-1706299.html'),
        TestCase(name="Example 5 with fragment lb-gs=0",
                 link="https://www.templeandwebster.com.au/Black-Caviar-28cm-Rectangular-Porcelain-Platters-AX0069"
                      "-MAWI1854.html#lb-gs=0",
                 expected="https://www.templeandwebster.com.au/Black-Caviar-28cm-Rectangular-Porcelain-Platters-AX0069"
                      "-MAWI1854.html#lb-gs=0"),
    ]

    @pytest.mark.parametrize(
        "link,expected, ", map(lambda x: (x.link, x.expected),test_cases),
        ids=map(lambda x: x.name, test_cases),
    )
    def test_get_offers_extras(self, link, expected):
        actual = get_sanitised_link(link)
        assert actual == expected


if __name__ == "__main__":
    pytest.main()
