"""Test the pypdf._encryption module."""
import secrets
from pathlib import Path

import pytest

import pypdf
from pypdf import PasswordType, PdfReader, PdfWriter
from pypdf._crypt_providers import crypt_provider
from pypdf._crypt_providers._fallback import _DEPENDENCY_ERROR_STR
from pypdf._encryption import AlgV5, CryptAES, CryptRC4
from pypdf.errors import DependencyError, PdfReadError

USE_CRYPTOGRAPHY = crypt_provider[0] == "cryptography"
USE_PYCRYPTODOME = crypt_provider[0] == "pycryptodome"
HAS_AES = USE_CRYPTOGRAPHY or USE_PYCRYPTODOME
TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = PROJECT_ROOT / "sample-files"


@pytest.mark.parametrize(
    ("name", "requires_aes"),
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
        # qpdf --encrypt "" "asdfzxcv" 40 -- unencrypted.pdf r2-owner-password.pdf
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
def test_encryption(name, requires_aes):
    """
    Encrypted PDFs are handled correctly.

    This test function ensures that:
    - If PyCryptodome or cryptography is not available and required, a DependencyError is raised
    - Encrypted PDFs are identified correctly
    - Decryption works for encrypted PDFs
    - Metadata is properly extracted from the decrypted PDF
    """
    inputfile = RESOURCE_ROOT / "encryption" / name
    if requires_aes and not HAS_AES:
        with pytest.raises(DependencyError) as exc:
            ipdf = pypdf.PdfReader(inputfile)
            ipdf.decrypt("asdfzxcv")
            dd = dict(ipdf.metadata)
        assert exc.value.args[0] == _DEPENDENCY_ERROR_STR
        return
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
@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_pdf_with_both_passwords(name, user_passwd, owner_passwd):
    """
    PDFs with both user and owner passwords are handled correctly.

    This test function ensures that:
    - Encrypted PDFs with both user and owner passwords are identified correctly
    - Decryption works for both user and owner passwords
    - The correct password type is returned after decryption
    - The number of pages is correctly identified after decryption
    """
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
@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_read_page_from_encrypted_file_aes_256(pdffile, password):
    """
    A page can be read from an encrypted.

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
@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_merge_encrypted_pdfs(names):
    """Encrypted PDFs can be merged after decryption."""
    merger = pypdf.PdfWriter()
    files = [RESOURCE_ROOT / "encryption" / x for x in names]
    pdfs = [pypdf.PdfReader(x) for x in files]
    for pdf in pdfs:
        if pdf.is_encrypted:
            pdf.decrypt("asdfzxcv")
        merger.append(pdf)
    # no need to write to file
    merger.close()


@pytest.mark.skipif(
    USE_CRYPTOGRAPHY,
    reason="Limitations of cryptography. see https://github.com/pyca/cryptography/issues/2494",
)
@pytest.mark.parametrize(
    "cryptcls",
    [
        CryptRC4,
    ],
)
def test_encrypt_decrypt_with_cipher_class(cryptcls):
    """Encryption and decryption using a cipher class work as expected."""
    message = b"Hello World"
    key = bytes(0 for _ in range(128))  # b"secret key"
    crypt = cryptcls(key)
    assert crypt.decrypt(crypt.encrypt(message)) == message


def test_attempt_decrypt_unencrypted_pdf():
    """Attempting to decrypt an unencrypted PDF raises a PdfReadError."""
    path = RESOURCE_ROOT / "crazyones.pdf"
    with pytest.raises(PdfReadError) as exc:
        PdfReader(path, password="nonexistent")
    assert exc.value.args[0] == "Not an encrypted file"


@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_alg_v5_generate_values():
    """
    Algorithm V5 values are generated without raising exceptions.

    This test function checks if there is an exception during the value generation.
    It does not verify that the content is correct.
    """
    key = b"0123456789123451"
    values = AlgV5.generate_values(
        R=5,
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


@pytest.mark.parametrize(
    ("alg", "requires_aes"),
    [
        ("RC4-40", False),
        ("RC4-128", False),
        ("AES-128", True),
        ("AES-256-R5", True),
        ("AES-256", True),
        ("ABCD", False),
    ],
)
def test_pdf_encrypt(pdf_file_path, alg, requires_aes):
    user_password = secrets.token_urlsafe(10)
    owner_password = secrets.token_urlsafe(10)

    reader = PdfReader(RESOURCE_ROOT / "encryption" / "unencrypted.pdf")
    page = reader.pages[0]
    text0 = page.extract_text()

    writer = PdfWriter()
    writer.add_page(page)

    # test with invalid algorithm name
    if alg == "ABCD":
        with pytest.raises(ValueError) as exc:
            writer.encrypt(
                user_password=user_password,
                owner_password=owner_password,
                algorithm=alg,
            )
        assert exc.value.args[0] == "Algorithm 'ABCD' NOT supported"
        return

    if requires_aes and not HAS_AES:
        with pytest.raises(DependencyError) as exc:
            writer.encrypt(
                user_password=user_password,
                owner_password=owner_password,
                algorithm=alg,
            )
            with open(pdf_file_path, "wb") as output_stream:
                writer.write(output_stream)
        assert exc.value.args[0] == _DEPENDENCY_ERROR_STR
        return

    writer.encrypt(
        user_password=user_password, owner_password=owner_password, algorithm=alg
    )
    with open(pdf_file_path, "wb") as output_stream:
        writer.write(output_stream)

    reader = PdfReader(pdf_file_path)
    assert reader.is_encrypted
    assert reader.decrypt(owner_password) == PasswordType.OWNER_PASSWORD
    assert reader.decrypt(user_password) == PasswordType.USER_PASSWORD

    page = reader.pages[0]
    text1 = page.extract_text()
    assert text0 == text1


@pytest.mark.parametrize(
    "count",
    [1, 2, 3, 4, 5, 10],
)
def test_pdf_encrypt_multiple(pdf_file_path, count):
    user_password = secrets.token_urlsafe(10)
    owner_password = secrets.token_urlsafe(10)

    reader = PdfReader(RESOURCE_ROOT / "encryption" / "unencrypted.pdf")
    page = reader.pages[0]
    text0 = page.extract_text()

    writer = PdfWriter()
    writer.add_page(page)

    if count == 1:
        owner_password = None

    for _i in range(count):
        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            algorithm="RC4-128",
        )
    with open(pdf_file_path, "wb") as output_stream:
        writer.write(output_stream)

    reader = PdfReader(pdf_file_path)
    assert reader.is_encrypted
    if owner_password is None:
        # NOTICE: owner_password will set to user_password if it's None
        assert reader.decrypt(user_password) == PasswordType.OWNER_PASSWORD
    else:
        assert reader.decrypt(owner_password) == PasswordType.OWNER_PASSWORD
        assert reader.decrypt(user_password) == PasswordType.USER_PASSWORD

    page = reader.pages[0]
    text1 = page.extract_text()
    assert text0 == text1


@pytest.mark.skipif(not HAS_AES, reason="No AES implementation")
def test_aes_decrypt_corrupted_data():
    """Just for robustness"""
    aes = CryptAES(secrets.token_bytes(16))
    for num in [0, 17, 32]:
        aes.decrypt(secrets.token_bytes(num))


@pytest.mark.samples
def test_encrypt_stream_dictionary(pdf_file_path):
    user_password = secrets.token_urlsafe(10)

    reader = PdfReader(SAMPLE_ROOT / "023-cmyk-image/cmyk-image.pdf")
    page = reader.pages[0]
    original_image_obj = reader.get_object(page.images["/I"].indirect_reference)

    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    writer.encrypt(
        user_password=user_password,
        owner_password=None,
        algorithm="RC4-128",
    )
    with open(pdf_file_path, "wb") as output_stream:
        writer.write(output_stream)

    reader = PdfReader(pdf_file_path)
    assert reader.is_encrypted
    assert reader.decrypt(user_password) == PasswordType.OWNER_PASSWORD
    page = reader.pages[0]
    decrypted_image_obj = reader.get_object(page.images["/I"].indirect_reference)

    assert decrypted_image_obj["/ColorSpace"][3] == original_image_obj["/ColorSpace"][3]
