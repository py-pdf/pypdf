"""
Code related to text extraction.

Some parts are still in _page.py. In doubt, they will stay there.
"""

import math
from collections.abc import Mapping
from typing import Any, Callable, Literal, Optional, Union

from .._font import Font
from .._utils import is_char_neutral, is_char_rtl
from ..generic import DictionaryObject, TextStringObject, encode_pdfdocencoding

CUSTOM_RTL_MIN: str = ""
CUSTOM_RTL_MAX: str = ""
CUSTOM_RTL_SPECIAL_CHARS: str = ""
LAYOUT_NEW_BT_GROUP_SPACE_WIDTHS: int = 5
UNICODE_LOWER_LIMIT = 0
UNICODE_UPPER_LIMIT = 0x10FFFF


class OrientationNotFoundError(Exception):
    pass


def set_custom_rtl(
    _min: Union[str, int, None] = "",
    _max: Union[str, int, None] = "",
    specials: Union[str, list[int], None] = None,
) -> tuple[str, str, str]:
    """
    Change the Right-To-Left and special characters custom parameters.

    Args:
        _min: The new minimum value for the range of custom characters that
            will be written right to left.
            If set to ``None``, the value will not be changed.
            If set to a valid integer, it will be converted to its corresponding character.
            The default value is "", which sets no additional range to be converted.
        _max: The new maximum value for the range of custom characters that will
            be written right to left.
            If set to ``None``, the value will not be changed.
            If set to a valid integer, it will be converted to its corresponding character.
            The default value is "", which sets no additional range to be converted.
        specials: The new list of special characters to be inserted in the
            current insertion order.
            If set to ``None``, the current value will not be changed.
            If set to a string, it will be converted to a list of ASCII codes.
            The default value is an empty list.

    Returns:
        A tuple containing the new values for ``CUSTOM_RTL_MIN``,
        ``CUSTOM_RTL_MAX``, and ``CUSTOM_RTL_SPECIAL_CHARS``.

    """
    global CUSTOM_RTL_MIN, CUSTOM_RTL_MAX, CUSTOM_RTL_SPECIAL_CHARS
    if isinstance(_min, int):
        CUSTOM_RTL_MIN = chr(_min) if UNICODE_LOWER_LIMIT <= _min <= UNICODE_UPPER_LIMIT else ""
    elif isinstance(_min, str):
        CUSTOM_RTL_MIN = _min
    if isinstance(_max, int):
        CUSTOM_RTL_MAX = chr(_max) if UNICODE_LOWER_LIMIT <= _max <= UNICODE_UPPER_LIMIT else ""
    elif isinstance(_max, str):
        CUSTOM_RTL_MAX = _max
    if isinstance(specials, str):
        CUSTOM_RTL_SPECIAL_CHARS = specials
    elif isinstance(specials, list):
        CUSTOM_RTL_SPECIAL_CHARS = "".join(
            chr(char) for char in specials if UNICODE_LOWER_LIMIT <= char <= UNICODE_UPPER_LIMIT
        )
    return CUSTOM_RTL_MIN, CUSTOM_RTL_MAX, CUSTOM_RTL_SPECIAL_CHARS


def mult(
    m: list[float],
    n: Union[
        list[float],
        Mapping[Union[int, Literal["is_text", "is_render"]], Union[float, bool]],
    ],
) -> list[float]:
    return [
        m[0] * n[0] + m[1] * n[2],
        m[0] * n[1] + m[1] * n[3],
        m[2] * n[0] + m[3] * n[2],
        m[2] * n[1] + m[3] * n[3],
        m[4] * n[0] + m[5] * n[2] + n[4],
        m[4] * n[1] + m[5] * n[3] + n[5],
    ]


def orient(m: list[float]) -> int:
    if m[3] > 1e-6:
        return 0
    if m[3] < -1e-6:
        return 180
    if m[1] > 0:
        return 90
    return 270


def crlf_space_check(
    text: str,
    cmtm_prev: tuple[list[float], list[float]],
    cmtm_matrix: tuple[list[float], list[float]],
    memo_cmtm: tuple[list[float], list[float]],
    font_resource: Optional[DictionaryObject],
    orientations: tuple[int, ...],
    output: str,
    font_size: float,
    visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
    str_widths: float,
    spacewidth: float,
    str_height: float,
) -> tuple[str, str, list[float], list[float]]:
    cm_prev = cmtm_prev[0]
    tm_prev = cmtm_prev[1]
    cm_matrix = cmtm_matrix[0]
    tm_matrix = cmtm_matrix[1]
    memo_cm = memo_cmtm[0]
    memo_tm = memo_cmtm[1]

    m_prev = mult(tm_prev, cm_prev)
    m = mult(tm_matrix, cm_matrix)
    orientation = orient(m)
    delta_x = m[4] - m_prev[4]
    delta_y = m[5] - m_prev[5]
    # Table 108 of the 1.7 reference ("Text positioning operators")
    # delta_x/delta_y are expressed in the coordinate system produced by
    # text matrix x current transformation matrix, so the scaling factors
    # they get compared against have to be taken from the same combined
    # matrices instead of the text matrices alone.
    scale_prev_x = math.sqrt(m_prev[0]**2 + m_prev[1]**2)
    scale_prev_y = math.sqrt(m_prev[2]**2 + m_prev[3]**2)
    scale_y = math.sqrt(m[2]**2 + m[3]**2)
    cm_prev = m

    if orientation not in orientations:
        raise OrientationNotFoundError
    if orientation in (0, 180):
        moved_height: float = delta_y
        moved_width: float = delta_x
    elif orientation in (90, 270):
        moved_height = delta_x
        moved_width = delta_y
    try:
        if abs(moved_height) > 0.8 * min(str_height * scale_prev_y, font_size * scale_y):
            if (output + text)[-1] != "\n":
                output += text + "\n"
                if visitor_text is not None:
                    visitor_text(
                        text + "\n",
                        memo_cm,
                        memo_tm,
                        font_resource,
                        font_size,
                    )
                text = ""
        elif (
            (moved_width >= (spacewidth + str_widths) * scale_prev_x)
            and (output + text)[-1] != " "
        ):
            text += " "
    except Exception:
        pass
    tm_prev = tm_matrix.copy()
    cm_prev = cm_matrix.copy()
    return text, output, cm_prev, tm_prev


def get_text_operands(
    operands: list[Union[str, TextStringObject]],
    cm_matrix: list[float],
    tm_matrix: list[float],
    font: Font,
    orientations: tuple[int, ...]
) -> tuple[str, bool]:
    t: str = ""
    is_str_operands = False
    m = mult(tm_matrix, cm_matrix)
    orientation = orient(m)
    if orientation in orientations and len(operands) > 0:
        if isinstance(operands[0], str):
            t = operands[0]
            is_str_operands = True
        else:
            t = ""
            tt: bytes = (
                encode_pdfdocencoding(operands[0])
                if isinstance(operands[0], str)
                else operands[0]
            )
            if isinstance(font.encoding, str):  # Apply named encoding
                try:
                    t = tt.decode(font.encoding, "surrogatepass")
                except Exception:
                    # The data does not match the expectation,
                    # we use "charmap" encoding as an alternative;
                    # text extraction may not be good.
                    t = tt.decode("charmap", "surrogatepass")
            else:  # Apply dict encoding
                t = "".join(
                    [font.encoding[x] if x in font.encoding else bytes((x,)).decode() for x in tt]
                )
    return (t, is_str_operands)


def get_display_str(
    text: str,
    cm_matrix: list[float],
    tm_matrix: list[float],
    font_resource: Optional[DictionaryObject],
    font: Font,
    text_operands: str,
    font_size: float,
    rtl_dir: bool,
    visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]]
) -> tuple[str, bool, float]:
    # "\u0590 - \u08FF \uFB50 - \uFDFF"
    widths: float = 0.0
    width_cache: dict[str, float] = {}
    neutral_cache: dict[str, bool] = {}
    rtl_cache: dict[str, bool] = {}
    for raw_character in text_operands:
        if raw_character == font.space_char:
            widths += font.space_width
        else:
            if raw_character not in width_cache:
                width_cache[raw_character] = font.get_text_width(raw_character)
            widths += width_cache[raw_character]
        x = font.character_map.get(raw_character, raw_character)
        # Test whether x is a sequence of bytes; ex: habibi.pdf
        if len(x) == 1:
            if x not in neutral_cache:
                neutral_cache[x] = is_char_neutral(x, CUSTOM_RTL_SPECIAL_CHARS)
            if neutral_cache[x]:
                # Cases where the current inserting order is kept
                text = x + text if rtl_dir else text + x
            else:
                if x not in rtl_cache:
                    rtl_cache[x] = is_char_rtl(x, CUSTOM_RTL_MIN, CUSTOM_RTL_MAX)
                if rtl_cache[x]:
                    # Right-to-left characters
                    if not rtl_dir:
                        rtl_dir = True
                        if visitor_text is not None:
                            visitor_text(text, cm_matrix, tm_matrix, font_resource, font_size)
                        text = ""
                    text = x + text
                else:
                    # Left-to-right characters
                    if rtl_dir:
                        rtl_dir = False
                        if visitor_text is not None:
                            visitor_text(text, cm_matrix, tm_matrix, font_resource, font_size)
                        text = ""
                    text = text + x
        else:
            # Treat a sequence of bytes as a neutral character.
            text = x + text if rtl_dir else text + x
    return text, rtl_dir, widths
