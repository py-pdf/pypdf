"""Check that all test data URLs are still accessible."""  # noqa: INP001
import ast
import sys
from collections.abc import Iterator
from operator import itemgetter
from pathlib import Path

from tests import _get_data_from_url, read_yaml_to_list_of_dicts

URL_PREFIXES_TO_IGNORE = (
    "http://ns.adobe.com/tiff/1.0/",
    "http://www.example.com",
    "https://example.com",
    "https://martin-thoma.com",
    "https://pypdf.readthedocs.io/",
    "https://www.example.com",
)

PDF_URLS_WHICH_DO_NOT_LOOK_LIKE_PDFS = {
    "https://github.com/user-attachments/files/18381726/tika-957721.pdf",
}


def get_urls_from_test_files() -> Iterator[str]:
    """Retrieve all URLs defined the test files."""
    tests_directory = Path(__file__).parent.parent.parent / "tests"
    for test_file in sorted(tests_directory.rglob("test_*.py")):
        tree = ast.parse(source=test_file.read_text(encoding="utf-8"), filename=str(test_file))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, str):
                continue
            if not node.value.startswith(("http://", "https://")):
                continue
            yield node.value


def get_urls_from_example_files() -> Iterator[str]:
    """Retrieve all URLs defined in the `example_files.yaml`."""
    pdfs = read_yaml_to_list_of_dicts(Path(__file__).parent.parent.parent / "tests" / "example_files.yaml")
    yield from map(itemgetter("url"), pdfs)


def check_url(url: str) -> bool:
    """Check if the given URL appears to still be valid."""
    if url.startswith(URL_PREFIXES_TO_IGNORE):
        return True

    try:
        data = _get_data_from_url(url)
    except Exception as exception:
        sys.stderr.write(f"Error getting data from {url}: {exception}\n")
        return False

    if len(data) < 75:
        sys.stderr.write(f"Not enough data from {url}: {data}\n")
        return False

    if (
            url.lower().endswith(".pdf") and
            url not in PDF_URLS_WHICH_DO_NOT_LOOK_LIKE_PDFS and
            not data.startswith(b"%PDF-")
    ):
        sys.stderr.write(f"The file at {url} does not look like a PDF: {data[:50]}\n")
        return False

    sys.stdout.write(f"URL {url} looks good.\n")
    return True


def main() -> bool:
    """Check if there are invalid URLs."""
    urls: set[str] = set()
    for url in get_urls_from_test_files():
        urls.add(url)
    for url in get_urls_from_example_files():
        urls.add(url)

    is_valid = True
    for url in sorted(urls):
        is_valid &= check_url(url)
    return not is_valid


if __name__ == "__main__":
    sys.exit(main())
