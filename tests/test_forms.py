"""Test form-related functionality. Separate file to keep overview."""

from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from tests import get_data_from_url


@pytest.mark.enable_socket
def test_form_button__v_value_should_be_name_object():
    url = "https://github.com/user-attachments/files/18736500/blank-form.pdf"
    name = "issue3115.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    writer = PdfWriter(clone_from=reader)
    writer.update_page_form_field_values(
        writer.pages[0],
        {"Other": "/On"},
        auto_regenerate=False,
    )
    stream = BytesIO()
    writer.write(stream)

    # Wrong: `/V (/On)`.
    assert b"\n/V /On\n" in stream.getvalue()
