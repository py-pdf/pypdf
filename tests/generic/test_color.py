"""Test the pypdf.generic.color module"""
from typing import cast

from pypdf.generic import ArrayObject
from pypdf.generic._color import Color, RGBColor


def test_color() -> None:
    color = Color.from_tuple(ArrayObject([]))
    assert not color

    color = Color.from_tuple(ArrayObject(["a", "b", "c", "d", "e"]))
    assert not color

    color = Color.from_tuple(ArrayObject([1, 0, 0]))
    assert cast(RGBColor, color).as_operator() == "1 0 0 rg"

    color = Color.from_tuple(ArrayObject([4, 5, 0]))
    assert not color
