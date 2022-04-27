import pytest

from PyPDF2.generic import FloatObject, NumberObject, createStringObject


def test_float_object_exception():
    assert FloatObject("abc") == 0


def test_number_object_exception():
    with pytest.raises(OverflowError):
        NumberObject(1.5 * 2**10000)


def test_createStringObject_exception():
    with pytest.raises(TypeError) as exc:
        createStringObject(123)
    assert exc.value.args[0] == "createStringObject should have str or unicode arg"
