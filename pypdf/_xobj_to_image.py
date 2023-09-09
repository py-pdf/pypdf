"""Code in here is only used by pypdf.filters._xobj_to_image"""

from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from ._utils import logger_warning
from .constants import ColorSpaces
from .constants import FilterTypes as FT
from .constants import ImageAttributes as IA
from .constants import StreamAttributes as SA
from .errors import PdfReadError
from .generic import (
    ArrayObject,
    DecodedStreamObject,
    EncodedStreamObject,
    IndirectObject,
    NullObject,
)

try:
    from typing import Literal, TypeAlias  # type: ignore[attr-defined]
except ImportError:
    # PEP 586 introduced typing.Literal with Python 3.8
    # For older Python versions, the backport typing_extensions is necessary:
    from typing_extensions import Literal, TypeAlias  # type: ignore[misc, assignment]


try:
    from PIL import Image
except ImportError:
    raise ImportError(
        "pillow is required to do image extraction. "
        "It can be installed via 'pip install pypdf[image]'"
    )

mode_str_type: TypeAlias = Literal[
    "", "1", "RGB", "2bits", "4bits", "P", "L", "RGBA", "CMYK"
]


def _xobj_to_image(x_object_obj: Dict[str, Any]) -> Tuple[Optional[str], bytes, Any]:
    """
    Users need to have the pillow package installed.

    It's unclear if pypdf will keep this function here, hence it's private.
    It might get removed at any point.

    Args:
      x_object_obj:

    Returns:
        Tuple[file extension, bytes, PIL.Image.Image]
    """
    # for error reporting
    if (
        hasattr(x_object_obj, "indirect_reference") and x_object_obj is None
    ):  # pragma: no cover
        obj_as_text = x_object_obj.indirect_reference.__repr__()
    else:
        obj_as_text = x_object_obj.__repr__()

    size = (x_object_obj[IA.WIDTH], x_object_obj[IA.HEIGHT])
    data = x_object_obj.get_data()  # type: ignore
    if isinstance(data, str):  # pragma: no cover
        data = data.encode()
    colors = x_object_obj.get("/Colors", 1)
    color_space: Any = x_object_obj.get("/ColorSpace", NullObject()).get_object()
    if isinstance(color_space, list) and len(color_space) == 1:
        color_space = color_space[0].get_object()
    if (
        IA.COLOR_SPACE in x_object_obj
        and x_object_obj[IA.COLOR_SPACE] == ColorSpaces.DEVICE_RGB
    ):
        # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes
        mode: mode_str_type = "RGB"
    if x_object_obj.get("/BitsPerComponent", 8) < 8:
        mode, invert_color = _get_imagemode(
            f"{x_object_obj.get('/BitsPerComponent', 8)}bit", 0, ""
        )
    else:
        mode, invert_color = _get_imagemode(
            color_space,
            2
            if (
                colors == 1
                and (
                    not isinstance(color_space, NullObject)
                    and "Gray" not in color_space
                )
            )
            else colors,
            "",
        )
    extension = None
    alpha = None
    filters = x_object_obj.get(SA.FILTER, [None])
    lfilters = filters[-1] if isinstance(filters, list) else filters
    if lfilters == FT.FLATE_DECODE:
        img, image_format, extension, invert_color = _handle_flate(
            size,
            data,
            mode,
            color_space,
            colors,
            obj_as_text,
        )
    elif lfilters in (FT.LZW_DECODE, FT.ASCII_85_DECODE, FT.CCITT_FAX_DECODE):
        # I'm not sure if the following logic is correct.
        # There might not be any relationship between the filters and the
        # extension
        if x_object_obj[SA.FILTER] in [[FT.LZW_DECODE], [FT.CCITT_FAX_DECODE]]:
            extension = ".tiff"  # mime_type = "image/tiff"
            image_format = "TIFF"
        else:
            extension = ".png"  # mime_type = "image/png"
            image_format = "PNG"
        img = Image.open(BytesIO(data), formats=("TIFF", "PNG"))
    elif lfilters == FT.DCT_DECODE:
        img, image_format, extension = Image.open(BytesIO(data)), "JPEG", ".jpg"
        # invert_color kept unchanged
    elif lfilters == FT.JPX_DECODE:
        img, image_format, extension, invert_color = _handle_jpx(
            size, data, mode, color_space, colors
        )
    elif lfilters == FT.CCITT_FAX_DECODE:
        img, image_format, extension, invert_color = (
            Image.open(BytesIO(data), formats=("TIFF",)),
            "TIFF",
            ".tiff",
            False,
        )
    else:
        if mode == "":
            raise PdfReadError(f"ColorSpace field not found in {x_object_obj}")
        img, image_format, extension, invert_color = (
            Image.frombytes(mode, size, data),
            "PNG",
            ".png",
            False,
        )

    # CMYK image and other colorspaces without decode
    # requires reverting scale (cf p243,2§ last sentence)
    decode = x_object_obj.get(
        IA.DECODE,
        ([1.0, 0.0] * len(img.getbands()))
        if (
            (img.mode == "CMYK" or (invert_color and img.mode == "L"))
            and lfilters in (FT.DCT_DECODE, FT.JPX_DECODE)
        )
        else None,
    )
    if (
        isinstance(color_space, ArrayObject)
        and color_space[0].get_object() == "/Indexed"
    ):
        decode = None  # decode is meanless of Indexed
    if decode is not None and not all(decode[i] == i % 2 for i in range(len(decode))):
        lut: List[int] = []
        for i in range(0, len(decode), 2):
            dmin = decode[i]
            dmax = decode[i + 1]
            lut.extend(
                round(255.0 * (j / 255.0 * (dmax - dmin) + dmin)) for j in range(256)
            )
        img = img.point(lut)

    if IA.S_MASK in x_object_obj:  # add alpha channel
        alpha = _xobj_to_image(x_object_obj[IA.S_MASK])[2]
        if img.size != alpha.size:
            logger_warning(f"image and mask size not matching: {obj_as_text}", __name__)
        else:
            # TODO : implement mask
            if alpha.mode != "L":
                alpha = alpha.convert("L")
            if img.mode == "P":
                img = img.convert("RGB")
            elif img.mode == "1":
                img = img.convert("L")
            img.putalpha(alpha)
        if "JPEG" in image_format:
            extension = ".jp2"
            image_format = "JPEG2000"
        else:
            extension = ".png"
            image_format = "PNG"

    img_byte_arr = BytesIO()
    try:
        img.save(img_byte_arr, format=image_format)
    except OSError:  # pragma: no cover
        # odd error
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format=image_format)
    data = img_byte_arr.getvalue()

    try:  # temporary try/except until other fixes of images
        img = Image.open(BytesIO(data))
    except Exception:
        img = None  # type: ignore
    return extension, data, img


def _get_imagemode(
    color_space: Union[str, List[Any], Any],
    color_components: int,
    prev_mode: mode_str_type,
) -> Tuple[mode_str_type, bool]:
    """
    Returns
        Image mode not taking into account mask(transparency)
        ColorInversion is required (like for some DeviceCMYK)
    """
    if isinstance(color_space, NullObject):
        return "", False
    if isinstance(color_space, str):
        pass
    elif not isinstance(color_space, list):
        raise PdfReadError(
            "can not interprete colorspace", color_space
        )  # pragma: no cover
    elif color_space[0].startswith("/Cal"):  # /CalRGB and /CalGray
        color_space = "/Device" + color_space[0][4:]
    elif color_space[0] == "/ICCBased":
        icc_profile = color_space[1].get_object()
        color_components = cast(int, icc_profile["/N"])
        color_space = icc_profile.get("/Alternate", "")
    elif color_space[0] == "/Indexed":
        color_space = color_space[1]
        if isinstance(color_space, IndirectObject):
            color_space = color_space.get_object()
        mode2, invert_color = _get_imagemode(color_space, color_components, prev_mode)
        if mode2 in ("RGB", "CMYK"):
            mode2 = "P"
        return mode2, invert_color
    elif color_space[0] == "/Separation":
        color_space = color_space[2]
        if isinstance(color_space, IndirectObject):
            color_space = color_space.get_object()
        mode2, invert_color = _get_imagemode(color_space, color_components, prev_mode)
        return mode2, True
    elif color_space[0] == "/DeviceN":
        color_components = len(color_space[1])
        color_space = color_space[2]
        if isinstance(color_space, IndirectObject):  # pragma: no cover
            color_space = color_space.get_object()

    mode_map = {
        "1bit": "1",  # pos [0] will be used for 1 bit
        "/DeviceGray": "L",  # must be in pos [1]
        "palette": "P",  # must be in pos [2] for color_components align.
        "/DeviceRGB": "RGB",  # must be in pos [3]
        "/DeviceCMYK": "CMYK",  # must be in pos [4]
        "2bit": "2bits",  # 2 bits images
        "4bit": "4bits",  # 4 bits
    }
    mode: mode_str_type = (
        mode_map.get(color_space)  # type: ignore
        or list(mode_map.values())[color_components]
        or prev_mode
    )  # type: ignore
    return mode, mode == "CMYK"


def _handle_flate(
    size: Tuple[int, int],
    data: bytes,
    mode: mode_str_type,
    color_space: str,
    colors: int,
    obj_as_text: str,
) -> Tuple[Image.Image, str, str, bool]:
    """
    Process image encoded in flateEncode
    Returns img, image_format, extension, color inversion
    """

    def bits2byte(data: bytes, size: Tuple[int, int], bits: int) -> bytes:
        mask = (2 << bits) - 1
        nbuff = bytearray(size[0] * size[1])
        by = 0
        bit = 8 - bits
        for y in range(size[1]):
            if (bit != 0) and (bit != 8 - bits):
                by += 1
                bit = 8 - bits
            for x in range(size[0]):
                nbuff[y * size[0] + x] = (data[by] >> bit) & mask
                bit -= bits
                if bit < 0:
                    by += 1
                    bit = 8 - bits
        return bytes(nbuff)

    extension = ".png"  # mime_type = "image/png"
    image_format = "PNG"
    lookup: Any
    base: Any
    hival: Any
    if isinstance(color_space, ArrayObject) and color_space[0] == "/Indexed":
        color_space, base, hival, lookup = (value.get_object() for value in color_space)
    if mode == "2bits":
        mode = "P"
        data = bits2byte(data, size, 2)
    elif mode == "4bits":
        mode = "P"
        data = bits2byte(data, size, 4)
    img = Image.frombytes(mode, size, data)
    if color_space == "/Indexed":
        from .generic import TextStringObject

        if isinstance(lookup, (EncodedStreamObject, DecodedStreamObject)):
            lookup = lookup.get_data()
        if isinstance(lookup, TextStringObject):
            lookup = lookup.original_bytes
        if isinstance(lookup, str):
            lookup = lookup.encode()
        try:
            nb, conv, mode = {  # type: ignore
                "1": (0, "", ""),
                "L": (1, "P", "L"),
                "P": (0, "", ""),
                "RGB": (3, "P", "RGB"),
                "CMYK": (4, "P", "CMYK"),
            }[_get_imagemode(base, 0, "")[0]]
        except KeyError:  # pragma: no cover
            logger_warning(
                f"Base {base} not coded please share the pdf file with pypdf dev team",
                __name__,
            )
            lookup = None
        else:
            if img.mode == "1":
                colors_arr = [lookup[x - nb : x] for x in range(nb, len(lookup), nb)]
                arr = b"".join(
                    [
                        b"".join(
                            [
                                colors_arr[1 if img.getpixel((x, y)) > 127 else 0]
                                for x in range(img.size[0])
                            ]
                        )
                        for y in range(img.size[1])
                    ]
                )
                img = Image.frombytes(mode, img.size, arr)
            else:
                img = img.convert(conv)
                if len(lookup) != (hival + 1) * nb:
                    logger_warning(f"Invalid Lookup Table in {obj_as_text}", __name__)
                    lookup = None
                elif mode == "L":
                    # gray lookup does not work : it is converted to a similar RGB lookup
                    lookup = b"".join([bytes([b, b, b]) for b in lookup])
                    mode = "RGB"
                # TODO : cf https://github.com/py-pdf/pypdf/pull/2039
                # this is a work around until PIL is able to process CMYK images
                elif mode == "CMYK":
                    _rgb = []
                    for _c, _m, _y, _k in (
                        lookup[n : n + 4] for n in range(0, 4 * (len(lookup) // 4), 4)
                    ):
                        _r = int(255 * (1 - _c / 255) * (1 - _k / 255))
                        _g = int(255 * (1 - _m / 255) * (1 - _k / 255))
                        _b = int(255 * (1 - _y / 255) * (1 - _k / 255))
                        _rgb.append(bytes((_r, _g, _b)))
                    lookup = b"".join(_rgb)
                    mode = "RGB"
                if lookup is not None:
                    img.putpalette(lookup, rawmode=mode)
            img = img.convert("L" if base == ColorSpaces.DEVICE_GRAY else "RGB")
    elif not isinstance(color_space, NullObject) and color_space[0] == "/ICCBased":
        # see Table 66 - Additional Entries Specific to an ICC Profile
        # Stream Dictionary
        mode2 = _get_imagemode(color_space, colors, mode)[0]
        if mode != mode2:
            img = Image.frombytes(mode2, size, data)  # reloaded as mode may have change
    if mode == "CMYK":
        extension = ".tif"
        image_format = "TIFF"
    return img, image_format, extension, False


def _handle_jpx(
    size: Tuple[int, int],
    data: bytes,
    mode: mode_str_type,
    color_space: str,
    colors: int,
) -> Tuple[Image.Image, str, str, bool]:
    """
    Process image encoded in flateEncode
    Returns img, image_format, extension, inversion
    """
    extension = ".jp2"  # mime_type = "image/x-jp2"
    img1 = Image.open(BytesIO(data), formats=("JPEG2000",))
    mode, invert_color = _get_imagemode(color_space, colors, mode)
    if mode == "":
        mode = cast(mode_str_type, img1.mode)
        invert_color = mode in ("CMYK",)
    if img1.mode == "RGBA" and mode == "RGB":
        mode = "RGBA"
    # we need to convert to the good mode
    try:
        if img1.mode != mode:
            img = Image.frombytes(mode, img1.size, img1.tobytes())
        else:
            img = img1
    except OSError:
        img = Image.frombytes(mode, img1.size, img1.tobytes())
    # for CMYK conversion :
    # https://stcom/questions/38855022/conversion-from-cmyk-to-rgb-with-pillow-is-different-from-that-of-photoshop
    # not implemented for the moment as I need to get properly the ICC
    if img.mode == "CMYK":
        img = img.convert("RGB")
    image_format = "JPEG2000"
    return img, image_format, extension, invert_color
