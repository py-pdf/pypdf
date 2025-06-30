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

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .._cmap import build_font_width_map, compute_font_width, get_actual_str_key
from ..generic import DictionaryObject, TextStringObject
from . import get_display_str, get_text_operands


class TextExtraction:
    """
    A class to handle PDF text extraction operations.

    This class encapsulates all the state and operations needed for extracting
    text from PDF content streams, replacing the nested functions and nonlocal
    variables in the original implementation.
    """

    def __init__(self) -> None:
        self._font_width_maps: Dict[str, Tuple[Dict[Any, float], str, float]] = {}

    def _get_actual_font_widths(
        self,
        cmap: Tuple[
            Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]
        ],
        text_operands: str,
        font_size: float,
        space_width: float
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
        actual_str_size: Dict[str, float]
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
                visitor_text)
        font_widths, actual_str_size["space_width"], actual_str_size["str_height"] = (
            self._get_actual_font_widths(cmap, text_operands, font_size, space_width))
        actual_str_size["str_widths"] += font_widths

        return text, rtl_dir, actual_str_size
