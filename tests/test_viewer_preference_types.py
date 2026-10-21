"""Tests for name-valued viewer preferences."""

from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject


@pytest.mark.parametrize("value_type", [str, NameObject])
@pytest.mark.parametrize(
    ("preference", "key", "value"),
    [
        ("non_fullscreen_pagemode", "/NonFullScreenPageMode", "/UseOutlines"),
        ("direction", "/Direction", "/R2L"),
        ("view_area", "/ViewArea", "/CropBox"),
        ("view_clip", "/ViewClip", "/CropBox"),
        ("print_area", "/PrintArea", "/CropBox"),
        ("print_clip", "/PrintClip", "/CropBox"),
        ("print_scaling", "/PrintScaling", "/AppDefault"),
        ("duplex", "/Duplex", "/DuplexFlipLongEdge"),
    ],
)
def test_viewer_preference_name_roundtrip(value_type, preference, key, value):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    preferences = writer.create_viewer_preferences()

    setattr(preferences, preference, value_type(value))

    assert preferences[NameObject(key)] == NameObject(value)
    assert isinstance(preferences[NameObject(key)], NameObject)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    saved_preferences = PdfReader(output).viewer_preferences
    assert saved_preferences is not None
    assert getattr(saved_preferences, preference) == value
    assert isinstance(saved_preferences[NameObject(key)], NameObject)


@pytest.mark.parametrize("value_type", [str, NameObject])
@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("R2L", "does not start with '/'"),
        ("/Unknown", "is an unacceptable value"),
    ],
)
def test_viewer_preference_name_rejects_invalid_value(value_type, value, message):
    preferences = PdfWriter().create_viewer_preferences()

    with pytest.raises(ValueError, match=message):
        preferences.direction = value_type(value)

    assert "/Direction" not in preferences
