# Copyright (c) 2006, Mathieu Fenniak
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


"""
Implementation of stream filters for PDF.

See TABLE H.1 Abbreviations for standard filter names
"""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

import math
import struct
import zlib
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from ._utils import (
    b_,
    deprecate_with_replacement,
    logger_warning,
    ord_,
)
from .constants import CcittFaxDecodeParameters as CCITT
from .constants import ColorSpaces
from .constants import FilterTypeAbbreviations as FTA
from .constants import FilterTypes as FT
from .constants import ImageAttributes as IA
from .constants import LzwFilterParameters as LZW
from .constants import StreamAttributes as SA
from .errors import PdfReadError, PdfStreamError
from .generic import (
    ArrayObject,
    DecodedStreamObject,
    DictionaryObject,
    IndirectObject,
    NullObject,
)

try:
    from typing import Literal, TypeAlias  # type: ignore[attr-defined]
except ImportError:
    # PEP 586 introduced typing.Literal with Python 3.8
    # For older Python versions, the backport typing_extensions is necessary:
    from typing_extensions import Literal, TypeAlias  # type: ignore[misc, assignment]


def decompress(data: bytes) -> bytes:
    """
    Decompress the given data using zlib.

    This function attempts to decompress the input data using zlib. If the
    decompression fails due to a zlib error, it falls back to using a
    decompression object with a larger window size.

    Args:
        data: The input data to be decompressed.

    Returns:
        The decompressed data.
    """
    try:
        return zlib.decompress(data)
    except zlib.error:
        d = zlib.decompressobj(zlib.MAX_WBITS | 32)
        result_str = b""
        for b in [data[i : i + 1] for i in range(len(data))]:
            try:
                result_str += d.decompress(b)
            except zlib.error:
                pass
        return result_str


class FlateDecode:
    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Decode data which is flate-encoded.

        Args:
          data: flate-encoded data.
          decode_parms: a dictionary of values, understanding the
            "/Predictor":<int> key only

        Returns:
          The flate-decoded data.

        Raises:
          PdfReadError:
        """
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]
        str_data = decompress(data)
        predictor = 1

        if decode_parms:
            try:
                if isinstance(decode_parms, ArrayObject):
                    for decode_parm in decode_parms:
                        if "/Predictor" in decode_parm:
                            predictor = decode_parm["/Predictor"]
                else:
                    predictor = decode_parms.get("/Predictor", 1)
            except (AttributeError, TypeError):  # Type Error is NullObject
                pass  # Usually an array with a null object was read
        # predictor 1 == no predictor
        if predictor != 1:
            # The /Columns param. has 1 as the default value; see ISO 32000,
            # §7.4.4.3 LZWDecode and FlateDecode Parameters, Table 8
            DEFAULT_BITS_PER_COMPONENT = 8
            if isinstance(decode_parms, ArrayObject):
                columns = 1
                bits_per_component = DEFAULT_BITS_PER_COMPONENT
                for decode_parm in decode_parms:
                    if "/Columns" in decode_parm:
                        columns = decode_parm["/Columns"]
                    if LZW.BITS_PER_COMPONENT in decode_parm:
                        bits_per_component = decode_parm[LZW.BITS_PER_COMPONENT]
            else:
                columns = (
                    1 if decode_parms is None else decode_parms.get(LZW.COLUMNS, 1)
                )
                colors = 1 if decode_parms is None else decode_parms.get(LZW.COLORS, 1)
                bits_per_component = (
                    decode_parms.get(LZW.BITS_PER_COMPONENT, DEFAULT_BITS_PER_COMPONENT)
                    if decode_parms
                    else DEFAULT_BITS_PER_COMPONENT
                )

            # PNG predictor can vary by row and so is the lead byte on each row
            rowlength = (
                math.ceil(columns * colors * bits_per_component / 8) + 1
            )  # number of bytes

            # TIFF prediction:
            if predictor == 2:
                rowlength -= 1  # remove the predictor byte
                bpp = rowlength // columns
                str_data = bytearray(str_data)
                for i in range(len(str_data)):
                    if i % rowlength >= bpp:
                        str_data[i] = (str_data[i] + str_data[i - bpp]) % 256
                str_data = bytes(str_data)
            # PNG prediction:
            elif 10 <= predictor <= 15:
                str_data = FlateDecode._decode_png_prediction(str_data, columns, rowlength)  # type: ignore
            else:
                # unsupported predictor
                raise PdfReadError(f"Unsupported flatedecode predictor {predictor!r}")
        return str_data

    @staticmethod
    def _decode_png_prediction(data: bytes, columns: int, rowlength: int) -> bytes:
        # PNG prediction can vary from row to row
        if len(data) % rowlength != 0:
            raise PdfReadError("Image data is not rectangular")
        output = []
        prev_rowdata = (0,) * rowlength
        bpp = (rowlength - 1) // columns  # recomputed locally to not change params
        for row in range(0, len(data), rowlength):
            rowdata: List[int] = list(data[row : row + rowlength])
            filter_byte = rowdata[0]

            if filter_byte == 0:
                pass
            elif filter_byte == 1:
                for i in range(bpp + 1, rowlength):
                    rowdata[i] = (rowdata[i] + rowdata[i - bpp]) % 256
            elif filter_byte == 2:
                for i in range(1, rowlength):
                    rowdata[i] = (rowdata[i] + prev_rowdata[i]) % 256
            elif filter_byte == 3:
                for i in range(1, bpp + 1):
                    # left = 0
                    floor = prev_rowdata[i] // 2
                    rowdata[i] = (rowdata[i] + floor) % 256
                for i in range(bpp + 1, rowlength):
                    left = rowdata[i - bpp]
                    floor = (left + prev_rowdata[i]) // 2
                    rowdata[i] = (rowdata[i] + floor) % 256
            elif filter_byte == 4:
                for i in range(1, bpp + 1):
                    # left = 0
                    up = prev_rowdata[i]
                    # up_left = 0
                    paeth = up
                    rowdata[i] = (rowdata[i] + paeth) % 256
                for i in range(bpp + 1, rowlength):
                    left = rowdata[i - bpp]
                    up = prev_rowdata[i]
                    up_left = prev_rowdata[i - bpp]

                    p = left + up - up_left
                    dist_left = abs(p - left)
                    dist_up = abs(p - up)
                    dist_up_left = abs(p - up_left)

                    if dist_left <= dist_up and dist_left <= dist_up_left:
                        paeth = left
                    elif dist_up <= dist_up_left:
                        paeth = up
                    else:
                        paeth = up_left

                    rowdata[i] = (rowdata[i] + paeth) % 256
            else:
                # unsupported PNG filter
                raise PdfReadError(
                    f"Unsupported PNG filter {filter_byte!r}"
                )  # pragma: no cover
            prev_rowdata = tuple(rowdata)
            output.extend(rowdata[1:])
        return bytes(output)

    @staticmethod
    def encode(data: bytes, level: int = -1) -> bytes:
        """
        Compress the input data using zlib.

        Args:
            data: The data to be compressed.
            level: See https://docs.python.org/3/library/zlib.html#zlib.compress

        Returns:
            The compressed data.
        """
        return zlib.compress(data, level)


class ASCIIHexDecode:
    """
    The ASCIIHexDecode filter decodes data that has been encoded in ASCII
    hexadecimal form into a base-7 ASCII format.
    """

    @staticmethod
    def decode(
        data: Union[str, bytes],
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Decode an ASCII-Hex encoded data stream.

        Args:
          data: a str sequence of hexadecimal-encoded values to be
            converted into a base-7 ASCII string
          decode_parms: a string conversion in base-7 ASCII, where each of its values
            v is such that 0 <= ord(v) <= 127.

        Returns:
          A string conversion in base-7 ASCII, where each of its values
          v is such that 0 <= ord(v) <= 127.

        Raises:
          PdfStreamError:
        """
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        if isinstance(data, str):
            data = data.encode()
        retval = b""
        hex_pair = b""
        index = 0
        while True:
            if index >= len(data):
                raise PdfStreamError("Unexpected EOD in ASCIIHexDecode")
            char = data[index : index + 1]
            if char == b">":
                break
            elif char.isspace():
                index += 1
                continue
            hex_pair += char
            if len(hex_pair) == 2:
                retval += bytes((int(hex_pair, base=16),))
                hex_pair = b""
            index += 1
        assert hex_pair == b""
        return retval


class RunLengthDecode:
    """
    The RunLengthDecode filter decodes data that has been encoded in a
    simple byte-oriented format based on run length.
    The encoded data is a sequence of runs, where each run consists of
    a length byte followed by 1 to 128 bytes of data. If the length byte is
    in the range 0 to 127,
    the following length + 1 (1 to 128) bytes are copied literally during
    decompression.
    If length is in the range 129 to 255, the following single byte is to be
    copied 257 − length (2 to 128) times during decompression. A length value
    of 128 denotes EOD.
    """

    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Decode an ASCII-Hex encoded data stream.

        Args:
          data: a bytes sequence of length/data
          decode_parms: ignored.

        Returns:
          A bytes decompressed sequence.

        Raises:
          PdfStreamError:
        """
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        lst = []
        index = 0
        while True:
            if index >= len(data):
                raise PdfStreamError("Unexpected EOD in RunLengthDecode")
            length = data[index]
            index += 1
            if length == 128:
                if index < len(data):
                    raise PdfStreamError("early EOD in RunLengthDecode")
                else:
                    break
            elif length < 128:
                length += 1
                lst.append(data[index : (index + length)])
                index += length
            else:  # >128
                length = 257 - length
                lst.append(bytes((data[index],)) * length)
                index += 1
        return b"".join(lst)


class LZWDecode:
    """
    Taken from:

    http://www.java2s.com/Open-Source/Java-Document/PDF/PDF-
    Renderer/com/sun/pdfview/decode/LZWDecode.java.htm
    """

    class Decoder:
        def __init__(self, data: bytes) -> None:
            self.STOP = 257
            self.CLEARDICT = 256
            self.data = data
            self.bytepos = 0
            self.bitpos = 0
            self.dict = [""] * 4096
            for i in range(256):
                self.dict[i] = chr(i)
            self.reset_dict()

        def reset_dict(self) -> None:
            self.dictlen = 258
            self.bitspercode = 9

        def next_code(self) -> int:
            fillbits = self.bitspercode
            value = 0
            while fillbits > 0:
                if self.bytepos >= len(self.data):
                    return -1
                nextbits = ord_(self.data[self.bytepos])
                bitsfromhere = 8 - self.bitpos
                bitsfromhere = min(bitsfromhere, fillbits)
                value |= (
                    (nextbits >> (8 - self.bitpos - bitsfromhere))
                    & (0xFF >> (8 - bitsfromhere))
                ) << (fillbits - bitsfromhere)
                fillbits -= bitsfromhere
                self.bitpos += bitsfromhere
                if self.bitpos >= 8:
                    self.bitpos = 0
                    self.bytepos = self.bytepos + 1
            return value

        def decode(self) -> str:
            """
            TIFF 6.0 specification explains in sufficient details the steps to
            implement the LZW encode() and decode() algorithms.

            algorithm derived from:
            http://www.rasip.fer.hr/research/compress/algorithms/fund/lz/lzw.html
            and the PDFReference

            Raises:
              PdfReadError: If the stop code is missing
            """
            cW = self.CLEARDICT
            baos = ""
            while True:
                pW = cW
                cW = self.next_code()
                if cW == -1:
                    raise PdfReadError("Missed the stop code in LZWDecode!")
                if cW == self.STOP:
                    break
                elif cW == self.CLEARDICT:
                    self.reset_dict()
                elif pW == self.CLEARDICT:
                    baos += self.dict[cW]
                else:
                    if cW < self.dictlen:
                        baos += self.dict[cW]
                        p = self.dict[pW] + self.dict[cW][0]
                        self.dict[self.dictlen] = p
                        self.dictlen += 1
                    else:
                        p = self.dict[pW] + self.dict[pW][0]
                        baos += p
                        self.dict[self.dictlen] = p
                        self.dictlen += 1
                    if (
                        self.dictlen >= (1 << self.bitspercode) - 1
                        and self.bitspercode < 12
                    ):
                        self.bitspercode += 1
            return baos

    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> str:
        """
        Decode an LZW encoded data stream.

        Args:
          data: bytes`` or ``str`` text to decode.
          decode_parms: a dictionary of parameter values.

        Returns:
          decoded data.
        """
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        return LZWDecode.Decoder(data).decode()


class ASCII85Decode:
    """Decodes string ASCII85-encoded data into a byte format."""

    @staticmethod
    def decode(
        data: Union[str, bytes],
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        if isinstance(data, str):
            data = data.encode("ascii")
        group_index = b = 0
        out = bytearray()
        for char in data:
            if ord("!") <= char <= ord("u"):
                group_index += 1
                b = b * 85 + (char - 33)
                if group_index == 5:
                    out += struct.pack(b">L", b)
                    group_index = b = 0
            elif char == ord("z"):
                assert group_index == 0
                out += b"\0\0\0\0"
            elif char == ord("~"):
                if group_index:
                    for _ in range(5 - group_index):
                        b = b * 85 + 84
                    out += struct.pack(b">L", b)[: group_index - 1]
                break
        return bytes(out)


class DCTDecode:
    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        return data


class JPXDecode:
    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        **kwargs: Any,
    ) -> bytes:
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]  # noqa: F841
        return data


class CCITParameters:
    """TABLE 3.9 Optional parameters for the CCITTFaxDecode filter."""

    def __init__(self, K: int = 0, columns: int = 0, rows: int = 0) -> None:
        self.K = K
        self.EndOfBlock = None
        self.EndOfLine = None
        self.EncodedByteAlign = None
        self.columns = columns  # width
        self.rows = rows  # height
        self.DamagedRowsBeforeError = None

    @property
    def group(self) -> int:
        if self.K < 0:
            CCITTgroup = 4
        else:
            # k == 0: Pure one-dimensional encoding (Group 3, 1-D)
            # k > 0: Mixed one- and two-dimensional encoding (Group 3, 2-D)
            CCITTgroup = 3
        return CCITTgroup


class CCITTFaxDecode:
    """
    See 3.3.5 CCITTFaxDecode Filter (PDF 1.7 Standard).

    Either Group 3 or Group 4 CCITT facsimile (fax) encoding.
    CCITT encoding is bit-oriented, not byte-oriented.

    See: TABLE 3.9 Optional parameters for the CCITTFaxDecode filter
    """

    @staticmethod
    def _get_parameters(
        parameters: Union[None, ArrayObject, DictionaryObject], rows: int
    ) -> CCITParameters:
        # TABLE 3.9 Optional parameters for the CCITTFaxDecode filter
        k = 0
        columns = 1728
        if parameters:
            if isinstance(parameters, ArrayObject):
                for decode_parm in parameters:
                    if CCITT.COLUMNS in decode_parm:
                        columns = decode_parm[CCITT.COLUMNS]
                    if CCITT.K in decode_parm:
                        k = decode_parm[CCITT.K]
            else:
                if CCITT.COLUMNS in parameters:
                    columns = parameters[CCITT.COLUMNS]  # type: ignore
                if CCITT.K in parameters:
                    k = parameters[CCITT.K]  # type: ignore

        return CCITParameters(k, columns, rows)

    @staticmethod
    def decode(
        data: bytes,
        decode_parms: Union[None, ArrayObject, DictionaryObject] = None,
        height: int = 0,
        **kwargs: Any,
    ) -> bytes:
        if "decodeParms" in kwargs:  # deprecated
            deprecate_with_replacement("decodeParms", "parameters", "4.0.0")
            decode_parms = kwargs["decodeParms"]
        parms = CCITTFaxDecode._get_parameters(decode_parms, height)

        img_size = len(data)
        tiff_header_struct = "<2shlh" + "hhll" * 8 + "h"
        tiff_header = struct.pack(
            tiff_header_struct,
            b"II",  # Byte order indication: Little endian
            42,  # Version number (always 42)
            8,  # Offset to first IFD
            8,  # Number of tags in IFD
            256,
            4,
            1,
            parms.columns,  # ImageWidth, LONG, 1, width
            257,
            4,
            1,
            parms.rows,  # ImageLength, LONG, 1, length
            258,
            3,
            1,
            1,  # BitsPerSample, SHORT, 1, 1
            259,
            3,
            1,
            parms.group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
            262,
            3,
            1,
            0,  # Thresholding, SHORT, 1, 0 = WhiteIsZero
            273,
            4,
            1,
            struct.calcsize(
                tiff_header_struct
            ),  # StripOffsets, LONG, 1, length of header
            278,
            4,
            1,
            parms.rows,  # RowsPerStrip, LONG, 1, length
            279,
            4,
            1,
            img_size,  # StripByteCounts, LONG, 1, size of image
            0,  # last IFD
        )

        return tiff_header + data


def decode_stream_data(stream: Any) -> Union[bytes, str]:  # utils.StreamObject
    """
    Decode the stream data based on the specified filters.

    This function decodes the stream data using the filters provided in the
    stream. It supports various filter types, including FlateDecode,
    ASCIIHexDecode, RunLengthDecode, LZWDecode, ASCII85Decode, DCTDecode, JPXDecode, and
    CCITTFaxDecode.

    Args:
        stream: The input stream object containing the data and filters.

    Returns:
        The decoded stream data.

    Raises:
        NotImplementedError: If an unsupported filter type is encountered.
    """
    filters = stream.get(SA.FILTER, ())
    if isinstance(filters, IndirectObject):
        filters = cast(ArrayObject, filters.get_object())
    if not isinstance(filters, ArrayObject):
        # we have a single filter instance
        filters = (filters,)
    decodparms = stream.get(SA.DECODE_PARMS, ({},) * len(filters))
    if not isinstance(decodparms, (list, tuple)):
        decodparms = (decodparms,)
    data: bytes = b_(stream._data)
    # If there is not data to decode we should not try to decode the data.
    if data:
        for filter_type, params in zip(filters, decodparms):
            if isinstance(params, NullObject):
                params = {}
            if filter_type in (FT.FLATE_DECODE, FTA.FL):
                data = FlateDecode.decode(data, params)
            elif filter_type in (FT.ASCII_HEX_DECODE, FTA.AHx):
                data = ASCIIHexDecode.decode(data)  # type: ignore
            elif filter_type in (FT.RUN_LENGTH_DECODE, FTA.RL):
                data = RunLengthDecode.decode(data)
            elif filter_type in (FT.LZW_DECODE, FTA.LZW):
                data = LZWDecode.decode(data, params)  # type: ignore
            elif filter_type in (FT.ASCII_85_DECODE, FTA.A85):
                data = ASCII85Decode.decode(data)
            elif filter_type == FT.DCT_DECODE:
                data = DCTDecode.decode(data)
            elif filter_type == FT.JPX_DECODE:
                data = JPXDecode.decode(data)
            elif filter_type == FT.CCITT_FAX_DECODE:
                height = stream.get(IA.HEIGHT, ())
                data = CCITTFaxDecode.decode(data, params, height)
            elif filter_type == "/Crypt":
                if "/Name" not in params and "/Type" not in params:
                    pass
                else:
                    raise NotImplementedError(
                        "/Crypt filter with /Name or /Type not supported yet"
                    )
            else:
                # Unsupported filter
                raise NotImplementedError(f"unsupported filter {filter_type}")
    return data


def decodeStreamData(stream: Any) -> Union[str, bytes]:  # deprecated
    """Deprecated. Use decode_stream_data."""
    deprecate_with_replacement("decodeStreamData", "decode_stream_data", "4.0.0")
    return decode_stream_data(stream)


mode_str_type: TypeAlias = Literal[
    "", "1", "RGB", "2bits", "4bits", "P", "L", "RGBA", "CMYK"
]


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
    try:
        from PIL import Image
    except ImportError:
        raise ImportError(
            "pillow is required to do image extraction. "
            "It can be installed via 'pip install pypdf[image]'"
        )

    def _handle_flate(
        size: Tuple[int, int],
        data: bytes,
        mode: mode_str_type,
        color_space: str,
        colors: int,
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
            color_space, base, hival, lookup = (
                value.get_object() for value in color_space
            )
        if mode == "2bits":
            mode = "P"
            data = bits2byte(data, size, 2)
        elif mode == "4bits":
            mode = "P"
            data = bits2byte(data, size, 4)
        img = Image.frombytes(mode, size, data)
        if color_space == "/Indexed":
            from .generic import TextStringObject

            if isinstance(lookup, DecodedStreamObject):
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
                    colors_arr = [
                        lookup[x - nb : x] for x in range(nb, len(lookup), nb)
                    ]
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
                        logger_warning(
                            f"Invalid Lookup Table in {obj_as_text}", __name__
                        )
                        lookup = None
                    if mode == "L":
                        # gray lookup does not work : it is converted to a similar RGB lookup
                        lookup = b"".join([bytes([b, b, b]) for b in lookup])
                        mode = "RGB"
                    # TODO : cf https://github.com/py-pdf/pypdf/pull/2039
                    # this is a work around until PIL is able to process CMYK images
                    elif mode == "CMYK":
                        _rgb = []
                        for _c, _m, _y, _k in (
                            lookup[n : n + 4]
                            for n in range(0, 4 * (len(lookup) // 4), 4)
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
                img = Image.frombytes(
                    mode2, size, data
                )  # reloaded as mode may have change
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
