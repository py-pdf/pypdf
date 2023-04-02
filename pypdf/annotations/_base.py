from abc import ABC
from typing import Any, Callable, Dict, Iterable, Optional

from ..constants import AnnotationFlag
from ..generic import (
    ArrayObject,
    BooleanObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    RectangleObject,
    TextStringObject,
)

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
        gets/sets the rectangle area containing the annotation
        Changing directly this value is not recommended for Lines, Polylines, Freetext with callouts
        """
        return self.get("/Rect", "")

    @rect.setter
    def rect(self, value: Optional[RectangleObject]) -> "AnnotationDictionary":
        self._set_str("/Rect", value)
        return self

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
