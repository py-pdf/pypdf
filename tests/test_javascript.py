from pathlib import Path

import pytest

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, NumberObject, TextStringObject

# Configure path environment
TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.fixture()
def pdf_file_writer():
    reader = PdfReader(RESOURCE_ROOT / "issue-604.pdf")
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


def test_added_js(pdf_file_writer):
    def get_javascript_name():
        assert "/Names" in pdf_file_writer._root_object
        assert "/JavaScript" in pdf_file_writer._root_object["/Names"]
        assert "/Names" in pdf_file_writer._root_object["/Names"]["/JavaScript"]
        return pdf_file_writer._root_object["/Names"]["/JavaScript"]["/Names"][
            -2
        ]  # return -2 in order to get the latest javascript

    pdf_file_writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    first_js = get_javascript_name()

    pdf_file_writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    second_js = get_javascript_name()

    assert (
        first_js != second_js
    ), "add_js should add to the previous script in the catalog."


def test_startup_dest(pdf_file_writer):
    assert pdf_file_writer.opening is None
    pdf_file_writer.opening = pdf_file_writer.pages[9]
    # checked also using Acrobrat to verify the good page is opened
    op = pdf_file_writer._root_object["/OpenAction"]
    assert op[0] == pdf_file_writer.pages[9].indirect_ref
    assert op[1] == "/Fit"
    op = pdf_file_writer.opening
    assert op.raw_get("/Page") == pdf_file_writer.pages[9].indirect_ref
    assert op["/Type"] == "/Fit"
    pdf_file_writer.opening = op
    assert pdf_file_writer.opening == op

    # irrelevant, just for coverage
    pdf_file_writer._root_object[NameObject("/OpenAction")][0] = NumberObject(0)
    pdf_file_writer.opening
    with pytest.raises(Exception) as exc:
        del pdf_file_writer._root_object[NameObject("/OpenAction")][0]
        pdf_file_writer.opening
    assert "Invalid Destination" in str(exc.value)

    pdf_file_writer.opening = "Test"
    # checked also using Acrobrat to verify opening
    op = pdf_file_writer._root_object["/OpenAction"]
    assert isinstance(op, TextStringObject)
    assert op == "Test"
    op = pdf_file_writer.opening
    assert isinstance(op, TextStringObject)
    assert op == "Test"

    # irrelevant, this is just for coverage
    pdf_file_writer._root_object[NameObject("/OpenAction")] = NumberObject(0)
    assert pdf_file_writer.opening == None
    pdf_file_writer.opening = None
    assert "/OpenAction" not in pdf_file_writer._root_object
    pdf_file_writer.opening = None
