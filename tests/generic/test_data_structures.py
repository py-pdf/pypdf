"""Test the pypdf.generic._data_structures module."""
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    ContentStream,
    DictionaryObject,
    NameObject,
    NullObject,
    RectangleObject,
    StreamObject,
    TreeObject,
)
from tests import RESOURCE_ROOT, get_data_from_url


def test_dictionary_object__get_next_object_position():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")

    # reader.xref = {0: {7: 15, 9: 10245, 12: 939, 14: 2999, 16: 4982, 18: 9949, 22: 11160}}
    assert DictionaryObject._get_next_object_position(
        position_before=12345, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 999999  # No value after 12345 in dictionary
    assert DictionaryObject._get_next_object_position(
        position_before=11111, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 11160  # First value after 11111 in dictionary.
    assert DictionaryObject._get_next_object_position(
        position_before=42, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 939  # First value after 42 in dictionary.

    # New generation.
    reader.xref[1] = {7: 42, 24: 15000}
    assert DictionaryObject._get_next_object_position(
        position_before=10, position_end=999999, generations=list(reader.xref), pdf=reader
    ) == 15


def test_tree_object__cyclic_reference(caplog):
    writer = PdfWriter()
    child1 = writer._add_object(DictionaryObject())
    child2 = writer._add_object(DictionaryObject({NameObject("/Next"): child1}))
    child3 = writer._add_object(DictionaryObject({NameObject("/Next"): child2}))
    child1.get_object()[NameObject("/Next")] = child3
    tree = TreeObject()
    tree[NameObject("/First")] = child2
    tree[NameObject("/Last")] = writer._add_object(DictionaryObject())

    assert list(tree.children()) == [child2.get_object(), child1.get_object(), child3.get_object()]
    assert "Detected cycle in outline structure for " in caplog.text


@pytest.mark.enable_socket
def test_array_object__clone_same_object_multiple_times(caplog):
    url = "https://github.com/user-attachments/files/25412858/Draft_OSMF_financial_statement_2013.pdf"
    name = "issue2991.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))

    writer = PdfWriter()
    for page in reader.pages:
        page2 = writer.add_page(page)
        assert page2.mediabox == RectangleObject((0, 0, 595, 841))
    assert caplog.messages == []


def test_array_object__clone_same_stream_multiple_times():
    writer = PdfWriter()

    # Unique streams.
    stream1 = StreamObject()
    stream1.set_data(b"Hello World!")
    stream2 = StreamObject()
    stream2.set_data(b"Lorem ipsum!")

    # Shared streams.
    shared_streams = [StreamObject() for _ in range(3)]
    [shared_stream.set_data(f"Shared stream {index}".encode()) for index, shared_stream in enumerate(shared_streams)]

    # Add to writer.
    writer._add_object(stream1)
    writer._add_object(stream2)
    shared_references = [writer._add_object(shared_stream) for shared_stream in shared_streams]

    # Arrays.
    array1 = ArrayObject([stream1.indirect_reference, *shared_references])
    array2 = ArrayObject([stream2.indirect_reference, *shared_references])

    # Cloned.
    cloned1 = array1.clone(pdf_dest=writer)
    cloned2 = array2.clone(pdf_dest=writer)

    # Nullify one shared object.
    writer._replace_object(shared_references[1].indirect_reference, NullObject())

    # The first entry is always different. The remaining shared entries should be dedicated copies.
    assert cloned1[1:] != cloned2[1:]

    assert ContentStream(stream=array1, pdf=None).get_data() == b"Hello World!\nShared stream 0\nShared stream 2\n"
    assert ContentStream(stream=array2, pdf=None).get_data() == b"Lorem ipsum!\nShared stream 0\nShared stream 2\n"
    assert (
        ContentStream(stream=cloned1, pdf=None).get_data() ==
        b"Hello World!\nShared stream 0\nShared stream 1\nShared stream 2\n"
    )
    assert (
        ContentStream(stream=cloned2, pdf=None).get_data() ==
        b"Lorem ipsum!\nShared stream 0\nShared stream 1\nShared stream 2\n"
    )
