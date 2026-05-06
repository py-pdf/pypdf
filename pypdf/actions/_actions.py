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


PageTriggerType = Literal["open", "close"]


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
    def _create_new(cls, page: "PageObject", trigger: PageTriggerType, action: "Action") -> None:
        """
        Create a new action and add it to the page.

        Args:
            page: The page to add the action to.
            trigger: The trigger event.
            action: An :py:class:`~pypdf.actions.Action` object.
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
            return

        """
        The action dictionary's Next entry allows sequences of actions to be
        chained together. For example, the effect of clicking a link
        annotation with the mouse can be to play a sound, jump to a new
        page, and start up a movie. Note that the Next entry is not
        restricted to a single action but can contain an array of actions,
        each of which in turn can have a Next entry of its own.
        §12.6.2 Action dictionaries ISO 32000-2:2020
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

    @classmethod
    def _delete(cls, page: "PageObject", trigger: PageTriggerType) -> None:
        if trigger not in {"open", "close"}:
            raise ValueError("The trigger must be 'open' or 'close'")

        trigger_name = NameObject("/O") if trigger == "open" else NameObject("/C")

        if NameObject("/AA") not in page:
            return

        additional_actions: DictionaryObject = cast(DictionaryObject, page[NameObject("/AA")])

        if trigger_name in additional_actions:
            del additional_actions[trigger_name]

            if not additional_actions:
                del page[NameObject("/AA")]


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
