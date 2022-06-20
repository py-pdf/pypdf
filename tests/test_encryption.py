import os

import pytest

import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


@pytest.mark.parametrize(
    "name",
    [
        # unencrypted pdf
        "unencrypted.pdf",
        # created by `qpdf --encrypt "" "" 40 -- unencrypted.pdf r2-empty-password.pdf`
        "r2-empty-password.pdf",
        # created by `qpdf --encrypt "" "" 128 -- unencrypted.pdf r3-empty-password.pdf`
        "r3-empty-password.pdf",
        # created by `qpdf --encrypt "asdfzxcv" "" 40 -- unencrypted.pdf r2-user-password.pdf`
        "r2-user-password.pdf",
        # created by `qpdf --encrypt "asdfzxcv" "" 128 -- unencrypted.pdf r3-user-password.pdf`
        "r3-user-password.pdf",
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --force-V4 -- unencrypted.pdf r4-user-password.pdf`
        "r4-user-password.pdf",
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --use-aes=y -- unencrypted.pdf r4-aes-user-password.pdf`
        "r4-aes-user-password.pdf",
        # # created by `qpdf --encrypt "" "" 256 --force-R5 -- unencrypted.pdf r5-empty-password.pdf`
        "r5-empty-password.pdf",
        # # created by `qpdf --encrypt "asdfzxcv" "" 256 --force-R5 -- unencrypted.pdf r5-user-password.pdf`
        "r5-user-password.pdf",
        # # created by `qpdf --encrypt "" "asdfzxcv" 256 --force-R5 -- unencrypted.pdf r5-owner-password.pdf`
        "r5-owner-password.pdf",
        # created by `qpdf --encrypt "" "" 256 -- unencrypted.pdf r6-empty-password.pdf`
        "r6-empty-password.pdf",
        # created by `qpdf --encrypt "asdfzxcv" "" 256 -- unencrypted.pdf r6-user-password.pdf`
        "r6-user-password.pdf",
        # created by `qpdf --encrypt "" "asdfzxcv" 256 -- unencrypted.pdf r6-owner-password.pdf`
        "r6-owner-password.pdf",
    ],
)
def test_encryption(name):
    inputfile = os.path.join(RESOURCE_ROOT, "encryption", name)
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
    "names",
    [
        (["unencrypted.pdf", "r3-user-password.pdf", "r4-aes-user-password.pdf", "r5-user-password.pdf"]),
    ],
)
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
