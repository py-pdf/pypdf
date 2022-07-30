"""Helpers for working with PDF types."""

from typing import List, Union

try:
    # Python 3.8+: https://peps.python.org/pep-0586
    from typing import Literal  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]

try:
    # Python 3.10+: https://www.python.org/dev/peps/pep-0484/
    from typing import TypeAlias  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import TypeAlias

from .generic import (
    ArrayObject,
    Destination,
    NameObject,
    NullObject,
    NumberObject,
    OutlineItem,
)

BorderArrayType: TypeAlias = List[Union[NameObject, NumberObject, ArrayObject]]
OutlineItemType: TypeAlias = Union[OutlineItem, Destination]
# BookmarkTypes is deprecated. Use OutlineItemType instead
BookmarkTypes: TypeAlias = OutlineItemType  # TODO: remove in version 3.0.0
FitType: TypeAlias = Literal[
    "/Fit", "/XYZ", "/FitH", "/FitV", "/FitR", "/FitB", "/FitBH", "/FitBV"
]
# Those go with the FitType: They specify values for the fit
ZoomArgType: TypeAlias = Union[NumberObject, NullObject, float]
ZoomArgsType: TypeAlias = List[ZoomArgType]

# Recursive types are not yet supported by mypy:
#    OutlinesType = List[Union[Destination, "OutlinesType"]]
# See https://github.com/python/mypy/issues/731
# Hence use this for the moment:
OutlineType = List[Union[Destination, List[Union[Destination, List[Destination]]]]]
# OutlinesType is deprecated. Use OutlineType instead
OutlinesType: TypeAlias = OutlineType  # TODO: remove in version 3.0.0

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
