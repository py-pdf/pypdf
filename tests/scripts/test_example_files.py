"""Tests related to the example files."""
from operator import itemgetter
from pathlib import Path

from tests import read_yaml_to_list_of_dicts


def test_consistency():
    pdfs = read_yaml_to_list_of_dicts(Path(__file__).parent.parent / "example_files.yaml")

    # Ensure the names are unique
    assert len(pdfs) == len(set(map(itemgetter("local_filename"), pdfs)))

    # Ensure the urls are unique
    assert len(pdfs) == len(set(map(itemgetter("url"), pdfs)))
