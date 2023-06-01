import pytest

from models.parsers import LinterParser


def test_get_linter_success():
    class LinterTest(LinterParser):
        cmd = "linter-test"

    assert LinterTest.get_linter("linter-test") == LinterTest


def test_get_linter_fail():
    class LinterTest(LinterParser):
        cmd = "linter-test"

    with pytest.raises(ValueError):
        LinterTest.get_linter("linter-test-fail")
