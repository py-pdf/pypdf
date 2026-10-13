"""Test the pypdf.generic.color module"""

from collections.abc import Sequence
from typing import Optional

import pytest

from pypdf.generic import ArrayObject
from pypdf.generic._color import Color


@pytest.mark.parametrize(
    ("sequence", "operator", "outcome"),
    [
        (ArrayObject([]), None, ""),
        (["a", "b", "c", "d", "e"], None, ""),
        ((4, 5, 0), None, ""),
        ((.4,), None, "0.4 g"),
        ((.2, .2, .8), None, "0.2 0.2 0.8 rg"),
        ((.800, .640, .300, 1), None, "0.8 0.64 0.3 1 k"),
        ((.4,), "g", "0.4 g"),
        ((.2, .2, .8), "rg", "0.2 0.2 0.8 rg"),
        ((.800, .640, .300, 1), "k", "0.8 0.64 0.3 1 k"),
        ((.2, .2, .8), "g", ""),
        ((.4,), "G", ""),
        ((.4,), "gs", ""),
    ]
)
def test_color(sequence: Optional[Sequence[float]], operator: Optional[str], outcome: str) -> None:
    color = Color.from_normalized_values(sequence, operator)
    if not color:  # This tests the input guards in Color.from_normalized_values()
        assert color is None
    else:
        assert color.as_operator() == outcome
        assert color.as_operator(stroke=True) == outcome.upper()
