import pytest

from parsers import LinterParser


class LinterTest(LinterParser):
    cmd = "linter-test"

    @classmethod
    def parse(cls, input_str) -> dict:
        return {}


def test_get_linter_success():
    assert LinterTest.get_linter("linter-test") == LinterTest


def test_get_linter_fail():
    with pytest.raises(ValueError):
        LinterTest.get_linter("linter-test-fail")


def test_run():
    LinterTest.run()
