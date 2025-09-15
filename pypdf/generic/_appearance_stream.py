from typing import Any, cast

from .._cmap import _default_fonts_space_width, build_char_map_from_dict
from .._page import PageObject
from .._utils import logger_warning
from ..constants import AnnotationDictionaryAttributes as AA
from ..constants import FieldDictionaryAttributes as FA
from ..generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    RectangleObject,
    StreamObject,
)
from ..generic._base import ByteStringObject, TextStringObject, is_null_or_none

DEFAULT_FONT_HEIGHT_IN_MULTILINE = 12


def generate_appearance_stream(
    txt: str,
    sel: list[str],
    da: str,
    font_full_rev: dict[str, bytes],
    rct: RectangleObject,
    font_height: float,
    y_offset: float,
) -> bytes:
    ap_stream = f"q\n/Tx BMC \nq\n1 1 {rct.width - 1} {rct.height - 1} re\nW\nBT\n{da}\n".encode()
    for line_number, line in enumerate(txt.replace("\n", "\r").split("\r")):
        if line in sel:
            # may be improved but cannot find how to get fill working => replaced with lined box
            ap_stream += (
                f"1 {y_offset - (line_number * font_height * 1.4) - 1} {rct.width - 2} {font_height + 2} re\n"
                f"0.5 0.5 0.5 rg s\n{da}\n"
            ).encode()
        if line_number == 0:
            ap_stream += f"2 {y_offset} Td\n".encode()
        else:
            # Td is a relative translation
            ap_stream += f"0 {- font_height * 1.4} Td\n".encode()
        enc_line: list[bytes] = [
            font_full_rev.get(c, c.encode("utf-16-be")) for c in line
        ]
        if any(len(c) >= 2 for c in enc_line):
            ap_stream += b"<" + (b"".join(enc_line)).hex().encode() + b"> Tj\n"
        else:
            ap_stream += b"(" + b"".join(enc_line) + b") Tj\n"
    ap_stream += b"ET\nQ\nEMC\nQ\n"
    return ap_stream


def update_field_annotation(
    af: DictionaryObject,  # _root_object[CatalogDictionary.ACRO_FORM])
    page: PageObject,
    field: DictionaryObject,
    annotation: DictionaryObject,
    font_name: str = "",
    font_size: float = -1,
) -> StreamObject:
    # Calculate rectangle dimensions
    _rct = cast(RectangleObject, annotation[AA.Rect])
    rct = RectangleObject((0, 0, abs(_rct[2] - _rct[0]), abs(_rct[3] - _rct[1])))

    # Extract font information
    da = annotation.get_inherited(
        AA.DA,
        af.get(
            AA.DA, None
        ),
    )
    if da is None:
        da = TextStringObject("/Helv 0 Tf 0 g")
    else:
        da = da.get_object()
    font_properties = da.replace("\n", " ").replace("\r", " ").split(" ")
    font_properties = [x for x in font_properties if x != ""]
    if font_name:
        font_properties[font_properties.index("Tf") - 2] = font_name
    else:
        font_name = font_properties[font_properties.index("Tf") - 2]
    font_height = (
        font_size
        if font_size >= 0
        else float(font_properties[font_properties.index("Tf") - 1])
    )
    if font_height == 0:
        if field.get(FA.Ff, 0) & FA.FfBits.Multiline:
            font_height = DEFAULT_FONT_HEIGHT_IN_MULTILINE
        else:
            font_height = rct.height - 2
    font_properties[font_properties.index("Tf") - 1] = str(font_height)
    da = " ".join(font_properties)
    y_offset = rct.height - 1 - font_height

    # Retrieve font information from local DR ...
    dr: Any = cast(
        DictionaryObject,
        cast(
            DictionaryObject,
            annotation.get_inherited(
                "/DR",
                af.get("/DR", DictionaryObject()),
            ),
        ).get_object(),
    )
    dr = dr.get("/Font", DictionaryObject()).get_object()
    # _default_fonts_space_width keys is the list of Standard fonts
    if font_name not in dr and font_name not in _default_fonts_space_width:
        # ...or AcroForm dictionary
        dr = cast(
            dict[Any, Any],
            af.get("/DR", {}),
        )
        dr = dr.get_object().get("/Font", DictionaryObject()).get_object()
    font_res = dr.get(font_name, None)
    if not is_null_or_none(font_res):
        font_res = cast(DictionaryObject, font_res.get_object())
        _font_subtype, _, font_encoding, font_map = build_char_map_from_dict(
            200, font_res
        )
        try:  # remove width stored in -1 key
            del font_map[-1]
        except KeyError:
            pass
        font_full_rev: dict[str, bytes]
        if isinstance(font_encoding, str):
            font_full_rev = {
                v: k.encode(font_encoding) for k, v in font_map.items()
            }
        else:
            font_full_rev = {v: bytes((k,)) for k, v in font_encoding.items()}
            font_encoding_rev = {v: bytes((k,)) for k, v in font_encoding.items()}
            for key, value in font_map.items():
                font_full_rev[value] = font_encoding_rev.get(key, key)
    else:
        logger_warning(f"Font dictionary for {font_name} not found.", __name__)
        font_full_rev = {}

    # Retrieve field text and selected values
    field_flags = field.get(FA.Ff, 0)
    if field.get(FA.FT, "/Tx") == "/Ch" and field_flags & FA.FfBits.Combo == 0:
        txt = "\n".join(annotation.get_inherited(FA.Opt, []))
        sel = field.get("/V", [])
        if not isinstance(sel, list):
            sel = [sel]
    else:  # /Tx
        txt = field.get("/V", "")
        sel = []
    # Escape parentheses (PDF 1.7 reference, table 3.2, Literal Strings)
    txt = txt.replace("\\", "\\\\").replace("(", r"\(").replace(")", r"\)")
    # Generate appearance stream
    ap_stream = generate_appearance_stream(
        txt, sel, da, font_full_rev, rct, font_height, y_offset
    )

    # Create appearance dictionary
    dct = DecodedStreamObject.initialize_from_dictionary(
        {
            NameObject("/Type"): NameObject("/XObject"),
            NameObject("/Subtype"): NameObject("/Form"),
            NameObject("/BBox"): rct,
            "__streamdata__": ByteStringObject(ap_stream),
            "/Length": 0,
        }
    )
    if AA.AP in annotation:
        for k, v in cast(DictionaryObject, annotation[AA.AP]).get("/N", {}).items():
            if k not in {"/BBox", "/Length", "/Subtype", "/Type", "/Filter"}:
                dct[k] = v

    # Update Resources with font information if necessary
    if font_res is not None:
        dct[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {
                        NameObject(font_name): getattr(
                            font_res, "indirect_reference", font_res
                        )
                    }
                )
            }
        )

    return dct
