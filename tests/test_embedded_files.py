"""Test the EmbeddedFile setters and read-only name property."""

from datetime import datetime
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject,
    NullObject,
    create_string_object,
)


def test_embedded_file_name_is_read_only():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    assert embedded_file.name == "test.txt"

    with pytest.raises(AttributeError):
        embedded_file.name = "new_name.txt"  # type: ignore


def test_embedded_file_alternative_name_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = "Alternative Name"  # type: ignore
    assert embedded_file.alternative_name == "Alternative Name"

    embedded_file.alternative_name = None  # type: ignore
    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()

    pdf_string = create_string_object("PDF String")
    embedded_file.alternative_name = pdf_string  # type: ignore
    assert embedded_file.alternative_name == "PDF String"


def test_embedded_file_description_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.description = "Test Description"  # type: ignore
    assert embedded_file.description == "Test Description"

    embedded_file.description = None  # type: ignore
    assert embedded_file.pdf_object[NameObject("/Desc")] == NullObject()


def test_embedded_file_subtype_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.subtype = "/text/plain"  # type: ignore
    assert embedded_file.subtype == "/text/plain"

    embedded_file.subtype = None  # type: ignore
    assert embedded_file._embedded_file[NameObject("/Subtype")] == NullObject()


def test_embedded_file_size_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.size = 1024  # type: ignore
    assert embedded_file.size == 1024

    embedded_file.size = None  # type: ignore
    assert embedded_file._ensure_params()[NameObject("/Size")] == NullObject()


def test_embedded_file_creation_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime(2023, 1, 1, 12, 0, 0)
    embedded_file.creation_date = test_date  # type: ignore
    assert embedded_file.creation_date == test_date

    embedded_file.creation_date = None  # type: ignore
    assert embedded_file._ensure_params()[NameObject("/CreationDate")] == NullObject()


def test_embedded_file_modification_date_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    test_date = datetime(2023, 1, 2, 12, 0, 0)
    embedded_file.modification_date = test_date  # type: ignore
    assert embedded_file.modification_date == test_date

    embedded_file.modification_date = None  # type: ignore
    assert embedded_file._ensure_params()[NameObject("/ModDate")] == NullObject()


def test_embedded_file_checksum_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    checksum_bytes = b"checksum_value"
    embedded_file.checksum = checksum_bytes  # type: ignore
    assert embedded_file.checksum == checksum_bytes

    embedded_file.checksum = None  # type: ignore
    assert embedded_file._ensure_params()[NameObject("/CheckSum")] == NullObject()


def test_embedded_file_associated_file_relationship_setter():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.associated_file_relationship = "/Data"  # type: ignore
    assert embedded_file.associated_file_relationship == "/Data"


def test_embedded_file_setters_integration():
    writer = PdfWriter()
    writer.add_blank_page(100, 100)

    embedded_file = writer.add_attachment("test.txt", b"Hello, World!")
    embedded_file.alternative_name = "Alternative Name"  # type: ignore
    embedded_file.description = "Test Description"  # type: ignore
    embedded_file.subtype = "/text/plain"  # type: ignore
    embedded_file.size = 13  # type: ignore
    embedded_file.creation_date = datetime(2023, 1, 1, 12, 0, 0)  # type: ignore
    embedded_file.modification_date = datetime(2023, 1, 2, 12, 0, 0)  # type: ignore
    embedded_file.checksum = b"checksum123"  # type: ignore
    embedded_file.associated_file_relationship = "/Data"  # type: ignore

    pdf_bytes = BytesIO()
    writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    reader = PdfReader(pdf_bytes)
    assert "test.txt" in reader.attachments
    assert reader.attachments["test.txt"][0] == b"Hello, World!"


def test_embedded_file_null_object_handling():
    writer = PdfWriter()
    embedded_file = writer.add_attachment("test.txt", b"content")

    embedded_file.alternative_name = "Name"  # type: ignore
    embedded_file.description = "Description"  # type: ignore
    embedded_file.subtype = "/text/plain"  # type: ignore
    embedded_file.size = 1024  # type: ignore
    embedded_file.checksum = b"checksum"  # type: ignore

    embedded_file.alternative_name = None  # type: ignore
    embedded_file.description = None  # type: ignore
    embedded_file.subtype = None  # type: ignore
    embedded_file.size = None  # type: ignore
    embedded_file.checksum = None  # type: ignore

    assert embedded_file.pdf_object[NameObject("/UF")] == NullObject()
    assert embedded_file.pdf_object[NameObject("/Desc")] == NullObject()
    assert embedded_file._embedded_file[NameObject("/Subtype")] == NullObject()
    assert embedded_file._ensure_params()[NameObject("/Size")] == NullObject()
    assert embedded_file._ensure_params()[NameObject("/CheckSum")] == NullObject()
