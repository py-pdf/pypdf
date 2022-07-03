import os

import pytest

import PyPDF2
from PyPDF2.errors import DependencyError

try:
    from Crypto.Cipher import AES  # noqa: F401

    HAS_PYCRYPTODOME = True
except ImportError:
    HAS_PYCRYPTODOME = False

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


@pytest.mark.parametrize(
    ("name", "requres_pycryptodome"),
    [
        # unencrypted pdf
        ("unencrypted.pdf", False),
        # created by `qpdf --encrypt "" "" 40 -- unencrypted.pdf r2-empty-password.pdf`
        ("r2-empty-password.pdf", False),
        # created by `qpdf --encrypt "" "" 128 -- unencrypted.pdf r3-empty-password.pdf`
        ("r3-empty-password.pdf", False),
        # created by `qpdf --encrypt "asdfzxcv" "" 40 -- unencrypted.pdf r2-user-password.pdf`
        ("r2-user-password.pdf", False),
        # created by `qpdf --encrypt "asdfzxcv" "" 128 -- unencrypted.pdf r3-user-password.pdf`
        ("r3-user-password.pdf", False),
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --force-V4 -- unencrypted.pdf r4-user-password.pdf`
        ("r4-user-password.pdf", False),
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --use-aes=y -- unencrypted.pdf r4-aes-user-password.pdf`
        ("r4-aes-user-password.pdf", True),
        # # created by `qpdf --encrypt "" "" 256 --force-R5 -- unencrypted.pdf r5-empty-password.pdf`
        ("r5-empty-password.pdf", True),
        # # created by `qpdf --encrypt "asdfzxcv" "" 256 --force-R5 -- unencrypted.pdf r5-user-password.pdf`
        ("r5-user-password.pdf", True),
        # # created by `qpdf --encrypt "" "asdfzxcv" 256 --force-R5 -- unencrypted.pdf r5-owner-password.pdf`
        ("r5-owner-password.pdf", True),
        # created by `qpdf --encrypt "" "" 256 -- unencrypted.pdf r6-empty-password.pdf`
        ("r6-empty-password.pdf", True),
        # created by `qpdf --encrypt "asdfzxcv" "" 256 -- unencrypted.pdf r6-user-password.pdf`
        ("r6-user-password.pdf", True),
        # created by `qpdf --encrypt "" "asdfzxcv" 256 -- unencrypted.pdf r6-owner-password.pdf`
        ("r6-owner-password.pdf", True),
    ],
)
def test_encryption(name, requres_pycryptodome):
    inputfile = os.path.join(RESOURCE_ROOT, "encryption", name)
    if requres_pycryptodome and not HAS_PYCRYPTODOME:
        with pytest.raises(DependencyError) as exc:
            ipdf = PyPDF2.PdfReader(inputfile)
            ipdf.decrypt("asdfzxcv")
            dd = dict(ipdf.metadata)
        assert exc.value.args[0] == "PyCryptodome is required for AES algorithm"
        return
    else:
        ipdf = PyPDF2.PdfReader(inputfile)
        if inputfile.endswith("unencrypted.pdf"):
            assert not ipdf.is_encrypted
        else:
            assert ipdf.is_encrypted
            ipdf.decrypt("asdfzxcv")
        assert len(ipdf.pages) == 1
        dd = dict(ipdf.metadata)
    # remove empty value entry
    dd = {x[0]: x[1] for x in dd.items() if x[1]}
    assert dd == {
        "/Author": "cheng",
        "/CreationDate": "D:20220414132421+05'24'",
        "/Creator": "WPS Writer",
        "/ModDate": "D:20220414132421+05'24'",
        "/SourceModified": "D:20220414132421+05'24'",
        "/Trapped": "/False",
    }


@pytest.mark.parametrize(
    ("name", "user_passwd", "owner_passwd"),
    [
        # created by `qpdf --encrypt "foo" "bar" 256 -- unencrypted.pdf r6-both-passwords.pdf`
        ("r6-both-passwords.pdf", "foo", "bar"),
    ],
)
@pytest.mark.skipif(not HAS_PYCRYPTODOME, reason="No pycryptodome")
def test_both_password(name, user_passwd, owner_passwd):
    from PyPDF2 import PasswordType

    inputfile = os.path.join(RESOURCE_ROOT, "encryption", name)
    ipdf = PyPDF2.PdfReader(inputfile)
    assert ipdf.is_encrypted
    assert ipdf.decrypt(user_passwd) == PasswordType.USER_PASSWORD
    assert ipdf.decrypt(owner_passwd) == PasswordType.OWNER_PASSWORD
    assert len(ipdf.pages) == 1


@pytest.mark.parametrize(
    ("pdffile", "password"),
    [
        ("crazyones-encrypted-256.pdf", "password"),
    ],
)
@pytest.mark.skipif(not HAS_PYCRYPTODOME, reason="No pycryptodome")
def test_get_page_of_encrypted_file_new_algorithm(pdffile, password):
    """
    Check if we can read a page of an encrypted file.

    This is a regression test for issue 327:
    IndexError for get_page() of decrypted file
    """
    path = os.path.join(RESOURCE_ROOT, pdffile)
    PyPDF2.PdfReader(path, password=password).pages[0]


@pytest.mark.parametrize(
    "names",
    [
        (
            [
                "unencrypted.pdf",
                "r3-user-password.pdf",
                "r4-aes-user-password.pdf",
                "r5-user-password.pdf",
            ]
        ),
    ],
)
@pytest.mark.skipif(not HAS_PYCRYPTODOME, reason="No pycryptodome")
def test_encryption_merge(names):
    pdf_merger = PyPDF2.PdfMerger()
    files = [os.path.join(RESOURCE_ROOT, "encryption", x) for x in names]
    pdfs = [PyPDF2.PdfReader(x) for x in files]
    for pdf in pdfs:
        if pdf.is_encrypted:
            pdf.decrypt("asdfzxcv")
        pdf_merger.append(pdf)
    # no need to write to file
    pdf_merger.close()
