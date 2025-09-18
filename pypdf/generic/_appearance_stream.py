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

    def _generate_appearance_stream_data(
        self,
        text: str = "",
        selection: Optional[list[str]] = None,
        default_appearance: str = "",
        font_glyph_byte_map: Optional[dict[str, bytes]] = None,
        rectangle: Union[RectangleObject, tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0),
        font_size: float = 0,
        y_offset: float = 0,
    ) -> bytes:
        font_glyph_byte_map = font_glyph_byte_map or {}
        if isinstance(rectangle, tuple):
            rectangle = RectangleObject(rectangle)
        ap_stream = (
            f"q\n/Tx BMC \nq\n1 1 {rectangle.width - 1} {rectangle.height - 1} "
            f"re\nW\nBT\n{default_appearance}\n"
        ).encode()
        for line_number, line in enumerate(text.replace("\n", "\r").split("\r")):
            if selection and line in selection:
                # Might be improved, but cannot find how to get fill working => replaced with lined box
                ap_stream += (
                    f"1 {y_offset - (line_number * font_size * 1.4) - 1} {rectangle.width - 2} {font_size + 2} re\n"
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
        default_appearance: str = "",
        font_glyph_byte_map: Optional[dict[str, bytes]] = None,
        rectangle: Union[RectangleObject, tuple[float, float, float, float]] = (0.0, 0.0, 0.0, 0.0),
        font_size: float = 0,
        y_offset: float = 0,
    ) -> None:
        super().__init__()
        font_glyph_byte_map = font_glyph_byte_map or {}
        if isinstance(rectangle, tuple):
            rectangle = RectangleObject(rectangle)

        ap_stream_data = self._generate_appearance_stream_data(
            text, selection, default_appearance, font_glyph_byte_map, rectangle, font_size, y_offset,
        )

        self[NameObject("/Type")] = NameObject("/XObject")
        self[NameObject("/Subtype")] = NameObject("/Form")
        self[NameObject("/BBox")] = rectangle
        self.set_data(ByteStringObject(ap_stream_data))
        self[NameObject("/Length")] = NumberObject(len(ap_stream_data))

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
        _rectangle = cast(RectangleObject, annotation[AnnotationDictionaryAttributes.Rect])
        rectangle = RectangleObject((0, 0, abs(_rectangle[2] - _rectangle[0]), abs(_rectangle[3] - _rectangle[1])))

        # Get default appearance dictionary from annotation
        default_appearance = annotation.get_inherited(
            AnnotationDictionaryAttributes.DA,
            acro_form.get(AnnotationDictionaryAttributes.DA, None),
        )
        if default_appearance is None:
            # Create a default appearance if none was found in the annotation
            default_appearance = TextStringObject("/Helv 0 Tf 0 g")
        else:
            default_appearance = default_appearance.get_object()

        # Embed user-provided font name and font size in the default appearance, also
        # taking into account whether the field flags indicate a multiline field.
        # Uses the variable font_properties as an intermediate.
        font_properties = default_appearance.replace("\n", " ").replace("\r", " ").split(" ")
        font_properties = [x for x in font_properties if x != ""]
        # Override default appearance font name with user provided font name, if given.
        if user_font_name:
            font_name = user_font_name
            font_properties[font_properties.index("Tf") - 2] = user_font_name
        else:
            # Indirectly this just reads font_name from default appearance.
            font_name = font_properties[font_properties.index("Tf") - 2]
        # Override default appearance font size with user provided font size, if given.
        font_size = (
            user_font_size
            if user_font_size >= 0
            else float(font_properties[font_properties.index("Tf") - 1])
        )
        # Parse the field flags to find whether we need to wrap text, find whether we need to scale font size
        if font_size == 0:  # Only when not set and / or 0 in default appearance
            if field.get(FieldDictionaryAttributes.Ff, 0) & FieldDictionaryAttributes.FfBits.Multiline:
                font_size = DEFAULT_FONT_SIZE_IN_MULTILINE  # 12
            else:
                font_size = rectangle.height - 2  # Set as large as possible
        font_properties[font_properties.index("Tf") - 1] = str(font_size)
        # Reconstruct default appearance with user info and flags information
        default_appearance = " ".join(font_properties)

        # Set the vertical offset
        y_offset = rectangle.height - 1 - font_size

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

        # If this annotation has a font resources, get the font character map
        if not is_null_or_none(font_resource):
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
                    value: key.encode(font_encoding) for key, value in font_map.items()
                }
            else:
                font_glyph_byte_map = {value: bytes((key,)) for key, value in font_encoding.items()}
                font_encoding_rev = {value: bytes((key,)) for key, value in font_encoding.items()}
                for key, value in font_map.items():
                    font_glyph_byte_map[value] = font_encoding_rev.get(key, key)
        else:
            logger_warning(f"Font dictionary for {font_name} not found.", __name__)
            font_glyph_byte_map = {}

        # Retrieve field text and selected values
        field_flags = field.get(FieldDictionaryAttributes.Ff, 0)
        if (
                field.get(FieldDictionaryAttributes.FT, "/Tx") == "/Ch" and
                field_flags & FieldDictionaryAttributes.FfBits.Combo == 0
        ):
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
            text, selection, default_appearance, font_glyph_byte_map, rectangle, font_size, y_offset
        )

        if AnnotationDictionaryAttributes.AP in annotation:
            for key, value in (
                cast(DictionaryObject, annotation[AnnotationDictionaryAttributes.AP]).get("/N", {}).items()
            ):
                if key not in {"/BBox", "/Length", "/Subtype", "/Type", "/Filter"}:
                    new_appearance_stream[key] = value

        # Update Resources with font information if necessary
        if font_resource is not None:
            new_appearance_stream[NameObject("/Resources")] = DictionaryObject(
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

        return new_appearance_stream
