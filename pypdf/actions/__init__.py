"""
PDF includes a wide variety of standard action types, whose characteristics and
behaviour are defined by an action dictionary. These are defined in this
submodule.

Trigger events, which are the other component of actions, are defined with their
associated object, elsewhere in the codebase.
"""


from ._actions import Action, JavaScript

__all__ = [
    "Action",
    "JavaScript",
]
