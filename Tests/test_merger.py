import os
import binascii
import sys

import PyPDF2

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")

sys.path.append(PROJECT_ROOT)


def test_merge():
    pdf_path = os.path.join(RESOURCE_ROOT, "crazyones.pdf")
    outline = os.path.join(RESOURCE_ROOT, "pdflatex-outline.pdf")
    pdf_forms = os.path.join(RESOURCE_ROOT, "pdflatex-forms.pdf")

    file_merger = PyPDF2.PdfFileMerger()

    # string path:
    file_merger.append(pdf_path)
    file_merger.append(outline)
    file_merger.append(pdf_path, pages=PyPDF2.pagerange.PageRange(slice(0, 0)))
    file_merger.append(pdf_forms)

    # PdfFileReader object:
    file_merger.append(PyPDF2.PdfFileReader(pdf_path, "rb"))

    # Is merging encrypted files broken?
    # encrypted = os.path.join(RESOURCE_ROOT, "libreoffice-writer-password.pdf")
    # reader = PyPDF2.PdfFileReader(pdf_path, "rb")
    # reader.decrypt("openpassword")
    # file_merger.append(reader)

    # File handle
    fh = open(pdf_path, "rb")
    file_merger.append(fh)

    file_merger.addBookmark("A bookmark", 0)

    file_merger.write("dont_commit_merged.pdf")
    file_merger.close()
