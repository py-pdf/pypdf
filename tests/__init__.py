import ssl
import urllib.request
from pathlib import Path
from typing import List
from urllib.error import HTTPError

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

    Returns:
        Read PDF as bytes
    """
    if url.startswith("file://"):
        with open(url[7:].replace("\\", "/"), "rb") as fp:
            return fp.read()
    cache_dir = Path(__file__).parent / "pdf_cache"
    if not cache_dir.exists():
        cache_dir.mkdir()
    cache_path = cache_dir / name
    if not cache_path.exists():
        ssl._create_default_https_context = ssl._create_unverified_context
        cpt = 3
        while cpt > 0:
            try:
                with urllib.request.urlopen(  # noqa: S310
                    url
                ) as response, cache_path.open("wb") as out_file:
                    out_file.write(response.read())
                cpt = 0
            except HTTPError as e:
                if cpt > 0:
                    cpt -= 1
                else:
                    raise e
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

    Args:
        line: the original line

    Returns:
        A line with stripped position
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
            def get_object(self) -> "DummyObj":
                return self

        return DictionaryObject()

    def get_reference(self, obj):
        return IndirectObject(idnum=1, generation=1, pdf=self)
