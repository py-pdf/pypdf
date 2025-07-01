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
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from .._cmap import (
    build_char_map,
    build_font_width_map,
    compute_font_width,
    get_actual_str_key,
    unknown_char_map,
)
from .._utils import logger_warning
from ..constants import PageAttributes as PG
from ..generic import (
    ContentStream,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)
from . import (
    OrientationNotFoundError,
    crlf_space_check,
    get_display_str,
    get_text_operands,
    mult,
)


class TextExtraction:
    """
    A class to handle PDF text extraction operations.

    This class encapsulates all the state and operations needed for extracting
    text from PDF content streams, replacing the nested functions and nonlocal
    variables in the original implementation.
    """

    def __init__(
        self,
        page_obj: Any,  # PageObject reference
        obj: Any,
        pdf: Any,
        orientations: Tuple[int, ...] = (0, 90, 180, 270),
        space_width: float = 200.0,
        content_key: Optional[str] = PG.CONTENTS,
        visitor_operand_before: Optional[Callable[[Any, Any, Any, Any], None]] = None,
        visitor_operand_after: Optional[Callable[[Any, Any, Any, Any], None]] = None,
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]] = None,
    ) -> None:
        """Initialize the text extraction with parameters and state."""
        self.page_obj = page_obj  # Reference to the PageObject for font width maps
        self.obj = obj
        self.pdf = pdf
        self.orientations = orientations
        self.space_width = space_width
        self.content_key = content_key
        self.visitor_operand_before = visitor_operand_before
        self.visitor_operand_after = visitor_operand_after
        self.visitor_text = visitor_text

        # Text state
        self.text: str = ""
        self.output: str = ""
        self.rtl_dir: bool = False  # right-to-left

        # Matrix state
        self.cm_matrix: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.tm_matrix: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.cm_stack: List[Tuple[Any, ...]] = []

        # Previous matrices for tracking changes
        self.cm_prev: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.tm_prev: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

        # Memo matrices for visitor callbacks
        self.memo_cm: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.memo_tm: List[float] = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

        # Font and text scaling state
        self.char_scale: float = 1.0
        self.space_scale: float = 1.0
        self._space_width: float = 500.0  # will be set correctly at first Tf
        self.TL: float = 0.0
        self.font_size: float = 12.0  # init just in case

        # Character map state
        self.cmap: Tuple[Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]] = (
            "charmap",
            {},
            "NotInitialized",
            None,
        )  # (encoding, CMAP, font resource name, font)

        # Actual string size tracking
        self._actual_str_size: Dict[str, float] = {"str_widths": 0.0, "space_width": 0.0, "str_height": 0.0}

        # Character maps for fonts
        self.cmaps: Dict[
            str,
            Tuple[str, float, Union[str, Dict[int, str]], Dict[str, str], DictionaryObject],
        ] = {}

        # Resources dictionary
        self.resources_dict: Optional[DictionaryObject] = None

        # Operation handler mapping
        self.operation_handlers = {
            b"BT": self._handle_operation_begin_text,
            b"ET": self._handle_operation_end_text,
            b"q": self._handle_operation_save_graphics_state,
            b"Q": self._handle_operation_restore_graphics_state,
            b"cm": self._handle_operation_modify_current_matrix,
            b"Tz": self._handle_operation_horizontal_text_scaling,
            b"Tw": self._handle_operation_word_spacing,
            b"TL": self._handle_operation_text_leading,
            b"Tf": self._handle_operation_set_font,
            b"Td": self._handle_operation_move_text_position,
            b"Tm": self._handle_operation_set_text_matrix,
            b"T*": self._handle_operation_move_to_next_line,
            b"Tj": self._handle_operation_show_text,
        }

    def extract_text(self) -> str:
        """Extract text from the PDF object."""
        # Initialize resources and content
        if not self._initialize_resources():
            return ""

        content = self._get_content()
        if content is None:
            return ""

        # Process all operations in the content stream
        for operands, operator in content.operations:
            self._process_operation(operator, operands)

        # Add any remaining text to output
        self.output += self.text
        if self.text != "" and self.visitor_text is not None:
            self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)

        return self.output

    def _initialize_resources(self) -> bool:
        """Initialize resources dictionary and character maps."""
        try:
            objr = self.obj
            while NameObject(PG.RESOURCES) not in objr:
                # /Resources can be inherited so we look to parents
                objr = objr["/Parent"].get_object()
                # If no parents then no /Resources will be available,
                # so an exception will be raised
            self.resources_dict = cast("DictionaryObject", objr[PG.RESOURCES])
        except Exception:
            # No resources means no text is possible (no font)
            return False

        if "/Font" in self.resources_dict and (font := self.resources_dict["/Font"]):
            for f in cast("DictionaryObject", font):
                self.cmaps[f] = build_char_map(f, self.space_width, self.obj)

        return True

    def _get_content(self) -> Optional[ContentStream]:
        """Get the content stream from the object."""
        try:
            content = self.obj[self.content_key].get_object() if isinstance(self.content_key, str) else self.obj
            if not isinstance(content, ContentStream):
                content = ContentStream(content, self.pdf, "bytes")
            return content
        except (AttributeError, KeyError):
            return None

    def _process_operation(self, operator: bytes, operands: List[Any]) -> None:
        """Process a single PDF operation."""
        if self.visitor_operand_before is not None:
            self.visitor_operand_before(operator, operands, self.cm_matrix, self.tm_matrix)

        # Handle compound operators
        if operator == b"'":
            self._handle_operation_move_to_next_line([])
            self._handle_operation_show_text(operands)
        elif operator == b'"':
            self._handle_operation_word_spacing([operands[0]])
            self._handle_operation_character_spacing([operands[1]])
            self._handle_operation_move_to_next_line([])
            self._handle_operation_show_text(operands[2:])
        elif operator == b"TJ":
            self._handle_operation_show_text_with_positioning(operands)
        elif operator == b"TD":
            self._handle_operation_text_leading([-operands[1]])
            self._handle_operation_move_text_position(operands)
        elif operator == b"Do":
            self._handle_operation_do(operands)
        else:
            # Use the operation handler mapping
            handler = self.operation_handlers.get(operator)
            if handler:
                handler(operands)

        if self.visitor_operand_after is not None:
            self.visitor_operand_after(operator, operands, self.cm_matrix, self.tm_matrix)

    def _compute_str_widths(self, str_widths: float) -> float:
        """Compute string widths."""
        return str_widths / 1000

    def _flush_text(self) -> None:
        """Flush current text to output."""
        self.output += self.text
        if self.visitor_text is not None:
            self.visitor_text(self.text, self.memo_cm, self.memo_tm, self.cmap[3], self.font_size)
        self.text = ""
        self.memo_cm = self.cm_matrix.copy()
        self.memo_tm = self.tm_matrix.copy()

    # Operation handlers
    def _handle_operation_begin_text(self, operands: List[Any]) -> None:
        """Handle BT (Begin Text) operation."""
        self.tm_matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self._flush_text()

    def _handle_operation_end_text(self, operands: List[Any]) -> None:
        """Handle ET (End Text) operation."""
        self._flush_text()

    def _handle_operation_save_graphics_state(self, operands: List[Any]) -> None:
        """Handle q (Save graphics state) operation."""
        self.cm_stack.append(
            (
                self.cm_matrix,
                self.cmap,
                self.font_size,
                self.char_scale,
                self.space_scale,
                self._space_width,
                self.TL,
            ),
        )

    def _handle_operation_restore_graphics_state(self, operands: List[Any]) -> None:
        """Handle Q (Restore graphics state) operation."""
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

    def _handle_operation_modify_current_matrix(self, operands: List[Any]) -> None:
        """Handle cm (Modify current matrix) operation."""
        self._flush_text()
        try:
            self.cm_matrix = mult([float(operand) for operand in operands[:6]], self.cm_matrix)
        except Exception:
            self.cm_matrix = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.memo_cm = self.cm_matrix.copy()
        self.memo_tm = self.tm_matrix.copy()

    def _handle_operation_horizontal_text_scaling(self, operands: List[Any]) -> None:
        """Handle Tz (Set horizontal text scaling) operation."""
        self.char_scale = float(operands[0]) / 100 if operands else 1.0

    def _handle_operation_word_spacing(self, operands: List[Any]) -> None:
        """Handle Tw (Set word spacing) operation."""
        self.space_scale = 1.0 + float(operands[0] if operands else 0.0)

    def _handle_operation_character_spacing(self, operands: List[Any]) -> None:
        """Handle Tc (Set character spacing) operation."""
        # This is a placeholder for character spacing handling

    def _handle_operation_text_leading(self, operands: List[Any]) -> None:
        """Handle TL (Set Text Leading) operation."""
        scale_x = math.sqrt(self.tm_matrix[0] ** 2 + self.tm_matrix[2] ** 2)
        self.TL = float(operands[0] if operands else 0.0) * self.font_size * scale_x

    def _handle_operation_set_font(self, operands: List[Any]) -> None:
        """Handle Tf (Set font size) operation."""
        if self.text != "":
            self._flush_text()

        try:
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

    def _handle_operation_move_text_position(self, operands: List[Any]) -> None:
        """Handle Td (Move text position) operation."""
        # A special case is a translating only tm:
        # tm = [1, 0, 0, 1, e, f]
        # i.e. tm[4] += tx, tm[5] += ty.
        tx, ty = float(operands[0]), float(operands[1])
        self.tm_matrix[4] += tx * self.tm_matrix[0] + ty * self.tm_matrix[2]
        self.tm_matrix[5] += tx * self.tm_matrix[1] + ty * self.tm_matrix[3]
        str_widths = self._compute_str_widths(self._actual_str_size["str_widths"])
        self._actual_str_size["str_widths"] = 0.0
        self._handle_position_change(str_widths)

    def _handle_operation_set_text_matrix(self, operands: List[Any]) -> None:
        """Handle Tm (Set text matrix) operation."""
        self.tm_matrix = [float(operand) for operand in operands[:6]]
        str_widths = self._compute_str_widths(self._actual_str_size["str_widths"])
        self._actual_str_size["str_widths"] = 0.0
        self._handle_position_change(str_widths)

    def _handle_operation_move_to_next_line(self, operands: List[Any]) -> None:
        """Handle T* (Move to next line) operation."""
        self.tm_matrix[4] -= self.TL * self.tm_matrix[2]
        self.tm_matrix[5] -= self.TL * self.tm_matrix[3]
        str_widths = self._compute_str_widths(self._actual_str_size["str_widths"])
        self._actual_str_size["str_widths"] = 0.0
        self._handle_position_change(str_widths)

    def _handle_operation_show_text(self, operands: List[Any]) -> None:
        """Handle Tj (Show text) operation."""
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
        str_widths = self._compute_str_widths(self._actual_str_size["str_widths"])
        self._handle_position_change(str_widths)

    def _handle_operation_show_text_with_positioning(self, operands: List[Any]) -> None:
        """Handle TJ (Show text with positioning) operation."""
        # The space width may be smaller than the font width, so the width should be 95%.
        _confirm_space_width = self._space_width * 0.95
        if operands:
            for op in operands[0]:
                if isinstance(op, (str, bytes)):
                    self._handle_operation_show_text([op])
                if isinstance(op, (int, float, NumberObject, FloatObject)) and (
                    abs(float(op)) >= _confirm_space_width and self.text and self.text[-1] != " "
                ):
                    self._handle_operation_show_text([" "])

    def _handle_operation_do(self, operands: List[Any]) -> None:
        """Handle Do (Execute XObject) operation."""
        self._flush_text()
        try:
            if self.output and self.output[-1] != "\n":
                self.output += "\n"
                if self.visitor_text is not None:
                    self.visitor_text(
                        "\n",
                        self.memo_cm,
                        self.memo_tm,
                        self.cmap[3],
                        self.font_size,
                    )
        except IndexError:
            pass

        try:
            xobj = self.resources_dict["/XObject"]  # type: ignore
            if xobj[operands[0]]["/Subtype"] != "/Image":  # type: ignore
                # Extract text from XForm object
                xform_extractor = TextExtraction(
                    self.page_obj,
                    xobj[operands[0]],  # type: ignore
                    self.pdf,
                    self.orientations,
                    self.space_width,
                    None,  # content_key = None for XForm objects
                    self.visitor_operand_before,
                    self.visitor_operand_after,
                    self.visitor_text,
                )
                text = xform_extractor.extract_text()
                self.output += text
                if self.visitor_text is not None:
                    self.visitor_text(
                        text,
                        self.memo_cm,
                        self.memo_tm,
                        self.cmap[3],
                        self.font_size,
                    )
        except Exception as exception:
            logger_warning(
                f"Impossible to decode XFormObject {operands[0]}: {exception}",
                __name__,
            )
        finally:
            self.text = ""
            self.memo_cm = self.cm_matrix.copy()
            self.memo_tm = self.tm_matrix.copy()

    def _handle_position_change(self, str_widths: float) -> None:
        """Handle position changes for text positioning operations."""
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
                self._compute_str_widths(self._actual_str_size["space_width"]),
                self._actual_str_size["str_height"],
            )
            if self.text == "":
                self.memo_cm = self.cm_matrix.copy()
                self.memo_tm = self.tm_matrix.copy()
        except OrientationNotFoundError:
            return

    def _handle_tj(
        self,
        text: str,
        operands: List[Union[str, TextStringObject]],
        cm_matrix: List[float],
        tm_matrix: List[float],
        cmap: Tuple[Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]],
        orientations: Tuple[int, ...],
        font_size: float,
        rtl_dir: bool,
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
        space_width: float,
        actual_str_size: Dict[str, float],
    ) -> Tuple[str, bool, Dict[str, float]]:
        """Handle text showing operations."""
        text_operands, is_str_operands = get_text_operands(operands, cm_matrix, tm_matrix, cmap, orientations)
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

        font_widths, actual_str_size["space_width"], actual_str_size["str_height"] = self._get_actual_font_widths(
            cmap,
            text_operands,
            font_size,
            space_width,
        )
        actual_str_size["str_widths"] += font_widths

        return text, rtl_dir, actual_str_size

    def _get_actual_font_widths(
        self,
        cmap: Tuple[Union[str, Dict[int, str]], Dict[str, str], str, Optional[DictionaryObject]],
        text_operands: str,
        font_size: float,
        space_width: float,
    ) -> Tuple[float, float, float]:
        """Get actual font widths for text operands."""
        font_widths: float = 0
        font_name: str = cmap[2]

        # Use the page object's font width maps
        if font_name not in self.page_obj._font_width_maps:
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
            self.page_obj._font_width_maps[font_name] = (font_width_map, space_char, actual_space_width)

        font_width_map = self.page_obj._font_width_maps[font_name][0]
        space_char = self.page_obj._font_width_maps[font_name][1]
        actual_space_width = self.page_obj._font_width_maps[font_name][2]

        if text_operands:
            for char in text_operands:
                if char == space_char:
                    font_widths += actual_space_width
                    continue
                font_widths += compute_font_width(font_width_map, char)

        return (font_widths * font_size, space_width * font_size, font_size)

