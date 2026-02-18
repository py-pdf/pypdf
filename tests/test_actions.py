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

    with pytest.raises(
            ValueError,
            match = "Currently the only action type supported is JavaScript"
    ):
        page.add_action("close", "xyzzy")

    # Add an open action without pre-existing action dictionary
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

    # Add a close action without pre-existing action dictionary
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

    # Add an open and close actions without pre-existing action dictionary
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

    # Add an open action with a null object as the AA entry
    page[NameObject("/AA")] = NullObject()
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

    # Add a close action with a null object as the AA entry
    page[NameObject("/AA")] = NullObject()
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

    # Add an open action with a pre-existing open action which has an invalid Next entry
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = NameObject("/xyzzy")
    with pytest.raises(
        TypeError,
        match = "'Next' must be an ArrayObject, DictionaryObject, or None",
    ):
        page.add_action("open", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add an open action with a pre-existing open action which has a Next key with a None value
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = None
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": {
                "/Type": "/Action",
                "/Next": NullObject(),
                "/S": "/JavaScript",
                "/JS": "app.alert('This is page ' + this.pageNum);"
            },
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add a close action without a pre-existing action dictionary
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

    # Add an open action when an additional-actions key exists, but is an empty dictionary
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

    # Add an open action when an additional-actions key exists and its value is an array
    page[NameObject("/AA")] = DictionaryObject()
    # The trigger events take dictionary values, not arrays, so first add an action on which to attach the array
    page.add_action("open", JavaScript("app.alert('Action to attach an array of actions');"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = ArrayObject(
        [JavaScript("app.alert('Array of actions element 1';)"), JavaScript("app.alert('Array of actions element 2';)")]
    )
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": [
                {
                    "/Type": "/Action",
                    "/Next": NullObject(),
                    "/S": "/JavaScript",
                    "/JS": "app.alert('Array of actions element 1';)"
                },
                {
                    "/Type": "/Action",
                    "/Next": NullObject(),
                    "/S": "/JavaScript",
                    "/JS": "app.alert('Array of actions element 2';)"
                }
            ],
            "/S": "/JavaScript",
            "/JS": "app.alert('Action to attach an array of actions');"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.add_action("open", JavaScript("app.alert('Test of add_action when array of actions is present');"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": [
                {
                    "/Type": "/Action",
                    "/Next": NullObject(),
                    "/S": "/JavaScript",
                    "/JS": "app.alert('Array of actions element 1';)"
                },
                {
                    "/Type": "/Action",
                    "/Next": {
                        "/Type": "/Action",
                        "/Next": NullObject(),
                        "/S": "/JavaScript",
                        "/JS": "app.alert('Test of add_action when array of actions is present');"
                    },
                    "/S": "/JavaScript",
                    "/JS": "app.alert('Array of actions element 2';)"
                }
            ],
            "/S": "/JavaScript",
            "/JS": "app.alert('Action to attach an array of actions');"
        }
    }
    assert page[NameObject("/AA")] == expected
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None


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

    with pytest.raises(
        ValueError,
        match = "An additional-actions dictionary is absent; nothing to delete",
    ):
        page.delete_action("close")

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
    # Redundantly delete again, for coverage
    page.delete_action("open")
    assert page[NameObject("/AA")] == expected
    page.delete_action("close")
    assert page.get(NameObject("/AA")) is None
