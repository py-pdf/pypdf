import concurrent.futures
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import yaml

from pypdf.generic import DictionaryObject, IndirectObject


def get_data_from_url(url: Optional[str] = None, name: Optional[str] = None) -> bytes:
    """
    Download a File from a URL and return its contents.

    This function makes sure the PDF is not downloaded too often.
    This function is a last resort for PDF files where we are uncertain if
    we may add it for testing purposes to https://github.com/py-pdf/sample-files

    Args:
        url: location of the PDF file
        name: unique name across all files

    Returns:
        Read File as bytes

    """
    if name is None:
        raise ValueError("A name must always be specified")

    cache_dir = Path(__file__).parent / "pdf_cache"
    if not cache_dir.exists():
        cache_dir.mkdir()
    cache_path = cache_dir / name

    if url is not None:
        if url.startswith("file://"):
            with open(url[7:].replace("\\", "/"), "rb") as fp:
                return fp.read()
        if not cache_path.exists():
            ssl._create_default_https_context = ssl._create_unverified_context
            attempts = 0
            while attempts < 3:
                try:
                    with urllib.request.urlopen(  # noqa: S310
                        url
                    ) as response, cache_path.open("wb") as out_file:
                        out_file.write(response.read())
                    break
                except HTTPError as e:
                    if attempts < 3:
                        attempts += 1
                    else:
                        raise e
    with open(cache_path, "rb") as fp:
        return fp.read()


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
    return " ".join(line.split(" ")[1:])


def normalize_warnings(caplog_text: str) -> List[str]:
    return [_strip_position(line) for line in caplog_text.strip().split("\n")]


class ReaderDummy:
    def __init__(self, strict=False) -> None:
        self.strict = strict

    def get_object(self, indirect_reference):
        class DummyObj:
            def get_object(self) -> "DummyObj":
                return self

        return DictionaryObject()

    def get_reference(self, obj):
        return IndirectObject(idnum=1, generation=1, pdf=self)


def is_sublist(child_list, parent_list):
    """
    Check if child_list is a sublist of parent_list, with respect to
    * elements order
    * elements repetition

    Elements are compared using `==`
    """
    if len(child_list) == 0:
        return True
    if len(parent_list) == 0:
        return False
    if parent_list[0] == child_list[0]:
        return is_sublist(child_list[1:], parent_list[1:])
    return is_sublist(child_list, parent_list[1:])


def read_yaml_to_list_of_dicts(yaml_file: Path) -> List[Dict[str, str]]:
    with open(yaml_file) as yaml_input:
        return yaml.safe_load(yaml_input)


def download_test_pdfs():
    """
    Run this before the tests are executed to ensure you have everything locally.

    This is especially important to avoid pytest timeouts.
    """
    pdfs = read_yaml_to_list_of_dicts(Path(__file__).parent / "example_files.yaml")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(get_data_from_url, pdf["url"], name=pdf["local_filename"])
            for pdf in pdfs
        ]
        concurrent.futures.wait(futures)


def test_csv_consistency():
    pdfs = read_yaml_to_list_of_dicts(Path(__file__).parent / "example_files.csv")
    # Ensure the names are unique
    assert len(pdfs) == len({pdf["name"] for pdf in pdfs})

    # Ensure the urls are unique
    assert len(pdfs) == len({pdf["url"] for pdf in pdfs})


class PILContext:
    """Allow changing the PIL/Pillow configuration for some limited scope."""

    def __init__(self) -> None:
        self._saved_load_truncated_images = False

    def __enter__(self) -> Self:
        # Allow loading incomplete images.
        from PIL import ImageFile  # noqa: PLC0415
        self._saved_load_truncated_images = ImageFile.LOAD_TRUNCATED_IMAGES
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        return self

    def __exit__(self, type_, value, traceback) -> Optional[bool]:
        from PIL import ImageFile  # noqa: PLC0415
        ImageFile.LOAD_TRUNCATED_IMAGES = self._saved_load_truncated_images
        if type_:
            # Error.
            return None
        return True
