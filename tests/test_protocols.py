"""Test the pypdf._protocols module."""
import inspect
import typing

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf._protocols import PdfObjectProtocol, PdfReaderProtocol, PdfWriterProtocol


class IPdfObjectProtocol(PdfObjectProtocol):
    pass


def test_pdfobjectprotocol():
    o = IPdfObjectProtocol()
    assert o.clone(None, False, None) is None
    assert o._reference_clone(None, None) is None
    assert o.get_object() is None
    assert o.hash_value() is None
    assert o.write_to_stream(None) is None


def _data_members(protocol: type) -> set:
    """Protocol members which are looked up as attributes rather than methods."""
    members = set(typing.get_type_hints(protocol))
    members.update(
        name
        for name in dir(protocol)
        if not name.startswith("__")
        and isinstance(inspect.getattr_static(protocol, name), property)
    )
    return members


@pytest.mark.parametrize(
    ("cls", "protocol"),
    [(PdfReader, PdfReaderProtocol), (PdfWriter, PdfWriterProtocol)],
)
def test_data_members_are_declared_on_the_class(cls, protocol):
    """
    Runtime protocol checks resolve members on the class, not on an instance.

    Attributes which are only assigned in ``__init__`` are therefore invisible
    to them, which is what made ``make testtype`` report hundreds of failures.
    """
    annotations = typing.get_type_hints(cls)
    missing = sorted(
        name
        for name in _data_members(protocol)
        if name not in annotations and not hasattr(cls, name)
    )
    assert not missing, (
        f"{cls.__name__} only assigns {missing} in __init__; declare them in the "
        f"class body as well so that runtime protocol checks can find them"
    )
