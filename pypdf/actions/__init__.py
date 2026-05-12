"""
PDF includes a wide variety of standard action types, whose characteristics and
behaviour are defined by an action dictionary. These are defined in this
submodule.

Trigger events are the other component of actions, and are specific to their
associated object.
"""


from ._actions import Action, JavaScript

__all__ = [
    "Action",
    "JavaScript",
]
