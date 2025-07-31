"""Test the pypdf.xmp module."""
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pytest

import pypdf.generic
import pypdf.xmp
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from pypdf.generic import NameObject, StreamObject
from pypdf.xmp import XmpInformation

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


@pytest.mark.enable_socket
def test_xmp_metadata__content_stream_is_dictionary_object():
    url = "https://github.com/user-attachments/files/18943249/testing.pdf"
    name = "issue3107.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    with pytest.raises(
            PdfReadError,
            match="XML in XmpInformation was invalid: 'DictionaryObject' object has no attribute 'get_data'"
    ):
        assert reader.xmp_metadata is not None


@pytest.mark.enable_socket
def test_dc_creator__bag_instead_of_seq():
    url = "https://github.com/user-attachments/files/18381698/tika-924562.pdf"
    name = "tika-924562.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))

    assert reader.xmp_metadata is not None
    assert reader.xmp_metadata.dc_creator == ["William J. Hussar"]


@pytest.mark.enable_socket
def test_dc_language__no_bag_container():
    reader = PdfReader(BytesIO(get_data_from_url(name="iss2138.pdf")))

    assert reader.xmp_metadata is not None
    assert reader.xmp_metadata.dc_language == ["x-unknown"]


def test_reading_does_not_destroy_root_object():
    """Test for #3391."""
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "commented-xmp.pdf")
    xmp = writer.xmp_metadata
    assert xmp is not None
    assert not isinstance(writer.root_object["/Metadata"], XmpInformation)
    assert isinstance(writer.root_object["/Metadata"].get_object(), StreamObject)

    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    assert b"\n/Metadata 27 0 R\n" in output_bytes


def test_xmp_information__write_to_stream():
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "commented-xmp.pdf")
    xmp = writer.xmp_metadata

    output = BytesIO()
    with pytest.warns(
            DeprecationWarning,
            match=(
                r"^XmpInformation\.write_to_stream is deprecated and will be removed in pypdf 6\.0\.0\. "
                r"Use PdfWriter\.xmp_metadata instead\.$"
            )
    ):
        xmp.write_to_stream(output)
    output_bytes = output.getvalue()
    assert output_bytes.startswith(b"<<\n/Type /Metadata\n/Subtype /XML\n/Length 2786\n>>\nstream\n<?xpacket begin")


def test_pdf_writer__xmp_metadata_setter():
    # Clear existing metadata.
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "commented-xmp.pdf")
    assert writer.xmp_metadata is not None
    original_metadata = writer.xmp_metadata.stream.get_data()
    writer.xmp_metadata = None
    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    reader = PdfReader(BytesIO(output_bytes))
    assert reader.xmp_metadata is None

    # Attempt to clear again.
    writer = PdfWriter(clone_from=reader)
    assert writer.xmp_metadata is None
    writer.xmp_metadata = None
    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    reader = PdfReader(BytesIO(output_bytes))
    assert reader.xmp_metadata is None

    # Set new metadata from bytes.
    writer = PdfWriter(clone_from=reader)
    assert writer.xmp_metadata is None
    writer.xmp_metadata = original_metadata
    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    reader = PdfReader(BytesIO(output_bytes))
    assert get_all_tiff(reader.xmp_metadata) == {"tiff:Artist": ["me"]}

    # Set metadata from XmpInformation.
    writer = PdfWriter(clone_from=reader)
    xmp_metadata = writer.xmp_metadata
    assert get_all_tiff(xmp_metadata) == {"tiff:Artist": ["me"]}
    new_metadata = original_metadata.replace(b"<tiff:Artist>me</tiff:Artist>", b"<tiff:Artist>Foo Bar</tiff:Artist>")
    xmp_metadata.stream.set_data(new_metadata)
    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    reader = PdfReader(BytesIO(output_bytes))
    assert get_all_tiff(reader.xmp_metadata) == {"tiff:Artist": ["Foo Bar"]}

    # Fix metadata not being an IndirectObject before.
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "commented-xmp.pdf")
    writer.root_object[NameObject("/Metadata")] = writer.root_object["/Metadata"].get_object()
    assert "/XML" in str(writer.root_object)
    writer.xmp_metadata = new_metadata
    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()
    reader = PdfReader(BytesIO(output_bytes))
    assert get_all_tiff(reader.xmp_metadata) == {"tiff:Artist": ["Foo Bar"]}
    assert "/XML" not in str(writer.root_object)


def test_xmp_information_create():
    """Test XmpInformation.create() classmethod."""
    xmp = XmpInformation.create()
    assert xmp is not None
    assert xmp.dc_title is None or xmp.dc_title == {}
    assert xmp.dc_creator is None or xmp.dc_creator == []
    assert xmp.dc_description is None or xmp.dc_description == {}
    assert xmp.xmp_create_date is None
    assert xmp.pdf_producer is None


def test_xmp_information_set_dc_title():
    """Test setting dc:title metadata."""
    xmp = XmpInformation.create()

    title_values = {"x-default": "Test Title", "en": "Test Title EN"}
    xmp.set_dc_title(title_values)
    assert xmp.dc_title == title_values

    xmp.set_dc_title(None)
    assert xmp.dc_title is None or xmp.dc_title == {}


def test_xmp_information_set_dc_creator():
    """Test setting dc:creator metadata."""
    xmp = XmpInformation.create()

    creators = ["Author One", "Author Two"]
    xmp.set_dc_creator(creators)
    assert xmp.dc_creator == creators

    xmp.set_dc_creator(None)
    assert xmp.dc_creator is None or xmp.dc_creator == []


def test_xmp_information_set_dc_description():
    """Test setting dc:description metadata."""
    xmp = XmpInformation.create()

    description_values = {"x-default": "Test Description", "en": "Test Description EN"}
    xmp.set_dc_description(description_values)
    assert xmp.dc_description == description_values

    xmp.set_dc_description(None)
    assert xmp.dc_description is None or xmp.dc_description == {}


def test_xmp_information_set_dc_subject():
    """Test setting dc:subject metadata."""
    xmp = XmpInformation.create()

    subjects = ["keyword1", "keyword2", "keyword3"]
    xmp.set_dc_subject(subjects)
    assert xmp.dc_subject == subjects

    xmp.set_dc_subject(None)
    assert xmp.dc_subject is None or xmp.dc_subject == []


def test_xmp_information_set_dc_date():
    """Test setting dc:date metadata."""
    xmp = XmpInformation.create()

    test_date = datetime(2023, 12, 25, 10, 30, 45)
    xmp.set_dc_date([test_date])
    stored_dates = xmp.dc_date
    assert len(stored_dates) == 1

    date_string = "2023-12-25T10:30:45.000000Z"
    xmp.set_dc_date([date_string])
    stored_dates = xmp.dc_date
    assert len(stored_dates) == 1

    xmp.set_dc_date(None)
    assert xmp.dc_date is None or xmp.dc_date == []


def test_xmp_information_set_single_fields():
    """Test setting single-value metadata fields."""
    xmp = XmpInformation.create()

    xmp.set_dc_coverage("Global coverage")
    assert xmp.dc_coverage == "Global coverage"
    xmp.set_dc_coverage(None)
    assert xmp.dc_coverage is None

    xmp.set_dc_format("application/pdf")
    assert xmp.dc_format == "application/pdf"
    xmp.set_dc_format(None)
    assert xmp.dc_format is None

    xmp.set_dc_identifier("unique-id-123")
    assert xmp.dc_identifier == "unique-id-123"
    xmp.set_dc_identifier(None)
    assert xmp.dc_identifier is None

    xmp.set_dc_source("Original Source")
    assert xmp.dc_source == "Original Source"
    xmp.set_dc_source(None)
    assert xmp.dc_source is None


def test_xmp_information_set_bag_fields():
    """Test setting bag (unordered array) metadata fields."""
    xmp = XmpInformation.create()

    contributors = ["Contributor One", "Contributor Two"]
    xmp.set_dc_contributor(contributors)
    assert xmp.dc_contributor == contributors
    xmp.set_dc_contributor(None)
    assert xmp.dc_contributor is None or xmp.dc_contributor == []

    languages = ["en", "fr", "de"]
    xmp.set_dc_language(languages)
    assert xmp.dc_language == languages
    xmp.set_dc_language(None)
    assert xmp.dc_language is None or xmp.dc_language == []

    publishers = ["Publisher One", "Publisher Two"]
    xmp.set_dc_publisher(publishers)
    assert xmp.dc_publisher == publishers
    xmp.set_dc_publisher(None)
    assert xmp.dc_publisher is None or xmp.dc_publisher == []

    relations = ["Related Doc 1", "Related Doc 2"]
    xmp.set_dc_relation(relations)
    assert xmp.dc_relation == relations
    xmp.set_dc_relation(None)
    assert xmp.dc_relation is None or xmp.dc_relation == []

    types = ["Document", "Text"]
    xmp.set_dc_type(types)
    assert xmp.dc_type == types
    xmp.set_dc_type(None)
    assert xmp.dc_type is None or xmp.dc_type == []


def test_xmp_information_set_dc_rights():
    """Test setting dc:rights metadata."""
    xmp = XmpInformation.create()

    rights_values = {"x-default": "All rights reserved", "en": "All rights reserved EN"}
    xmp.set_dc_rights(rights_values)
    assert xmp.dc_rights == rights_values

    xmp.set_dc_rights(None)
    assert xmp.dc_rights is None or xmp.dc_rights == {}


def test_xmp_information_set_pdf_fields():
    """Test setting PDF namespace metadata fields."""
    xmp = XmpInformation.create()

    xmp.set_pdf_keywords("keyword1, keyword2, keyword3")
    assert xmp.pdf_keywords == "keyword1, keyword2, keyword3"
    xmp.set_pdf_keywords(None)
    assert xmp.pdf_keywords is None

    xmp.set_pdf_pdfversion("1.4")
    assert xmp.pdf_pdfversion == "1.4"
    xmp.set_pdf_pdfversion(None)
    assert xmp.pdf_pdfversion is None

    xmp.set_pdf_producer("pypdf")
    assert xmp.pdf_producer == "pypdf"
    xmp.set_pdf_producer(None)
    assert xmp.pdf_producer is None


def test_xmp_information_set_xmp_date_fields():
    """Test setting XMP date metadata fields."""
    xmp = XmpInformation.create()
    test_date = datetime(2023, 12, 25, 10, 30, 45)

    xmp.set_xmp_create_date(test_date)
    stored_date = xmp.xmp_create_date
    assert isinstance(stored_date, datetime)
    xmp.set_xmp_create_date(None)
    assert xmp.xmp_create_date is None

    xmp.set_xmp_modify_date(test_date)
    stored_date = xmp.xmp_modify_date
    assert isinstance(stored_date, datetime)
    xmp.set_xmp_modify_date(None)
    assert xmp.xmp_modify_date is None

    xmp.set_xmp_metadata_date(test_date)
    stored_date = xmp.xmp_metadata_date
    assert isinstance(stored_date, datetime)
    xmp.set_xmp_metadata_date(None)
    assert xmp.xmp_metadata_date is None


def test_xmp_information_set_xmp_creator_tool():
    """Test setting xmp:CreatorTool metadata."""
    xmp = XmpInformation.create()

    xmp.set_xmp_creator_tool("pypdf")
    assert xmp.xmp_creator_tool == "pypdf"
    xmp.set_xmp_creator_tool(None)
    assert xmp.xmp_creator_tool is None


def test_xmp_information_set_xmpmm_fields():
    """Test setting XMPMM namespace metadata fields."""
    xmp = XmpInformation.create()

    doc_id = "uuid:12345678-1234-1234-1234-123456789abc"
    xmp.set_xmpmm_document_id(doc_id)
    assert xmp.xmpmm_document_id == doc_id
    xmp.set_xmpmm_document_id(None)
    assert xmp.xmpmm_document_id is None

    instance_id = "uuid:87654321-4321-4321-4321-cba987654321"
    xmp.set_xmpmm_instance_id(instance_id)
    assert xmp.xmpmm_instance_id == instance_id
    xmp.set_xmpmm_instance_id(None)
    assert xmp.xmpmm_instance_id is None


def test_xmp_information_set_pdfaid_fields():
    """Test setting PDF/A ID namespace metadata fields."""
    xmp = XmpInformation.create()

    xmp.set_pdfaid_part("1")
    assert xmp.pdfaid_part == "1"
    xmp.set_pdfaid_part(None)
    assert xmp.pdfaid_part is None

    xmp.set_pdfaid_conformance("B")
    assert xmp.pdfaid_conformance == "B"
    xmp.set_pdfaid_conformance(None)
    assert xmp.pdfaid_conformance is None


def test_xmp_information_create_with_writer():
    """Test using XmpInformation.create() with PdfWriter."""
    xmp = XmpInformation.create()
    xmp.set_dc_title({"x-default": "Created with pypdf"})
    xmp.set_dc_creator(["pypdf user"])
    xmp.set_pdf_producer("pypdf library")

    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.xmp_metadata = xmp

    output = BytesIO()
    writer.write(output)
    output_bytes = output.getvalue()

    reader = PdfReader(BytesIO(output_bytes))
    xmp_read = reader.xmp_metadata
    assert xmp_read is not None
    assert xmp_read.dc_title == {"x-default": "Created with pypdf"}
    assert xmp_read.dc_creator == ["pypdf user"]
    assert xmp_read.pdf_producer == "pypdf library"


def test_xmp_information_namespace_prefix():
    """Test _get_namespace_prefix method."""
    xmp = XmpInformation.create()

    assert xmp._get_namespace_prefix(pypdf.xmp.DC_NAMESPACE) == "dc"
    assert xmp._get_namespace_prefix(pypdf.xmp.XMP_NAMESPACE) == "xmp"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDF_NAMESPACE) == "pdf"
    assert xmp._get_namespace_prefix(pypdf.xmp.XMPMM_NAMESPACE) == "xmpMM"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDFAID_NAMESPACE) == "pdfaid"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDFX_NAMESPACE) == "pdfx"
    assert xmp._get_namespace_prefix("unknown://namespace") == "unknown"


def test_xmp_information_owner_document_none_errors():
    """Test error handling when ownerDocument is None."""
    xmp = XmpInformation.create()

    # Save original owner document
    original_owner = xmp.rdf_root.ownerDocument

    try:
        # Remove existing descriptions to force creation of new one
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)

        # Set ownerDocument to None to trigger error conditions
        xmp.rdf_root.ownerDocument = None

        # Test _get_or_create_description error (lines 459-465)
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp._get_or_create_description()

        # Test _update_stream error (line 597)
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp._update_stream()

        # Restore owner document for other tests (but clear the descriptions again)
        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        # Test _set_single_value error (line 484) - this will try to create description
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp.set_dc_coverage("test coverage")

        # Restore and clear again for bag values test
        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        # Test _set_bag_values error (line 506)
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp.set_dc_contributor(["contributor"])

        # Restore and clear again for seq values test
        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        # Test _set_seq_values error (line 535)
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp.set_dc_creator(["creator"])

        # Restore and clear again for langalt values test
        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        # Test _set_langalt_values error (line 564)
        with pytest.raises(RuntimeError, match="XMP Document is None"):
            xmp.set_dc_title({"x-default": "title"})

    finally:
        # Restore original owner document
        xmp.rdf_root.ownerDocument = original_owner


def test_xmp_information_remove_existing_attribute():
    """Test removing existing attribute node (line 479)."""
    xmp = XmpInformation.create()

    # Set a single value first to create an attribute
    xmp.set_dc_coverage("initial coverage")
    assert xmp.dc_coverage == "initial coverage"

    # Set a different value to trigger attribute removal and replacement
    xmp.set_dc_coverage("updated coverage")
    assert xmp.dc_coverage == "updated coverage"

    # Set to None to remove the attribute entirely
    xmp.set_dc_coverage(None)
    assert xmp.dc_coverage is None


def test_xmp_information_edge_case_coverage():
    """Test additional edge cases for complete coverage."""
    xmp = XmpInformation.create()

    # Test setting empty values
    xmp.set_dc_contributor([])
    assert xmp.dc_contributor == []

    xmp.set_dc_creator([])
    assert xmp.dc_creator == []

    xmp.set_dc_title({})
    assert xmp.dc_title == {}

    # Test setting None values
    xmp.set_dc_contributor(None)
    assert xmp.dc_contributor == []

    xmp.set_dc_creator(None)
    assert xmp.dc_creator == []

    xmp.set_dc_title(None)
    assert xmp.dc_title == {}


def test_xmp_information_create_new_description():
    """Test creating new description elements (lines 462-465)."""
    xmp = XmpInformation.create()

    # Remove all existing descriptions
    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    # Create a new description with specific about URI (covers lines 462-465)
    desc = xmp._get_or_create_description("test-uri")
    assert desc.getAttributeNS(pypdf.xmp.RDF_NAMESPACE, "about") == "test-uri"

    # Test that it creates the element with proper namespace
    assert desc.tagName == "rdf:Description"
    assert desc.namespaceURI == pypdf.xmp.RDF_NAMESPACE


def test_xmp_information_attribute_handling():
    """Test attribute node removal and creation (line 479, 484, 506, 535, 564)."""
    xmp = XmpInformation.create()

    # Remove all existing descriptions first
    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    # Test _set_single_value with new description creation (covers line 484 path where doc is not None)
    xmp.set_dc_coverage("test coverage")
    assert xmp.dc_coverage == "test coverage"

    # Test _set_bag_values with new description creation (covers line 506 path where doc is not None)
    xmp.set_dc_contributor(["contributor1", "contributor2"])
    assert xmp.dc_contributor == ["contributor1", "contributor2"]

    # Test _set_seq_values with new description creation (covers line 535 path where doc is not None)
    xmp.set_dc_creator(["creator1", "creator2"])
    assert xmp.dc_creator == ["creator1", "creator2"]

    # Test _set_langalt_values with new description creation (covers line 564 path where doc is not None)
    xmp.set_dc_title({"x-default": "Test Title", "en": "Test Title EN"})
    assert xmp.dc_title == {"x-default": "Test Title", "en": "Test Title EN"}

    # Test attribute node removal (line 479) by setting an attribute first, then changing it
    xmp.set_dc_format("application/pdf")
    assert xmp.dc_format == "application/pdf"

    # Change the value - this should trigger attribute node removal
    xmp.set_dc_format("text/plain")
    assert xmp.dc_format == "text/plain"


def test_xmp_information_complete_coverage():
    """Test remaining uncovered lines for complete coverage."""
    xmp = XmpInformation.create()

    # Test scenario where ownerDocument is available for all setter error paths
    # First remove all descriptions to force new creation
    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    # Test scenario where ownerDocument is available

    # Test the case where ownerDocument is not None in _set_single_value (covers line 484 success path)
    desc = xmp._get_or_create_description()
    desc.setAttribute("test", "value")
    # Now modify an existing attribute to test attribute removal (line 479)
    xmp.set_dc_source("original")
    xmp.set_dc_source("modified")  # This should trigger existing attribute removal
    assert xmp.dc_source == "modified"

    # Force recreate and test non-None document paths in other setters
    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    # Test success paths (non-None document) for all setter types
    xmp.set_dc_contributor(["test1"])  # covers line 506 success path
    xmp.set_dc_creator(["test2"])      # covers line 535 success path
    xmp.set_dc_title({"x-default": "test3"})  # covers line 564 success path

    assert xmp.dc_contributor == ["test1"]
    assert xmp.dc_creator == ["test2"]
    assert xmp.dc_title == {"x-default": "test3"}
