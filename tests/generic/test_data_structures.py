"""Test the pypdf.generic._data_structures module."""
from pypdf import PdfReader
from pypdf.generic import DictionaryObject
from tests import RESOURCE_ROOT


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
