"""Test the pypdf.generic._link module."""
from io import BytesIO

import pytest

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject, NullObject, extract_links
from tests import get_data_from_url


@pytest.mark.enable_socket
def test_extract_links__null_object_in_old_page():
    url = "https://github.com/user-attachments/files/25507697/sample.pdf"
    name = "issue3656.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    writer = PdfWriter()
    writer.append(reader)


def test_extract_links(caplog):
    page1 = PageObject()
    page2 = PageObject()

    # No annotations.
    assert extract_links(page1, page2) == []
    assert caplog.messages == []

    # Only old annotations.
    page1[NameObject("/Annots")] = NullObject()
    assert extract_links(page1, page2) == []
    assert caplog.messages == []
    caplog.clear()

    page1[NameObject("/Annots")] = ArrayObject([NullObject()])
    assert extract_links(page1, page2) == []
    assert caplog.messages == ["Annotation sizes differ: [] vs. [NullObject]"]
    caplog.clear()

    # Both old and new annotations.
    page2[NameObject("/Annots")] = ArrayObject([NullObject()])
    assert extract_links(page1, page2) == []
    assert caplog.messages == []  # Same size.
    caplog.clear()

    page2[NameObject("/Annots")] = NullObject()
    assert extract_links(page1, page2) == []
    assert caplog.messages == ["Annotation sizes differ: [] vs. [NullObject]"]
    caplog.clear()

    # Only new annotations.
    del page1[NameObject("/Annots")]
    page2[NameObject("/Annots")] = ArrayObject([NullObject()])
    assert extract_links(page1, page2) == []
    assert caplog.messages == ["Annotation sizes differ: [NullObject] vs. []"]
