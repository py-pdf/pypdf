"""Action types"""
from abc import ABC

from ..generic import DictionaryObject
from ..generic._base import (
    NameObject,
    NullObject,
    TextStringObject,
)


class Action(DictionaryObject, ABC):
    """An action dictionary defines the characteristics and behaviour of an action."""
    def __init__(self) -> None:
        super().__init__()
        self[NameObject("/Type")] = NameObject("/Action")
        # The next action or sequence of actions that shall be performed after the action
        # represented by this dictionary. The value is either a single action dictionary
        # or an array of action dictionaries that shall be performed in order.
        self[NameObject("/Next")] = NullObject()  # Optional


class JavaScript(Action):
    # Upon invocation of an ECMAScript action, a PDF processor shall execute a script
    # that is written in the ECMAScript programming language. ECMAScript extensions
    # described in ISO/DIS 21757-1 shall also be allowed.
    def __init__(self, JS: str) -> None:
        super().__init__()
        self[NameObject("/S")] = NameObject("/JavaScript")
        self[NameObject("/JS")] = TextStringObject(JS)
