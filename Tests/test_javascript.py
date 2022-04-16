import os

import pytest

from PyPDF2 import PdfFileReader, PdfFileWriter

# Configure path environment
TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "Resources")


@pytest.fixture
def pdf_file_writer():
    reader = PdfFileReader(os.path.join(RESOURCE_ROOT, "crazyones.pdf"))
    writer = PdfFileWriter()
    writer.appendPagesFromReader(reader)
    yield writer


def test_add_js(pdf_file_writer):
    pdf_file_writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    assert (
        "/Names" in pdf_file_writer._root_object
    ), "addJS should add a name catalog in the root object."
    assert (
        "/JavaScript" in pdf_file_writer._root_object["/Names"]
    ), "addJS should add a JavaScript name tree under the name catalog."
    assert (
        "/OpenAction" in pdf_file_writer._root_object
    ), "addJS should add an OpenAction to the catalog."


def test_overwrite_js(pdf_file_writer):
    def get_javascript_name():
        assert "/Names" in pdf_file_writer._root_object
        assert "/JavaScript" in pdf_file_writer._root_object["/Names"]
        assert "/Names" in pdf_file_writer._root_object["/Names"]["/JavaScript"]
        return pdf_file_writer._root_object["/Names"]["/JavaScript"]["/Names"][0]

    pdf_file_writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    first_js = get_javascript_name()

    pdf_file_writer.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    second_js = get_javascript_name()

    assert (
        first_js != second_js
    ), "addJS should overwrite the previous script in the catalog."
