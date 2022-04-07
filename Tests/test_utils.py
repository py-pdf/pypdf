import pytest
import PyPDF2.utils


@pytest.mark.parametrize(
    "value,expected", [(0, True), (-1, True), (1, True), ("1", False), (1.5, False)]
)
def test_isInt(value, expected):
    assert PyPDF2.utils.isInt(value) == expected
