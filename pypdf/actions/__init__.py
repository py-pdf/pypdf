"""
In addition to jumping to a destination in the document, an annotation or
outline item may specify an action to perform, such as launching an application,
playing a sound, changing an annotation’s appearance state. The optional A entry
in the outline item dictionary and the dictionaries of some annotation types
specifies an action performed when the annotation or outline item is activated;
a variety of other circumstances may trigger an action as well. In addition, the
optional OpenAction entry in a document’s catalog dictionary may specify an
action that shall be performed when the document is opened. Selected types of
annotations, page objects, or interactive form fields may include an entry named
AA that specifies an additional-actions dictionary that extends the set of
events that can trigger the execution of an action. The document catalog
dictionary may also contain an AA entry for trigger events affecting the
document as a whole.
ISO 32000-2:2020
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
