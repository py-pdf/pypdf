"""Test form-related functionality. Separate file to keep overview."""

from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
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


@pytest.mark.enable_socket
def test_radio_button_handling():
    url = "https://github.com/user-attachments/files/23957527/TemplateReproBug.pdf"
    name = "issue3549.pdf"
    writer = PdfWriter(clone_from=BytesIO(get_data_from_url(url, name=name)))
    writer.update_page_form_field_values(
        writer.pages[0],
        {"Radio Button 3": "/1"},
    )

    radio_button3 = writer.get_fields()["Radio Button 3"]
    assert radio_button3 == {
        "/T": "Radio Button 3",
        "/FT": "/Btn",
        "/TU": "Reason for Enrollment",
        "/Ff": 49152,
        "/V": "/1",
        "/Kids": [writer.get_object(17).indirect_reference, writer.get_object(52).indirect_reference],
        "/Opt": ["New", "Add Dependant"],
        "/_States_": ["/0", "/1"]
    }
    assert isinstance(radio_button3["/V"], NameObject), type(radio_button3["/V"])

    writer.update_page_form_field_values(
        writer.pages[0],
        {"Radio Button 3": "/0"},
    )
    radio_button3 = writer.get_fields()["Radio Button 3"]
    assert radio_button3 == {
        "/T": "Radio Button 3",
        "/FT": "/Btn",
        "/TU": "Reason for Enrollment",
        "/Ff": 49152,
        # TODO: Should be `/0`. Issue: https://github.com/py-pdf/pypdf/issues/3549
        #       Then we might want to use a parametrized function instead of repeating everything.
        "/V": "/Off",
        "/Kids": [writer.get_object(17).indirect_reference, writer.get_object(52).indirect_reference],
        "/Opt": ["New", "Add Dependant"],
        "/_States_": ["/0", "/1"]
    }
    assert isinstance(radio_button3["/V"], NameObject), type(radio_button3["/V"])
