"""Test the pypdf.filters module."""
import string
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

from pypdf import PdfReader

from . import get_data_from_url

filter_inputs = (
    # "", '', """""",
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.ascii_letters,
    string.digits,
    string.hexdigits,
    string.punctuation,
    string.whitespace,  # Add more...
)

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"

#    Tests to be run before others


# issues if images is used before due to some initialisations
@pytest.mark.enable_socket()
def test_image_without_pillow():
    with patch.dict(sys.modules):
        sys.modules["PIL"] = None
        url = "https://corpora.tika.apache.org/base/docs/govdocs1/914/914102.pdf"
        name = "tika-914102.pdf"
        data = BytesIO(get_data_from_url(url, name=name))
        reader = PdfReader(data, strict=True)

        for page in reader.pages:
            with pytest.raises(ImportError) as exc:
                page.images[0]
            assert exc.value.args[0] == (
                "pillow is required to do image extraction. "
                "It can be installed via 'pip install pypdf[image]'"
            )
