from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Optional, Union, cast

from pypdf.generic import DictionaryObject, IndirectObject

from .errors import ParseError


@dataclass(frozen=True)
class FontDescriptor:
    """
    Represents the FontDescriptor dictionary as defined in the PDF specification.
    This contains both descriptive and metric information.

    The defaults are derived from the mean values of the 14 core fonts, rounded
    to 100.
    """

    name: str = "Unknown"
    family: str = "Unknown"
    weight: str = "Unknown"

    ascent: float = 700.0
    descent: float = -200.0
    cap_height: float = 600.0
    x_height: float = 500.0
    italic_angle: float = 0.0  # Non-italic
    flags: int = 32  # Non-serif, non-symbolic, not fixed width
    bbox: tuple[float, float, float, float] = field(default_factory=lambda: (-100.0, -200.0, 1000.0, 900.0))

    character_widths: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_font_resource(
        cls,
        pdf_font_dict: DictionaryObject,
        encoding: Optional[Union[str, dict[int, str]]] = None,
        char_map: Optional[dict[Any, Any]] = None
    ) -> "FontDescriptor":
        from pypdf._cmap import get_encoding  # noqa: PLC0415
        from pypdf._codecs.core_fontmetrics import CORE_FONT_METRICS  # noqa: PLC0415
        # Prioritize information from the PDF font dictionary
        font_name = pdf_font_dict.get("/BaseFont", "Unknown").removeprefix("/")
        if font_name in CORE_FONT_METRICS:
            return CORE_FONT_METRICS[font_name]

        if not (encoding and char_map):
            encoding, char_map = get_encoding(pdf_font_dict)

        # TrueType fonts have a /Widths array mapping character codes to widths
        if isinstance(encoding, dict) and "/Widths" in pdf_font_dict:
            first_char = pdf_font_dict.get("/FirstChar", 0)
            character_widths = {
                encoding.get(idx + first_char, chr(idx + first_char)): width
                for idx, width in enumerate(pdf_font_dict["/Widths"])
            }

        # CID fonts have a /W array mapping character codes to widths stashed in /DescendantFonts
        if "/DescendantFonts" in pdf_font_dict:
            d_font: dict[Any, Any]
            for d_font_idx, d_font in enumerate(
                pdf_font_dict["/DescendantFonts"]
            ):
                while isinstance(d_font, IndirectObject):
                    d_font = d_font.get_object()
                pdf_font_dict["/DescendantFonts"][d_font_idx] = d_font
                ord_map = {
                    ord(_target): _surrogate
                    for _target, _surrogate in char_map.items()
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
                    w_entry = w_entry.get_object()
                    if skip_count:
                        skip_count -= 1
                        continue
                    if not isinstance(w_entry, (int, float)):  # pragma: no cover
                        # We should never get here due to skip_count above. Add a
                        # warning and or use reader's "strict" to force an ex???
                        continue
                    # check for format (1): `int [int int int int ...]`
                    w_next_entry = _w[idx + 1].get_object()
                    if isinstance(w_next_entry, Sequence):
                        start_idx, width_list = w_entry, w_next_entry
                        character_widths.update(
                            {
                                ord_map[_cidx]: _width
                                for _cidx, _width in zip(
                                    range(
                                        cast(int, start_idx),
                                        cast(int, start_idx) + len(width_list),
                                        1,
                                    ),
                                    width_list,
                                )
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 1
                    # check for format (2): `int int int`
                    elif isinstance(w_next_entry, (int, float)) and isinstance(
                        _w[idx + 2].get_object(), (int, float)
                    ):
                        start_idx, stop_idx, const_width = (
                            w_entry,
                            w_next_entry,
                            _w[idx + 2].get_object(),
                        )
                        character_widths.update(
                            {
                                ord_map[_cidx]: const_width
                                for _cidx in range(
                                    cast(int, start_idx), cast(int, stop_idx + 1), 1
                                )
                                if _cidx in ord_map
                            }
                        )
                        skip_count = 2
                    else:
                        # Note: this doesn't handle the case of out of bounds (reaching the end of the width definitions
                        # while expecting more elements). This raises an IndexError which is sufficient.
                        raise ParseError(
                            f"Invalid font width definition. Next elements: {w_entry}, {w_next_entry}, {_w[idx + 2]}"
                        )  # pragma: no cover

        if not character_widths and "/BaseFont" in pdf_font_dict:
            for key in CORE_FONT_METRICS:
                if pdf_font_dict["/BaseFont"] == f"/{key}":
                    character_widths = CORE_FONT_METRICS[key].character_widths
                    break
        return cls(name=font_name, character_widths=character_widths)

    def text_width(self, text: str) -> float:
        """Sum of character widths specified in PDF font for the supplied text."""
        return sum(
            [self.character_widths.get(char, self.character_widths.get("default", 0)) for char in text], 0.0
        )
