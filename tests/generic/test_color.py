"""Test the pypdf.generic.color module"""

from collections.abc import Sequence
from typing import Optional

import pytest

from pypdf.generic import ArrayObject
from pypdf.generic._color import Color


@pytest.mark.parametrize(
    ("sequence", "outcome"),
    [
        (ArrayObject([]), ""),
        (["a", "b", "c", "d", "e"], ""),
        ((4, 5, 0), ""),
        ((.4,), "0.4 g"),
        ((.2, .2, .8), "0.2 0.2 0.8 rg"),
        ((.800, .640, .300, 1), "0.8 0.64 0.3 1 k")
    ]
)
def test_color(sequence: Optional[Sequence[float]], outcome: str) -> None:
    color = Color.from_normalized_values(sequence)
    if not color:  # This tests the input guards in Color.from_normalized_values()
        assert color is None
    else:
        assert color.as_operator() == outcome
        assert color.as_operator(stroke=True) == outcome.upper()
