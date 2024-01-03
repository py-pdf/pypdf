"""font constants and classes for "layout" mode text operations"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Union

from .. import mult


@dataclass
class Font:
    """A font object extracted from a pdf page

    Attributes:
        subtype (str): font subtype
        space_width (int | float): width of a space character
        encoding (str | Dict[int, str]): font encoding
        char_map (dict): character map
        font_dictionary (dict): font dictionary

    Methods:
        word_width: character width
        to_dict: dataclass to dict
    """

    subtype: str
    space_width: Union[int, float]
    encoding: Union[str, Dict[int, str]]
    char_map: Dict
    font_dictionary: Dict

    def __post_init__(self):
        self.width_map = {}
        # TrueType fonts have a /Widths array mapping character codes to widths
        if isinstance(self.encoding, dict) and "/Widths" in self.font_dictionary:
            first_char = self.font_dictionary.get("/FirstChar", 0)
            self.width_map = {
                self.encoding.get(idx + first_char, chr(idx + first_char)): width
                for idx, width in enumerate(self.font_dictionary["/Widths"])
            }

        # CID fonts have a /W array mapping character codes to widths stashed in /DescendantFonts
        if "/DescendantFonts" in self.font_dictionary:
            d_font: dict
            for d_font in self.font_dictionary["/DescendantFonts"]:
                ord_map = {
                    ord(_targ): _surg
                    for _targ, _surg in self.char_map.items()
                    if isinstance(_targ, str)
                }
                # /W can be a list of character codes and widths or a range of character codes
                # followed by a width. e.g. `45 65 500` applies width 500 to characters 45-65,
                # whereas `45 [500 600 700]` applies widths 500, 600, 700 to characters 45-47.
                skip_count = 0
                _w = d_font.get("/W", [])
                for idx, w_entry in enumerate(_w):
                    if skip_count:
                        skip_count -= 1
                        continue
                    if not isinstance(w_entry, Sequence) and isinstance(
                        _w[idx + 1], Sequence
                    ):
                        start_idx, width_list = _w[idx : idx + 2]
                        self.width_map |= {
                            ord_map[_cidx]: _width
                            for _cidx, _width in zip(
                                range(start_idx, start_idx + len(width_list), 1), width_list
                            )
                            if _cidx in ord_map
                        }
                        skip_count = 1
                    if (
                        not isinstance(w_entry, Sequence)
                        and not isinstance(_w[idx + 1], Sequence)
                        and not isinstance(_w[idx + 2], Sequence)
                    ):
                        start_idx, stop_idx, const_width = _w[idx:idx + 3]

                        self.width_map |= {
                            ord_map[_cidx]: const_width
                            for _cidx in range(start_idx, stop_idx + 1, 1)
                            if _cidx in ord_map
                        }
                        skip_count = 2
        if not self.width_map and "/BaseFont" in self.font_dictionary:
            for key in STANDARD_WIDTHS:
                if any(self.font_dictionary["/BaseFont"].startswith(f"/{key}")):
                    self.width_map = STANDARD_WIDTHS[key]
                    break

    def word_width(self, word: str) -> float:
        """sum of character widths specified in PDF font for the supplied word"""
        return sum((self.width_map.get(char, self.space_width * 2) for char in word), start=0.0)

    @staticmethod
    def to_dict(font_instance: "Font") -> dict:
        """converts this dataclass to dict for serialization and adds non-field
        attribute `width_map`
        """
        return {k: getattr(font_instance, k) for k in font_instance.__dataclass_fields__} | {
            "width_map": font_instance.width_map
        }


@dataclass
class TextStateParams:
    """Text state parameters and operator values for a single text value in a
    TJ or Tj PDF operation.

    Attributes:
        font (Font): font object
        font_size (int | float): font size
        Tc (float): character spacing. Defaults to 0.0.
        Tw (float): word spacing. Defaults to 0.0.
        Tz (float): horizontal scaling. Defaults to 100.0.
        TL (float): leading, vertical displacement between text lines. Defaults to 0.0.
        Ts (float): text rise. Defaults to 0.0.
        xform (List[float]): text transform matrix. Defaults to [1.0, 0.0, 0.0, 1.0, 0.0, 0.0].
        displaced_xform (List[float]): text transform matrix after text has been rendered.
        render_xform (List[float]): text transform matrix accounting for font size, Tz, and Ts.
        displaced_tx (float): tx from displaced_xform
        space_tx (float): tx for a space character
        font_height (float): font height

    Methods:
        font_size_matrix: matrix accounting for font size, horizontal scale, and text rise.
        displacement_matrix: matrix accounting for horizontal translation during rendering.
    """

    txt: str
    font: Font
    font_size: Union[int, float]
    Tc: float = 0.0
    Tw: float = 0.0
    Tz: float = 100.0
    TL: float = 0.0
    Ts: float = 0.0
    xform: List[float] = field(default_factory=lambda: [1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
    displaced_xform: List[float] = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], init=False
    )
    render_xform: List[float] = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 1.0, 0.0, 0.0], init=False
    )
    displaced_tx: float = field(default=0.0, init=False)
    space_tx: float = field(default=0.0, init=False)
    font_height: float = field(default=0.0, init=False)
    flip_vertical: bool = field(default=False, init=False)

    def __post_init__(self):
        self.displaced_xform = mult(self.displacement_matrix(), self.xform)
        self.render_xform = mult(self.font_size_matrix(), self.xform)
        self.displaced_tx = self.displaced_xform[4]
        self.space_tx = round(
            mult(self.displacement_matrix(" "), self.xform)[4] - self.xform[4], 3
        )
        self.font_height = self.font_size * math.sqrt(self.xform[1] ** 2 + self.xform[3] ** 2)
        self.flip_vertical = self.xform[3] < -1e-6

    def font_size_matrix(self) -> List[float]:
        """font size matrix"""
        return [self.font_size * (self.Tz / 100.0), 0.0, 0.0, self.font_size, 0.0, self.Ts]

    def displacement_matrix(self, word: Union[str, None] = None, TD_offset=0.0) -> List[float]:
        """text displacement matrix

        Args:
            TD_offset (float, optional): translation applied by TD operator. Defaults to 0.0.
        """
        word = word or self.txt
        return [1.0, 0.0, 0.0, 1.0, self.word_tx(word, TD_offset), 0.0]

    def word_tx(self, word: str, TD_offset=0.0) -> float:
        """text displacement for any word according this text state"""
        return (
            (self.font_size * ((self.font.word_width(word) - TD_offset) / 1000.0))
            + self.Tc
            + self.txt.count(" ") * self.Tw
        ) * (self.Tz / 100.0)

    @staticmethod
    def to_dict(inst: "TextStateParams") -> Dict[str, Any]:
        """dataclass to dict"""
        return {k: getattr(inst, k) for k in inst.__dataclass_fields__ if k != "font"}


# Widths for some of the standard 14 fonts
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
    "Courier": {  # 4 fonts, includes bold, oblique and boldoblique variants
        " ": 600,
        "!": 600,
        '"': 600,
        "#": 600,
        "$": 600,
        "%": 600,
        "&": 600,
        "'": 600,
        "(": 600,
        ")": 600,
        "*": 600,
        "+": 600,
        ",": 600,
        "-": 600,
        ".": 600,
        "/": 600,
        "0": 600,
        "1": 600,
        "2": 600,
        "3": 600,
        "4": 600,
        "5": 600,
        "6": 600,
        "7": 600,
        "8": 600,
        "9": 600,
        ":": 600,
        ";": 600,
        "<": 600,
        "=": 600,
        ">": 600,
        "?": 600,
        "@": 600,
        "A": 600,
        "B": 600,
        "C": 600,
        "D": 600,
        "E": 600,
        "F": 600,
        "G": 600,
        "H": 600,
        "I": 600,
        "J": 600,
        "K": 600,
        "L": 600,
        "M": 600,
        "N": 600,
        "O": 600,
        "P": 600,
        "Q": 600,
        "R": 600,
        "S": 600,
        "T": 600,
        "U": 600,
        "V": 600,
        "W": 600,
        "X": 600,
        "Y": 600,
        "Z": 600,
        "[": 600,
        "\\": 600,
        "]": 600,
        "^": 600,
        "_": 600,
        "`": 600,
        "a": 600,
        "b": 600,
        "c": 600,
        "d": 600,
        "e": 600,
        "f": 600,
        "g": 600,
        "h": 600,
        "i": 600,
        "j": 600,
        "k": 600,
        "l": 600,
        "m": 600,
        "n": 600,
        "o": 600,
        "p": 600,
        "q": 600,
        "r": 600,
        "s": 600,
        "t": 600,
        "u": 600,
        "v": 600,
        "w": 600,
        "x": 600,
        "y": 600,
        "z": 600,
        "{": 600,
        "|": 600,
        "}": 600,
        "~": 600,
    },
}
