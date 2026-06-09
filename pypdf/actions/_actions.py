"""Action types"""
import sys
from abc import ABC
from enum import Enum, unique
from typing import (
    TYPE_CHECKING,
    cast,
)

from .._utils import logger_warning
from ..errors import ParseError
from ..generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    TextStringObject,
    is_null_or_none,
)

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    class StrEnum(str, Enum):
        def __str__(self) -> str:
            return str(self.value)

if TYPE_CHECKING:
    from .._page import PageObject


@unique
class PageTrigger(StrEnum):
    """Trigger event entries in a page object's additional-actions dictionary."""
    OPEN = "open"
    """Trigger an action when the page is opened."""
    CLOSE = "close"
    """Trigger an action when the page is closed."""

    @property
    def name_object(self) -> NameObject:
        """Returns the corresponding NameObject for the trigger."""
        mapping = {
            PageTrigger.OPEN: NameObject("/O"),
            PageTrigger.CLOSE: NameObject("/C"),
        }
        return mapping[self]


class Action(DictionaryObject, ABC):
    """An action dictionary defines the characteristics and behaviour of an action."""
    def __init__(self) -> None:
        super().__init__()
        self[NameObject("/Type")] = NameObject("/Action")
        # The next action or sequence of actions that shall be performed after the action
        # represented by this dictionary. The value is either a single action dictionary
        # or an array of action dictionaries that shall be performed in order.
        self[NameObject("/Next")] = NullObject()  # Optional

    @classmethod
    def _create_new(cls, page: "PageObject", trigger: PageTrigger, action: "Action") -> None:
        """
        Create a new action and add it to the page.

        Args:
            page: The page to add the action to.
            trigger: An open or close trigger.
            action: The action to be done.
        """
        trigger_name = trigger.name_object

        if "/AA" not in page:
            # Additional actions key not present
            page[NameObject("/AA")] = DictionaryObject(
                {trigger_name: action}
            )
            return

        if isinstance(page["/AA"], NullObject):
            page[NameObject("/AA")] = DictionaryObject()

        if not isinstance(page["/AA"].get_object(), DictionaryObject):
            #current_type = type(page["/AA"])
            current_type = type(page["/AA"]).__name__
            if page.pdf is not None and getattr(page.pdf, "strict", False):
                raise ParseError(
                    f"The AA entry of the page should be a DictionaryObject. "
                    f"It currently is a {current_type}."
                )
            logger_warning(
                "The AA entry of the page should be a DictionaryObject. It currently is a %(type)s.",
                source=__name__,
                type=current_type
            )
            return

        additional_actions = cast(DictionaryObject, page["/AA"])

        if is_null_or_none(additional_actions.get(trigger_name)):
            additional_actions.update({trigger_name: action})
            return

        # The action dictionary's Next entry allows sequences of actions to be
        # chained together. For example, the effect of clicking a link
        # annotation with the mouse can be to play a sound, jump to a new
        # page, and start up a movie. Note that the Next entry is not
        # restricted to a single action but can contain an array of actions,
        # each of which in turn can have a Next entry of its own.
        # §12.6.2 Action dictionaries ISO 32000-2:2020
        head = current = additional_actions.get(trigger_name)
        if not isinstance(head, DictionaryObject):
            raise ParseError(
                f"The type in a page object's additional-actions key must be a DictionaryObject: "
                f"received type {type(head)}"
            )
        current = cast(DictionaryObject, current)

        visited = set()
        while True:
            next_node = current.get("/Next", None)

            if is_null_or_none(next_node):
                break

            if not isinstance(next_node, (ArrayObject, DictionaryObject)):
                raise TypeError(
                    f"An action dictionary’s Next entry must be an Action dictionary "
                    f"or an array of Action dictionaries: received type {type(next_node)}"
                )

            id_next = id(next_node)
            if id_next in visited:
                logger_warning("Detected cycle in the action tree for %(current)s", source=__name__, current=current)
                break
            visited.add(id_next)

            if isinstance(next_node, ArrayObject):
                current = next_node[-1]
            else:
                current = next_node

        if not is_null_or_none(next_node := current.get("/Next")) and id(next_node) in visited:
            logger_warning("Detected cycle in the action tree for %(current)s", source=__name__, current=current)

        current[NameObject("/Next")] = action
        additional_actions.update({trigger_name: head})

    @classmethod
    def _delete(cls, page: "PageObject", trigger: PageTrigger) -> None:
        """
        Delete an action from the page.

        Args:
            page: The page to delete the action.
            trigger: An open or close trigger.
        """
        if "/AA" not in page:
            return

        trigger_name = trigger.name_object

        additional_actions = cast(DictionaryObject, page["/AA"])

        if trigger_name not in additional_actions:
            return

        del additional_actions[trigger_name]

        if not additional_actions:
            del page["/AA"]


class JavaScript(Action):
    """
    Upon invocation of an ECMAScript action, a PDF processor shall execute a
    script that is written in the ECMAScript programming language. ECMAScript
    extensions described in ISO/DIS 21757-1 shall also be allowed.

    Args:
        js: A text string containing the ECMAScript script to be executed.
    """

    def __init__(self, js: str) -> None:
        """Initialize JavaScript with a string."""
        super().__init__()
        self[NameObject("/S")] = NameObject("/JavaScript")
        self[NameObject("/JS")] = TextStringObject(js)
