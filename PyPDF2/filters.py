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


"""Implementation of stream filters for PDF."""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

import math
import struct
from io import StringIO
from typing import Any, Dict, Optional, Tuple, Union

try:
    from typing import Literal  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]

from PyPDF2.constants import CcittFaxDecodeParameters as CCITT
from PyPDF2.constants import ColorSpaces
from PyPDF2.constants import FilterTypeAbbreviations as FTA
from PyPDF2.constants import FilterTypes as FT
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import LzwFilterParameters as LZW
from PyPDF2.constants import StreamAttributes as SA
from PyPDF2.errors import PdfReadError, PdfStreamError
from PyPDF2.utils import ord_, paethPredictor

try:
    import zlib

    def decompress(data: bytes) -> bytes:
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

    def compress(data: bytes) -> bytes:
        return zlib.compress(data)

except ImportError:  # pragma: no cover
    # Unable to import zlib.  Attempt to use the System.IO.Compression
    # library from the .NET framework. (IronPython only)
    import System  # type: ignore[import]
    from System import IO, Array  # type: ignore[import]

    def _string_to_bytearr(buf):  # type: ignore[no-untyped-def]
        retval = Array.CreateInstance(System.Byte, len(buf))
        for i in range(len(buf)):
            retval[i] = ord(buf[i])
        return retval

    def _bytearr_to_string(bytes) -> str:  # type: ignore[no-untyped-def]
        retval = ""
        for i in range(bytes.Length):
            retval += chr(bytes[i])
        return retval

    def _read_bytes(stream):  # type: ignore[no-untyped-def]
        ms = IO.MemoryStream()
        buf = Array.CreateInstance(System.Byte, 2048)
        while True:
            bytes = stream.Read(buf, 0, buf.Length)
            if bytes == 0:
                break
            else:
                ms.Write(buf, 0, bytes)
        retval = ms.ToArray()
        ms.Close()
        return retval

    def decompress(data):  # type: ignore
        bytes = _string_to_bytearr(data)
        ms = IO.MemoryStream()
        ms.Write(bytes, 0, bytes.Length)
        ms.Position = 0  # fseek 0
        gz = IO.Compression.DeflateStream(ms, IO.Compression.CompressionMode.Decompress)
        bytes = _read_bytes(gz)
        retval = _bytearr_to_string(bytes)
        gz.Close()
        return retval

    def compress(data):  # type: ignore
        bytes = _string_to_bytearr(data)
        ms = IO.MemoryStream()
        gz = IO.Compression.DeflateStream(
            ms, IO.Compression.CompressionMode.Compress, True
        )
        gz.Write(bytes, 0, bytes.Length)
        gz.Close()
        ms.Position = 0  # fseek 0
        bytes = ms.ToArray()
        retval = _bytearr_to_string(bytes)
        ms.Close()
        return retval


class FlateDecode:
    @staticmethod
    def decode(data: bytes, decodeParms: Optional[Dict[str, Any]]) -> bytes:
        """
        :param data: flate-encoded data.
        :param decodeParms: a dictionary of values, understanding the
            "/Predictor":<int> key only
        :return: the flate-decoded data.
        """
        str_data = decompress(data)
        predictor = 1

        if decodeParms:
            try:
                from PyPDF2.generic import ArrayObject

                if isinstance(decodeParms, ArrayObject):
                    for decodeParm in decodeParms:
                        if "/Predictor" in decodeParm:
                            predictor = decodeParm["/Predictor"]
                else:
                    predictor = decodeParms.get("/Predictor", 1)
            except AttributeError:
                pass  # Usually an array with a null object was read
        # predictor 1 == no predictor
        if predictor != 1:
            # The /Columns param. has 1 as the default value; see ISO 32000,
            # §7.4.4.3 LZWDecode and FlateDecode Parameters, Table 8
            columns = 1 if decodeParms is None else decodeParms.get(LZW.COLUMNS, 1)

            # PNG prediction:
            if 10 <= predictor <= 15:
                str_data = FlateDecode._decode_png_prediction(str_data, columns)  # type: ignore
            else:
                # unsupported predictor
                raise PdfReadError("Unsupported flatedecode predictor %r" % predictor)
        return str_data  # type: ignore

    @staticmethod
    def _decode_png_prediction(data: str, columns: int) -> str:
        output = StringIO()
        # PNG prediction can vary from row to row
        rowlength = columns + 1
        assert len(data) % rowlength == 0
        prev_rowdata = (0,) * rowlength
        for row in range(len(data) // rowlength):
            rowdata = [
                ord_(x) for x in data[(row * rowlength) : ((row + 1) * rowlength)]
            ]
            filter_byte = rowdata[0]
            if filter_byte == 0:
                pass
            elif filter_byte == 1:
                for i in range(2, rowlength):
                    rowdata[i] = (rowdata[i] + rowdata[i - 1]) % 256
            elif filter_byte == 2:
                for i in range(1, rowlength):
                    rowdata[i] = (rowdata[i] + prev_rowdata[i]) % 256
            elif filter_byte == 3:
                for i in range(1, rowlength):
                    left = rowdata[i - 1] if i > 1 else 0
                    floor = math.floor(left + prev_rowdata[i]) / 2
                    rowdata[i] = (rowdata[i] + int(floor)) % 256
            elif filter_byte == 4:
                for i in range(1, rowlength):
                    left = rowdata[i - 1] if i > 1 else 0
                    up = prev_rowdata[i]
                    up_left = prev_rowdata[i - 1] if i > 1 else 0
                    paeth = paethPredictor(left, up, up_left)
                    rowdata[i] = (rowdata[i] + paeth) % 256
            else:
                # unsupported PNG filter
                raise PdfReadError("Unsupported PNG filter %r" % filter_byte)
            prev_rowdata = tuple(rowdata)
            output.write("".join([chr(x) for x in rowdata[1:]]))
        return output.getvalue()

    @staticmethod
    def encode(data: bytes) -> bytes:
        return compress(data)


class ASCIIHexDecode:
    """
    The ASCIIHexDecode filter decodes data that has been encoded in ASCII
    hexadecimal form into a base-7 ASCII format.
    """

    @staticmethod
    def decode(data: str, decodeParms: Optional[Dict[str, Any]] = None) -> str:
        """
        :param data: a str sequence of hexadecimal-encoded values to be
            converted into a base-7 ASCII string
        :param decodeParms:
        :return: a string conversion in base-7 ASCII, where each of its values
            v is such that 0 <= ord(v) <= 127.
        """
        retval = ""
        hex_pair = ""
        index = 0
        while True:
            if index >= len(data):
                raise PdfStreamError("Unexpected EOD in ASCIIHexDecode")
            char = data[index]
            if char == ">":
                break
            elif char.isspace():
                index += 1
                continue
            hex_pair += char
            if len(hex_pair) == 2:
                retval += chr(int(hex_pair, base=16))
                hex_pair = ""
            index += 1
        assert hex_pair == ""
        return retval


class LZWDecode:
    """Taken from:
    http://www.java2s.com/Open-Source/Java-Document/PDF/PDF-Renderer/com/sun/pdfview/decode/LZWDecode.java.htm
    """

    class decoder:
        def __init__(self, data: bytes) -> None:
            self.STOP = 257
            self.CLEARDICT = 256
            self.data = data
            self.bytepos = 0
            self.bitpos = 0
            self.dict = [""] * 4096
            for i in range(256):
                self.dict[i] = chr(i)
            self.resetDict()

        def resetDict(self) -> None:
            self.dictlen = 258
            self.bitspercode = 9

        def nextCode(self) -> int:
            fillbits = self.bitspercode
            value = 0
            while fillbits > 0:
                if self.bytepos >= len(self.data):
                    return -1
                nextbits = ord_(self.data[self.bytepos])
                bitsfromhere = 8 - self.bitpos
                if bitsfromhere > fillbits:
                    bitsfromhere = fillbits
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

            :rtype: bytes
            """
            cW = self.CLEARDICT
            baos = ""
            while True:
                pW = cW
                cW = self.nextCode()
                if cW == -1:
                    raise PdfReadError("Missed the stop code in LZWDecode!")
                if cW == self.STOP:
                    break
                elif cW == self.CLEARDICT:
                    self.resetDict()
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
    def decode(data: bytes, decodeParms: Optional[Dict[str, Any]] = None) -> str:
        """
        :param data: ``bytes`` or ``str`` text to decode.
        :param decodeParms: a dictionary of parameter values.
        :return: decoded data.
        :rtype: bytes
        """
        return LZWDecode.decoder(data).decode()


class ASCII85Decode:
    """Decodes string ASCII85-encoded data into a byte format."""

    @staticmethod
    def decode(data: bytes, decodeParms: Optional[Dict[str, Any]] = None) -> bytes:
        if isinstance(data, str):
            data = data.encode("ascii")
        group_index = b = 0
        out = bytearray()
        for char in data:
            if ord("!") <= char and char <= ord("u"):
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
    def decode(data: bytes, decodeParms: Optional[Dict[str, Any]] = None) -> bytes:
        return data


class JPXDecode:
    @staticmethod
    def decode(data: bytes, decodeParms: Optional[Dict[str, Any]] = None) -> bytes:
        return data


class CCITParameters:
    """TABLE 3.9 Optional parameters for the CCITTFaxDecode filter"""

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
        parameters: Optional[Dict[str, Any]], rows: int
    ) -> CCITParameters:
        k = 0
        columns = 0
        if parameters:
            from PyPDF2.generic import ArrayObject

            if isinstance(parameters, ArrayObject):
                for decodeParm in parameters:
                    if CCITT.COLUMNS in decodeParm:
                        columns = decodeParm[CCITT.COLUMNS]
                    if CCITT.K in decodeParm:
                        k = decodeParm[CCITT.K]
            else:
                columns = parameters[CCITT.COLUMNS]
                k = parameters[CCITT.K]

        return CCITParameters(k, columns, rows)

    @staticmethod
    def decode(
        data: bytes, decodeParms: Optional[Dict[str, Any]] = None, height: int = 0
    ) -> bytes:
        parms = CCITTFaxDecode._get_parameters(decodeParms, height)

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


def decodeStreamData(stream: Any) -> Union[str, bytes]:  # utils.StreamObject
    from .generic import NameObject

    filters = stream.get(SA.FILTER, ())

    if len(filters) and not isinstance(filters[0], NameObject):
        # we have a single filter instance
        filters = (filters,)
    data: bytes = stream._data
    # If there is not data to decode we should not try to decode the data.
    if data:
        for filterType in filters:
            if filterType == FT.FLATE_DECODE or filterType == FTA.FL:
                data = FlateDecode.decode(data, stream.get(SA.DECODE_PARMS))  # type: ignore
            elif filterType == FT.ASCII_HEX_DECODE or filterType == FTA.AHx:
                data = ASCIIHexDecode.decode(data)  # type: ignore
            elif filterType == FT.LZW_DECODE or filterType == FTA.LZW:
                data = LZWDecode.decode(data, stream.get(SA.DECODE_PARMS))  # type: ignore
            elif filterType == FT.ASCII_85_DECODE or filterType == FTA.A85:
                data = ASCII85Decode.decode(data)
            elif filterType == FT.DCT_DECODE:
                data = DCTDecode.decode(data)
            elif filterType == "/JPXDecode":
                data = JPXDecode.decode(data)
            elif filterType == FT.CCITT_FAX_DECODE:
                height = stream.get(IA.HEIGHT, ())
                data = CCITTFaxDecode.decode(data, stream.get(SA.DECODE_PARMS), height)
            elif filterType == "/Crypt":
                decodeParms = stream.get(SA.DECODE_PARMS, {})
                if "/Name" not in decodeParms and "/Type" not in decodeParms:
                    pass
                else:
                    raise NotImplementedError(
                        "/Crypt filter with /Name or /Type not supported yet"
                    )
            else:
                # Unsupported filter
                raise NotImplementedError("unsupported filter %s" % filterType)
    return data


def _xobj_to_image(x_object_obj: Dict[str, Any]) -> Tuple[Optional[str], bytes]:
    """
    Users need to have the pillow package installed.

    It's unclear if PyPDF2 will keep this function here, hence it's private.
    It might get removed at any point.

    :return: Tuple[file extension, bytes]
    """
    import io

    from PIL import Image

    from PyPDF2.constants import GraphicsStateParameters as G

    size = (x_object_obj[IA.WIDTH], x_object_obj[IA.HEIGHT])
    data = x_object_obj.getData()  # type: ignore
    if x_object_obj[IA.COLOR_SPACE] == ColorSpaces.DEVICE_RGB:
        mode: Literal["RGB", "P"] = "RGB"
    else:
        mode = "P"
    extension = None
    if SA.FILTER in x_object_obj:
        if x_object_obj[SA.FILTER] == FT.FLATE_DECODE:
            extension = ".png"
            img = Image.frombytes(mode, size, data)
            if G.S_MASK in x_object_obj:  # add alpha channel
                alpha = Image.frombytes("L", size, x_object_obj[G.S_MASK].getData())
                img.putalpha(alpha)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            data = img_byte_arr.getvalue()
        elif x_object_obj[SA.FILTER] in (
            [FT.LZW_DECODE],
            [FT.ASCII_85_DECODE],
            [FT.CCITT_FAX_DECODE],
        ):
            from PyPDF2.utils import b_

            extension = ".png"
            data = b_(data)
        elif x_object_obj[SA.FILTER] == FT.DCT_DECODE:
            extension = ".jpg"
        elif x_object_obj[SA.FILTER] == "/JPXDecode":
            extension = ".jp2"
        elif x_object_obj[SA.FILTER] == FT.CCITT_FAX_DECODE:
            extension = ".tiff"
    else:
        extension = ".png"
        img = Image.frombytes(mode, size, data)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        data = img_byte_arr.getvalue()

    return extension, data
