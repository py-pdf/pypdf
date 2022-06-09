import os
from datetime import datetime

import pytest

import PyPDF2.generic
import PyPDF2.xmp
from PyPDF2 import PdfReader

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


@pytest.mark.parametrize(
    ("src", "has_xmp"),
    [
        (os.path.join(RESOURCE_ROOT, "commented-xmp.pdf"), True),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), False),
    ],
)
def test_read_xmp(src, has_xmp):
    reader = PdfReader(src)
    xmp = reader.xmp_metadata
    assert (xmp is None) == (not has_xmp)
    if has_xmp:
        for el in xmp.get_element(
            about_uri="", namespace=PyPDF2.xmp.RDF_NAMESPACE, name="Artist"
        ):
            print(f"el={el}")

        assert get_all_tiff(xmp) == {"tiff:Artist": ["me"]}
        assert xmp.dc_contributor == []


def get_all_tiff(xmp: PyPDF2.xmp.XmpInformation):
    data = {}
    tiff_ns = xmp.get_nodes_in_namespace(
        about_uri="", namespace="http://ns.adobe.com/tiff/1.0/"
    )
    for tag in tiff_ns:
        contents = []
        for content in tag.childNodes:
            contents.append(content.data)
        data[tag.tagName] = contents
    return data


def test_regression_issue774():
    date = PyPDF2.xmp._converter_date("2021-04-28T12:23:34.123Z")
    assert date.year == 2021
    assert date.month == 4
    assert date.day == 28
    assert date.hour == 12
    assert date.minute == 23
    assert date.second == 34
    assert date.microsecond == 123000
    with pytest.raises(ValueError) as exc:
        PyPDF2.xmp._converter_date("today")
    assert exc.value.args[0].startswith("Invalid date format")

    date = PyPDF2.xmp._converter_date("2021-04-28T12:23:01-03:00")
    assert date.year == 2021
    assert date.month == 4
    assert date.day == 28
    assert date.hour == 15
    assert date.minute == 23
    assert date.second == 1
    assert date.microsecond == 0


def test_regression_issue914():
    path = os.path.join(RESOURCE_ROOT, "issue-914-xmp-data.pdf")
    reader = PdfReader(path)
    assert reader.xmp_metadata.xmp_modify_date == datetime(2022, 4, 9, 15, 22, 43)


@pytest.mark.parametrize(
    "x",
    ["a", 42, 3.141, False, True],
)
def test_identity(x):
    assert PyPDF2.xmp._identity(x) == x


# def test_getter_bag():
#     f = PyPDF2.xmp._getter_bag("namespace", "name")
#     class Tst:  # to replace pdf
#         strict = False

#     reader = PdfReader(os.path.join(RESOURCE_ROOT, "commented-xmp.pdf"))
#     xmp_info = reader.xmp_metadata
#     # <?xpacket begin='ï»¿' id='W5M0MpCehiHzreSzNTczkc9d'?>
#     # <x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 11.88'>
#     # <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>

#     # <rdf:Description rdf:about=''
#     # xmlns:tiff='http://ns.adobe.com/tiff/1.0/'>
#     # <tiff:Artist>me</tiff:Artist>
#     # </rdf:Description>
#     # </rdf:RDF>
#     # </x:xmpmeta>

#     assert xmp_info is not None
#     f(xmp_info)
