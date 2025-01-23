"""Test the pypdf._doc_common module."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from pypdf import PdfReader

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"

PDFATTACH_BINARY = shutil.which("pdfattach")


@pytest.mark.skipif(PDFATTACH_BINARY is None, reason="Requires poppler-utils")
def test_list_attachments(tmpdir):
    # No attachments.
    clean_path = SAMPLE_ROOT / "002-trivial-libre-office-writer" / "002-trivial-libre-office-writer.pdf"
    with PdfReader(clean_path) as pdf:
        assert pdf._list_attachments() == []

    # UF = name.
    attached_path = tmpdir / "attached.pdf"
    file_path = tmpdir / "test.txt"
    file_path.write_binary(b"Hello World\n")
    subprocess.run([PDFATTACH_BINARY, clean_path, file_path, attached_path])  # noqa: S603
    with PdfReader(str(attached_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]

    # UF != name.
    different_path = tmpdir / "different.pdf"
    different_path.write_binary(re.sub(rb" /UF [^/]+ /", b" /UF(my-file.txt) /", attached_path.read_binary()))
    with PdfReader(str(different_path)) as pdf:
        assert set(pdf._list_attachments()) == {"test.txt", "my-file.txt"}

    # Only name.
    no_f_path = tmpdir / "no-f.pdf"
    no_f_path.write_binary(re.sub(rb" /UF [^/]+ /", b" /", attached_path.read_binary()))
    with PdfReader(str(no_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]

    # UF and F.
    uf_f_path = tmpdir / "uf-f.pdf"
    uf_f_path.write_binary(re.sub(rb" /UF ", b"/F(file.txt) /UF ", attached_path.read_binary()))
    with PdfReader(str(uf_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]

    # Only F.
    only_f_path = tmpdir / "f.pdf"
    only_f_path.write_binary(re.sub(rb" /UF ", b" /F ", attached_path.read_binary()))
    with PdfReader(str(only_f_path)) as pdf:
        assert pdf._list_attachments() == ["test.txt"]


@pytest.mark.skipif(PDFATTACH_BINARY is None, reason="Requires poppler-utils")
def test_get_attachments(tmpdir):
    clean_path = SAMPLE_ROOT / "002-trivial-libre-office-writer" / "002-trivial-libre-office-writer.pdf"
    attached_path = tmpdir / "attached.pdf"
    file_path = tmpdir / "test.txt"
    file_path.write_binary(b"Hello World\n")
    subprocess.run([PDFATTACH_BINARY, clean_path, file_path, attached_path])  # noqa: S603

    # Request with UF and key being identical (only return one file!)
    with PdfReader(str(attached_path)) as pdf:
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}

    # Request by key.
    different_path = tmpdir / "different.pdf"
    different_path.write_binary(re.sub(rb" /UF [^/]+ /", b" /UF(my-file.txt) /", attached_path.read_binary()))
    with PdfReader(str(different_path)) as pdf:
        assert pdf._get_attachments("test.txt") == {"test.txt": b"Hello World\n"}
        # Request by different UF.
        assert pdf._get_attachments("my-file.txt") == {"my-file.txt": b"Hello World\n"}
