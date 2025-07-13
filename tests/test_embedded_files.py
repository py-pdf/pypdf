"""Test the EmbeddedFile setters and read-only name property."""

from datetime import datetime
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ByteStringObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
    create_string_object,
)


def test_embedded_file_name_is_read_only():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    assert embedded_file.name == "test.txt"

    with pytest.raises(AttributeError):
        embedded_file.name = "new_name.txt"


def test_embedded_file_alternative_name_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = "Alternative Name"
    assert embedded_file.alternative_name == "Alternative Name"

    embedded_file.alternative_name = None
    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()

    pdf_string = create_string_object("PDF String")
    embedded_file.alternative_name = pdf_string
    assert embedded_file.alternative_name == "PDF String"


def test_embedded_file_description_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.description = "Test Description"
    assert embedded_file.description == "Test Description"

    embedded_file.description = None
    assert embedded_file.pdf_object[NameObject("/Desc")] == NullObject()

    pdf_string = TextStringObject("PDF Description")
    embedded_file.description = pdf_string
    assert embedded_file.description == "PDF Description"


def test_embedded_file_subtype_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.subtype = "/text/plain"
    assert embedded_file.subtype == "/text/plain"

    embedded_file.subtype = None
    assert embedded_file._embedded_file[NameObject("/Subtype")] == NullObject()

    name_obj = NameObject("/application#2Fjson")
    embedded_file.subtype = name_obj
    assert embedded_file.subtype == "/application#2Fjson"


def test_embedded_file_size_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.size = 1024
    assert embedded_file.size == 1024

    embedded_file.size = None
    assert embedded_file._ensure_params()[NameObject("/Size")] == NullObject()

    num_obj = NumberObject(2048)
    embedded_file.size = num_obj
    assert embedded_file.size == 2048


def test_embedded_file_creation_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime(2023, 1, 1, 12, 0, 0)
    embedded_file.creation_date = test_date
    assert embedded_file.creation_date == test_date

    embedded_file.creation_date = None
    assert embedded_file._ensure_params()[NameObject("/CreationDate")] == NullObject()

    date_string = TextStringObject("D:20230101120000")
    embedded_file.creation_date = date_string
    assert embedded_file.creation_date is not None


def test_embedded_file_modification_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime(2023, 1, 2, 12, 0, 0)
    embedded_file.modification_date = test_date
    assert embedded_file.modification_date == test_date

    embedded_file.modification_date = None
    assert embedded_file._ensure_params()[NameObject("/ModDate")] == NullObject()

    date_string = TextStringObject("D:20230102120000")
    embedded_file.modification_date = date_string
    assert embedded_file.modification_date is not None


def test_embedded_file_checksum_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    checksum_bytes = b"checksum_value"
    embedded_file.checksum = checksum_bytes
    assert embedded_file.checksum == checksum_bytes

    embedded_file.checksum = None
    assert embedded_file._ensure_params()[NameObject("/CheckSum")] == NullObject()

    byte_string = ByteStringObject(b"pdf_checksum")
    embedded_file.checksum = byte_string
    assert embedded_file.checksum == b"pdf_checksum"


def test_embedded_file_associated_file_relationship_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.associated_file_relationship = "/Data"
    assert embedded_file.associated_file_relationship == "/Data"


def test_embedded_file_setters_integration():
    writer = PdfWriter()
    writer.add_blank_page(100, 100)

    embedded_file = writer.add_attachment("test.txt", b"Hello, World!")
    embedded_file.alternative_name = "Alternative Name"
    embedded_file.description = "Test Description"
    embedded_file.subtype = "/text/plain"
    embedded_file.size = 13
    embedded_file.creation_date = datetime(2023, 1, 1, 12, 0, 0)
    embedded_file.modification_date = datetime(2023, 1, 2, 12, 0, 0)
    embedded_file.checksum = b"checksum123"
    embedded_file.associated_file_relationship = "/Data"

    pdf_bytes = BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    reader = PdfReader(pdf_bytes)
    assert "test.txt" in reader.attachments
    assert reader.attachments["test.txt"][0] == b"Hello, World!"


def test_embedded_file_null_object_handling():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = "Name"
    embedded_file.description = "Description"
    embedded_file.subtype = "/text/plain"
    embedded_file.size = 1024
    embedded_file.checksum = b"checksum"

    embedded_file.alternative_name = None
    embedded_file.description = None
    embedded_file.subtype = None
    embedded_file.size = None
    embedded_file.checksum = None

    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()
    assert embedded_file.pdf_object[NameObject("/Desc")] == NullObject()
    assert embedded_file._embedded_file[NameObject("/Subtype")] == NullObject()
    assert embedded_file._ensure_params()[NameObject("/Size")] == NullObject()
    assert embedded_file._ensure_params()[NameObject("/CheckSum")] == NullObject()
