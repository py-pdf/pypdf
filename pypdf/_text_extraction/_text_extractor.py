# Copyright (c) 2006, Mathieu Fenniak
# Copyright (c) 2007, Ashish Kulkarni <kulkarni.ashish@gmail.com>
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .._cmap import build_font_width_map, compute_font_width, get_actual_str_key
from ..generic import DictionaryObject, TextStringObject
from . import OrientationNotFoundError, crlf_space_check, get_display_str, get_text_operands, mult


class TextExtraction:
    """
    A class to handle PDF text extraction operations.

    This class encapsulates all the state and operations needed for extracting
    text from PDF content streams, replacing the nested functions and nonlocal
    variables in the original implementation.
    """

    def __init__(self) -> None:
        self._font_width_maps: Dict[str, Tuple[Dict[Any, float], str, float]] = {}

        # Text extraction state variables
        self.cm_matrix: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.tm_matrix: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.cm_stack: List[
            Tuple[
                List[float],
                Tuple[Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]],
                float,
                float,
                float,
                float,
                float,
            ]
        ] = []

        # Store the last modified matrices; can be an intermediate position
        self.cm_prev: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.tm_prev: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

        # Store the position at the beginning of building the text
        self.memo_cm: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.memo_tm: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

        self.char_scale = 1.0
        self.space_scale = 1.0
        self._space_width: float = 500.0  # will be set correctly at first Tf
        self._actual_str_size: Dict[str, float] = {
            "str_widths": 0.0,
            "space_width": 0.0,
            "str_height": 0.0,
        }  # will be set to string length calculation result
        self.TL = 0.0
        self.font_size = 12.0  # init just in case of

        # Text extraction variables
        self.text: str = ""
        self.output: str = ""
        self.rtl_dir: bool = False  # right-to-left
        self.cmap: Tuple[Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]] = (
            "charmap",
            {},
            "NotInitialized",
            None,
        )  # (encoding, CMAP, font resource name, font)
        self.orientations: Tuple[int, ...] = (0, 90, 180, 270)
        self.visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]] = None
        self.cmaps: Dict[str, Tuple[str, float, Union[str, Dict[int, str]], Dict[str, str], DictionaryObject]] = {}

    def initialize_extraction(
        self,
        orientations: Tuple[int, ...] = (0, 90, 180, 270),
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]] = None,
        cmaps: Optional[
            Dict[str, Tuple[str, float, Union[str, Dict[int, str]], Dict[str, str], DictionaryObject]]
        ] = None,
    ) -> None:
        """Initialize the extractor with extraction parameters."""
        self.orientations = orientations
        self.visitor_text = visitor_text
        self.cmaps = cmaps or {}

        # Reset state
        self.text = ""
        self.output = ""
        self.rtl_dir = False

    def compute_str_widths(self, str_widths: float) -> float:
        return str_widths / 1000

    def process_operation(self, operator: bytes, operands: List[Any]) -> None:
        str_widths: float = 0.0

        # Table 5.4 page 405
        if operator == b"BT":  # Begin Text
            self.tm_matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
            # Flush text:
            self.output += self.text
            if self.visitor_text is not None:
                self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)
            self.text = ""
            self.memo_cm = self.cm_matrix.copy()
            self.memo_tm = self.tm_matrix.copy()
            return
        if operator == b"ET":  # End Text
            # Flush text:
            self.output += self.text
            if self.visitor_text is not None:
                self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)
            self.text = ""
            self.memo_cm = self.cm_matrix.copy()
            self.memo_tm = self.tm_matrix.copy()

        # Table 4.7 "Graphics state operators", page 219
        # cm_matrix calculation is reserved for later
        elif operator == b"q":  # Save graphics state
            self.cm_stack.append(
                (
                    self.cm_matrix,
                    self.cmap,
                    self.font_size,
                    self.char_scale,
                    self.space_scale,
                    self._space_width,
                    self.TL,
                )
            )
        elif operator == b"Q":  # Restore graphics state
            try:
                (
                    self.cm_matrix,
                    self.cmap,
                    self.font_size,
                    self.char_scale,
                    self.space_scale,
                    self._space_width,
                    self.TL,
                ) = self.cm_stack.pop()
            except Exception:
                self.cm_matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        elif operator == b"cm":  # Modify current matrix
            self.output += self.text
            if self.visitor_text is not None:
                self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)
            self.text = ""
            try:
                self.cm_matrix = mult([float(operand) for operand in operands[:6]], self.cm_matrix)
            except Exception:
                self.cm_matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
            self.memo_cm = self.cm_matrix.copy()
            self.memo_tm = self.tm_matrix.copy()

        # Table 5.2 page 398
        elif operator == b"Tz":  # Set horizontal text scaling
            self.char_scale = float(operands[0]) / 100 if operands else 1.0
        elif operator == b"Tw":  # Set word spacing
            self.space_scale = 1.0 + float(operands[0] if operands else 0.0)
        elif operator == b"TL":  # Set Text Leading
            scale_x = math.sqrt(self.tm_matrix[0] ** 2 + self.tm_matrix[2] ** 2)
            self.TL = float(operands[0] if operands else 0.0) * self.font_size * scale_x
        elif operator == b"Tf":  # Set font size
            if self.text != "":
                self.output += self.text  # .translate(cmap)
                if self.visitor_text is not None:
                    self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)
            self.text = ""
            self.memo_cm = self.cm_matrix.copy()
            self.memo_tm = self.tm_matrix.copy()
            try:
                # Import here to avoid circular imports
                from .._cmap import unknown_char_map  # noqa: PLC0415

                # char_map_tuple: font_type,
                #                 float(sp_width / 2),
                #                 encoding,
                #                 map_dict,
                #                 font_dict (describes the font)
                char_map_tuple = self.cmaps[operands[0]]
                # current cmap: encoding,
                #               map_dict,
                #               font resource name (internal name, not the real font name),
                #               font_dict
                self.cmap = (
                    char_map_tuple[2],
                    char_map_tuple[3],
                    operands[0],
                    char_map_tuple[4],
                )
                self._space_width = char_map_tuple[1]
            except KeyError:  # font not found
                self.cmap = (
                    unknown_char_map[2],
                    unknown_char_map[3],
                    f"???{operands[0]}",
                    None,
                )
                self._space_width = unknown_char_map[1]
            try:
                self.font_size = float(operands[1])
            except Exception:
                pass  # keep previous size
        # Table 5.5 page 406
        elif operator == b"Td":  # Move text position
            # A special case is a translating only tm:
            # tm = [1, 0, 0, 1, e, f]
            # i.e. tm[4] += tx, tm[5] += ty.
            tx, ty = float(operands[0]), float(operands[1])
            self.tm_matrix[4] += tx * self.tm_matrix[0] + ty * self.tm_matrix[2]
            self.tm_matrix[5] += tx * self.tm_matrix[1] + ty * self.tm_matrix[3]
            str_widths = self.compute_str_widths(self._actual_str_size["str_widths"])
            self._actual_str_size["str_widths"] = 0.0
        elif operator == b"Tm":  # Set text matrix
            self.tm_matrix = [float(operand) for operand in operands[:6]]
            str_widths = self.compute_str_widths(self._actual_str_size["str_widths"])
            self._actual_str_size["str_widths"] = 0.0
        elif operator == b"T*":  # Move to next line
            self.tm_matrix[4] -= self.TL * self.tm_matrix[2]
            self.tm_matrix[5] -= self.TL * self.tm_matrix[3]
            str_widths = self.compute_str_widths(self._actual_str_size["str_widths"])
            self._actual_str_size["str_widths"] = 0.0
        elif operator == b"Tj":  # Show text
            self.text, self.rtl_dir, self._actual_str_size = self._handle_tj(
                self.text,
                operands,
                self.cm_matrix,
                self.tm_matrix,
                self.cmap,
                self.orientations,
                self.font_size,
                self.rtl_dir,
                self.visitor_text,
                self._space_width,
                self._actual_str_size,
            )
        else:
            return

        if operator in {b"Td", b"Tm", b"T*", b"Tj"}:
            try:
                self.text, self.output, self.cm_prev, self.tm_prev = crlf_space_check(
                    self.text,
                    (self.cm_prev, self.tm_prev),
                    (self.cm_matrix, self.tm_matrix),
                    (self.memo_cm, self.memo_tm),
                    self.cmap,
                    self.orientations,
                    self.output,
                    self.font_size,
                    self.visitor_text,
                    str_widths,
                    self.compute_str_widths(self._actual_str_size["space_width"]),
                    self._actual_str_size["str_height"],
                )
                if self.text == "":
                    self.memo_cm = self.cm_matrix.copy()
                    self.memo_tm = self.tm_matrix.copy()
            except OrientationNotFoundError:
                return

    def _get_actual_font_widths(
        self,
        cmap: Tuple[
            Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
        ],
        text_operands: str,
        font_size: float,
        space_width: float,
    ) -> Tuple[float, float, float]:
        font_widths: float = 0
        font_name: str = cmap[2]
        if font_name not in self._font_width_maps:
            if cmap[3] is None:
                font_width_map: Dict[Any, float] = {}
                space_char = " "
                actual_space_width: float = space_width
                font_width_map["default"] = actual_space_width * 2
            else:
                space_char = get_actual_str_key(" ", cmap[0], cmap[1])
                font_width_map = build_font_width_map(cmap[3], space_width * 2)
                actual_space_width = compute_font_width(font_width_map, space_char)
            if actual_space_width == 0:
                actual_space_width = space_width
            self._font_width_maps[font_name] = (font_width_map, space_char, actual_space_width)
        font_width_map = self._font_width_maps[font_name][0]
        space_char = self._font_width_maps[font_name][1]
        actual_space_width = self._font_width_maps[font_name][2]

        if text_operands:
            for char in text_operands:
                if char == space_char:
                    font_widths += actual_space_width
                    continue
                font_widths += compute_font_width(font_width_map, char)
        return (font_widths * font_size, space_width * font_size, font_size)

    def _handle_tj(
        self,
        text: str,
        operands: List[Union[str, TextStringObject]],
        cm_matrix: List[float],
        tm_matrix: List[float],
        cmap: Tuple[
            Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
        ],
        orientations: Tuple[int, ...],
        font_size: float,
        rtl_dir: bool,
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
        space_width: float,
        actual_str_size: Dict[str, float],
    ) -> Tuple[str, bool, Dict[str, float]]:
        text_operands, is_str_operands = get_text_operands(
            operands, cm_matrix, tm_matrix, cmap, orientations)
        if is_str_operands:
            text += text_operands
        else:
            text, rtl_dir = get_display_str(
                text,
                cm_matrix,
                tm_matrix,  # text matrix
                cmap,
                text_operands,
                font_size,
                rtl_dir,
                visitor_text,
            )
        font_widths, actual_str_size["space_width"], actual_str_size["str_height"] = (
            self._get_actual_font_widths(cmap, text_operands, font_size, space_width))
        actual_str_size["str_widths"] += font_widths

        return text, rtl_dir, actual_str_size
