import re
from typing import Any, Optional, Union, cast

from .._cmap import _default_fonts_space_width, build_char_map_from_dict
from .._codecs.core_fontmetrics import CORE_FONT_METRICS
from .._font import FontDescriptor
from .._utils import logger_warning
from ..constants import AnnotationDictionaryAttributes, FieldDictionaryAttributes
from ..generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    RectangleObject,
)
from ..generic._base import ByteStringObject, TextStringObject, is_null_or_none

DEFAULT_FONT_SIZE_IN_MULTILINE = 12


class TextStreamAppearance(DecodedStreamObject):
    """
    A class representing the appearance stream for a text-based form field.

    This class generates the content stream (the `ap_stream_data`) that dictates
    how text is rendered within a form field's bounding box. It handles properties
    like font, font size, color, multiline text, and text selection highlighting.
    """
    def _scale_text(
        self,
        font_descriptor: FontDescriptor,
        font_size: float,
        field_width: float,
        field_height: float,
        txt: str,
        multiline: bool,
        min_font_size: float = 4.0,       # Minimum font size to attempt
        font_size_step: float = 0.2       # How much to decrease font size by each step
    ) -> tuple[list[tuple[float, str]], float]:
        """
        Takes a piece of text and scales it to field_width or field_height, given font_name
        and font_size. For multiline fields, adds newlines to wrap the text.

        Args:
            font_descriptor: A FontDescriptor for the font to be used.
            font_size: The font size in points.
            field_width: The width of the field in which to fit the text.
            field_height: The height of the field in which to fit the text.
            txt: The text to fit with the field.
            multiline: Whether to scale and wrap the text, or only to scale.
            min_font_size: The minimum font size at which to scale the text.
            font_size_step: The amount by which to decrement font size per step while scaling.

        Returns:
            The text in in the form of list of tuples, each tuple containing the length of a line
            and it contents, and the font_size for these lines and lengths.
        """
        # Single line:
        if not multiline:
            test_width = font_descriptor.text_width(txt) * font_size / 1000
            if test_width > field_width or font_size > field_height:
                new_font_size = font_size - font_size_step
                if new_font_size >= min_font_size:
                    # Text overflows height; Retry with smaller font size.
                    return self._scale_text(
                        font_descriptor,
                        round(new_font_size, 1),
                        field_width,
                        field_height,
                        txt,
                        multiline,
                        min_font_size,
                        font_size_step
                    )
                # Font size lower than set minimum font size, give up.
                return [(test_width, txt)], font_size
            return [(test_width, txt)], font_size
        # Multiline:
        orig_txt = txt
        paragraphs = re.sub(r"\n", "\r", txt).split("\r")
        wrapped_lines = []
        current_line_words: list[str] = []
        current_line_width: float = 0
        space_width = font_descriptor.text_width(" ") * font_size / 1000
        for paragraph in paragraphs:
            if not paragraph.strip():
                wrapped_lines.append((0.0, ""))
                continue
            words = paragraph.split(" ")
            for i, word in enumerate(words):
                word_width = font_descriptor.text_width(word) * font_size / 1000
                test_width = current_line_width + word_width + (space_width if i else 0)
                if test_width > field_width and current_line_words:
                    wrapped_lines.append((current_line_width, " ".join(current_line_words)))
                    current_line_words = [word]
                    current_line_width = word_width
                elif not current_line_words and word_width > field_width:
                    wrapped_lines.append((word_width, word))
                    current_line_words = []
                    current_line_width = 0
                else:
                    if current_line_words:
                        current_line_width += space_width
                    current_line_words.append(word)
                    current_line_width += word_width
            if current_line_words:
                wrapped_lines.append((current_line_width, " ".join(current_line_words)))
                current_line_words = []
                current_line_width = 0
        # Estimate total height.
        # Assumed line spacing of 1.4
        estimated_total_height = font_size + (len(wrapped_lines) - 1) * 1.4 * font_size
        if estimated_total_height > field_height:
            new_font_size = font_size - font_size_step
            if new_font_size >= min_font_size:
                # Text overflows height; Retry with smaller font size.
                return self._scale_text(
                    font_descriptor,
                    round(new_font_size, 1),
                    field_width,
                    field_height,
                    orig_txt,
                    multiline,
                    min_font_size,
                    font_size_step
                )
            # Font size lower than set minimum font size, give up.
            return (wrapped_lines, font_size)
        return (wrapped_lines, font_size)

    def _appearance_stream_data(
        self,
        text: str = "",
        selection: Optional[list[str]] = None,
        rect: Union[RectangleObject, tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0),
        font_descriptor: FontDescriptor = CORE_FONT_METRICS["Helvetica"],
        font_glyph_byte_map: Optional[dict[str, bytes]] = None,
        font_name: str = "/Helv",
        font_size: float = 0.0,
        font_color: str = "0 g",
        multiline: bool = False
    ) -> bytes:
        """
        Generates the raw bytes of the PDF appearance stream for a text field.

        This private method assembles the PDF content stream operators to draw
        the provided text within the specified rectangle. It handles text positioning,
        font application, color, and special formatting like selected text.

        Args:
            text: The text to be rendered in the form field.
            selection: An optional list of strings that should be highlighted as selected.
            font_glyph_byte_map: An optional dictionary mapping characters to their
                byte representation for glyph encoding.
            rect: The bounding box of the form field. Can be a `RectangleObject`
                or a tuple of four floats (x1, y1, x2, y2).
            font_name: The name of the font resource to use (e.g., "/Helv").
            font_size: The font size. If 0, it is automatically calculated
                based on whether the field is multiline or not.
            font_color: The color to apply to the font, represented as a PDF
                graphics state string (e.g., "0 g" for black).
            multiline: A boolean indicating if the text field is multiline.

        Returns:
            A byte string containing the PDF content stream data.

        """
        font_glyph_byte_map = font_glyph_byte_map or {}
        if isinstance(rect, tuple):
            rect = RectangleObject(rect)

        # If font_size is 0, apply the logic for multiline or large-as-possible font
        if font_size == 0:
            if selection:          # Don't wrap text when dealing with a /Ch field, in order to prevent problems
                multiline = False  # with matching "selection" with "line" later on.
            if multiline:
                font_size = DEFAULT_FONT_SIZE_IN_MULTILINE
            else:
                font_size = rect.height - 2
            lines, font_size = self._scale_text(
                font_descriptor,
                font_size,
                rect.width - 3,    # One point margin left and right, and an additional point because the first offset
                                   # takes one extra point (see below, under "line_number == 0:")
                rect.height - 3,   # One point margin for top and bottom, one point extra for the first line
                                   # (see y_offset)
                text,
                multiline,
            )
        else:
            lines = [(
                font_descriptor.text_width(line) * font_size / 1000,
                line
            ) for line in text.replace("\n", "\r").split("\r")]


        # Set the vertical offset
        y_offset = rect.height - 1 - font_size
        default_appearance = f"{font_name} {font_size} Tf {font_color}"
        ap_stream = f"q\n/Tx BMC \nq\n1 1 {rect.width - 1} {rect.height - 1} re\nW\nBT\n{default_appearance}\n".encode()
        for line_number, (line_width, line) in enumerate(lines):
            # Escape parentheses (PDF 1.7 reference, table 3.2, Literal Strings)
            line = line.replace("\\", "\\\\").replace("(", r"\(").replace(")", r"\)")
            if selection and line in selection:
                # may be improved but cannot find how to get fill working => replaced with lined box
                ap_stream += (
                    f"1 {y_offset - (line_number * font_size * 1.4) - 1} {rect.width - 2} {font_size + 2} re\n"
                    f"0.5 0.5 0.5 rg s\n{default_appearance}\n"
                ).encode()
            if line_number == 0:
                ap_stream += f"2 {y_offset} Td\n".encode()
            else:
                # Td is a relative translation
                ap_stream += f"0 {-font_size * 1.4} Td\n".encode()
            encoded_line: list[bytes] = [
                font_glyph_byte_map.get(c, c.encode("utf-16-be")) for c in line
            ]
            if any(len(c) >= 2 for c in encoded_line):
                ap_stream += b"<" + (b"".join(encoded_line)).hex().encode() + b"> Tj\n"
            else:
                ap_stream += b"(" + b"".join(encoded_line) + b") Tj\n"
        ap_stream += b"ET\nQ\nEMC\nQ\n"
        return ap_stream

    def __init__(
        self,
        text: str = "",
        selection: Optional[list[str]] = None,
        rect: Union[RectangleObject, tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0),
        font_resource: Optional[DictionaryObject] = None,
        font_name: str = "/Helv",
        font_size: float = 0.0,
        font_color: str = "0 g",
        multiline: bool = False
    ) -> None:
        """
        Initializes a TextStreamAppearance object.

        This constructor creates a new PDF stream object configured as an XObject
        of subtype Form. It uses the `_appearance_stream_data` method to generate
        the content for the stream.

        Args:
            text: The text to be rendered in the form field.
            selection: An optional list of strings that should be highlighted as selected.
            rect: The bounding box of the form field. Can be a `RectangleObject`
                or a tuple of four floats (x1, y1, x2, y2).
            font_resource: A font resource dictionary for a specific font
            font_name: The name of the font resource, e.g., "/Helv".
            font_size: The font size. If 0, it's auto-calculated.
            font_color: The font color string.
            multiline: A boolean indicating if the text field is multiline.

        """
        # If a font resource was added, get the font character map
        if font_resource:
            font_resource = cast(DictionaryObject, font_resource.get_object())
            font_descriptor = FontDescriptor.from_font_resource(font_resource)
        else:
            logger_warning(f"Font dictionary for {font_name} not found; defaulting to Helvetica.", __name__)
            font_name = "/Helv"
            font_resource = DictionaryObject()
            font_resource[NameObject("/Type")] = NameObject("/Font")
            font_resource[NameObject("/Subtype")] = NameObject("/Type1")
            font_resource[NameObject("/Name")] = NameObject("/Helv")
            font_resource[NameObject("/BaseFont")] = NameObject("/Helvetica")
            font_resource[NameObject("/Encoding")] = NameObject("/MacRomanEncoding")
            font_descriptor = CORE_FONT_METRICS["Helvetica"]

        # Get the font glyph data
        _font_subtype, _, font_encoding, font_map = build_char_map_from_dict(
            200, font_resource
        )
        try:  # remove width stored in -1 key
            del font_map[-1]
        except KeyError:
            pass
        font_glyph_byte_map: dict[str, bytes]
        if isinstance(font_encoding, str):
            font_glyph_byte_map = {
                v: k.encode(font_encoding) for k, v in font_map.items()
            }
        else:
            font_glyph_byte_map = {v: bytes((k,)) for k, v in font_encoding.items()}
            font_encoding_rev = {v: bytes((k,)) for k, v in font_encoding.items()}
            for key, value in font_map.items():
                font_glyph_byte_map[value] = font_encoding_rev.get(key, key)

        ap_stream_data = self._appearance_stream_data(
            text, selection, rect, font_descriptor, font_glyph_byte_map, font_name, font_size, font_color, multiline
        )
        super().__init__()
        self[NameObject("/Type")] = NameObject("/XObject")
        self[NameObject("/Subtype")] = NameObject("/Form")
        self[NameObject("/BBox")] = RectangleObject(rect)
        self.set_data(ByteStringObject(ap_stream_data))
        self[NameObject("/Length")] = NumberObject(len(ap_stream_data))
        # Update Resources with font information
        self[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {
                        NameObject(font_name): getattr(
                            font_resource, "indirect_reference", font_resource
                        )
                    }
                )
            }
        )

    @classmethod
    def from_text_annotation(
        cls,
        acro_form: DictionaryObject,  # _root_object[CatalogDictionary.ACRO_FORM])
        field: DictionaryObject,
        annotation: DictionaryObject,
        user_font_name: str = "",
        user_font_size: float = -1,
    ) -> "TextStreamAppearance":
        """
        Creates a TextStreamAppearance object from a text field annotation.

        This class method is a factory for creating a `TextStreamAppearance`
        instance by extracting all necessary information (bounding box, font,
        text content, etc.) from the PDF field and annotation dictionaries.
        It respects inheritance for properties like default appearance (`/DA`).

        Args:
            acro_form: The root AcroForm dictionary from the PDF catalog.
            field: The field dictionary object.
            annotation: The widget annotation dictionary object associated with the field.
            user_font_name: An optional user-provided font name to override the
                default. Defaults to an empty string.
            user_font_size: An optional user-provided font size to override the
                default. A value of -1 indicates no override.

        Returns:
            A new `TextStreamAppearance` instance configured for the given field.

        """
        # Calculate rectangle dimensions
        _rect = cast(RectangleObject, annotation[AnnotationDictionaryAttributes.Rect])
        rect = RectangleObject((0, 0, abs(_rect[2] - _rect[0]), abs(_rect[3] - _rect[1])))

        # Get default appearance dictionary from annotation
        default_appearance = annotation.get_inherited(
            AnnotationDictionaryAttributes.DA,
            acro_form.get(AnnotationDictionaryAttributes.DA, None),
        )
        if not default_appearance:
            # Create a default appearance if none was found in the annotation
            default_appearance = TextStringObject("/Helv 0 Tf 0 g")
        else:
            default_appearance = default_appearance.get_object()

        # Derive font name, size and color from the default appearance. Also set
        # user-provided font name and font size in the default appearance, if given.
        # For a font name, this presumes that we can find an associated font resource
        # dictionary. Uses the variable font_properties as an intermediate.
        # As per the PDF spec:
        # "At a minimum, the string [that is, default_appearance] shall include a Tf (text
        # font) operator along with its two operands, font and size" (p. 519 of Version 2.0).
        font_properties = [prop for prop in re.split(r"\s", default_appearance) if prop]
        font_name = font_properties.pop(font_properties.index("Tf") - 2)
        font_size = float(font_properties.pop(font_properties.index("Tf") - 1))
        font_properties.remove("Tf")
        font_color = " ".join(font_properties)
        # Determine the font name to use, prioritizing the user's input
        if user_font_name:
            font_name = user_font_name
        # Determine the font size to use, prioritizing the user's input
        if user_font_size > 0:
            font_size = user_font_size

        # Try to find a resource dictionary for the font
        document_resources: Any = cast(
            DictionaryObject,
            cast(
                DictionaryObject,
                annotation.get_inherited(
                    "/DR",
                    acro_form.get("/DR", DictionaryObject()),
                ),
            ).get_object(),
        )
        document_font_resources = document_resources.get("/Font", DictionaryObject()).get_object()
        # _default_fonts_space_width keys is the list of Standard fonts
        if font_name not in document_font_resources and font_name not in _default_fonts_space_width:
            # ...or AcroForm dictionary
            document_resources = cast(
                dict[Any, Any],
                acro_form.get("/DR", {}),
            )
            document_font_resources = document_resources.get_object().get("/Font", DictionaryObject()).get_object()
        font_resource = document_font_resources.get(font_name, None)
        if not is_null_or_none(font_resource):
            font_resource = cast(DictionaryObject, font_resource.get_object())

        # Retrieve field text, selected values and formatting information
        multiline = False
        field_flags = field.get(FieldDictionaryAttributes.Ff, 0)
        if field_flags & FieldDictionaryAttributes.FfBits.Multiline:
            multiline = True
        if (field.get(FieldDictionaryAttributes.FT, "/Tx") == "/Ch" and
            field_flags & FieldDictionaryAttributes.FfBits.Combo == 0):
            text = "\n".join(annotation.get_inherited(FieldDictionaryAttributes.Opt, []))
            selection = field.get("/V", [])
            if not isinstance(selection, list):
                selection = [selection]
        else:  # /Tx
            text = field.get("/V", "")
            selection = []

        # Create the TextStreamAppearance instance
        new_appearance_stream = cls(
            text, selection, rect, font_resource, font_name, font_size, font_color, multiline
        )
        if AnnotationDictionaryAttributes.AP in annotation:
            for k, v in cast(DictionaryObject, annotation[AnnotationDictionaryAttributes.AP]).get("/N", {}).items():
                if k not in {"/BBox", "/Length", "/Subtype", "/Type", "/Filter"}:
                    new_appearance_stream[k] = v

        return new_appearance_stream
