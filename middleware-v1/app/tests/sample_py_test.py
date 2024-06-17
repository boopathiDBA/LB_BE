# Sample test cases to verify pytest runs correctly with different syntax
# Will be removed when the test cases for use-cases are covered
import pytest


class TestClass:
    def test_one(self):
        x = 'lb'
        assert 'l' in x

    @pytest.mark.xfail
    def test_two(self):
        x = 'hello'
        assert 'random' in x


def func(x):
    return x + 5


@pytest.mark.skip
def test_method1():
    x = 5
    y = 10
    assert x == y


# $ pytest -m test_mark
# @pytest.mark.test_mark
# def test_method2():
#     a: int = 15
#     b: int = 10
#     assert b + 5 == a


@pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 54)])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
