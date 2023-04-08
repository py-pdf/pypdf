from abc import ABC
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from .._page import PageObject
from .._utils import from_timestamp, to_timestamp
from ..constants import AnnotationFlag
from ..generic import (
    ArrayObject,
    BooleanObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    PdfObject,
    RectangleObject,
    TextStringObject,
)

try:
    from PIL import ImageColor as ImageColorLoaded
except ImportError:
    ImageColorLoaded = None  # type: ignore

DEFAULT_FLAGS = AnnotationFlag(0)
### !!!!!!! 0 is not actually no flags but the default value !!!!!


class AnnotationDictionary(DictionaryObject, ABC):
    def __init__(self, call_post_init: bool = False, **kwargs: Any) -> None:
        DictionaryObject.__init__(self)
        # "rect" should not be added here as PolyLine can automatically set it
        self._set_name("/Type", "/Annot")
        if call_post_init:
            self._post_init(**kwargs)

    def _post_init(self, **kwargs: Any) -> None:
        props = self.lst_properties()
        for k, v in kwargs.items():
            if k in props:
                setattr(self, k, v)

    def lst_properties(self) -> Dict[str, Callable]:
        """Returns a dictionnary with the setters"""
        return {
            x: v.setter
            for (x, v) in self.__class__.__dict__.items()
            if isinstance(v, property)
        }

    @property
    def subtype(self) -> str:
        """Return SubType"""
        return self.get("/SubType", "")

    @property
    def flags(self) -> AnnotationFlag:
        return self.get("/F", DEFAULT_FLAGS)

    @flags.setter
    def flags(
        self, value: Optional[AnnotationFlag]
    ) -> "AnnotationDictionary":  # to return cascading
        self._set_int("/F", value)
        return self

    @property
    def rect(self) -> str:
        """
        Gets/sets the rectangle area containing the annotation.
        Changing directly this value is not recommended for Lines, Polylines, Freetext with callouts
        """
        return self.get("/Rect", "")

    @rect.setter
    def rect(self, value: Optional[RectangleObject]) -> "AnnotationDictionary":
        self._set_str("/Rect", value)
        return self

    @property
    def page(self) -> Optional[PageObject]:
        """Gets/sets the page where the annotation is present"""
        o = self.get("/P", None)
        if o is not None:
            o = o.get_object()
        return o

    @page.setter
    def page(self, value: Optional[PageObject]) -> "AnnotationDictionary":
        self._set_indirect("/P", value.indirect_reference)
        return self

    @property
    def name(self) -> str:
        return self.get("/NM", DEFAULT_FLAGS)

    @name.setter
    def name(
        self, value: Optional[str]
    ) -> "AnnotationDictionary":  # to return cascading
        self._set_str("/NM", value)
        return self

    @property
    def color(self) -> ArrayObject:
        return self.get("/C", ArrayObject())

    @color.setter
    def color(
        self, value: Union[None, ArrayObject, Iterable[float], str]
    ) -> "AnnotationDictionary":  # to return cascading
        if isinstance(value, str):
            if ImageColorLoaded is None:
                raise ImportError("PIL required but not installed")
            value = (x / 255.0 for x in ImageColorLoaded.getrgb(value)[:3])
        if isinstance(value, (list, tuple)):
            value = ArrayObject(
                [FloatObject(n if n <= 1.0 else n / 255.0) for n in value[:3]]
            )
        self._set_str("/C", value)
        return self

    def _decode_border(self, value: List[Any]) -> Dict[str, Any]:
        d = {}
        d["hor_corner_radius"] = value[0]
        d["ver_corner_radius"] = value[1]
        d["width"] = value[2]
        if len(value) >= 4:
            d["dash"] = value[3:]
        return d

    def _undecode_border(self, d: Dict[str, Any]) -> List[Any]:
        value = []
        value[0] = d["hor_corner_radius"]
        value[1] = d["ver_corner_radius"]
        value[2] = d["width"]
        if "dash" in d:
            value[3:] = d["dash"]
        return value

    @property
    def border(self) -> Dict:
        v = self.get("/Border", [0, 0, 1])
        return self._decode_border(v)

    @border.setter
    def border(
        self, value: Optional[List[Any], Dict[str, Any]]
    ) -> "AnnotationDictionary":  # to return cascading
        if isinstance(value, dict):
            value = self._undecode_border(value)
        self._set_str("/Border", value)
        return self

    @property
    def text(self) -> str:
        return self.get("/Contents", "")

    @text.setter
    def text(
        self, value: Optional[str]
    ) -> "AnnotationDictionary":  # to return cascading
        self._set_str("/Contents", value)
        return self

    @property
    def modified_date(self) -> datetime:
        d = self.get("/M", None)
        if d is None:
            return None
        else:
            return from_timestamp(d)

    @name.setter
    def name(
        self, value: Optional[datetime, str]
    ) -> "AnnotationDictionary":  # to return cascading
        if isinstance(value, datetime):
            value = to_timestamp(value)
        elif isinstance(value, str) and value[:2] == "D:":
            self._set_str("/M", value)
        else:
            raise ValueError(f"can not process {value} as a date")
        return self

    # TODO : add /AP, /AS

    """
    internal functions used to modify properties
    """

    def _set_bool(self, key: str, value: Optional[bool]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = BooleanObject(value)

    def _set_int(self, key: str, value: Optional[int]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = NumberObject(value)

    def _set_float(self, key: str, value: Optional[float]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = FloatObject(value)

    def _set_str(self, key: str, value: Optional[str]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = TextStringObject(value)

    def _set_name(self, key: str, value: Optional[str]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = NameObject(value)

    def _set_dict(self, key: str, value: Optional[Dict]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = DictionaryObject(value)

    def _set_indirect(self, key: str, value: Optional[PdfObject]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = value.indirect_reference

    def _set_array(self, key: str, value: Optional[Iterable]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = ArrayObject(value)

    def _set_rectangle(self, key: str, value: Optional[RectangleObject]) -> None:
        if value is None:
            if key in self:
                del self[NameObject(key)]
        else:
            self[NameObject(key)] = RectangleObject(value)
