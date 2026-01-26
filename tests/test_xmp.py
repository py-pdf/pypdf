"""Test the pypdf.xmp module."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

import pytest

import pypdf.generic
import pypdf.xmp
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError, XmpDocumentError
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


def test_xmp_information__create():
    """Test XmpInformation.create() classmethod."""
    xmp = XmpInformation.create()
    assert xmp is not None
    assert xmp.dc_title == {}
    assert xmp.dc_creator == []
    assert xmp.dc_description == {}
    assert xmp.xmp_create_date is None
    assert xmp.pdf_producer is None


def test_xmp_information__set_dc_title():
    """Test setting dc:title metadata."""
    xmp = XmpInformation.create()

    title_values = {"x-default": "Test Title", "en": "Test Title EN"}
    xmp.dc_title = title_values
    assert xmp.dc_title == title_values

    xmp.dc_title = None
    assert xmp.dc_title is None or xmp.dc_title == {}


def test_xmp_information__set_dc_creator():
    """Test setting dc:creator metadata."""
    xmp = XmpInformation.create()

    creators = ["Author One", "Author Two"]
    xmp.dc_creator = creators
    assert xmp.dc_creator == creators

    xmp.dc_creator = None
    assert xmp.dc_creator is None or xmp.dc_creator == []


def test_xmp_information__set_dc_description():
    """Test setting dc:description metadata."""
    xmp = XmpInformation.create()

    description_values = {"x-default": "Test Description", "en": "Test Description EN"}
    xmp.dc_description = description_values
    assert xmp.dc_description == description_values

    xmp.dc_description = None
    assert xmp.dc_description is None or xmp.dc_description == {}


def test_xmp_information__set_dc_subject():
    """Test setting dc:subject metadata."""
    xmp = XmpInformation.create()

    subjects = ["keyword1", "keyword2", "keyword3"]
    xmp.dc_subject = subjects
    assert xmp.dc_subject == subjects

    xmp.dc_subject = None
    assert xmp.dc_subject is None or xmp.dc_subject == []


def test_xmp_information__set_dc_date():
    """Test setting dc:date metadata."""
    xmp = XmpInformation.create()

    test_date = datetime(2023, 12, 25, 10, 30, 45)
    xmp.dc_date = [test_date]
    stored_dates = xmp.dc_date
    assert len(stored_dates) == 1

    date_string = "2023-12-25T10:30:45.000000Z"
    xmp.dc_date = [date_string]
    stored_dates = xmp.dc_date
    assert len(stored_dates) == 1

    xmp.dc_date = None
    assert xmp.dc_date is None or xmp.dc_date == []


def test_xmp_information__set_single_fields():
    """Test setting single-value metadata fields."""
    xmp = XmpInformation.create()

    xmp.dc_coverage = "Global coverage"
    assert xmp.dc_coverage == "Global coverage"
    xmp.dc_coverage = None
    assert xmp.dc_coverage is None

    xmp.dc_format = "application/pdf"
    assert xmp.dc_format == "application/pdf"
    xmp.dc_format = None
    assert xmp.dc_format is None

    xmp.dc_identifier = "unique-id-123"
    assert xmp.dc_identifier == "unique-id-123"
    xmp.dc_identifier = None
    assert xmp.dc_identifier is None

    xmp.dc_source = "Original Source"
    assert xmp.dc_source == "Original Source"
    xmp.dc_source = None
    assert xmp.dc_source is None


def test_xmp_information__set_bag_fields():
    """Test setting bag (unordered array) metadata fields."""
    xmp = XmpInformation.create()

    contributors = ["Contributor One", "Contributor Two"]
    xmp.dc_contributor = contributors
    assert xmp.dc_contributor == contributors
    xmp.dc_contributor = None
    assert xmp.dc_contributor is None or xmp.dc_contributor == []

    languages = ["en", "fr", "de"]
    xmp.dc_language = languages
    assert xmp.dc_language == languages
    xmp.dc_language = None
    assert xmp.dc_language is None or xmp.dc_language == []

    publishers = ["Publisher One", "Publisher Two"]
    xmp.dc_publisher = publishers
    assert xmp.dc_publisher == publishers
    xmp.dc_publisher = None
    assert xmp.dc_publisher is None or xmp.dc_publisher == []

    relations = ["Related Doc 1", "Related Doc 2"]
    xmp.dc_relation = relations
    assert xmp.dc_relation == relations
    xmp.dc_relation = None
    assert xmp.dc_relation is None or xmp.dc_relation == []

    types = ["Document", "Text"]
    xmp.dc_type = types
    assert xmp.dc_type == types
    xmp.dc_type = None
    assert xmp.dc_type is None or xmp.dc_type == []


def test_xmp_information__set_dc_rights():
    """Test setting dc:rights metadata."""
    xmp = XmpInformation.create()

    rights_values = {"x-default": "All rights reserved", "en": "All rights reserved EN"}
    xmp.dc_rights = rights_values
    assert xmp.dc_rights == rights_values

    xmp.dc_rights = None
    assert xmp.dc_rights is None or xmp.dc_rights == {}


def test_xmp_information__set_pdf_fields():
    """Test setting PDF namespace metadata fields."""
    xmp = XmpInformation.create()

    xmp.pdf_keywords = "keyword1, keyword2, keyword3"
    assert xmp.pdf_keywords == "keyword1, keyword2, keyword3"
    xmp.pdf_keywords = None
    assert xmp.pdf_keywords is None

    xmp.pdf_pdfversion = "1.4"
    assert xmp.pdf_pdfversion == "1.4"
    xmp.pdf_pdfversion = None
    assert xmp.pdf_pdfversion is None

    xmp.pdf_producer = "pypdf"
    assert xmp.pdf_producer == "pypdf"
    xmp.pdf_producer = None
    assert xmp.pdf_producer is None


def test_xmp_information__set_xmp_date_fields():
    """Test setting XMP date metadata fields."""
    xmp = XmpInformation.create()
    test_date = datetime(2023, 12, 25, 10, 30, 45)
    aware_date = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=-5)))

    xmp.xmp_create_date = test_date
    stored_date = xmp.xmp_create_date
    assert isinstance(stored_date, datetime)
    xmp.xmp_create_date = aware_date
    stored_date = xmp.xmp_create_date
    assert stored_date == datetime(2023, 1, 1, 17, 0, 0)
    xmp.xmp_create_date = None
    assert xmp.xmp_create_date is None

    xmp.xmp_modify_date = test_date
    stored_date = xmp.xmp_modify_date
    assert isinstance(stored_date, datetime)
    xmp.xmp_modify_date = aware_date
    stored_date = xmp.xmp_modify_date
    assert stored_date == datetime(2023, 1, 1, 17, 0, 0)
    xmp.xmp_modify_date = None
    assert xmp.xmp_modify_date is None

    xmp.xmp_metadata_date = test_date
    stored_date = xmp.xmp_metadata_date
    assert isinstance(stored_date, datetime)
    xmp.xmp_metadata_date = aware_date
    stored_date = xmp.xmp_metadata_date
    assert stored_date == datetime(2023, 1, 1, 17, 0, 0)
    xmp.xmp_metadata_date = None
    assert xmp.xmp_metadata_date is None


def test_xmp_information__set_xmp_creator_tool():
    """Test setting xmp:CreatorTool metadata."""
    xmp = XmpInformation.create()

    xmp.xmp_creator_tool = "pypdf"
    assert xmp.xmp_creator_tool == "pypdf"
    xmp.xmp_creator_tool = None
    assert xmp.xmp_creator_tool is None


def test_xmp_information__set_xmpmm_fields():
    """Test setting XMPMM namespace metadata fields."""
    xmp = XmpInformation.create()

    doc_id = "uuid:12345678-1234-1234-1234-123456789abc"
    xmp.xmpmm_document_id = doc_id
    assert xmp.xmpmm_document_id == doc_id
    xmp.xmpmm_document_id = None
    assert xmp.xmpmm_document_id is None

    instance_id = "uuid:87654321-4321-4321-4321-cba987654321"
    xmp.xmpmm_instance_id = instance_id
    assert xmp.xmpmm_instance_id == instance_id
    xmp.xmpmm_instance_id = None
    assert xmp.xmpmm_instance_id is None


def test_xmp_information__set_pdfaid_fields():
    """Test setting PDF/A ID namespace metadata fields."""
    xmp = XmpInformation.create()

    xmp.pdfaid_part = "1"
    assert xmp.pdfaid_part == "1"
    xmp.pdfaid_part = None
    assert xmp.pdfaid_part is None

    xmp.pdfaid_conformance = "B"
    assert xmp.pdfaid_conformance == "B"
    xmp.pdfaid_conformance = None
    assert xmp.pdfaid_conformance is None


def test_xmp_information__create_with_writer():
    """Test using XmpInformation.create() with PdfWriter."""
    xmp = XmpInformation.create()
    xmp.dc_title = {"x-default": "Created with pypdf"}
    xmp.dc_creator = ["pypdf user"]
    xmp.pdf_producer = "pypdf library"

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


def test_xmp_information__namespace_prefix():
    """Test _get_namespace_prefix method."""
    xmp = XmpInformation.create()

    assert xmp._get_namespace_prefix(pypdf.xmp.DC_NAMESPACE) == "dc"
    assert xmp._get_namespace_prefix(pypdf.xmp.XMP_NAMESPACE) == "xmp"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDF_NAMESPACE) == "pdf"
    assert xmp._get_namespace_prefix(pypdf.xmp.XMPMM_NAMESPACE) == "xmpMM"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDFAID_NAMESPACE) == "pdfaid"
    assert xmp._get_namespace_prefix(pypdf.xmp.PDFX_NAMESPACE) == "pdfx"
    assert xmp._get_namespace_prefix("unknown://namespace") == "unknown"


def test_xmp_information__owner_document_none_errors():
    xmp = XmpInformation.create()

    original_owner = xmp.rdf_root.ownerDocument

    try:
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)

        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._get_or_create_description()

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._update_stream()

        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp.dc_coverage = "test coverage"

        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp.dc_contributor = ["contributor"]

        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp.dc_creator = ["creator"]

        xmp.rdf_root.ownerDocument = original_owner
        for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
            xmp.rdf_root.removeChild(desc)
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp.dc_title = {"x-default": "title"}

        xmp.rdf_root.ownerDocument = original_owner
        desc = xmp._get_or_create_description()
        desc.setAttribute("test-attr", "test-value")
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._set_single_value("test-namespace", "test-attr", "new-value")

        xmp.rdf_root.ownerDocument = original_owner
        desc = xmp._get_or_create_description()
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._set_bag_values("test-namespace", "test-name", ["value"])

        xmp.rdf_root.ownerDocument = original_owner
        desc = xmp._get_or_create_description()
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._set_seq_values("test-namespace", "test-name", ["value"])

        xmp.rdf_root.ownerDocument = original_owner
        desc = xmp._get_or_create_description()
        xmp.rdf_root.ownerDocument = None

        with pytest.raises(XmpDocumentError, match="XMP Document is None"):
            xmp._set_langalt_values("test-namespace", "test-name", {"x-default": "value"})

    finally:
        xmp.rdf_root.ownerDocument = original_owner


def test_xmp_information__remove_existing_attribute():
    xmp = XmpInformation.create()

    xmp.dc_coverage = "initial coverage"
    assert xmp.dc_coverage == "initial coverage"

    xmp.dc_coverage = "updated coverage"
    assert xmp.dc_coverage == "updated coverage"

    xmp.dc_coverage = None
    assert xmp.dc_coverage is None

    desc = xmp._get_or_create_description()
    desc.setAttributeNS(pypdf.xmp.DC_NAMESPACE, "dc:coverage", "original attribute")

    assert desc.getAttributeNS(pypdf.xmp.DC_NAMESPACE, "coverage") == "original attribute"

    xmp.dc_coverage = "new element value"
    assert xmp.dc_coverage == "new element value"

    assert desc.getAttributeNS(pypdf.xmp.DC_NAMESPACE, "coverage") == ""

    elements = desc.getElementsByTagNameNS(pypdf.xmp.DC_NAMESPACE, "coverage")
    assert len(elements) == 1
    assert elements[0].firstChild.data == "new element value"


def test_xmp_information__edge_case_coverage():
    xmp = XmpInformation.create()

    xmp.dc_contributor = []
    assert xmp.dc_contributor == []

    xmp.dc_creator = []
    assert xmp.dc_creator == []

    xmp.dc_title = {}
    assert xmp.dc_title == {}

    xmp.dc_contributor = None
    assert xmp.dc_contributor == []

    xmp.dc_creator = None
    assert xmp.dc_creator == []

    xmp.dc_title = None
    assert xmp.dc_title == {}


def test_xmp_information__create_new_description():
    """Test creating new description elements."""
    xmp = XmpInformation.create()

    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    desc = xmp._get_or_create_description("test-uri")
    assert desc.getAttributeNS(pypdf.xmp.RDF_NAMESPACE, "about") == "test-uri"

    assert desc.tagName == "rdf:Description"
    assert desc.namespaceURI == pypdf.xmp.RDF_NAMESPACE


def test_xmp_information__get_text_skips_non_text_nodes():
    xmp = XmpInformation.create()

    doc = xmp.rdf_root.ownerDocument
    el = doc.createElementNS(pypdf.xmp.DC_NAMESPACE, "dc:test")
    el.appendChild(doc.createTextNode("hello"))
    el.appendChild(doc.createElement("ignored-node"))
    el.appendChild(doc.createTextNode(" world"))

    assert xmp._get_text(el) == "hello world"


def test_xmp_information__get_or_create_description_mismatch_about_uri():
    xmp = XmpInformation.create()

    existing = xmp._get_or_create_description()
    existing.setAttributeNS(pypdf.xmp.RDF_NAMESPACE, "rdf:about", "foo-uri")

    new_desc = xmp._get_or_create_description("bar-uri")
    assert new_desc is not existing
    assert new_desc.getAttributeNS(pypdf.xmp.RDF_NAMESPACE, "about") == "bar-uri"

    all_desc = list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description"))
    about_values = {d.getAttributeNS(pypdf.xmp.RDF_NAMESPACE, "about") for d in all_desc}
    assert {"foo-uri", "bar-uri"}.issubset(about_values)


def test_xmp_information__attribute_handling():
    """Test attribute node removal and creation (line 479, 484, 506, 535, 564)."""
    xmp = XmpInformation.create()

    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    xmp.dc_coverage = "test coverage"
    assert xmp.dc_coverage == "test coverage"

    xmp.dc_contributor = ["contributor1", "contributor2"]
    assert xmp.dc_contributor == ["contributor1", "contributor2"]

    xmp.dc_creator = ["creator1", "creator2"]
    assert xmp.dc_creator == ["creator1", "creator2"]

    xmp.dc_title = {"x-default": "Test Title", "en": "Test Title EN"}
    assert xmp.dc_title == {"x-default": "Test Title", "en": "Test Title EN"}

    xmp.dc_format = "application/pdf"
    assert xmp.dc_format == "application/pdf"

    xmp.dc_format = "text/plain"
    assert xmp.dc_format == "text/plain"


def test_xmp_information__create_and_set_metadata():
    xmp = XmpInformation.create()

    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    desc = xmp._get_or_create_description()
    desc.setAttribute("test", "value")
    xmp.dc_source = "original"
    xmp.dc_source = "modified"
    assert xmp.dc_source == "modified"

    for desc in list(xmp.rdf_root.getElementsByTagNameNS(pypdf.xmp.RDF_NAMESPACE, "Description")):
        xmp.rdf_root.removeChild(desc)

    xmp.dc_contributor = ["test1"]
    xmp.dc_creator = ["test2"]
    xmp.dc_title = {"x-default": "test3"}

    assert xmp.dc_contributor == ["test1"]
    assert xmp.dc_creator == ["test2"]
    assert xmp.dc_title == {"x-default": "test3"}
