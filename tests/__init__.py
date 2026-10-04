import concurrent.futures
import functools
import os
import random
import ssl
import sys
import tempfile
import time
import urllib.request
from http.client import HTTPException
from pathlib import Path
from types import TracebackType
from typing import Callable, Optional, cast
from urllib.error import HTTPError

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

import yaml

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = Path(PROJECT_ROOT) / "sample-files"
EXAMPLE_FILES_YAML = TESTS_ROOT / "example_files.yaml"

_DOWNLOAD_ATTEMPTS = 5
_DOWNLOAD_TIMEOUT = 60  # seconds
# Retrying these makes no sense. Everything else (rate limits, 5xx, ...) might be transient.
_PERMANENT_HTTP_STATUS_CODES = {404, 410}
_USER_AGENT = "Mozilla/5.0 (compatible; pypdf-tests; +https://github.com/py-pdf/pypdf)"


def _report(message: str) -> None:
    """
    Write a message to stderr.

    The logging module is deliberately not used as many tests assert on `caplog`.
    """
    sys.stderr.write(f"{message}\n")


def _get_data_from_url(url: str) -> bytes:
    ssl._create_default_https_context = cast(
        Callable[..., ssl.SSLContext],
        ssl._create_unverified_context,
    )
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})  # noqa: S310
    for attempt in range(1, _DOWNLOAD_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=_DOWNLOAD_TIMEOUT) as response:  # noqa: S310
                return response.read()
        except HTTPError as error:
            if error.code in _PERMANENT_HTTP_STATUS_CODES or attempt == _DOWNLOAD_ATTEMPTS:
                raise
            reason = f"HTTP {error.code}"
        except (OSError, HTTPException) as error:
            # Covers URLError, timeouts, connection resets and incomplete reads.
            if attempt == _DOWNLOAD_ATTEMPTS:
                raise
            reason = repr(error)
        delay = 2 ** attempt + random.random()  # noqa: S311
        _report(
            f"Download of {url} failed ({reason}), attempt {attempt}/{_DOWNLOAD_ATTEMPTS}. "
            f"Retrying in {delay:.0f}s."
        )
        time.sleep(delay)
    raise ValueError(f"Unknown error handling {url}")


def _store_in_cache(cache_path: Path, data: bytes) -> None:
    """Write atomically, so that an interrupted download never leaves a truncated file in the cache."""
    file_descriptor, temporary_name = tempfile.mkstemp(dir=cache_path.parent, suffix=".tmp")
    try:
        with os.fdopen(file_descriptor, "wb") as temporary_file:
            temporary_file.write(data)
        Path(temporary_name).replace(cache_path)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise


@functools.lru_cache(maxsize=1)
def _get_urls_of_example_files() -> dict[str, str]:
    pdfs = read_yaml_to_list_of_dicts(EXAMPLE_FILES_YAML)
    return {pdf["local_filename"]: pdf["url"] for pdf in pdfs}


def get_data_from_url(*, url: Optional[str] = None, name: str) -> bytes:
    """
    Download a File from a URL and return its contents.

    This function makes sure the PDF is not downloaded too often.
    This function is a last resort for PDF files where we are uncertain if
    we may add it for testing purposes to https://github.com/py-pdf/sample-files

    Args:
        url: location of the PDF file. If it is not given and the file is not
            cached, the URL is looked up by name in `example_files.yaml`.
        name: unique name across all files

    Returns:
        Read File as bytes

    """
    if os.getenv("GITHUB_JOB", None) is not None:
        cache_dir = Path("tests", "pdf_cache").resolve()
    else:
        cache_dir = Path(__file__).parent / "pdf_cache"
    # Several pytest-xdist workers may get here at the same time.
    cache_dir.mkdir(exist_ok=True)
    cache_path = cache_dir / name

    if url is not None and url.startswith("file://"):
        path = Path(url[7:].replace("\\", "/"))
        return path.read_bytes()
    if not cache_path.exists():
        # Without a URL, the file was expected to be downloaded in advance
        # (see `download_test_pdfs`). Try again if that did not work out.
        url = url or _get_urls_of_example_files().get(name)
        if url is not None:
            _store_in_cache(cache_path, _get_data_from_url(url))
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


def is_sublist(child_list: list[int], parent_list: list[int]) -> bool:
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


def download_test_pdfs() -> None:
    """
    Run this before the tests are executed to ensure you have everything locally.

    This is especially important to avoid pytest timeouts.

    Failed downloads are reported, but do not raise: `get_data_from_url` tries
    again when a test needs a missing file, which might succeed later on.
    """
    pdfs = read_yaml_to_list_of_dicts(EXAMPLE_FILES_YAML)
    failures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(get_data_from_url, url=pdf["url"], name=pdf["local_filename"]): pdf
            for pdf in pdfs
        }
        for future in concurrent.futures.as_completed(futures):
            error = future.exception()
            if error is not None:
                failures.append((futures[future], error))

    for pdf, error in failures:
        _report(f"Failed to download {pdf['local_filename']} from {pdf['url']}: {error!r}")
    total = len(pdfs)
    _report(f"Downloaded {total - len(failures)} of {total} test files.")


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

    def __exit__(
        self,
        type_: Optional[type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        from PIL import ImageFile  # noqa: PLC0415
        ImageFile.LOAD_TRUNCATED_IMAGES = self._saved_load_truncated_images
        if type_:
            # Error.
            return None
        return True
