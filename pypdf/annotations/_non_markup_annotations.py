from typing import Optional, Tuple, Union

from ..generic._base import (
    BooleanObject,
    NameObject,
    NumberObject,
)
from ..generic._data_structures import DictionaryObject
from ..generic._rectangle import RectangleObject


class Popup(DictionaryObject):
    def __init__(
        self,
        *,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        flags: int = 0,
        parent: Optional[DictionaryObject] = None,
        open: bool = False,
    ):
        self.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Popup"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/Open"): BooleanObject(open),
                NameObject("/F"): NumberObject(flags),
            }
        )
        if parent:
            # This needs to be an indirect object
            try:
                self[NameObject("/Parent")] = parent.indirect_reference
            except AttributeError:
                from .._utils import logger_warning

                logger_warning(
                    "Unregistered Parent object : No Parent field set",
                    __name__,
                )
