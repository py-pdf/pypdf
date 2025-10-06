import re
from typing import Any, Optional, Union, cast

from .._cmap import _default_fonts_space_width, build_char_map_from_dict
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
    This class is similar in form to the FreeText class in pypdf.
    """
    def _appearance_stream_data(
        self,
        text: str = "",
        selection: Optional[list[str]] = None,
        rect: Union[RectangleObject, tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0),
        font_glyph_byte_map: Optional[dict[str, bytes]] = None,
        font_name: str = "/Helv",
        font_size: float = 0.0,
        font_color: str = "0 g",
        multiline: bool = False
    ) -> bytes:
        font_glyph_byte_map = font_glyph_byte_map or {}
        if isinstance(rect, tuple):
            rect = RectangleObject(rect)

        # If font_size is 0, apply the logic for multiline or large-as-possible font
        if font_size == 0:
            if multiline:
                font_size = DEFAULT_FONT_SIZE_IN_MULTILINE
            else:
                font_size = rect.height - 2

        # Set the vertical offset
        y_offset = rect.height - 1 - font_size
        default_appearance = f"{font_name} {font_size} Tf {font_color}"
        ap_stream = f"q\n/Tx BMC \nq\n1 1 {rect.width - 1} {rect.height - 1} re\nW\nBT\n{default_appearance}\n".encode()
        for line_number, line in enumerate(text.replace("\n", "\r").split("\r")):
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
        # If a font resource was added, get the font character map
        if font_resource:
            font_resource = cast(DictionaryObject, font_resource.get_object())
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
        else:
            logger_warning(f"Font dictionary for {font_name} not found.", __name__)
            font_glyph_byte_map = {}

        ap_stream_data = self._appearance_stream_data(
            text, selection, rect, font_glyph_byte_map, font_name, font_size, font_color, multiline
        )

        super().__init__()
        self[NameObject("/Type")] = NameObject("/XObject")
        self[NameObject("/Subtype")] = NameObject("/Form")
        self[NameObject("/BBox")] = RectangleObject(rect)
        self.set_data(ByteStringObject(ap_stream_data))
        self[NameObject("/Length")] = NumberObject(len(ap_stream_data))
        # Update Resources with font information if necessary
        if font_resource is not None:
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
        """Creates a TextStreamAppearance object from a given text field annotation."""
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

        # Escape parentheses (PDF 1.7 reference, table 3.2, Literal Strings)
        text = text.replace("\\", "\\\\").replace("(", r"\(").replace(")", r"\)")

        # Create the TextStreamAppearance instance
        new_appearance_stream = cls(
            text, selection, rect, font_resource, font_name, font_size, font_color, multiline
        )
        if AnnotationDictionaryAttributes.AP in annotation:
            for k, v in cast(DictionaryObject, annotation[AnnotationDictionaryAttributes.AP]).get("/N", {}).items():
                if k not in {"/BBox", "/Length", "/Subtype", "/Type", "/Filter"}:
                    new_appearance_stream[k] = v

        return new_appearance_stream
