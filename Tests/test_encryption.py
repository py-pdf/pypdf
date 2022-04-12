import os
import pytest
import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.mark.parametrize(
    "src",
    [
        # unencrypted pdf
        (os.path.join(RESOURCE_ROOT, "encryption", "enc0.pdf")),

        # created by `qpdf --encrypt "" "" 40 -- enc0.pdf enc1.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc1.pdf")),
        # created by `qpdf --encrypt "" "" 128 -- enc0.pdf enc2.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc2.pdf")),
        # created by `qpdf --encrypt "asdfzxcv" "" 40 -- enc0.pdf enc3.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc3.pdf")),
        # created by `qpdf --encrypt "asdfzxcv" "" 128 -- enc0.pdf enc4.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc4.pdf")),

        # V=4 and AES128
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --force-V4 -- enc0.pdf enc5.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc5.pdf")),
        # created by `qpdf --encrypt "asdfzxcv" "" 128 --use-aes=y -- enc0.pdf enc6.pdf`
        (os.path.join(RESOURCE_ROOT, "encryption", "enc6.pdf")),

        # # V=5 and AES256 (TODO)
        # # created by `qpdf --encrypt "" "" 256 -- enc0.pdf enc6.pdf`
        # (os.path.join(RESOURCE_ROOT, "encryption", "enc7.pdf")),
        # # created by `qpdf --encrypt "asdfzxcv" "" 256 -- enc0.pdf enc6.pdf`
        # (os.path.join(RESOURCE_ROOT, "encryption", "enc8.pdf")),
        # # created by `qpdf --encrypt "" "asdfzxcv" 256 -- enc0.pdf enc6.pdf`
        # (os.path.join(RESOURCE_ROOT, "encryption", "enc9.pdf")),
    ],
)
def test_encryption(src):
    with open(src, "rb") as inputfile:
        ipdf = PyPDF2.PdfFileReader(inputfile)
        if src.endswith("enc0.pdf"):
            assert ipdf.isEncrypted == False
        else:
            assert ipdf.isEncrypted == True
            ipdf.decrypt("asdfzxcv")
        assert ipdf.getNumPages() == 1
