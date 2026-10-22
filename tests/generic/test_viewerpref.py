"""Tests for name-valued viewer preferences."""

from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

NAME_PREFERENCES = [
    ("non_fullscreen_pagemode", "/NonFullScreenPageMode", "/UseOutlines"),
    ("direction", "/Direction", "/R2L"),
    ("view_area", "/ViewArea", "/CropBox"),
    ("view_clip", "/ViewClip", "/CropBox"),
    ("print_area", "/PrintArea", "/CropBox"),
    ("print_clip", "/PrintClip", "/CropBox"),
    ("print_scaling", "/PrintScaling", "/AppDefault"),
    ("duplex", "/Duplex", "/DuplexFlipLongEdge"),
]


@pytest.mark.parametrize("value_type", [str, NameObject])
@pytest.mark.parametrize(
    ("preference", "key", "value"),
    NAME_PREFERENCES,
)
def test_viewer_preference_name_roundtrip(value_type: type[str], preference: str, key: str, value: str) -> None:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    preferences = writer.create_viewer_preferences()

    setattr(preferences, preference, value_type(value))

    assert preferences[key] == NameObject(value)
    assert isinstance(preferences[key], NameObject)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    saved_preferences = PdfReader(output).viewer_preferences
    assert saved_preferences is not None
    assert getattr(saved_preferences, preference) == value
    assert isinstance(saved_preferences[key], NameObject)


@pytest.mark.parametrize("value_type", [str, NameObject])
@pytest.mark.parametrize("value", ["/Unknown", "Invalid", ""])
@pytest.mark.parametrize(
    ("preference", "key"),
    [(preference, key) for preference, key, _ in NAME_PREFERENCES],
)
def test_viewer_preference_name_rejects_invalid_value(
    value_type: type[str], preference: str, key: str, value: str,
) -> None:
    preferences = PdfWriter().create_viewer_preferences()

    with pytest.raises(ValueError, match="is an unacceptable value"):
        setattr(preferences, preference, value_type(value))

    assert key not in preferences
