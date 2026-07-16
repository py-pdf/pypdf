"""Test the pypdf.generic.color module"""
from pypdf.generic import ArrayObject
from pypdf.generic._color import Color


def test_color():
    color = Color.from_tuple(ArrayObject([]))
    assert not color

    color = Color.from_tuple(ArrayObject(["a", "b", "c", "d", "e"]))
    assert not color

    color = Color.from_tuple(ArrayObject([1, 0, 0]))
    assert color.as_operator() == "1 0 0 rg"

    color = Color.from_tuple(ArrayObject([4, 5, 0]))
    assert not color
