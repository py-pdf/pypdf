"""Test the pypdf.generic._files module."""
import datetime
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from pypdf.generic import (
    ByteStringObject,
    DictionaryObject,
    EmbeddedFile,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
    create_string_object,
)
from tests import get_data_from_url

TESTS_ROOT = Path(__file__).parent.parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"

PDFATTACH_BINARY = shutil.which("pdfattach")


@pytest.mark.skipif(PDFATTACH_BINARY is None, reason="Requires poppler-utils")
def test_embedded_file__basic(tmpdir):
    clean_path = SAMPLE_ROOT / "002-trivial-libre-office-writer" / "002-trivial-libre-office-writer.pdf"
    attached_path = tmpdir / "attached.pdf"
    file_path = tmpdir / "test.txt"
    file_path.write_binary(b"Hello World\n")
    subprocess.run([PDFATTACH_BINARY, clean_path, file_path, attached_path])  # noqa: S603
    with PdfReader(str(attached_path)) as reader:
        attachment = next(iter(EmbeddedFile._load(reader.root_object)))

        assert attachment.name == "test.txt"
        assert attachment.alternative_name == "test.txt"
        assert attachment.description is None
        assert attachment.associated_file_relationship == "/Unspecified"
        assert attachment.subtype is None
        assert attachment.content == b"Hello World\n"
        assert attachment.size == 12
        assert attachment.creation_date is None
        assert attachment.modification_date is None
        assert attachment.checksum is None
        assert repr(attachment) == "<EmbeddedFile name='test.txt'>"


def test_embedded_file__artificial():
    # No alternative name.
    pdf_object = DictionaryObject(answer=42)
    attachment = EmbeddedFile(name="dummy", pdf_object=pdf_object)
    assert attachment.alternative_name is None

    # No /EF.
    with pytest.raises(PdfReadError, match=f"/EF entry not found: {pdf_object}"):
        _ = attachment._embedded_file

    # Empty /EF dictionary.
    pdf_object = DictionaryObject()
    pdf_object[NameObject("/EF")] = DictionaryObject()
    attachment = EmbeddedFile(name="dummy", pdf_object=pdf_object)
    with pytest.raises(PdfReadError, match=r"No /\(U\)F key found in file dictionary: {}"):
        _ = attachment._embedded_file

    # Missing /Params key.
    pdf_object[NameObject("/EF")] = DictionaryObject()
    pdf_object[NameObject("/EF")][NameObject("/F")] = DictionaryObject(answer=42)
    assert attachment._params == DictionaryObject()

    # An actual checksum is set.
    # Generated using `hashlib.md5(b"Hello World!\n").digest()`
    params = DictionaryObject()
    params[NameObject("/CheckSum")] = ByteStringObject(b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X")
    pdf_object[NameObject("/EF")][NameObject("/F")][NameObject("/Params")] = params
    assert attachment.checksum == b"\x8d\xdd\x8b\xe4\xb1y\xa5)\xaf\xa5\xf2\xff\xaeK\x98X"


@pytest.mark.enable_socket
def test_embedded_file__kids():
    # Generated using the instructions available from
    # https://medium.com/@pymupdf/zugferd-and-ghostscript-how-to-create-industry-standard-and-compliant-pdf-e-invoices-83c9fde31ee5
    # Notes:
    #   * Yes, we need the full paths. Otherwise, the output file will only have an empty page.
    #   * The XML file has been a custom basic text file.
    #   * The input PDF file has been the `002-trivial-libre-office-writer.pdf` file.
    url = "https://github.com/user-attachments/files/18691309/embedded_files_kids.pdf"
    name = "embedded_files_kids.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    attachments = list(EmbeddedFile._load(reader.root_object))
    assert len(attachments) == 1
    attachment = attachments[0]

    assert attachment.name == "factur-x.xml"
    assert attachment.alternative_name == "factur-x.xml"
    assert attachment.description == "ZUGFeRD electronic invoice"
    assert attachment.associated_file_relationship == "/Alternative"
    assert attachment.subtype == "/text/xml"
    assert attachment.content.startswith(b"Hello World!\n\nLorem ipsum dolor sit amet, ")
    assert attachment.content.endswith(b"\ntakimata sanctus est Lorem ipsum dolor sit amet.\n")
    assert attachment.size == 606
    assert attachment.creation_date is None
    assert attachment.modification_date == datetime.datetime(
        2013, 1, 21, 8, 14, 33, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
    )
    assert attachment.checksum is None
    assert repr(attachment) == "<EmbeddedFile name='factur-x.xml'>"

    # No /Names in /Kids.
    del (
        reader.root_object[NameObject("/Names")][NameObject("/EmbeddedFiles")][NameObject("/Kids")][0]
        .get_object()[NameObject("/Names")]
    )
    attachments = list(EmbeddedFile._load(reader.root_object))
    assert attachments == []


@pytest.mark.enable_socket
def test_embedded_file_ensure_params_existing_params():
    url = "https://github.com/user-attachments/files/18691309/embedded_files_kids.pdf"
    name = "embedded_files_kids.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    attachments = list(EmbeddedFile._load(reader.root_object))
    assert len(attachments) == 1
    attachment = attachments[0]

    assert "/Params" in attachment._embedded_file
    params_dict = attachment._ensure_params

    assert isinstance(params_dict, DictionaryObject)

    assert NameObject("/ModDate") in params_dict

    original_mod_date = params_dict.get(NameObject("/ModDate"))
    params_dict[NameObject("/TestParam")] = TextStringObject("test_value")

    assert params_dict[NameObject("/TestParam")] == TextStringObject("test_value")
    assert params_dict[NameObject("/ModDate")] == original_mod_date

    params_dict2 = attachment._ensure_params
    assert params_dict is params_dict2
    assert params_dict2[NameObject("/TestParam")] == TextStringObject("test_value")


def test_embedded_file_name_is_read_only():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    assert embedded_file.name == "test.txt"

    with pytest.raises(AttributeError):
        embedded_file.name = "new_name.txt"


def test_embedded_file_alternative_name_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = TextStringObject("Alternative Name")
    assert embedded_file.alternative_name == "Alternative Name"

    embedded_file.alternative_name = None
    if NameObject("/UF") in embedded_file.pdf_object:
        assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()
    if NameObject("/F") in embedded_file.pdf_object:
        assert embedded_file.pdf_object[NameObject("/F")] == NullObject()
    assert embedded_file.alternative_name is None

    pdf_string = TextStringObject("PDF String")
    embedded_file.alternative_name = pdf_string
    assert embedded_file.alternative_name == "PDF String"


def test_embedded_file_alternative_name_only_uf_key():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.pdf_object[NameObject("/UF")] = create_string_object("original_uf")
    del embedded_file.pdf_object[NameObject("/F")]

    assert NameObject("/UF") in embedded_file.pdf_object
    assert NameObject("/F") not in embedded_file.pdf_object

    embedded_file.alternative_name = None
    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()
    assert NameObject("/F") not in embedded_file.pdf_object

    embedded_file.alternative_name = TextStringObject("new_uf")
    assert embedded_file.pdf_object[NameObject("/UF")] == create_string_object("new_uf")
    assert NameObject("/F") not in embedded_file.pdf_object


def test_embedded_file_alternative_name_only_f_key():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.pdf_object[NameObject("/F")] = create_string_object("original_f")
    if NameObject("/UF") in embedded_file.pdf_object:
        del embedded_file.pdf_object[NameObject("/UF")]

    assert NameObject("/F") in embedded_file.pdf_object
    assert NameObject("/UF") not in embedded_file.pdf_object

    embedded_file.alternative_name = None
    assert embedded_file.pdf_object[NameObject("/F")] == NullObject()
    assert NameObject("/UF") not in embedded_file.pdf_object

    embedded_file.alternative_name = TextStringObject("new_f")
    assert embedded_file.pdf_object[NameObject("/F")] == create_string_object("new_f")
    assert NameObject("/UF") not in embedded_file.pdf_object


def test_embedded_file_alternative_name_both_f_and_uf():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.pdf_object[NameObject("/F")] = create_string_object("original_f")
    embedded_file.pdf_object[NameObject("/UF")] = create_string_object("original_uf")

    embedded_file.alternative_name = TextStringObject("new_name")
    assert embedded_file.pdf_object[NameObject("/F")] == create_string_object("new_name")
    assert embedded_file.pdf_object[NameObject("/UF")] == create_string_object("new_name")
    assert embedded_file.alternative_name == "new_name"

    embedded_file.alternative_name = None
    assert embedded_file.pdf_object[NameObject("/F")] == NullObject()
    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()
    assert embedded_file.alternative_name is None


def test_embedded_file_description_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.description = TextStringObject("Test Description")
    assert embedded_file.description == "Test Description"

    embedded_file.description = None
    assert embedded_file.pdf_object[NameObject("/Desc")] == NullObject()

    pdf_string = TextStringObject("PDF Description")
    embedded_file.description = pdf_string
    assert embedded_file.description == "PDF Description"


def test_embedded_file_subtype_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.subtype = NameObject("/text/plain")
    assert embedded_file.subtype == "/text/plain"

    embedded_file.subtype = None
    assert embedded_file._embedded_file[NameObject("/Subtype")] == NullObject()

    name_obj = NameObject("/application#2Fjson")
    embedded_file.subtype = name_obj
    assert embedded_file.subtype == "/application#2Fjson"


def test_embedded_file_content_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")
    assert embedded_file.content == b"content"

    embedded_file.content = b"Hello World!"
    assert embedded_file.content == b"Hello World!"

    embedded_file.content = "Lorem ipsum dolor sit amet"
    assert embedded_file.content == b"Lorem ipsum dolor sit amet"


def test_embedded_file_size_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.size = NumberObject(1024)
    assert embedded_file.size == 1024

    embedded_file.size = None
    assert embedded_file._ensure_params[NameObject("/Size")] == NullObject()

    num_obj = NumberObject(2048)
    embedded_file.size = num_obj
    assert embedded_file.size == 2048


def test_embedded_file_size_getter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file._ensure_params[NameObject("/Size")] = NullObject()
    assert embedded_file.size is None

    embedded_file._ensure_params[NameObject("/Size")] = NumberObject(4096)
    retrieved_size = embedded_file.size
    assert retrieved_size == 4096


def test_embedded_file_creation_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime.datetime(2023, 1, 1, 12, 0, 0)
    embedded_file.creation_date = test_date
    assert embedded_file.creation_date == test_date

    embedded_file.creation_date = None
    assert embedded_file._ensure_params[NameObject("/CreationDate")] == NullObject()


def test_embedded_file_modification_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime.datetime(2023, 1, 2, 12, 0, 0)
    embedded_file.modification_date = test_date
    assert embedded_file.modification_date == test_date

    embedded_file.modification_date = None
    assert embedded_file._ensure_params[NameObject("/ModDate")] == NullObject()


def test_embedded_file_checksum_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    checksum_bytes = ByteStringObject(b"checksum_value")
    embedded_file.checksum = checksum_bytes
    assert embedded_file.checksum == b"checksum_value"

    embedded_file.checksum = None
    assert embedded_file._ensure_params[NameObject("/CheckSum")] == NullObject()

    byte_string = ByteStringObject(b"pdf_checksum")
    embedded_file.checksum = byte_string
    assert embedded_file.checksum == b"pdf_checksum"


def test_embedded_file_associated_file_relationship_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.associated_file_relationship = NameObject("/Data")
    assert embedded_file.associated_file_relationship == "/Data"


def test_embedded_file_setters_integration():
    writer = PdfWriter()
    writer.add_blank_page(100, 100)

    embedded_file = writer.add_attachment("test.txt", b"Hello, World!")
    embedded_file.alternative_name = TextStringObject("Alternative Name")
    embedded_file.description = TextStringObject("Test Description")
    embedded_file.subtype = NameObject("/text/plain")
    embedded_file.size = NumberObject(13)
    creation_date = datetime.datetime(2023, 1, 1, 12, 0, 0)
    embedded_file.creation_date = creation_date
    modification_date = datetime.datetime(2023, 1, 2, 12, 0, 0)
    embedded_file.modification_date = modification_date
    embedded_file.checksum = ByteStringObject(b"checksum123")
    embedded_file.associated_file_relationship = NameObject("/Data")

    pdf_bytes = BytesIO()
    writer.write(pdf_bytes)

    reader = PdfReader(pdf_bytes)
    assert "test.txt" in reader.attachments


def test_embedded_file_null_object_handling():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = TextStringObject("Name")
    embedded_file.description = TextStringObject("Description")
    embedded_file.subtype = NameObject("/text/plain")
    embedded_file.size = NumberObject(1024)
    embedded_file.checksum = ByteStringObject(b"checksum")

    embedded_file.alternative_name = None
    embedded_file.description = None
    embedded_file.subtype = None
    embedded_file.size = None
    embedded_file.checksum = None

    assert embedded_file.alternative_name is None
    assert embedded_file.description is None
    assert embedded_file.subtype is None
    assert embedded_file.size is None
    assert embedded_file.checksum is None
