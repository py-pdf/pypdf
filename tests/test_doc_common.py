"""Test the pypdf._doc_common module."""
import re
import shutil
import subprocess
from pathlib import Path
from unittest import mock

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.generic import EmbeddedFile

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"

PDFATTACH_BINARY = shutil.which("pdfattach")


@pytest.mark.skipif(PDFATTACH_BINARY is None, reason="Requires poppler-utils")
def test_attachments(tmpdir):
    # No attachments.
    clean_path = SAMPLE_ROOT / "002-trivial-libre-office-writer" / "002-trivial-libre-office-writer.pdf"
    with PdfReader(clean_path) as pdf:
        assert pdf._list_attachments() == []
        assert list(pdf.attachment_list) == []

    # UF = name.
    attached_path = tmpdir / "attached.pdf"
    file_path = tmpdir / "test.txt"
    file_path.write_binary(b"Hello World\n")
    subprocess.run([PDFATTACH_BINARY, clean_path, file_path, attached_path])  # noqa: S603
    with PdfReader(str(attached_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        assert [(x.name, x.content) for x in pdf.attachment_list] == [("test.txt", b"Hello World\n")]
        assert next(pdf.attachment_list).alternative_name == "test.txt"

    # UF != name.
    different_path = tmpdir / "different.pdf"
    different_path.write_binary(re.sub(rb" /UF [^/]+ /", b" /UF(my-file.txt) /", attached_path.read_binary()))
    with PdfReader(str(different_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt", "my-file.txt"]
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        assert pdf._get_attachments("my-file.txt") == {"my-file.txt": b"Hello World\n"}
        assert [(x.name, x.content) for x in pdf.attachment_list] == [("test.txt", b"Hello World\n")]
        assert next(pdf.attachment_list).alternative_name == "my-file.txt"

    # Only name.
    no_f_path = tmpdir / "no-f.pdf"
    no_f_path.write_binary(re.sub(rb" /UF [^/]+ /", b" /", attached_path.read_binary()))
    with PdfReader(str(no_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        assert [(x.name, x.content) for x in pdf.attachment_list] == [("test.txt", b"Hello World\n")]
        assert next(pdf.attachment_list).alternative_name is None

    # UF and F.
    uf_f_path = tmpdir / "uf-f.pdf"
    uf_f_path.write_binary(attached_path.read_binary().replace(b" /UF ", b"/F(file.txt) /UF "))
    with PdfReader(str(uf_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        assert [(x.name, x.content) for x in pdf.attachment_list] == [("test.txt", b"Hello World\n")]
        assert next(pdf.attachment_list).alternative_name == "test.txt"

    # Only F.
    only_f_path = tmpdir / "f.pdf"
    only_f_path.write_binary(attached_path.read_binary().replace(b" /UF ", b" /F "))
    with PdfReader(str(only_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        assert [(x.name, x.content) for x in pdf.attachment_list] == [("test.txt", b"Hello World\n")]
        assert next(pdf.attachment_list).alternative_name == "test.txt"


def test_get_attachments__same_attachment_more_than_twice():
    writer = PdfWriter()
    writer.add_blank_page(100, 100)
    for i in range(5):
        writer.add_attachment("test.txt", f"content{i}")
    assert writer._get_attachments("test.txt") == {
        "test.txt": [b"content0", b"content1", b"content2", b"content3", b"content4"]
    }
    assert [(x.name, x.content) for x in writer.attachment_list] == [
        ("test.txt", b"content0"),
        ("test.txt", b"content1"),
        ("test.txt", b"content2"),
        ("test.txt", b"content3"),
        ("test.txt", b"content4"),
    ]


def test_get_attachments__alternative_name_is_none():
    writer = PdfWriter()
    attachment = EmbeddedFile(name="test.txt", pdf_object=writer.root_object)
    assert attachment.alternative_name is None
    with mock.patch(
            "pypdf._writer.PdfWriter.attachment_list",
            new_callable=mock.PropertyMock(return_value=[attachment])
    ), mock.patch(
            "pypdf.generic._files.EmbeddedFile.content",
            new_callable=mock.PropertyMock(return_value=b"content")
    ):
        assert writer._get_attachments() == {"test.txt": b"content"}
