"""Font constants and classes for "layout" mode text operations"""

from dataclasses import dataclass, field
from typing import Any, Dict, Sequence, Union

from ...generic import IndirectObject


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
    """

    subtype: str
    space_width: Union[int, float]
    encoding: Union[str, Dict[int, str]]
    char_map: Dict[Any, Any]
    font_dictionary: Dict[Any, Any]
    width_map: Dict[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        # TrueType fonts have a /Widths array mapping character codes to widths
        if isinstance(self.encoding, dict) and "/Widths" in self.font_dictionary:
            first_char = self.font_dictionary.get("/FirstChar", 0)
            self.width_map = {
                self.encoding.get(idx + first_char, chr(idx + first_char)): width
                for idx, width in enumerate(self.font_dictionary["/Widths"])
            }

        # CID fonts have a /W array mapping character codes to widths stashed in /DescendantFonts
        if "/DescendantFonts" in self.font_dictionary:
            d_font: Dict[Any, Any]
            for d_font_idx, d_font in enumerate(self.font_dictionary["/DescendantFonts"]):
                while isinstance(d_font, IndirectObject):
                    d_font = d_font.get_object()  # type: ignore[assignment]
                self.font_dictionary["/DescendantFonts"][d_font_idx] = d_font
                ord_map = {
                    ord(_target): _surrogate
                    for _target, _surrogate in self.char_map.items()
                    if isinstance(_target, str)
                }
                # /W width definitions have two valid formats which can be mixed and matched:
                #   (1) A character start index followed by a list of widths, e.g.
                #       `45 [500 600 700]` applies widths 500, 600, 700 to characters 45-47.
                #   (2) A character start index, a character stop index, and a width, e.g.
                #       `45 65 500` applies width 500 to characters 45-65.
                skip_count = 0
                _w = d_font.get("/W", [])
                for idx, w_entry in enumerate(_w):
                    if skip_count:
                        skip_count -= 1
                        continue
                    if not isinstance(w_entry, (int, float)):  # pragma: no cover
                        # We should never get here due to skip_count above. Add a
                        # warning and or use reader's "strict" to force an ex???
                        continue
                    # check for format (1): `int [int int int int ...]`
                    if isinstance(_w[idx + 1], Sequence):
                        start_idx, width_list = _w[idx : idx + 2]
                        self.width_map.update(
                            {
                                ord_map[_cidx]: _width
                                for _cidx, _width in zip(
                                    range(start_idx, start_idx + len(width_list), 1), width_list
                                )
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 1
                    # check for format (2): `int int int`
                    if (
                        not isinstance(_w[idx + 1], Sequence)
                        and not isinstance(_w[idx + 2], Sequence)
                    ):
                        start_idx, stop_idx, const_width = _w[idx:idx + 3]
                        self.width_map.update(
                            {
                                ord_map[_cidx]: const_width
                                for _cidx in range(start_idx, stop_idx + 1, 1)
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 2
        if not self.width_map and "/BaseFont" in self.font_dictionary:
            for key in STANDARD_WIDTHS:
                if self.font_dictionary["/BaseFont"].startswith(f"/{key}"):
                    self.width_map = STANDARD_WIDTHS[key]
                    break

    def word_width(self, word: str) -> float:
        """Sum of character widths specified in PDF font for the supplied word"""
        return sum([self.width_map.get(char, self.space_width * 2) for char in word], 0.0)

    @staticmethod
    def to_dict(font_instance: "Font") -> Dict[str, Any]:
        """Dataclass to dict for json.dumps serialization."""
        return {k: getattr(font_instance, k) for k in font_instance.__dataclass_fields__}


# Widths for the standard 14 fonts as described on page 416 of the PDF 1.7 standard
STANDARD_WIDTHS = {
    "Helvetica": {  # 4 fonts, includes bold, oblique and boldoblique variants
        " ": 278,
        "!": 278,
        '"': 355,
        "#": 556,
        "$": 556,
        "%": 889,
        "&": 667,
        "'": 191,
        "(": 333,
        ")": 333,
        "*": 389,
        "+": 584,
        ",": 278,
        "-": 333,
        ".": 278,
        "/": 278,
        "0": 556,
        "1": 556,
        "2": 556,
        "3": 556,
        "4": 556,
        "5": 556,
        "6": 556,
        "7": 556,
        "8": 556,
        "9": 556,
        ":": 278,
        ";": 278,
        "<": 584,
        "=": 584,
        ">": 584,
        "?": 611,
        "@": 975,
        "A": 667,
        "B": 667,
        "C": 722,
        "D": 722,
        "E": 667,
        "F": 611,
        "G": 778,
        "H": 722,
        "I": 278,
        "J": 500,
        "K": 667,
        "L": 556,
        "M": 833,
        "N": 722,
        "O": 778,
        "P": 667,
        "Q": 944,
        "R": 667,
        "S": 667,
        "T": 611,
        "U": 278,
        "V": 278,
        "W": 584,
        "X": 556,
        "Y": 556,
        "Z": 500,
        "[": 556,
        "\\": 556,
        "]": 556,
        "^": 278,
        "_": 278,
        "`": 278,
        "a": 278,
        "b": 278,
        "c": 333,
        "d": 556,
        "e": 556,
        "f": 556,
        "g": 556,
        "h": 556,
        "i": 556,
        "j": 556,
        "k": 556,
        "l": 556,
        "m": 556,
        "n": 278,
        "o": 278,
        "p": 556,
        "q": 556,
        "r": 500,
        "s": 556,
        "t": 556,
        "u": 278,
        "v": 500,
        "w": 500,
        "x": 222,
        "y": 222,
        "z": 556,
        "{": 222,
        "|": 833,
        "}": 556,
        "~": 556,
    },
    "Times": {  # 4 fonts, includes bold, oblique and boldoblique variants
        " ": 250,
        "!": 333,
        '"': 408,
        "#": 500,
        "$": 500,
        "%": 833,
        "&": 778,
        "'": 180,
        "(": 333,
        ")": 333,
        "*": 500,
        "+": 564,
        ",": 250,
        "-": 333,
        ".": 250,
        "/": 564,
        "0": 500,
        "1": 500,
        "2": 500,
        "3": 500,
        "4": 500,
        "5": 500,
        "6": 500,
        "7": 500,
        "8": 500,
        "9": 500,
        ":": 278,
        ";": 278,
        "<": 564,
        "=": 564,
        ">": 564,
        "?": 444,
        "@": 921,
        "A": 722,
        "B": 667,
        "C": 667,
        "D": 722,
        "E": 611,
        "F": 556,
        "G": 722,
        "H": 722,
        "I": 333,
        "J": 389,
        "K": 722,
        "L": 611,
        "M": 889,
        "N": 722,
        "O": 722,
        "P": 556,
        "Q": 722,
        "R": 667,
        "S": 556,
        "T": 611,
        "U": 722,
        "V": 722,
        "W": 944,
        "X": 722,
        "Y": 722,
        "Z": 611,
        "[": 333,
        "\\": 278,
        "]": 333,
        "^": 469,
        "_": 500,
        "`": 333,
        "a": 444,
        "b": 500,
        "c": 444,
        "d": 500,
        "e": 444,
        "f": 333,
        "g": 500,
        "h": 500,
        "i": 278,
        "j": 278,
        "k": 500,
        "l": 278,
        "m": 722,
        "n": 500,
        "o": 500,
        "p": 500,
        "q": 500,
        "r": 333,
        "s": 389,
        "t": 278,
        "u": 500,
        "v": 444,
        "w": 722,
        "x": 500,
        "y": 444,
        "z": 389,
        "{": 348,
        "|": 220,
        "}": 348,
        "~": 469,
    },
}
STANDARD_WIDTHS["Courier"] = {  # 4 fonts, includes bold, oblique and boldoblique variants
    c: 600 for c in STANDARD_WIDTHS["Times"]  # fixed width
}
STANDARD_WIDTHS["ZapfDingbats"] = {c: 1000 for c in STANDARD_WIDTHS["Times"]}  # 1 font
STANDARD_WIDTHS["Symbol"] = {c: 500 for c in STANDARD_WIDTHS["Times"]}  # 1 font
# add aliases per table H.3 on page 1110 of the PDF 1.7 standard
STANDARD_WIDTHS["CourierNew"] = STANDARD_WIDTHS["Courier"]
STANDARD_WIDTHS["Arial"] = STANDARD_WIDTHS["Helvetica"]
STANDARD_WIDTHS["TimesNewRoman"] = STANDARD_WIDTHS["Times"]
