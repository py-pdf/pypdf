"""Test the pypdf.actions submodule."""
import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.actions import JavaScript
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NullObject, is_null_or_none

from . import RESOURCE_ROOT


@pytest.fixture
def pdf_file_writer():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    return writer


def test_page_add_action(pdf_file_writer, caplog):
    page = pdf_file_writer.pages[0]

    with pytest.raises(
        ValueError,
        match = "The trigger must be 'open' or 'close'",
    ):
        page.add_action("xyzzy", JavaScript('app.alert("This is page " + this.pageNum);'))  # type: ignore

    with pytest.raises(
        ValueError,
        match = "Currently the only action type supported is JavaScript"
    ):
        page.add_action("open", "xyzzy")  # type: ignore

    with pytest.raises(
            ValueError,
            match = "Currently the only action type supported is JavaScript"
    ):
        page.add_action("close", "xyzzy")  # type: ignore

    # Add an open action without a pre-existing action dictionary
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

    # Add an open and close action without a pre-existing action dictionary
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

    # Add an open action where a non-dictionary object is the entry in the trigger
    with pytest.raises(
            TypeError,
            match = "The entries in a page object's additional-actions dictionary must be dictionaries"
    ):
        page[NameObject("/AA")] = DictionaryObject()
        page[NameObject("/AA")][NameObject("/O")] = NameObject("/xyzzy")
        page.add_action("open", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add an open action with a pre-existing open action which has an invalid Next entry
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = NameObject("/xyzzy")
    with pytest.raises(
        TypeError,
        match = "Must be either a single action dictionary or an array of action dictionaries",
    ):
        page.add_action("open", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add an open action with a pre-existing open action which has a Next key with a NullObject value
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = NullObject()
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

    # Add two open actions without a pre-existing action dictionary
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

    # Add two close actions without a pre-existing action dictionary
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

    # Add identical open actions to create a cycle
    action = JavaScript("app.alert('Page opened');")
    page.add_action("open", action)
    page.add_action("open", action)
    page.add_action("open", action)
    assert caplog.messages[0].startswith("Detected cycle in the action tree")
    page.delete_action("open")
    assert page.get(NameObject("/AA")) is None

    # Add an open action when an additional-actions key exists and its tree contains an array
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
    page.add_action("open", JavaScript("app.alert('Test when an array of actions is present');"))
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
                        "/JS": "app.alert('Test when an array of actions is present');"
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
        page.delete_action("xyzzy")  # type: ignore

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


def test_page_add_action_chaining_with_dictionary_next(pdf_file_writer):
    """Test chaining actions when /Next is a DictionaryObject to cover line 118."""
    page = pdf_file_writer.pages[0]

    # Add first action
    page.add_action("open", JavaScript("app.alert('First action');"))

    # Add second action - this will set the first action's /Next to this action
    page.add_action("open", JavaScript("app.alert('Second action');"))

    # Add third action - this will traverse the chain and hit line 118
    # since the first action's /Next is a DictionaryObject (the second action)
    page.add_action("open", JavaScript("app.alert('Third action');"))

    # Verify the chain is correct
    aa = page[NameObject("/AA")]
    first_action = aa[NameObject("/O")]
    second_action = first_action[NameObject("/Next")]
    third_action = second_action[NameObject("/Next")]

    assert first_action[NameObject("/JS")] == "app.alert('First action');"
    assert second_action[NameObject("/JS")] == "app.alert('Second action');"
    assert third_action[NameObject("/JS")] == "app.alert('Third action');"
    assert is_null_or_none(third_action[NameObject("/Next")])
