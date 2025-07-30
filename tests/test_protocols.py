"""Test the pypdf._protocols module."""
from pypdf._protocols import PdfObjectProtocol


class IPdfObjectProtocol(PdfObjectProtocol):
    pass


def test_pdfobjectprotocol():
    o = IPdfObjectProtocol()
    assert o.clone(None, False, None) is None
    assert o._reference_clone(None, None) is None
    assert o.get_object() is None
    assert o.hash_value() is None
    assert o.write_to_stream(None) is None
