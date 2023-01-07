import os
import ssl
import urllib.request
from typing import List

from pypdf.generic import DictionaryObject, IndirectObject


def get_pdf_from_url(url: str, name: str) -> bytes:
    """
    Download a PDF from a URL and return its contents.

    This function makes sure the PDF is not downloaded too often.
    This function is a last resort for PDF files where we are uncertain if
    we may add it for testing purposes to https://github.com/py-pdf/sample-files

    Args:
        url: location of the PDF file
        name: unique name across all files
    """
    if url.startswith("file://"):
        with open(url[7:].replace("\\", "/"), "rb") as fp:
            return fp.read()
    cache_dir = os.path.join(os.path.dirname(__file__), "pdf_cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_path = os.path.join(cache_dir, name)
    if not os.path.exists(cache_path):
        ssl._create_default_https_context = ssl._create_unverified_context
        with urllib.request.urlopen(url) as response, open(
            cache_path, "wb"
        ) as out_file:
            out_file.write(response.read())
    with open(cache_path, "rb") as fp:
        data = fp.read()
    return data


def _strip_position(line: str) -> str:
    """
    Remove the location information.

    The message
        WARNING  pypdf._reader:_utils.py:364 Xref table not zero-indexed.

    becomes
        Xref table not zero-indexed.
    """
    line = ".py".join(line.split(".py:")[1:])
    line = " ".join(line.split(" ")[1:])
    return line


def normalize_warnings(caplog_text: str) -> List[str]:
    return [_strip_position(line) for line in caplog_text.strip().split("\n")]


class ReaderDummy:
    def __init__(self, strict=False):
        self.strict = strict

    def get_object(self, indirect_reference):
        class DummyObj:
            def get_object(self):
                return self

        return DictionaryObject()

    def get_reference(self, obj):
        return IndirectObject(idnum=1, generation=1, pdf=self)
