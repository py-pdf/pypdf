from collections.abc import Sequence
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any, Union, cast

from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

from ._cmap import get_encoding
from ._codecs.adobe_glyphs import adobe_glyphs
from ._utils import logger_warning
from .constants import FontFlags
from .errors import PdfReadError

try:
    from fontTools.ttLib import TTFont
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False


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
    font_file: Union[StreamObject, None] = None

    def as_font_descriptor_resource(self) -> DictionaryObject:
        font_descriptor_resource = DictionaryObject({
            NameObject("/Type"): NameObject("/FontDescriptor"),
            NameObject("/FontName"): NameObject(f"/{self.name}"),
            NameObject("/Flags"): NumberObject(self.flags),
            NameObject("/FontBBox"): ArrayObject([FloatObject(n) for n in self.bbox]),
            NameObject("/ItalicAngle"): FloatObject(self.italic_angle),
            NameObject("/Ascent"): FloatObject(self.ascent),
            NameObject("/Descent"): FloatObject(self.descent),
            NameObject("/CapHeight"): FloatObject(self.cap_height),
            NameObject("/XHeight"): FloatObject(self.x_height),
        })

        if self.font_file:
            # Add the stream. For now, we assume a TrueType font (FontFile2)
            font_descriptor_resource [NameObject("/FontFile2")] = self.font_file

        return font_descriptor_resource


@dataclass(frozen=True)
class CoreFontMetrics:
    font_descriptor: FontDescriptor
    character_widths: dict[str, int]


@dataclass
class Font:
    """
    A font object for use during text extraction and for producing
    text appearance streams.

    Attributes:
        name: Font name, derived from font["/BaseFont"]
        character_map: The font's character map
        encoding: Font encoding
        sub_type: The font type, such as Type1, TrueType, or Type3.
        font_descriptor: Font metrics, including a mapping of characters to widths
        character_widths: A mapping of characters to widths
        space_width: The width of a space, or an approximation
        interpretable: Default True. If False, the font glyphs cannot
            be translated to characters, e.g. Type3 fonts that do not define
            a '/ToUnicode' mapping.

    """

    name: str
    encoding: Union[str, dict[int, str]]
    character_map: dict[Any, Any] = field(default_factory=dict)
    sub_type: str = "Unknown"
    font_descriptor: FontDescriptor = field(default_factory=FontDescriptor)
    character_widths: dict[str, int] = field(default_factory=lambda: {"default": 500})
    space_width: Union[float, int] = 250
    interpretable: bool = True

    @staticmethod
    def _collect_tt_t1_character_widths(
        pdf_font_dict: DictionaryObject,
        char_map: dict[Any, Any],
        encoding: Union[str, dict[int, str]],
        current_widths: dict[str, int]
    ) -> None:
        """Parses a TrueType or Type1 font's /Widths array from a font dictionary and updates character widths"""
        widths_array = cast(ArrayObject, pdf_font_dict["/Widths"])
        first_char = pdf_font_dict.get("/FirstChar", 0)
        if not isinstance(encoding, str):
            # This means that encoding is a dict
            current_widths.update({
                encoding.get(idx + first_char, chr(idx + first_char)): width
                for idx, width in enumerate(widths_array)
            })
            return

        # We map the character code directly to the character
        # using the string encoding
        for idx, width in enumerate(widths_array):
            # Often "idx == 0" will denote the .notdef character, but we add it anyway
            char_code = idx + first_char  # This is a raw code
            # Get the "raw" character or byte representation
            raw_char = bytes([char_code]).decode(encoding, "surrogatepass")
            # Translate raw_char to the REAL Unicode character using the char_map
            unicode_char = char_map.get(raw_char)
            if unicode_char:
                current_widths[unicode_char] = int(width)
            else:
                current_widths[raw_char] = int(width)

    @staticmethod
    def _collect_cid_character_widths(
        d_font: DictionaryObject, char_map: dict[Any, Any], current_widths: dict[str, int]
    ) -> None:
        """Parses the /W array from a DescendantFont dictionary and updates character widths."""
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
            if not isinstance(w_entry, (int, float)):
                # We should never get here due to skip_count above. But
                # sometimes we do.
                logger_warning(f"Expected numeric value for width, got {w_entry}. Ignoring it.", __name__)
                continue
            # check for format (1): `int [int int int int ...]`
            w_next_entry = _w[idx + 1].get_object()
            if isinstance(w_next_entry, Sequence):
                start_idx, width_list = w_entry, w_next_entry
                current_widths.update(
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
                current_widths.update(
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
                # This handles the case of out of bounds (reaching the end of the width definitions
                # while expecting more elements).
                logger_warning(
                    f"Invalid font width definition. Last element: {w_entry}.",
                    __name__
                )

    @staticmethod
    def _add_default_width(current_widths: dict[str, int], flags: int) -> None:
        if not current_widths:
            current_widths["default"] = 500
            return

        if " " in current_widths and current_widths[" "] != 0:
            # Setting default to once or twice the space width, depending on fixed pitch
            if (flags & FontFlags.FIXED_PITCH) == FontFlags.FIXED_PITCH:
                current_widths["default"] = current_widths[" "]
                return

            current_widths["default"] = int(2 * current_widths[" "])
            return

        # Use the average width of existing glyph widths
        valid_widths = [w for w in current_widths.values() if w > 0]
        current_widths["default"] = sum(valid_widths) // len(valid_widths) if valid_widths else 500

    @staticmethod
    def _add_space_width(character_widths: dict[str, int], flags: int) -> int:
        space_width = character_widths.get(" ", 0)
        if space_width != 0:
            return space_width

        if (flags & FontFlags.FIXED_PITCH) == FontFlags.FIXED_PITCH:
            return character_widths["default"]

        return character_widths["default"] // 2

    @staticmethod
    def _parse_font_descriptor(font_descriptor_obj: DictionaryObject) -> dict[str, Any]:
        font_descriptor_kwargs: dict[Any, Any] = {}
        for source_key, target_key in [
            ("/FontName", "name"),
            ("/FontFamily", "family"),
            ("/FontWeight", "weight"),
            ("/Ascent", "ascent"),
            ("/Descent", "descent"),
            ("/CapHeight", "cap_height"),
            ("/XHeight", "x_height"),
            ("/ItalicAngle", "italic_angle"),
            ("/Flags", "flags"),
            ("/FontBBox", "bbox")
        ]:
            if source_key in font_descriptor_obj:
                font_descriptor_kwargs[target_key] = font_descriptor_obj[source_key]
        # Handle missing bbox gracefully - PDFs may have fonts without valid bounding boxes
        if "bbox" in font_descriptor_kwargs:
            bbox_tuple = tuple(map(float, font_descriptor_kwargs["bbox"]))
            assert len(bbox_tuple) == 4, bbox_tuple
            font_descriptor_kwargs["bbox"] = bbox_tuple

        # Find the binary stream for this font if there is one
        for source_key in ["/FontFile", "/FontFile2", "/FontFile3"]:
            if source_key in font_descriptor_obj:
                if "font_file" in font_descriptor_kwargs:
                    raise PdfReadError(f"More than one /FontFile found in {font_descriptor_obj}")

                try:
                    font_file = font_descriptor_obj[source_key].get_object()
                    font_descriptor_kwargs["font_file"] = font_file
                except PdfReadError as e:
                    logger_warning(f"Failed to get '{source_key}' in {font_descriptor_obj}: {e}", __name__)
        return font_descriptor_kwargs

    @classmethod
    def from_font_resource(
        cls,
        pdf_font_dict: DictionaryObject,
    ) -> "Font":
        from pypdf._codecs.core_font_metrics import CORE_FONT_METRICS  # noqa: PLC0415

        # Can collect base_font, name and encoding directly from font resource
        name = pdf_font_dict.get("/BaseFont", "Unknown").removeprefix("/")
        sub_type = pdf_font_dict.get("/Subtype", "Unknown").removeprefix("/")
        encoding, character_map = get_encoding(pdf_font_dict)
        font_descriptor = None
        character_widths: dict[str, int] = {}
        interpretable = True

        # Deal with fonts by type; Type1, TrueType and certain Type3
        if pdf_font_dict.get("/Subtype") in ("/Type1", "/MMType1", "/TrueType", "/Type3"):
            # Type3 fonts that do not specify a "/ToUnicode" mapping cannot be
            # reliably converted into character codes unless all named chars
            # in /CharProcs map to a standard adobe glyph. See §9.10.2 of the
            # PDF 1.7 standard.
            if sub_type == "Type3" and "/ToUnicode" not in pdf_font_dict:
                interpretable = all(
                    cname in adobe_glyphs
                    for cname in pdf_font_dict.get("/CharProcs") or []
                )
            if interpretable:  # Save some overhead if font is not interpretable
                if "/Widths" in pdf_font_dict:
                    cls._collect_tt_t1_character_widths(
                        pdf_font_dict, character_map, encoding, character_widths
                    )
                elif name in CORE_FONT_METRICS:
                    font_descriptor = CORE_FONT_METRICS[name].font_descriptor
                    character_widths = CORE_FONT_METRICS[name].character_widths
                if "/FontDescriptor" in pdf_font_dict:
                    font_descriptor_obj = pdf_font_dict.get("/FontDescriptor", DictionaryObject()).get_object()
                    if "/MissingWidth" in font_descriptor_obj:
                        character_widths["default"] = cast(int, font_descriptor_obj["/MissingWidth"].get_object())
                    font_descriptor = FontDescriptor(**cls._parse_font_descriptor(font_descriptor_obj))
                elif "/FontBBox" in pdf_font_dict:
                    # For Type3 without Font Descriptor but with FontBBox, see Table 110 in the PDF specification 2.0
                    bbox_tuple = tuple(map(float, cast(ArrayObject, pdf_font_dict["/FontBBox"])))
                    assert len(bbox_tuple) == 4, bbox_tuple
                    font_descriptor = FontDescriptor(name=name, bbox=bbox_tuple)

        else:
            # Composite font or CID font - CID fonts have a /W array mapping character codes
            # to widths stashed in /DescendantFonts. No need to test for /DescendantFonts though,
            # because all other fonts have already been dealt with.
            d_font: DictionaryObject
            for d_font_idx, d_font in enumerate(
                cast(ArrayObject, pdf_font_dict["/DescendantFonts"])
            ):
                d_font = cast(DictionaryObject, d_font.get_object())
                cast(ArrayObject, pdf_font_dict["/DescendantFonts"])[d_font_idx] = d_font
                cls._collect_cid_character_widths(
                    d_font, character_map, character_widths
                )
                if "/DW" in d_font:
                    character_widths["default"] = cast(int, d_font["/DW"].get_object())
                font_descriptor_obj = d_font.get("/FontDescriptor", DictionaryObject()).get_object()
                font_descriptor = FontDescriptor(**cls._parse_font_descriptor(font_descriptor_obj))

        if not font_descriptor:
            font_descriptor = FontDescriptor(name=name)

        if character_widths.get("default", 0) == 0:
            cls._add_default_width(character_widths, font_descriptor.flags)

        space_width = cls._add_space_width(character_widths, font_descriptor.flags)

        return cls(
            name=name,
            sub_type=sub_type,
            encoding=encoding,
            font_descriptor=font_descriptor,
            character_map=character_map,
            character_widths=character_widths,
            space_width=space_width,
            interpretable=interpretable
        )

    @classmethod
    def from_truetype_font_file(cls, font_file: BytesIO) -> "Font":
        with TTFont(font_file) as tt_font_object:
            header = tt_font_object["head"]
            names = tt_font_object["name"]
            postscript_info = tt_font_object["post"]
            horizontal_header = tt_font_object["hhea"]
            os_2 = tt_font_object["OS/2"]
            metrics = tt_font_object["hmtx"].metrics

            # Get the scaling factor to convert font file's units per em to PDF's 1000 units per em
            units_per_em = header.unitsPerEm
            scale_factor = 1000.0 / units_per_em

            # Get the font descriptor
            font_descriptor_kwargs: dict[Any, Any] = {}
            font_descriptor_kwargs["name"] = names.getDebugName(6) or names.getDebugName(1)  # PostScript name
            font_descriptor_kwargs["family"] = names.getDebugName(16) or names.getDebugName(1)  # Prefer typographic
            font_descriptor_kwargs["weight"] = names.getDebugName(17) or names.getDebugName(2)  # names
            font_descriptor_kwargs["ascent"] = int(round(horizontal_header.ascent * scale_factor, 0))
            font_descriptor_kwargs["descent"] = int(round(horizontal_header.descent * scale_factor, 0))
            font_descriptor_kwargs["cap_height"] = int(round(os_2.sCapHeight * scale_factor, 0))
            font_descriptor_kwargs["x_height"] = int(round(os_2.sxHeight  * scale_factor, 0))

            # Get the font flags
            flags: int = 0
            italic_angle = postscript_info.italicAngle
            if italic_angle != 0.0:
                flags |= FontFlags.ITALIC
            if postscript_info.isFixedPitch > 0:
                flags |= FontFlags.FIXED_PITCH

            # See Chapter 6 of the TrueType reference manual for the definition of the OS/2 table:
            # https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6OS2.html
            family_class = os_2.sFamilyClass >> 8
            if 2 <= family_class <= 9 and family_class != 6:
                flags |= FontFlags.SERIF
            if family_class == 10:
                flags |= FontFlags.SCRIPT
            if family_class == 12:
                flags |= FontFlags.SYMBOLIC
            else:
                flags |= FontFlags.NONSYMBOLIC
            font_descriptor_kwargs["flags"] = flags

            font_descriptor_kwargs["bbox"] = (
                round(header.xMin * scale_factor, 0),
                round(header.yMin * scale_factor, 0),
                round(header.xMax * scale_factor, 0),
                round(header.yMax * scale_factor, 0)
            )

            font_file_data = StreamObject()
            font_file_raw_bytes = font_file.getvalue()
            font_file_data.set_data(font_file_raw_bytes)
            font_file_data.update({NameObject("/Length1"): NumberObject(len(font_file_raw_bytes))})
            font_descriptor_kwargs["font_file"] = font_file_data

            font_descriptor = FontDescriptor(**font_descriptor_kwargs)
            character_map = {chr(key): value for key, value in tt_font_object.getBestCmap().items()}
            encoding = "utf_16_be"  # Assume unicode

            character_widths: dict[str, int] = {}
            for character, glyph in character_map.items():
                character_widths[character] = int(round(metrics[glyph][0] * scale_factor, 0))
            cls._add_default_width(character_widths, flags)
            space_width = cls._add_space_width(character_widths, flags)

        return cls(
            name=font_descriptor.name,
            sub_type="TrueType",
            encoding=encoding,
            font_descriptor=font_descriptor,
            character_map=character_map,
            character_widths=character_widths,
            space_width=space_width,
            interpretable=True
        )

    def as_font_resource(self) -> DictionaryObject:
        # If we have an embedded Truetype font, we assume that we need to produce a Type 2 CID font resource.
        if self.font_descriptor.font_file and self.sub_type == "TrueType":
            # Create the descendant font, using Identity mapping
            cid_font = DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/CIDFontType2"),
                NameObject("/BaseFont"): NameObject(f"/{self.name}"),
                NameObject("/CIDSystemInfo"): DictionaryObject({
                    NameObject("/Registry"): TextStringObject("Adobe"),  # Should be something read from font file
                    NameObject("/Ordering"): TextStringObject("Identity"),
                    NameObject("/Supplement"): NumberObject(0)
                }),
                # "/FontDescriptor" should be an IndirectObject. We don't add it here.
            })

            # Build the widths (/W) array. This can have to formats:
            # [first_cid [w1 w2 w3]] or [first last width]
            # Here we choose the first format and simply provide one array with one width for every cid.
            widths_list = []
            for char, width in self.character_widths.items():
                if char != "default":
                    cid = ord(char)
                    widths_list.extend([NumberObject(cid), ArrayObject([NumberObject(width)])])

            cid_font[NameObject("/W")] = ArrayObject(widths_list)
            cid_font[NameObject("/DW")] = NumberObject(self.character_widths.get("default", 1000))
            cid_font[NameObject("/CIDToGIDMap")] = NameObject("/Identity")

            # Create the Type 0 font object)
            return DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type0"),
                NameObject("/BaseFont"): NameObject(f"/{self.name}"),
                NameObject("/Encoding"): NameObject("/Identity-H"),
                NameObject("/DescendantFonts"): ArrayObject([cid_font]),
            })

        # Fallback: Return a font resource for the 14 Adobe Core fonts.
        return DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/Name"): NameObject(f"/{self.name}"),
            NameObject("/BaseFont"): NameObject(f"/{self.name}"),
            NameObject("/Encoding"): NameObject("/WinAnsiEncoding")
        })

    def text_width(self, text: str = "") -> float:
        """Sum of character widths specified in PDF font for the supplied text."""
        return sum(
            [self.character_widths.get(char, self.character_widths["default"]) for char in text], 0.0
        )
