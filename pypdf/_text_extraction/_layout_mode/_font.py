"""Font constants and classes for "layout" mode text operations"""

from dataclasses import dataclass, field
from typing import Any, Union

from ..._codecs import adobe_glyphs
from ..._font import FontDescriptor
from ...generic import DictionaryObject


@dataclass
class Font:
    """
    A font object formatted for use during "layout" mode text extraction

    Attributes:
        subtype (str): font subtype
        space_width (int | float): width of a space character
        encoding (str | Dict[int, str]): font encoding
        char_map (dict): character map
        font_dictionary (dict): font dictionary
        font_descriptor: font metrics, including a mapping of characters to widths
        width_map (Dict[str, int]): mapping of characters to widths
        interpretable (bool): Default True. If False, the font glyphs cannot
            be translated to characters, e.g. Type3 fonts that do not define
            a '/ToUnicode' mapping.

    """

    subtype: str
    space_width: Union[int, float]
    encoding: Union[str, dict[int, str]]
    char_map: dict[Any, Any]
    font_dictionary: DictionaryObject
    font_descriptor: FontDescriptor = field(default_factory=FontDescriptor, init=False)
    interpretable: bool = True

    def __post_init__(self) -> None:
        # Type3 fonts that do not specify a "/ToUnicode" mapping cannot be
        # reliably converted into character codes unless all named chars
        # in /CharProcs map to a standard adobe glyph. See §9.10.2 of the
        # PDF 1.7 standard.
        if self.subtype == "/Type3" and "/ToUnicode" not in self.font_dictionary:
            self.interpretable = all(
                cname in adobe_glyphs
                for cname in self.font_dictionary.get("/CharProcs") or []
            )

        if not self.interpretable:  # save some overhead if font is not interpretable
            return

        self.font_descriptor = FontDescriptor.from_font_resource(self.font_dictionary, self.encoding, self.char_map)

    def word_width(self, word: str) -> float:
        """Sum of character widths specified in PDF font for the supplied word"""
        return sum(
            [self.font_descriptor.character_widths.get(char, self.space_width * 2) for char in word], 0.0
        )

    @staticmethod
    def to_dict(font_instance: "Font") -> dict[str, Any]:
        """Dataclass to dict for json.dumps serialization."""
        return {
            k: getattr(font_instance, k) for k in font_instance.__dataclass_fields__
        }
