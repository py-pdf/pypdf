import concurrent.futures
import os
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Optional, Union
from urllib.error import HTTPError

from PIL import Image

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import yaml

from pypdf.generic import DictionaryObject, IndirectObject


def _get_data_from_url(url: str) -> bytes:
    ssl._create_default_https_context = ssl._create_unverified_context
    attempts = 0
    while attempts < 3:
        try:
            with urllib.request.urlopen(  # noqa: S310
                    url
            ) as response:
                return response.read()
        except HTTPError as e:
            if attempts < 3:
                attempts += 1
            else:
                raise e
    raise ValueError(f"Unknown error handling {url}")


# TODO: Make keyword-only and drop name being optional.
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

    if os.getenv("GITHUB_JOB", None) is not None:
        cache_dir = Path("tests", "pdf_cache").resolve()
    else:
        cache_dir = Path(__file__).parent / "pdf_cache"
    if not cache_dir.exists():
        cache_dir.mkdir()
    cache_path = cache_dir / name

    if url is not None:
        if url.startswith("file://"):
            path = Path(url[7:].replace("\\", "/"))
            return path.read_bytes()
        if not cache_path.exists():
            cache_path.write_bytes(_get_data_from_url(url))
    return cache_path.read_bytes()


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


def normalize_warnings(caplog_text: str) -> list[str]:
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


def read_yaml_to_list_of_dicts(yaml_file: Path) -> list[dict[str, str]]:
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


def get_image_data(
        image: Image.Image, band: Union[int, None] = None
) -> Union[tuple[tuple[int, ...], ...], tuple[float, ...]]:
    try:
        return image.get_flattened_data(band=band)
    except AttributeError:
        # For Pillow < 12.1.0
        return tuple(image.getdata(band=band))
