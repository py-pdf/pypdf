"""Action types"""
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Literal,
    cast,
)

from .._utils import logger_warning
from ..generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NullObject,
    TextStringObject,
    is_null_or_none,
)

if TYPE_CHECKING:
    from .._page import PageObject


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
    def _create_new(cls, page: "PageObject", trigger: Literal["open", "close"], action: "Action") -> None:
        """
        Create a new action and add it to the page.

        Args:
            page: The page to add the action to.
            trigger: "open" or "close" trigger event.
            action: An :py:class:`~pypdf.actions.Action` object;
                    JavaScript is currently the only available action type.
        """
        if trigger not in {"open", "close"}:
            raise ValueError("The trigger must be 'open' or 'close'")

        trigger_name = NameObject("/O") if trigger == "open" else NameObject("/C")

        if not isinstance(action, JavaScript):
            raise ValueError("Currently the only action type supported is JavaScript")

        if NameObject("/AA") not in page:
            # Additional actions key not present
            page[NameObject("/AA")] = DictionaryObject(
                {trigger_name: action}
            )
            return

        if not isinstance(page[NameObject("/AA")], DictionaryObject):
            page[NameObject("/AA")] = DictionaryObject()

        additional_actions: DictionaryObject = cast(DictionaryObject, page[NameObject("/AA")])

        if trigger_name not in additional_actions or is_null_or_none(additional_actions[trigger_name]):
            additional_actions.update({trigger_name: action})
            page[NameObject("/AA")] = additional_actions
            return

        """
        The action dictionary's Next entry allows sequences of actions to be
        chained together. For example, the effect of clicking a link
        annotation with the mouse can be to play a sound, jump to a new
        page, and start up a movie. Note that the Next entry is not
        restricted to a single action but can contain an array of actions,
        each of which in turn can have a Next entry of its own. The actions
        can thus form a tree instead of a simple linked list. Actions within
        each Next array are executed in order, each followed in turn by any
        actions specified in its Next entry, and so on recursively. It is
        recommended that interactive PDF processors attempt to provide
        reasonable behaviour in anomalous situations. For example,
        self-referential actions ought not be executed more than once, and
        actions that close the document or otherwise render the next action
        impossible ought to terminate the execution sequence. Applications
        need also provide some mechanism for the user to interrupt and
        manually terminate a sequence of actions.
        ISO 32000-2:2020
        """
        head = current = additional_actions.get(trigger_name)
        if not isinstance(head, DictionaryObject):
            raise TypeError(
                "The entries in a page object's additional-actions dictionary must be dictionaries"
            )
        current = cast(DictionaryObject, current)

        visited = set()
        while True:
            next_ = current[NameObject("/Next")]

            if is_null_or_none(next_):
                break

            if not isinstance(next_, (ArrayObject, DictionaryObject)):
                raise TypeError(
                    "Must be either a single action dictionary or an array of action dictionaries"
                )

            id_ = id(next_)
            if id_ in visited:
                logger_warning(f"Detected cycle in the action tree for {current}", __name__)
                break
            visited.add(id_)

            if isinstance(next_, ArrayObject):
                current = next_[-1]
            else:
                current = next_

        if not is_null_or_none(current[NameObject("/Next")]) and id(current[NameObject("/Next")]) in visited:
            logger_warning(f"Detected cycle in the action tree for {current}", __name__)

        current[NameObject("/Next")] = action
        additional_actions.update({trigger_name: head})
        page[NameObject("/AA")] = additional_actions


class JavaScript(Action):
    """
    Upon invocation of an ECMAScript action, a PDF processor shall execute a
    script that is written in the ECMAScript programming language. ECMAScript
    extensions described in ISO/DIS 21757-1 shall also be allowed.
    """
    def __init__(self, JS: str) -> None:
        super().__init__()
        self[NameObject("/S")] = NameObject("/JavaScript")
        self[NameObject("/JS")] = TextStringObject(JS)
