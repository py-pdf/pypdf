"""Helpers for working with PDF types."""

from typing import List, Union

try:
    from typing import Literal  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]

try:
    from typing import TypeAlias  # type: ignore[attr-defined]
except ImportError:
    # Python 3.9 and earlier
    from typing_extensions import TypeAlias  # type: ignore[misc]

from PyPDF2.generic import (
    ArrayObject,
    Bookmark,
    Destination,
    NameObject,
    NullObject,
    NumberObject,
)

BorderArrayType: TypeAlias = List[Union[NameObject, NumberObject, ArrayObject]]
BookmarkTypes: TypeAlias = Union[Bookmark, Destination]
FitType: TypeAlias = Literal[
    "/Fit", "/XYZ", "/FitH", "/FitV", "/FitR", "/FitB", "/FitBH", "/FitBV"
]
# Those go with the FitType: They specify values for the fit
ZoomArgType: TypeAlias = Union[NumberObject, NullObject]
ZoomArgsType: TypeAlias = List[ZoomArgType]


LayoutType: TypeAlias = Literal[
    "/NoLayout",
    "/SinglePage",
    "/OneColumn",
    "/TwoColumnLeft",
    "/TwoColumnRight",
    "/TwoPageLeft",
    "/TwoPageRight",
]
PagemodeType: TypeAlias = Literal[
    "/UseNone",
    "/UseOutlines",
    "/UseThumbs",
    "/FullScreen",
    "/UseOC",
    "/UseAttachments",
]
