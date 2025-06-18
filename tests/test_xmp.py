"""Test the pypdf.xmp module."""
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pytest

import pypdf.generic
import pypdf.xmp
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = Path(PROJECT_ROOT) / "sample-files"


@pytest.mark.samples
@pytest.mark.parametrize(
    "src",
    [
        (SAMPLE_ROOT / "020-xmp/output_with_metadata_pymupdf.pdf"),
    ],
)
def test_read_xmp_metadata_samples(src):
    reader = PdfReader(src)
    xmp = reader.xmp_metadata
    assert xmp
    assert xmp.dc_contributor == []
    assert xmp.dc_creator == ["John Doe"]
    assert xmp.dc_source == "Martin Thoma"  # attribute node
    assert xmp.dc_description == {"x-default": "This is a text"}
    assert xmp.dc_date == [datetime(1990, 4, 28, 0, 0)]
    assert xmp.dc_title == {"x-default": "Sample PDF with XMP Metadata"}
    assert xmp.custom_properties == {
        "Style": "FooBarStyle",
        "other": "worlds",
        "⏰": "time",
    }


@pytest.mark.samples
def test_writer_xmp_metadata_samples():
    writer = PdfWriter(SAMPLE_ROOT / "020-xmp/output_with_metadata_pymupdf.pdf")
    xmp = writer.xmp_metadata
    assert xmp
    assert xmp.dc_contributor == []
    assert xmp.dc_creator == ["John Doe"]
    assert xmp.dc_source == "Martin Thoma"  # attribute node
    assert xmp.dc_description == {"x-default": "This is a text"}
    assert xmp.dc_date == [datetime(1990, 4, 28, 0, 0)]
    assert xmp.dc_title == {"x-default": "Sample PDF with XMP Metadata"}
    assert xmp.custom_properties == {
        "Style": "FooBarStyle",
        "other": "worlds",
        "⏰": "time",
    }
    co = pypdf.generic.ContentStream(None, None)
    co.set_data(
        xmp.stream.get_data().replace(
            b'dc:source="Martin Thoma"', b'dc:source="Pubpub-Zz"'
        )
    )
    writer.xmp_metadata = pypdf.xmp.XmpInformation(co)
    b = BytesIO()
    writer.write(b)
    reader = PdfReader(b)
    xmp2 = reader.xmp_metadata
    assert xmp2.dc_source == "Pubpub-Zz"


@pytest.mark.parametrize(
    ("src", "has_xmp"),
    [
        (RESOURCE_ROOT / "commented-xmp.pdf", True),
        (RESOURCE_ROOT / "crazyones.pdf", False),
    ],
)
def test_read_xmp_metadata(src, has_xmp):
    """Read XMP metadata from PDF files."""
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
    """Return all TIFF metadata as a dictionary."""
    data = {}
    tiff_ns = xmp.get_nodes_in_namespace(
        about_uri="", namespace="http://ns.adobe.com/tiff/1.0/"
    )
    for tag in tiff_ns:
        contents = [content.data for content in tag.childNodes]
        data[tag.tagName] = contents
    return data


def test_converter_date():
    """
    _converter_date returns the correct datetime.

    This is a regression test for issue #774.
    """
    date = pypdf.xmp._converter_date("2021-04-28T12:23:34.123Z")
    assert date == datetime(2021, 4, 28, 12, 23, 34, 123000)

    with pytest.raises(ValueError) as exc:
        pypdf.xmp._converter_date("today")
    assert exc.value.args[0].startswith("Invalid date format")

    date = pypdf.xmp._converter_date("2021-04-28T12:23:01-03:00")
    assert date == datetime(2021, 4, 28, 15, 23, 1)


def test_modify_date():
    """
    xmp_modify_date is extracted correctly.

    This is a regression test for issue #914.
    """
    path = RESOURCE_ROOT / "issue-914-xmp-data.pdf"
    reader = PdfReader(path)
    assert reader.xmp_metadata.xmp_modify_date == datetime(2022, 4, 9, 15, 22, 43)


@pytest.mark.parametrize(
    "x",
    ["a", 42, 3.141, False, True],
)
def test_identity_function(x):
    """The identity is returning its input."""
    assert pypdf.xmp._identity(x) == x


@pytest.mark.enable_socket
@pytest.mark.parametrize(
    ("url", "name", "xmpmm_instance_id"),
    [
        (
            None,
            "tika-955562.pdf",
            "uuid:ca96e032-c2af-49bd-a71c-95889bafbf1d",
        )
    ],
)
def test_xmpmm_instance_id(url, name, xmpmm_instance_id):
    """XMPMM instance id is correctly extracted."""
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.xmpmm_instance_id == xmpmm_instance_id
    # cache hit:
    assert xmp_metadata.xmpmm_instance_id == xmpmm_instance_id


@pytest.mark.enable_socket
def test_xmp_dc_description_extraction():
    """XMP dc_description is correctly extracted."""
    url = "https://github.com/user-attachments/files/18381721/tika-953770.pdf"
    name = "tika-953770.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.dc_description == {
        "x-default": "U.S. Title 50 Certification Form"
    }
    # cache hit:
    assert xmp_metadata.dc_description == {
        "x-default": "U.S. Title 50 Certification Form"
    }


@pytest.mark.enable_socket
def test_dc_creator_extraction():
    """XMP dc_creator is correctly extracted."""
    url = "https://github.com/user-attachments/files/18381721/tika-953770.pdf"
    name = "tika-953770.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.dc_creator == ["U.S. Fish and Wildlife Service"]
    # cache hit:
    assert xmp_metadata.dc_creator == ["U.S. Fish and Wildlife Service"]


@pytest.mark.enable_socket
def test_custom_properties_extraction():
    """XMP custom_properties is correctly extracted."""
    url = "https://github.com/user-attachments/files/18381764/tika-986065.pdf"
    name = "tika-986065.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    xmp_metadata = reader.xmp_metadata
    assert xmp_metadata.custom_properties == {"Style": "Searchable Image (Exact)"}
    # cache hit:
    assert xmp_metadata.custom_properties == {"Style": "Searchable Image (Exact)"}


@pytest.mark.enable_socket
def test_dc_subject_extraction():
    """XMP dc_subject is correctly extracted."""
    url = "https://github.com/user-attachments/files/18381730/tika-959519.pdf"
    name = "tika-959519.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
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


@pytest.mark.enable_socket
def test_invalid_xmp_information_handling():
    """
    Invalid XML in xmp_metadata is gracefully handled.

    This is a regression test for issue #585.
    """
    url = "https://github.com/py-pdf/pypdf/files/5536984/test.pdf"
    name = "pypdf-5536984.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    with pytest.raises(PdfReadError) as exc:
        reader.xmp_metadata
    assert exc.value.args[0].startswith("XML in XmpInformation was invalid")


def test_xmp_getter_bag_function():
    """xmp._getter_bag does not crash."""
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


@pytest.mark.samples
def test_pdfa_xmp_metadata_with_values():
    """Test PDF/A XMP metadata extraction from a file with PDF/A metadata."""
    reader = PdfReader(SAMPLE_ROOT / "021-pdfa" / "crazyones-pdfa.pdf")
    xmp = reader.xmp_metadata

    assert xmp is not None
    assert xmp.pdfaid_part == "1"
    assert xmp.pdfaid_conformance == "B"


@pytest.mark.samples
def test_pdfa_xmp_metadata_without_values():
    """Test PDF/A XMP metadata extraction from a file without PDF/A metadata."""
    reader = PdfReader(SAMPLE_ROOT / "020-xmp" / "output_with_metadata_pymupdf.pdf")
    xmp = reader.xmp_metadata

    assert xmp is not None
    assert xmp.pdfaid_part is None
    assert xmp.pdfaid_conformance is None
