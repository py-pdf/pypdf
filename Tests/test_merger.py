import os
import binascii
import sys

import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")

sys.path.append(PROJECT_ROOT)


def test_merge():
    file_merger = PyPDF2.PdfFileMerger()
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    for path in [pdf_path, pdf_path, pdf_path]:
        file_merger.append(PyPDF2.PdfFileReader(path, "rb"))

    file_merger.write("dont_commit_merged.pdf")
