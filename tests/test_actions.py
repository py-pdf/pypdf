"""Test the pypdf.actions submodule."""
import re

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.actions import JavaScript
from pypdf.errors import ParseError
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NullObject, is_null_or_none

from . import RESOURCE_ROOT


@pytest.fixture
def pdf_file_writer():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    return writer


def test_page_add_action__error(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    with pytest.raises(
        ValueError,
        #match=re.escape("The trigger must be one of ['open', 'close']"),
        match="The trigger must be one of ['open', 'close']",
    ):
        page.add_action("xyzzy", JavaScript('app.alert("This is page " + this.pageNum);'))  # type: ignore[arg-type]


def test_page_add_action__without_existing_action_dictionary(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    # Add an open action
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/O": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page["/AA"] == expected
    page.delete_action("open")
    assert "/AA" not in page

    # Add a close action
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None

    # Add an open and close action
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
    assert page["/AA"] == expected
    page.delete_action("open")
    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_add_action__with_existing_null_object(pdf_file_writer):
    page = pdf_file_writer.pages[0]

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
    assert page["/AA"] == expected
    page.delete_action("open")
    assert page.get("/AA") is None

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
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None

    # Add an open and close action with a null object as the AA entry
    page[NameObject("/AA")] = NullObject()
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
    assert page["/AA"] == expected
    page.delete_action("open")
    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_add_action__with_existing_array_object__strict():
    writer = PdfWriter(clone_from=RESOURCE_ROOT / "crazyones.pdf", strict=True)
    page = writer.pages[0]

    # Add an open action with an array object as the AA entry
    page[NameObject("/AA")] = ArrayObject()
    with pytest.raises(
        ParseError,
        match=rf"^The PageObject AA entry should be a DictionaryObject. "
              rf"It currently is a {type(page["/AA"])}.$"
    ):
        page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    assert page.get("/AA") == ArrayObject()

    # Add a close action with an array object as the AA entry
    page[NameObject("/AA")] = ArrayObject()
    with pytest.raises(
            ParseError,
            match=rf"^The PageObject AA entry should be a DictionaryObject. "
                  rf"It currently is a {type(page["/AA"])}.$"
    ):
        page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    assert page.get("/AA") == ArrayObject()


def test_page_add_action__with_existing_array_object(pdf_file_writer, caplog):
    page = pdf_file_writer.pages[0]

    # Add an open action with an array object as the AA entry
    page[NameObject("/AA")] = ArrayObject()
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    assert (caplog.messages[0] == rf"The PageObject AA entry should be a DictionaryObject. "
                                  rf"It currently is a {type(page["/AA"])}."
            )
    assert page.get("/AA") == ArrayObject()

    # Add a close action with an array object as the AA entry
    page[NameObject("/AA")] = ArrayObject()
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    assert (caplog.messages[0] == rf"The PageObject AA entry should be a DictionaryObject. "
                                  rf"It currently is a {type(page["/AA"])}."
            )
    assert page.get("/AA") == ArrayObject()


def test_page_add_action__edge_cases(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    # Add an open action where a non-dictionary object is the entry in the trigger
    with pytest.raises(
            TypeError,
            match="The type in a page object's additional-actions key must be a DictionaryObject"
    ):
        page[NameObject("/AA")] = DictionaryObject()
        page[NameObject("/AA")][NameObject("/O")] = NameObject("/xyzzy")
        page.add_action("open", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("open")
    assert page.get("/AA") is None

    # Add a close action where a non-dictionary object is the entry in the trigger
    with pytest.raises(
            TypeError,
            match="The type in a page object's additional-actions key must be a DictionaryObject"
    ):
        page[NameObject("/AA")] = DictionaryObject()
        page[NameObject("/AA")][NameObject("/C")] = NameObject("/xyzzy")
        page.add_action("close", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("close")
    assert page.get("/AA") is None

    # Add an open action with a pre-existing open action which has an invalid Next entry
    page.add_action("open", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = NameObject("/xyzzy")
    with pytest.raises(
        TypeError,
        match="An action dictionary’s Next entry must be an Action dictionary or an array of Action dictionaries",
    ):
        page.add_action("open", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("open")
    assert page.get("/AA") is None

    # Add a close action with a pre-existing open action which has an invalid Next entry
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/C")][NameObject("/Next")] = NameObject("/xyzzy")
    with pytest.raises(
            TypeError,
            match="An action dictionary’s Next entry must be an Action dictionary or an array of Action dictionaries",
    ):
        page.add_action("close", JavaScript('app.alert("This is page " + this.pageNum);'))
    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_add_action__next_is_null(pdf_file_writer):
    page = pdf_file_writer.pages[0]

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
    assert page["/AA"] == expected
    page.delete_action("open")
    assert page.get("/AA") is None

    # Add a close action with a pre-existing open action which has a Next key with a NullObject value
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    page[NameObject("/AA")][NameObject("/C")][NameObject("/Next")] = NullObject()
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/C": {
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
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_add_action__empty_dictionary(pdf_file_writer):
    page = pdf_file_writer.pages[0]

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
    assert page["/AA"] == expected
    page.delete_action("open")
    assert page.get("/AA") is None

    # Add a close action when an additional-actions key exists, but is an empty dictionary
    page[NameObject("/AA")] = DictionaryObject()
    page.add_action("close", JavaScript("app.alert('This is page ' + this.pageNum);"))
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('This is page ' + this.pageNum);"
        }
    }
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_add_action__multiple(pdf_file_writer, caplog):
    page = pdf_file_writer.pages[0]

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
    assert page["/AA"] == expected
    page.delete_action("open")
    assert page.get("/AA") is None

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
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None

    # Add identical open actions to create a cycle
    action = JavaScript("app.alert('Page opened');")
    page.add_action("open", action)
    page.add_action("open", action)
    page.add_action("open", action)
    assert caplog.messages[0].startswith("Detected cycle in the action tree")
    page.delete_action("open")
    assert page.get("/AA") is None


def test_page_add_action__with_existing_array(pdf_file_writer):
    page = pdf_file_writer.pages[0]

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
    assert page["/AA"] == expected
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
    assert page["/AA"] == expected
    page.delete_action("open")
    assert page.get("/AA") is None


def test_page_add_action__chaining_with_dictionary(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    page.add_action("open", JavaScript("app.alert('First action');"))
    page.add_action("open", JavaScript("app.alert('Second action');"))
    page.add_action("open", JavaScript("app.alert('Third action');"))

    # Verify the chain is correct
    aa = page["/AA"]
    first_action = aa[NameObject("/O")]
    second_action = first_action[NameObject("/Next")]
    third_action = second_action[NameObject("/Next")]

    assert first_action[NameObject("/JS")] == "app.alert('First action');"
    assert second_action[NameObject("/JS")] == "app.alert('Second action');"
    assert third_action[NameObject("/JS")] == "app.alert('Third action');"
    assert is_null_or_none(third_action[NameObject("/Next")])


def test_page_add_action__chaining_with_array(pdf_file_writer):
    page = pdf_file_writer.pages[0]

    page.add_action("open", JavaScript("app.alert('First action');"))
    action1_in_array = JavaScript("app.alert('Array action 1');")
    action2_in_array = JavaScript("app.alert('Array action 2');")

    # Create intermediate dict that will be /Next of the array
    intermediate_dict = JavaScript("app.alert('Intermediate dict');")
    action2_in_array[NameObject("/Next")] = intermediate_dict

    # Set the first action's /Next to an array
    page[NameObject("/AA")][NameObject("/O")][NameObject("/Next")] = ArrayObject([action1_in_array, action2_in_array])

    page.add_action("open", JavaScript("app.alert('Final action');"))

    # Verify the structure
    aa = page["/AA"]
    first_action = aa[NameObject("/O")]
    next_array = first_action[NameObject("/Next")]

    assert isinstance(next_array, ArrayObject)
    assert len(next_array) == 2
    # The last element of array has the intermediate dict as /Next
    last_array_element = next_array[-1]
    intermediate = last_array_element[NameObject("/Next")]
    # The intermediate dict has the final action as /Next
    final_action = intermediate[NameObject("/Next")]

    assert final_action[NameObject("/JS")] == "app.alert('Final action');"


def test_page_delete_action__without_existing(pdf_file_writer):
    page = pdf_file_writer.pages[0]
    assert page.get("/AA") is None

    page.delete_action("open")
    assert page.get("/AA") is None

    page.delete_action("close")
    assert page.get("/AA") is None


def test_page_delete_action(pdf_file_writer):
    page = pdf_file_writer.pages[0]
    page[NameObject("/AA")] = DictionaryObject()

    with pytest.raises(
        ValueError,
        match=re.escape("The trigger must be one of ['open', 'close']")
    ):
        page.delete_action("xyzzy")  # type: ignore

    page.delete_action("open")
    assert page.get("/AA") is None

    page.delete_action("close")
    assert page.get("/AA") is None

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
    assert page["/AA"] == expected
    page.delete_action("open")
    expected = {
        "/C": {
            "/Type": "/Action",
            "/Next": NullObject(),
            "/S": "/JavaScript",
            "/JS": "app.alert('Page closed');"
        }
    }
    assert page["/AA"] == expected
    # Redundantly delete again, for coverage
    page.delete_action("open")
    assert page["/AA"] == expected
    page.delete_action("close")
    assert page.get("/AA") is None
