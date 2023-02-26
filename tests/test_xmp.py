from datetime import datetime
from io import BytesIO
from pathlib import Path

import pytest

import pypdf.generic
import pypdf.xmp
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from . import get_pdf_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.mark.parametrize(
    ("src", "has_xmp"),
    [
        (RESOURCE_ROOT / "commented-xmp.pdf", True),
        (RESOURCE_ROOT / "crazyones.pdf", False),
    ],
)
def test_read_xmp(src, has_xmp):
    reader = PdfReader(src)
    xmp = reader.xmp_metadata
    assert (xmp is None) == (not has_xmp)
    if has_xmp:
        for _ in xmp.get_element(
            about_uri="", namespace=pypdf.xmp.RDF_NAMESPACE, name="Artist"
        ):
            pass

        assert get_all_tiff(xmp) == {"tiff:Artist": ["me"]}
        assert xmp.dc_contributor == []


def get_all_tiff(xmp: pypdf.xmp.XmpInformation):
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
    date = pypdf.xmp._converter_date("2021-04-28T12:23:34.123Z")
    assert date.year == 2021
    assert date.month == 4
    assert date.day == 28
    assert date.hour == 12
    assert date.minute == 23
    assert date.second == 34
    assert date.microsecond == 123000
    with pytest.raises(ValueError) as exc:
        pypdf.xmp._converter_date("today")
    assert exc.value.args[0].startswith("Invalid date format")

    date = pypdf.xmp._converter_date("2021-04-28T12:23:01-03:00")
    assert date.year == 2021
    assert date.month == 4
    assert date.day == 28
    assert date.hour == 15
    assert date.minute == 23
    assert date.second == 1
    assert date.microsecond == 0


def test_regression_issue914():
    path = RESOURCE_ROOT / "issue-914-xmp-data.pdf"
    reader = PdfReader(path)
    assert reader.xmp_metadata.xmp_modify_date == datetime(2022, 4, 9, 15, 22, 43)


@pytest.mark.parametrize(
    "x",
    ["a", 42, 3.141, False, True],
)
def test_identity(x):
    assert pypdf.xmp._identity(x) == x


@pytest.mark.external
@pytest.mark.parametrize(
    ("url", "name", "xmpmm_instance_id"),
    [
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/955/955562.pdf",
            "tika-955562.pdf",
            "uuid:ca96e032-c2af-49bd-a71c-95889bafbf1d",
        )
    ],
)
def test_xmpmm(url, name, xmpmm_instance_id):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.xmpmm_instance_id == xmpmm_instance_id
    # cache hit:
    assert xmp_metadata.xmpmm_instance_id == xmpmm_instance_id


@pytest.mark.external
def test_dc_description():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/953/953770.pdf"
    name = "tika-953770.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.dc_description == {
        "x-default": "U.S. Title 50 Certification Form"
    }
    # cache hit:
    assert xmp_metadata.dc_description == {
        "x-default": "U.S. Title 50 Certification Form"
    }


@pytest.mark.external
def test_dc_creator():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/953/953770.pdf"
    name = "tika-953770.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.dc_creator == ["U.S. Fish and Wildlife Service"]
    # cache hit:
    assert xmp_metadata.dc_creator == ["U.S. Fish and Wildlife Service"]


@pytest.mark.external
def test_custom_properties():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/986/986065.pdf"
    name = "tika-986065.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.custom_properties == {"Style": "Searchable Image (Exact)"}
    # cache hit:
    assert xmp_metadata.custom_properties == {"Style": "Searchable Image (Exact)"}


@pytest.mark.external
def test_dc_subject():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/959/959519.pdf"
    name = "tika-959519.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.dc_subject == [
        "P&P",
        "manual",
        "1240.2325",
        "CVM",
        "PROCEDURES ON MEDIA INQUIRIES",
        "animal",
        "media",
        "procedures",
        "inquiries",
    ]
    # Cache hit:
    assert xmp_metadata.dc_subject == [
        "P&P",
        "manual",
        "1240.2325",
        "CVM",
        "PROCEDURES ON MEDIA INQUIRIES",
        "animal",
        "media",
        "procedures",
        "inquiries",
    ]


@pytest.mark.external
def test_issue585():
    url = "https://github.com/py-pdf/pypdf/files/5536984/test.pdf"
    name = "pypdf-5536984.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    with pytest.raises(PdfReadError) as exc:
        reader.xmp_metadata
    assert exc.value.args[0].startswith("XML in XmpInformation was invalid")


def test_getter_bag():
    f = pypdf.xmp._getter_bag("namespace", "name")

    class Tst:  # to replace pdf
        strict = False

    reader = PdfReader(RESOURCE_ROOT / "commented-xmp.pdf")
    xmp_info = reader.xmp_metadata
    # <?xpacket begin='ï»¿' id='W5M0MpCehiHzreSzNTczkc9d'?>
    # <x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 11.88'>
    # <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>

    # <rdf:Description rdf:about=''
    # xmlns:tiff='http://ns.adobe.com/tiff/1.0/'>
    # <tiff:Artist>me</tiff:Artist>
    # </rdf:Description>
    # </rdf:RDF>
    # </x:xmpmeta>

    assert xmp_info is not None
    f(xmp_info)
