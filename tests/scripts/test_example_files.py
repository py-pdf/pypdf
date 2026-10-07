"""Tests related to the example files."""
from operator import itemgetter

from tests import EXAMPLE_FILES_YAML, read_yaml_to_list_of_dicts


def test_consistency() -> None:
    pdfs = read_yaml_to_list_of_dicts(EXAMPLE_FILES_YAML)

    # Ensure the names are unique
    assert len(pdfs) == len(set(map(itemgetter("local_filename"), pdfs)))

    # Ensure the urls are unique
    assert len(pdfs) == len(set(map(itemgetter("url"), pdfs)))
