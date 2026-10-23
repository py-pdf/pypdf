"""Test the pypdf.generic._link module."""
from io import BytesIO

import pytest

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    DirectReferenceLink,
    NamedReferenceLink,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
    extract_links,
)
from tests import get_data_from_url


@pytest.mark.enable_socket
def test_extract_links__null_object_in_old_page() -> None:
    url = "https://github.com/user-attachments/files/25507697/sample.pdf"
    name = "issue3656.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    writer = PdfWriter()
    writer.append(reader)


def test_extract_links(caplog: pytest.LogCaptureFixture) -> None:
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


def test_extract_links_ignores_non_link_annotation_offsets() -> None:
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


def test_extract_links_ignores_uri_annotation_offsets(caplog: pytest.LogCaptureFixture) -> None:
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


def test_extract_links_warns_when_internal_links_are_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    old_page = PageObject()
    new_page = PageObject()
    old_page[NameObject("/Annots")] = ArrayObject([
        DictionaryObject({
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/Dest"): ArrayObject([NumberObject(7)]),
        })
    ])

    assert extract_links(new_page, old_page) == []
    assert caplog.messages == ["Annotation sizes differ: 1 vs. 0"]


def test_direct_reference_link_empty_reference() -> None:
    # An empty destination array has no target page to resolve.
    assert DirectReferenceLink(ArrayObject([])).find_referenced_page() is None
    # A populated array still resolves to its first element.
    assert DirectReferenceLink(ArrayObject([NumberObject(7)])).find_referenced_page() == 7


def test_named_reference_link_patch_reference() -> None:
    """
    A named link adds its name as a named destination to the given page,
    unless the name already exists. The existing names are read from the writer,
    or taken from `known_names` if given.
    """
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    writer.add_blank_page(100, 100)
    page = writer.pages[1].indirect_reference
    assert page is not None

    link = NamedReferenceLink(TextStringObject("first"), source_pdf=None)  # type: ignore[arg-type]
    link.patch_reference(writer, page)
    link.patch_reference(writer, page)
    assert list(writer.named_destinations) == ["first"]
    assert writer.named_destinations["first"].page == page

    # The given names are used instead of the ones of the writer, and kept up to date.
    known_names = {"second"}
    NamedReferenceLink(TextStringObject("second"), source_pdf=None).patch_reference(  # type: ignore[arg-type]
        writer, page, known_names=known_names
    )
    NamedReferenceLink(TextStringObject("third"), source_pdf=None).patch_reference(  # type: ignore[arg-type]
        writer, page, known_names=known_names
    )
    assert known_names == {"second", "third"}
    assert list(writer.named_destinations) == ["first", "third"]
