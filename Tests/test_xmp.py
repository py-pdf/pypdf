import os

import pytest

import PyPDF2.xmp
from PyPDF2 import PdfFileReader

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    ("src", "has_xmp"),
    [
        (os.path.join(RESOURCE_ROOT, "commented-xmp.pdf"), True),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), False),
    ],
)
def test_read_xmp(src, has_xmp):
    reader = PdfFileReader(src)
    xmp = reader.xmpMetadata
    assert (xmp is None) == (not has_xmp)
    if has_xmp:
        for el in xmp.getElement(
            aboutUri="", namespace=PyPDF2.xmp.RDF_NAMESPACE, name="Artist"
        ):
            print("el={el}".format(el=el))

        assert get_all_tiff(xmp) == {"tiff:Artist": ["me"]}
        assert xmp.dc_contributor == []


def get_all_tiff(xmp):
    data = {}
    tiff_ns = xmp.getNodesInNamespace(
        aboutUri="", namespace="http://ns.adobe.com/tiff/1.0/"
    )
    for tag in tiff_ns:
        contents = []
        for content in tag.childNodes:
            contents.append(content.data)
        data[tag.tagName] = contents
    return data


def test_regression_issue774():
    cls = PyPDF2.xmp.XmpInformation
    date = cls._converter_date("2021-04-28T12:23:34.123Z")
    assert date.year == 2021
    assert date.month == 4
    assert date.day == 28
    assert date.hour == 12
    assert date.minute == 23
    assert date.second == 34
    assert date.microsecond == 123000
