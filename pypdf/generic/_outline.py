from typing import TYPE_CHECKING, Union, cast

from .._utils import StreamType, deprecation_no_replacement, logger_warning
from ._base import IndirectObject, NameObject
from ._data_structures import ArrayObject, Destination, DictionaryObject

if TYPE_CHECKING:
    from .._writer import PdfWriter
    from ._data_structures import TreeObject


class OutlineItem(Destination):
    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[str, bytes, None] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecation_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(b"<<\n")
        for key in [
            NameObject(x)
            for x in ["/Title", "/Parent", "/First", "/Last", "/Next", "/Prev"]
            if x in self
        ]:
            key.write_to_stream(stream)
            stream.write(b" ")
            value = self.raw_get(key)
            value.write_to_stream(stream)
            stream.write(b"\n")
        key = NameObject("/Dest")
        key.write_to_stream(stream)
        stream.write(b" ")
        value = self.dest_array
        value.write_to_stream(stream)
        stream.write(b"\n")
        stream.write(b">>")


def _find_outline_item_before_page(
    page_number: int,
    parent: "TreeObject",
    writer: "PdfWriter",
) -> Union["TreeObject", "IndirectObject", None]:
    """
    Find the first top-level outline child whose destination page index is >= page_number.

    Args:
        page_number: The page index to compare against.
        parent: The TreeObject representing the parent outline node.
        writer: The PdfWriter object used to resolve page references.

    Returns:
        The child's ``IndirectObject`` (suitable for the *before* parameter of
        ``TreeObject.insert_child``), or ``None`` if no such child exists.
    """
    for child in parent.children():
        page_ref = None
        if "/Dest" in child:
            dest = child["/Dest"].get_object()
            if isinstance(dest, ArrayObject) and len(dest) > 0:
                page_ref = dest[0]
        elif "/A" in child:
            action = child["/A"].get_object()
            if isinstance(action, DictionaryObject) and action.get("/S") == "/GoTo":
                d = action.get("/D")
                if d is not None:
                    d = d.get_object()
                if isinstance(d, ArrayObject) and len(d) > 0:
                    page_ref = d[0]
        if page_ref is None:
            continue
        try:
            pn = writer._get_page_number_by_indirect(page_ref)
        except Exception as exc:
            logger_warning(
                "Could not resolve page number for outline item: %(exc)s",
                source=__name__,
                exc=exc,
            )
            continue
        if pn is not None and pn >= page_number:
            ir = child.indirect_reference
            return cast(IndirectObject, ir) if ir is not None else child
    return None
