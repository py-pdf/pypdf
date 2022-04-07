import os
import pytest
import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")

@pytest.mark.parametrize(
    "src,has_xmp",
    [
        (os.path.join(RESOURCE_ROOT, "commented-xmp.pdf"), True),
        (os.path.join(RESOURCE_ROOT, "crazyones.pdf"), False),
    ],
)
def test_read_xmp(src, has_xmp):
    with open(src, "rb") as inputfile:
        ipdf = PyPDF2.PdfFileReader(inputfile)
        xmp = ipdf.getXmpMetadata()
        assert (xmp is None) == (not has_xmp)
        if has_xmp:
            print(xmp.xmp_createDate )
