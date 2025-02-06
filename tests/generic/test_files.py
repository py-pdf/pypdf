"""Test the pypdf.generic._files module."""
import datetime
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import pytest

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pypdf.generic import ByteStringObject, DictionaryObject, EmbeddedFile, NameObject
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
