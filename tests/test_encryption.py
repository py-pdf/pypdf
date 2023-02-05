from pathlib import Path

import pytest

import pypdf
from pypdf import PasswordType, PdfReader
from pypdf._encryption import AlgV5, CryptRC4
from pypdf.errors import DependencyError, PdfReadError

try:
    from Crypto.Cipher import AES  # noqa

    HAS_PYCRYPTODOME = True
except ImportError:
    HAS_PYCRYPTODOME = False

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.mark.parametrize(
    ("name", "requires_pycryptodome"),
    [
        # unencrypted pdf
        ("unencrypted.pdf", False),
        # created by:
        # qpdf --encrypt "" "" 40 -- unencrypted.pdf r2-empty-password.pdf
        ("r2-empty-password.pdf", False),
        # created by:
        # qpdf --encrypt "" "" 128 -- unencrypted.pdf r3-empty-password.pdf
        ("r3-empty-password.pdf", False),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 40 -- unencrypted.pdf r2-user-password.pdf
        ("r2-user-password.pdf", False),
        # created by:
        # qpdf --encrypt "" "asdfzxcv" 40 -- unencrypted.pdf r2-user-password.pdf
        ("r2-owner-password.pdf", False),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 128 -- unencrypted.pdf r3-user-password.pdf
        ("r3-user-password.pdf", False),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 128 --force-V4 -- unencrypted.pdf r4-user-password.pdf
        ("r4-user-password.pdf", False),
        # created by:
        # qpdf --encrypt "" "asdfzxcv" 128 --force-V4 -- unencrypted.pdf r4-owner-password.pdf
        ("r4-owner-password.pdf", False),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 128 --use-aes=y -- unencrypted.pdf r4-aes-user-password.pdf
        ("r4-aes-user-password.pdf", True),
        # created by:
        # qpdf --encrypt "" "" 256 --force-R5 -- unencrypted.pdf r5-empty-password.pdf
        ("r5-empty-password.pdf", True),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 256 --force-R5 -- unencrypted.pdf r5-user-password.pdf
        ("r5-user-password.pdf", True),
        # created by:
        # qpdf --encrypt "" "asdfzxcv" 256 --force-R5 -- unencrypted.pdf r5-owner-password.pdf
        ("r5-owner-password.pdf", True),
        # created by:
        # qpdf --encrypt "" "" 256 -- unencrypted.pdf r6-empty-password.pdf
        ("r6-empty-password.pdf", True),
        # created by:
        # qpdf --encrypt "asdfzxcv" "" 256 -- unencrypted.pdf r6-user-password.pdf
        ("r6-user-password.pdf", True),
        # created by:
        # qpdf --encrypt "" "asdfzxcv" 256 -- unencrypted.pdf r6-owner-password.pdf
        ("r6-owner-password.pdf", True),
    ],
)
def test_encryption(name, requires_pycryptodome):
    inputfile = RESOURCE_ROOT / "encryption" / name
    if requires_pycryptodome and not HAS_PYCRYPTODOME:
        with pytest.raises(DependencyError) as exc:
            ipdf = pypdf.PdfReader(inputfile)
            ipdf.decrypt("asdfzxcv")
            dd = dict(ipdf.metadata)
        assert exc.value.args[0] == "PyCryptodome is required for AES algorithm"
        return
    else:
        ipdf = pypdf.PdfReader(inputfile)
        if str(inputfile).endswith("unencrypted.pdf"):
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
        # created by
        # qpdf --encrypt "foo" "bar" 256 -- unencrypted.pdf r6-both-passwords.pdf
        ("r6-both-passwords.pdf", "foo", "bar"),
    ],
)
@pytest.mark.skipif(not HAS_PYCRYPTODOME, reason="No pycryptodome")
def test_both_password(name, user_passwd, owner_passwd):
    inputfile = RESOURCE_ROOT / "encryption" / name
    ipdf = pypdf.PdfReader(inputfile)
    assert ipdf.is_encrypted
    assert ipdf.decrypt(user_passwd) == PasswordType.USER_PASSWORD
    assert ipdf.decrypt(owner_passwd) == PasswordType.OWNER_PASSWORD
    assert len(ipdf.pages) == 1


@pytest.mark.parametrize(
    ("pdffile", "password"),
    [
        ("crazyones-encrypted-256.pdf", "password"),
        ("crazyones-encrypted-256.pdf", b"password"),
    ],
)
@pytest.mark.skipif(not HAS_PYCRYPTODOME, reason="No pycryptodome")
def test_get_page_of_encrypted_file_new_algorithm(pdffile, password):
    """
    Check if we can read a page of an encrypted file.

    This is a regression test for issue 327:
    IndexError for get_page() of decrypted file
    """
    path = RESOURCE_ROOT / pdffile
    pypdf.PdfReader(path, password=password).pages[0]


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
    merger = pypdf.PdfMerger()
    files = [RESOURCE_ROOT / "encryption" / x for x in names]
    pdfs = [pypdf.PdfReader(x) for x in files]
    for pdf in pdfs:
        if pdf.is_encrypted:
            pdf.decrypt("asdfzxcv")
        merger.append(pdf)
    # no need to write to file
    merger.close()


@pytest.mark.parametrize(
    "cryptcls",
    [
        CryptRC4,
    ],
)
def test_encrypt_decrypt_class(cryptcls):
    message = b"Hello World"
    key = bytes(0 for _ in range(128))  # b"secret key"
    crypt = cryptcls(key)
    assert crypt.decrypt(crypt.encrypt(message)) == message


def test_decrypt_not_decrypted_pdf():
    path = RESOURCE_ROOT / "crazyones.pdf"
    with pytest.raises(PdfReadError) as exc:
        PdfReader(path, password="nonexistant")
    assert exc.value.args[0] == "Not encrypted file"


def test_generate_values():
    """
    This test only checks if there is an exception.

    It does not verify that the content is correct.
    """
    if not HAS_PYCRYPTODOME:
        return
    key = b"0123456789123451"
    values = AlgV5.generate_values(
        user_password=b"foo",
        owner_password=b"bar",
        key=key,
        p=0,
        metadata_encrypted=True,
    )
    assert values == {
        "/U": values["/U"],
        "/UE": values["/UE"],
        "/O": values["/O"],
        "/OE": values["/OE"],
        "/Perms": values["/Perms"],
    }
