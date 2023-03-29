from abc import ABC

from ..constants import AnnotationFlag
from ..generic._data_structures import DictionaryObject

NO_FLAGS = AnnotationFlag(0)


class AnnotationDictionary(DictionaryObject, ABC):
    def __init__(self) -> None:
        from ..generic._base import NameObject

        # "rect" should not be added here as PolyLine can automatically set it
        self[NameObject("/Type")] = NameObject("/Annot")
