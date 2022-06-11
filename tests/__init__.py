import os
import urllib.request


def get_pdf_from_url(url: str, name: str) -> bytes:
    """
    Download a PDF from a URL and return its contents.

    This function makes sure the PDF is not downloaded too often.
    This function is a last resort for PDF files where we are uncertain if
    we may add it for testing purposes to https://github.com/py-pdf/sample-files

    :param str url: location of the PDF file
    :param str name: unique name accross all files
    """
    if url.startswith("file://"):
        with open(url[7:].replace("\\", "/"), "rb") as fp:
            return fp.read()
    cache_dir = os.path.join(os.path.dirname(__file__), "pdf_cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_path = os.path.join(cache_dir, name)
    if not os.path.exists(cache_path):
        with urllib.request.urlopen(url) as response, open(
            cache_path, "wb"
        ) as out_file:
            out_file.write(response.read())
    with open(cache_path, "rb") as fp:
        data = fp.read()
    return data
