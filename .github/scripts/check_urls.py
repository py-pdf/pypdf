"""Check that all test data URLs are still accessible."""  # noqa: INP001
import ast
import ipaddress
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from operator import itemgetter
from pathlib import Path

from tests import read_yaml_to_list_of_dicts

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

ALLOWED_URL_HOSTS = (
    "example.com",
    "github.com",
    "githubusercontent.com",
    "martin-thoma.com",
    "ns.adobe.com",
    "pypdf.readthedocs.io",
)


def _is_allowed_host(host: str) -> bool:
    return any(
        host == allowed_host or host.endswith(f".{allowed_host}") for allowed_host in ALLOWED_URL_HOSTS
    )


def _resolves_to_public_ip(host: str) -> bool:
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, None)}
    except socket.gaierror:
        return False

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if (
            ip.is_loopback
            or ip.is_link_local
            or ip.is_private
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False
    return True


def _is_allowed_url(url: str) -> bool:
    parsed_url = urllib.parse.urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname:
        return False

    host = parsed_url.hostname.lower()
    return _is_allowed_host(host) and _resolves_to_public_ip(host)


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirect_url = urllib.parse.urljoin(req.full_url, newurl)
        if not _is_allowed_url(redirect_url):
            raise urllib.error.HTTPError(redirect_url, code, "Blocked redirect target", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_URL_OPENER = urllib.request.build_opener(_SafeRedirectHandler())


def _get_data_from_url(url: str) -> bytes:
    if not _is_allowed_url(url):
        raise ValueError("URL host is not allowed")

    request = urllib.request.Request(url, headers={"User-Agent": "pypdf-url-checker"})
    with _URL_OPENER.open(request, timeout=10) as response:
        return response.read()


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
        sys.stderr.write(f"Not enough data from {url}: {len(data)} bytes\n")
        return False

    if (
            url.lower().endswith(".pdf") and
            url not in PDF_URLS_WHICH_DO_NOT_LOOK_LIKE_PDFS and
            not data.startswith(b"%PDF-")
    ):
        sys.stderr.write(f"The file at {url} does not look like a PDF.\n")
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
