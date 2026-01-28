"""Test the pypdf.actions submodule."""

from pathlib import Path

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.actions import JavaScript
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NullObject

# Configure path environment
TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.fixture
def pdf_file_writer():
    reader = PdfReader(RESOURCE_ROOT / "issue-604.pdf")
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    return writer


def test_page_add_action(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    with pytest.raises(
        ValueError,
        match = "The trigger must be 'open' or 'close'",
    ):
        page.add_action("xyzzy", JavaScript('app.alert("This is page " + this.pageNum);'))

    with pytest.raises(
        ValueError,
        match = "Currently the only action type supported is JavaScript"
    ):
        page.add_action("open", "xyzzy")

    # Add open action without pre-existing action dictionary
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add close action without pre-existing action dictionary
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("close")
    assert page.get(NameObject("/AA")) is None

    # Add open and close actions without pre-existing action dictionary
    page.add_action("open", JavaScript("app.alert('Page opened');"))
    page.add_action("close", JavaScript("app.alert('Page closed');"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page opened');"
        },
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page closed');"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    page.delete_action("close")
    assert page.get(NameObject("/AA")) is None

    # Add open action when an additional-actions key exists, but is an empty dictionary
    page[NameObject("/AA")] = DictionaryObject()
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add two open actions without pre-existing action dictionary
    page.add_action("open", JavaScript("app.alert('Page opened 1');"))
    page.add_action("open", JavaScript("app.alert('Page opened 2');"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": {
                "/Type": "/Action",
                "/Next": NullObject(),
                "/S": "/JavaScript",
                "/JS": "app.alert('Page opened 2');"
            },
            "/S": "/JavaScript",
            "/JS": "app.alert('Page opened 1');"
        },
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add two close actions without pre-existing action dictionary
    page.add_action("close", JavaScript("app.alert('Page closed 1');"))
    page.add_action("close", JavaScript("app.alert('Page closed 2');"))
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next":
                {
                    "/Type": "/Action",
                    "/Next": NullObject(),
                    "/S": "/JavaScript",
                    "/JS": "app.alert('Page closed 2');"
                },
            "/S": "/JavaScript",
            "/JS": "app.alert('Page closed 1');"
        },
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("close")
    assert page.get(NameObject("/AA")) is None

    # Add open action when an additional-actions key exists and its value is an array
    page[NameObject("/AA")] = DictionaryObject()
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    assert NameObject("/Next") in page[NameObject("/AA")][NameObject("/O")]
    #page.add_action("open", JavaScript("app.alert('Open 1');"))
    #expected = {"/O": {"/Type": "/Action", "/Next": NullObject(), "/S": "/JavaScript", "/JS": "app.alert('Open 1');"}}
    #assert page[NameObject("/AA")] == expected
    #page.delete_action("open")
    #page.delete_action("close")  # Error!!!
    #assert page.get(NameObject("/AA")) is None


def test_page_delete_action(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    with pytest.raises(
        ValueError,
        match = "The trigger must be 'open' or 'close'",
    ):
        page.delete_action("xyzzy")

    with pytest.raises(
        ValueError,
        match = "An additional-actions dictionary is absent; nothing to delete",
    ):
        page.delete_action("open")

    page.add_action("open", JavaScript("app.alert('Page opened');"))
    page.add_action("close", JavaScript("app.alert('Page closed');"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page opened');"
        },
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page closed');"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page closed');"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("close")
    assert page.get(NameObject("/AA")) is None
