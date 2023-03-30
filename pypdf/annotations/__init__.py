"""PDF annotations"""


from ._base import NO_FLAGS
from ._markup_annotations import (
    Ellipse,
    FreeText,
    Highlight,
    Line,
    Link,
    MarkupAnnotation,
    Polygon,
    PolyLine,
    Rectangle,
    Text,
)

__all__ = [
    "Ellipse",
    "FreeText",
    "Highlight",
    "Line",
    "Link",
    "MarkupAnnotation",
    "NO_FLAGS",
    "Polygon",
    "PolyLine",
    "Rectangle",
    "Text",
]
