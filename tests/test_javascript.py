from pathlib import Path

import pytest

from PyPDF2 import PdfReader, PdfWriter

# Configure path environment
TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.fixture()
def pdf_file_writer():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    return writer


def test_add_js(pdf_file_writer):
    pdf_file_writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

    assert (
        "/Names" in pdf_file_writer._root_object
    ), "add_js should add a name catalog in the root object."
    assert (
        "/JavaScript" in pdf_file_writer._root_object["/Names"]
    ), "add_js should add a JavaScript name tree under the name catalog."
    assert (
        "/OpenAction" in pdf_file_writer._root_object
    ), "add_js should add an OpenAction to the catalog."


def test_overwrite_js(pdf_file_writer):
    def get_javascript_name():
        assert "/Names" in pdf_file_writer._root_object
        assert "/JavaScript" in pdf_file_writer._root_object["/Names"]
        assert "/Names" in pdf_file_writer._root_object["/Names"]["/JavaScript"]
        return pdf_file_writer._root_object["/Names"]["/JavaScript"]["/Names"][0]

    pdf_file_writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    first_js = get_javascript_name()

    pdf_file_writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    second_js = get_javascript_name()

    assert (
        first_js != second_js
    ), "add_js should overwrite the previous script in the catalog."
