from typing import TYPE_CHECKING, Optional, Union, cast

from .._utils import StreamType, deprecation_no_replacement, logger_warning
from ..errors import PdfReadError
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


def _resolve_outline_dest_page_ref(
    child: "DictionaryObject",
) -> Union[IndirectObject, None]:
    """
    Extract the page reference from an outline child's destination.

    Handles both ``/Dest`` array-style and ``/A`` GoTo action-style
    destinations.

    Args:
        child: An outline dictionary object.

    Returns:
        The page indirect reference, or ``None`` if it cannot be resolved.

    """
    if "/Dest" in child:
        dest = child["/Dest"].get_object()
        if isinstance(dest, ArrayObject) and len(dest) > 0:
            return cast(IndirectObject, dest[0])
    elif "/A" in child:
        action = child["/A"].get_object()
        if isinstance(action, DictionaryObject) and action.get("/S") == "/GoTo":
            dest_obj = action.get("/D")
            if dest_obj is not None:
                dest_obj = dest_obj.get_object()
            if isinstance(dest_obj, ArrayObject) and len(dest_obj) > 0:
                return cast(IndirectObject, dest_obj[0])
    return None


def _find_outline_item_before_page(
    page_number: int,
    parent: "TreeObject",
    writer: "PdfWriter",
) -> Union["TreeObject", "IndirectObject", None]:
    """
    Find the top-level outline child with the smallest destination page
    index that is still >= *page_number*.

    Scanning all direct children and picking the minimum-page candidate
    >= *page_number* makes this robust even when outline items are not
    stored in page-number order.

    Only direct children of *parent* are examined (not nested
    sub-outlines), because ``TreeObject.insert_child`` operates on the
    sibling linked list of *parent*'s direct children.  Nested outline
    items inherit their parent's position in the tree and do not affect
    the insertion point.

    Args:
        page_number: The page index to compare against.
        parent: The TreeObject representing the parent outline node.
        writer: The PdfWriter object used to resolve page references.

    Returns:
        The child's ``IndirectObject`` (suitable for the *before*
        parameter of ``TreeObject.insert_child``), or ``None`` if no
        such child exists.

    """
    page_cache = writer._build_page_id_cache()
    best_child = None
    best_page_number: Optional[int] = None
    for child in parent.children():
        page_ref = _resolve_outline_dest_page_ref(child)
        if page_ref is None:
            continue
        try:
            child_page_number = writer._get_page_number_by_indirect(
                page_ref, _page_cache=page_cache
            )
        except (PdfReadError, ValueError):
            logger_warning(
                "Could not resolve page number for outline item",
                source=__name__,
            )
            continue
        if (
            child_page_number is not None
            and child_page_number >= page_number
            and (best_page_number is None or child_page_number < best_page_number)
        ):
            best_child = child
            best_page_number = child_page_number
    if best_child is not None:
        indirect_ref = best_child.indirect_reference
        return cast(IndirectObject, indirect_ref) if indirect_ref is not None else best_child
    return None
