import pytest
from PyPDF2.context import get_context, set_context, Context
from PyPDF2.generic._base import FloatObject

@pytest.mark.parametrize(
    ("prec"),
    [1, 2, 3, 4, 5, 6, 7,]
)
def test_precision(prec):
    set_context(Context(decimal_precision=prec))
    assert get_context().prec == prec


@pytest.mark.parametrize(
    ("prec", "expected"),
    [
        (1, "0.1"),
        (2, "0.11"),
        (3, "0.111"),
        (4, "0.1111"),
        (5, "0.11111"),
        (6, "0.111111"),
        (7, "0.1111111")
    ]
)
def test_float_precision(prec, expected):
    set_context(Context(decimal_precision=prec))
    assert repr(FloatObject(value=0.111111111)) == expected


def test_float_precision_none():
    set_context(Context(decimal_precision=None))
    assert repr(FloatObject(value="99900000000000000123.456000")) == '99900000000000000123.456'