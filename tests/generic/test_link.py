"""Test the pypdf.generic._link module."""
from io import BytesIO

import pytest

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    DirectReferenceLink,
    NameObject,
    NullObject,
    NumberObject,
    extract_links,
)
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
    assert caplog.messages == []
    caplog.clear()

    # Both old and new annotations.
    page2[NameObject("/Annots")] = ArrayObject([NullObject()])
    assert extract_links(page1, page2) == []
    assert caplog.messages == []  # Same size.
    caplog.clear()

    page2[NameObject("/Annots")] = NullObject()
    assert extract_links(page1, page2) == []
    assert caplog.messages == []
    caplog.clear()

    # Only new annotations.
    del page1[NameObject("/Annots")]
    page2[NameObject("/Annots")] = ArrayObject([NullObject()])
    assert extract_links(page1, page2) == []
    assert caplog.messages == []


def test_extract_links_ignores_non_link_annotation_offsets():
    old_page = PageObject()
    new_page = PageObject()

    old_link = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Dest"): ArrayObject([NumberObject(7)]),
        }
    )
    new_link = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Dest"): ArrayObject([NumberObject(11)]),
        }
    )

    old_page[NameObject("/Annots")] = ArrayObject([NullObject(), old_link])
    new_page[NameObject("/Annots")] = ArrayObject([new_link])

    links = extract_links(new_page, old_page)
    assert len(links) == 1
    assert isinstance(links[0][0], DirectReferenceLink)
    assert isinstance(links[0][1], DirectReferenceLink)


def test_extract_links_ignores_uri_annotation_offsets(caplog):
    old_page = PageObject()
    new_page = PageObject()

    goto_link = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Dest"): ArrayObject([NumberObject(7)]),
        }
    )
    uri_link = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/A"): DictionaryObject(
                {
                    NameObject("/S"): NameObject("/URI"),
                    NameObject("/URI"): NameObject("https://example.com"),
                }
            ),
        }
    )

    old_page[NameObject("/Annots")] = ArrayObject([goto_link])
    new_page[NameObject("/Annots")] = ArrayObject([uri_link, goto_link])

    links = extract_links(new_page, old_page)

    assert len(links) == 1
    assert isinstance(links[0][0], DirectReferenceLink)
    assert isinstance(links[0][1], DirectReferenceLink)
    assert caplog.messages == []
