"""Tests for pypdf.generic._outline module."""
from io import BytesIO

import pytest

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    Destination,
    DictionaryObject,
    IndirectObject,
    NameObject,
    TextStringObject,
    TreeObject,
)
from pypdf.generic._outline import (
    _find_outline_item_before_page,
    _resolve_outline_dest_page_ref,
)

# ── helpers ──────────────────────────────────────────────────────────


def _write_pdf_with_outlines(
    page_count: int,
    titles: list[str],
) -> BytesIO:
    """Create an in-memory PDF with one outline item per page."""
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(200, 200)
    for idx, title in enumerate(titles):
        writer.add_outline_item(title, idx)
    buf = BytesIO()
    writer.write(buf)
    buf.seek(0)
    return buf


# ── _resolve_outline_dest_page_ref ───────────────────────────────────


def test_resolve_dest_array() -> None:
    """Resolve a /Dest [pageref /Fit] entry."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    page_ref = writer.pages[0].indirect_reference

    child = DictionaryObject()
    child[NameObject("/Dest")] = ArrayObject([page_ref, NameObject("/Fit")])

    assert _resolve_outline_dest_page_ref(child) == page_ref


def test_resolve_goto_action() -> None:
    """Resolve a /A << /S /GoTo /D [pageref /Fit] >> entry."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    page_ref = writer.pages[0].indirect_reference

    action = DictionaryObject({
        NameObject("/S"): NameObject("/GoTo"),
        NameObject("/D"): ArrayObject([page_ref, NameObject("/Fit")]),
    })
    child = DictionaryObject()
    child[NameObject("/A")] = action

    assert _resolve_outline_dest_page_ref(child) == page_ref


def test_resolve_returns_none_for_no_dest() -> None:
    """Return None when child has neither /Dest nor /A."""
    child = DictionaryObject()
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_non_goto_action() -> None:
    """Return None when /A action is not /GoTo."""
    action = DictionaryObject({NameObject("/S"): NameObject("/URI")})
    child = DictionaryObject()
    child[NameObject("/A")] = action

    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_empty_dest_array() -> None:
    """Return None when /Dest is an empty array."""
    child = DictionaryObject()
    child[NameObject("/Dest")] = ArrayObject([])
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_non_array_dest() -> None:
    """Return None when /Dest is a string (named destination)."""
    child = DictionaryObject()
    child[NameObject("/Dest")] = TextStringObject("named_dest")
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_goto_without_d() -> None:
    """Return None when /A GoTo has no /D key."""
    action = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    child = DictionaryObject()
    child[NameObject("/A")] = action
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_goto_empty_d() -> None:
    """Return None when /A GoTo has an empty /D array."""
    action = DictionaryObject({
        NameObject("/S"): NameObject("/GoTo"),
        NameObject("/D"): ArrayObject([]),
    })
    child = DictionaryObject()
    child[NameObject("/A")] = action
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_invalid_a() -> None:
    """Return None when /A is not a dictionary."""
    child = DictionaryObject()
    child[NameObject("/A")] = TextStringObject("invalid")
    assert _resolve_outline_dest_page_ref(child) is None


def test_resolve_returns_none_for_a_without_s() -> None:
    """Return None when /A is a dictionary but has no /S key."""
    child = DictionaryObject()
    child[NameObject("/A")] = DictionaryObject({})
    assert _resolve_outline_dest_page_ref(child) is None


# ── _find_outline_item_before_page ───────────────────────────────────


def test_find_before_page_returns_child_at_page() -> None:
    """Return the child whose page >= requested page_number."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    writer.add_blank_page(200, 200)

    parent = writer.get_outline_root()
    writer.add_outline_item("Page0", 0)
    writer.add_outline_item("Page1", 1)

    result = _find_outline_item_before_page(1, parent, writer)
    assert result is not None
    child = result.get_object()
    assert child is not None
    assert str(child["/Title"]) == "Page1"  # type: ignore[index]


def test_find_before_page_returns_none_when_all_before() -> None:
    """Return None when all outline items point to pages before page_number."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    writer.add_blank_page(200, 200)
    writer.add_outline_item("Page0", 0)

    parent = writer.get_outline_root()
    result = _find_outline_item_before_page(1, parent, writer)
    assert result is None


def test_find_before_page_returns_none_for_empty_outline() -> None:
    """Return None when the outline has no children."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    parent = writer.get_outline_root()

    result = _find_outline_item_before_page(0, parent, writer)
    assert result is None


def test_find_before_page_skips_unresolvable(caplog: pytest.LogCaptureFixture) -> None:
    """Skip children whose page references cannot be resolved."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    # Unresolvable child (idnum 9999 doesn't correspond to a page)
    bad_child = TreeObject()
    bad_child[NameObject("/Dest")] = ArrayObject(
        [IndirectObject(9999, 0, writer), NameObject("/Fit")]
    )
    writer._add_object(bad_child)
    parent.insert_child(bad_child, None, writer)

    # Good child pointing to page 1
    good_child = TreeObject()
    good_child[NameObject("/Dest")] = ArrayObject(
        [writer.pages[1].indirect_reference, NameObject("/Fit")]
    )
    writer._add_object(good_child)
    parent.insert_child(good_child, None, writer)

    result = _find_outline_item_before_page(1, parent, writer)
    assert result is not None


def test_find_before_page_skips_value_error(caplog: pytest.LogCaptureFixture) -> None:
    """Skip children that raise ValueError when resolving their page."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    bad_child = TreeObject()

    # Create an IndirectObject belonging to a DIFFERENT PdfWriter
    # This will trigger ValueError("PDF must be self") in get_object()
    other_writer = PdfWriter()
    other_writer.add_blank_page(200, 200)
    bad_ref = other_writer.pages[0].indirect_reference

    bad_child[NameObject("/Dest")] = ArrayObject([bad_ref, NameObject("/Fit")])
    writer._add_object(bad_child)
    parent.insert_child(bad_child, None, writer)

    # Good child pointing to page 0
    good_child = TreeObject()
    good_child[NameObject("/Dest")] = ArrayObject(
        [writer.pages[0].indirect_reference, NameObject("/Fit")]
    )
    writer._add_object(good_child)
    parent.insert_child(good_child, None, writer)

    result = _find_outline_item_before_page(0, parent, writer)
    assert result is not None


def test_find_before_page_handles_direct_page_object() -> None:
    """Handle children where /Dest array contains a direct PageObject rather than IndirectObject."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    child = TreeObject()
    # Put the actual PageObject in the array, not its reference
    page_obj = writer.pages[0]
    child[NameObject("/Dest")] = ArrayObject([page_obj, NameObject("/Fit")])
    writer._add_object(child)
    parent.insert_child(child, None, writer)
    result = _find_outline_item_before_page(0, parent, writer)
    assert result is not None


def test_find_before_page_skips_none_page_ref() -> None:
    """Skip children that have no resolvable page reference."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    # Child with no /Dest or /A
    bad_child = TreeObject()
    writer._add_object(bad_child)
    parent.insert_child(bad_child, None, writer)

    # Good child pointing to page 0
    good_child = TreeObject()
    good_child[NameObject("/Dest")] = ArrayObject(
        [writer.pages[0].indirect_reference, NameObject("/Fit")]
    )
    writer._add_object(good_child)
    parent.insert_child(good_child, None, writer)

    result = _find_outline_item_before_page(0, parent, writer)
    assert result is not None


def test_find_before_page_handles_page_object_without_indirect_reference() -> None:
    """Handle PageObject directly in /Dest array that has no indirect_reference."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    child = TreeObject()
    # Bare PageObject, no indirect_reference
    page_obj = PageObject()
    child[NameObject("/Dest")] = ArrayObject([page_obj, NameObject("/Fit")])
    writer._add_object(child)
    parent.insert_child(child, None, writer)

    # The page_obj has no indirect_reference, so it falls back to obj.page_number
    # which raises PdfReadError. The function catches this and skips the child.
    result = _find_outline_item_before_page(0, parent, writer)
    assert result is None


def test_find_before_page_handles_page_object_not_in_cache() -> None:
    """Handle PageObject directly in /Dest array that has an indirect_reference but is not in pages."""
    writer = PdfWriter()
    writer.add_blank_page(200, 200)

    parent = TreeObject()
    writer._add_object(parent)

    child = TreeObject()
    # PageObject added to writer but NOT to writer.pages
    page_obj_fake = PageObject()
    writer._add_object(page_obj_fake)

    child[NameObject("/Dest")] = ArrayObject([page_obj_fake, NameObject("/Fit")])
    writer._add_object(child)
    parent.insert_child(child, None, writer)

    # The page_obj_fake has an indirect_reference, but it's not in writer.pages
    # so _page_cache.get() returns None and it falls back to obj.page_number
    # which raises PdfReadError.
    result = _find_outline_item_before_page(0, parent, writer)
    assert result is None


# ── Merge-level integration tests ────────────────────────────────────


def test_merge_outline_ordering_at_position() -> None:
    """Merging Doc B at position 1 of Doc A produces [A1, B1, B2, A2, A3]."""
    buf_a = _write_pdf_with_outlines(3, ["A1", "A2", "A3"])
    buf_b = _write_pdf_with_outlines(2, ["B1", "B2"])

    merged = PdfWriter()
    merged.append(buf_a)
    merged.merge(1, buf_b)

    buf = BytesIO()
    merged.write(buf)
    buf.seek(0)
    titles = [el.title for el in PdfReader(buf).outline if isinstance(el, Destination)]
    assert titles == ["A1", "B1", "B2", "A2", "A3"]


def test_merge_outline_ordering_at_start() -> None:
    """Merging at position 0 inserts bookmarks before all existing ones."""
    buf_a = _write_pdf_with_outlines(1, ["A1"])
    buf_b = _write_pdf_with_outlines(1, ["B1"])

    merged = PdfWriter()
    merged.append(buf_a)
    merged.merge(0, buf_b)

    buf = BytesIO()
    merged.write(buf)
    buf.seek(0)
    titles = [el.title for el in PdfReader(buf).outline if isinstance(el, Destination)]
    assert titles == ["B1", "A1"]


def test_merge_outline_ordering_at_end() -> None:
    """Merging after all pages appends bookmarks at the end."""
    buf_a = _write_pdf_with_outlines(1, ["A1"])
    buf_b = _write_pdf_with_outlines(1, ["B1"])

    merged = PdfWriter()
    merged.append(buf_a)
    merged.merge(1, buf_b)

    buf = BytesIO()
    merged.write(buf)
    buf.seek(0)
    titles = [el.title for el in PdfReader(buf).outline if isinstance(el, Destination)]
    assert titles == ["A1", "B1"]


def test_merge_outline_with_dest_array() -> None:
    """Outlines using /Dest arrays (not /A GoTo) are handled correctly."""
    writer_a = PdfWriter()
    writer_a.add_blank_page(200, 200)
    writer_a.add_blank_page(200, 200)

    # Manually add a /Dest-style outline item pointing to page 1
    outline_root = writer_a.get_outline_root()
    item = TreeObject()
    writer_a._add_object(item)
    item[NameObject("/Title")] = TextStringObject("A_Dest")
    item[NameObject("/Dest")] = ArrayObject(
        [writer_a.pages[1].indirect_reference, NameObject("/Fit")]
    )
    outline_root.insert_child(item, None, writer_a)
    buf_a = BytesIO()
    writer_a.write(buf_a)
    buf_a.seek(0)

    buf_b = _write_pdf_with_outlines(1, ["B1"])

    merged = PdfWriter()
    merged.append(buf_a)
    merged.merge(0, buf_b)

    buf = BytesIO()
    merged.write(buf)
    buf.seek(0)
    titles = [el.title for el in PdfReader(buf).outline if isinstance(el, Destination)]
    assert titles == ["B1", "A_Dest"]
