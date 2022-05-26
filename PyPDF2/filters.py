# -*- coding: utf-8 -*-
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
import warnings
from sys import version_info

from PyPDF2._utils import DEPR_MSG, ord_, paeth_predictor
from PyPDF2.constants import CcittFaxDecodeParameters as CCITT
from PyPDF2.constants import ColorSpaces
from PyPDF2.constants import FilterTypeAbbreviations as FTA
from PyPDF2.constants import FilterTypes as FT
from PyPDF2.constants import ImageAttributes as IA
from PyPDF2.constants import LzwFilterParameters as LZW
from PyPDF2.constants import StreamAttributes as SA
from PyPDF2.errors import PdfReadError, PdfStreamError

if version_info < (3, 0):
    from cStringIO import StringIO
else:
    from io import StringIO

import struct
import zlib


def decompress(data):
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


def compress(data):
    return zlib.compress(data)


class FlateDecode(object):
    @staticmethod
    def decode(data, decodeParms):
        """
        :param data: flate-encoded data.
        :param decodeParms: a dictionary of values, understanding the
            "/Predictor":<int> key only
        :return: the flate-decoded data.
        """
        data = decompress(data)
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
            columns = decodeParms.get(LZW.COLUMNS, 1)

            # PNG prediction:
            if 10 <= predictor <= 15:
                data = FlateDecode._decode_png_prediction(data, columns)
            else:
                # unsupported predictor
                raise PdfReadError("Unsupported flatedecode predictor %r" % predictor)
        return data

    @staticmethod
    def _decode_png_prediction(data, columns):
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
                    paeth = paeth_predictor(left, up, up_left)
                    rowdata[i] = (rowdata[i] + paeth) % 256
            else:
                # unsupported PNG filter
                raise PdfReadError("Unsupported PNG filter %r" % filter_byte)
            prev_rowdata = rowdata
            output.write("".join([chr(x) for x in rowdata[1:]]))
        return output.getvalue()

    @staticmethod
    def encode(data):
        return compress(data)


class ASCIIHexDecode(object):
    """
    The ASCIIHexDecode filter decodes data that has been encoded in ASCII
    hexadecimal form into a base-7 ASCII format.
    """

    @staticmethod
    def decode(data, decodeParms=None):
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


class LZWDecode(object):
    """Taken from:
    http://www.java2s.com/Open-Source/Java-Document/PDF/PDF-Renderer/com/sun/pdfview/decode/LZWDecode.java.htm
    """

    class Decoder(object):
        def __init__(self, data):
            self.STOP = 257
            self.CLEARDICT = 256
            self.data = data
            self.bytepos = 0
            self.bitpos = 0
            self.dict = [""] * 4096
            for i in range(256):
                self.dict[i] = chr(i)
            self.reset_dict()

        def reset_dict(self):
            self.dictlen = 258
            self.bitspercode = 9

        def next_code(self):
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

        def decode(self):
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
    def decode(data, decodeParms=None):
        """
        :param data: ``bytes`` or ``str`` text to decode.
        :param decodeParms: a dictionary of parameter values.
        :return: decoded data.
        :rtype: bytes
        """
        return LZWDecode.Decoder(data).decode()


class ASCII85Decode(object):
    """Decodes string ASCII85-encoded data into a byte format."""

    @staticmethod
    def decode(data, decodeParms=None):
        if version_info < (3, 0):
            retval = ""
            group = []
            index = 0
            hit_eod = False
            # remove all whitespace from data
            data = [y for y in data if y not in " \n\r\t"]
            while not hit_eod:
                char = data[index]
                if len(retval) == 0 and char == "<" and data[index + 1] == "~":
                    index += 2
                    continue
                # elif c.isspace():
                #    index += 1
                #    continue
                elif char == "z":
                    assert len(group) == 0
                    retval += "\x00\x00\x00\x00"
                    index += 1
                    continue
                elif char == "~" and data[index + 1] == ">":
                    if len(group) != 0:
                        # cannot have a final group of just 1 char
                        assert len(group) > 1
                        cnt = len(group) - 1
                        group += [85, 85, 85]
                        hit_eod = cnt
                    else:
                        break
                else:
                    char = ord(char) - 33
                    assert char >= 0 and char < 85
                    group += [char]
                if len(group) >= 5:
                    b = (
                        group[0] * (85**4)
                        + group[1] * (85**3)
                        + group[2] * (85**2)
                        + group[3] * 85
                        + group[4]
                    )
                    if b > (2**32 - 1):
                        raise OverflowError(
                            "The sum of a ASCII85-encoded 4-byte group shall "
                            "not exceed 2 ^ 32 - 1. See ISO 32000, 2008, 7.4.3"
                        )
                    assert b <= (2**32 - 1)
                    c4 = chr((b >> 0) % 256)
                    c3 = chr((b >> 8) % 256)
                    c2 = chr((b >> 16) % 256)
                    c1 = chr(b >> 24)
                    retval += c1 + c2 + c3 + c4
                    if hit_eod:
                        retval = retval[: -4 + hit_eod]
                    group = []
                index += 1
            return retval
        else:
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


class DCTDecode(object):
    @staticmethod
    def decode(data, decodeParms=None):
        return data


class JPXDecode(object):
    @staticmethod
    def decode(data, decodeParms=None):
        return data


class CCITParameters(object):
    """TABLE 3.9 Optional parameters for the CCITTFaxDecode filter"""

    def __init__(self, K=0, columns=0, rows=0):
        self.K = K
        self.EndOfBlock = None
        self.EndOfLine = None
        self.EncodedByteAlign = None
        self.columns = columns  # width
        self.rows = rows  # height
        self.DamagedRowsBeforeError = None

    @property
    def group(self):
        if self.K < 0:
            CCITTgroup = 4
        else:
            # k == 0: Pure one-dimensional encoding (Group 3, 1-D)
            # k > 0: Mixed one- and two-dimensional encoding (Group 3, 2-D)
            CCITTgroup = 3
        return CCITTgroup


class CCITTFaxDecode(object):
    """
    See 3.3.5 CCITTFaxDecode Filter (PDF 1.7 Standard).

    Either Group 3 or Group 4 CCITT facsimile (fax) encoding.
    CCITT encoding is bit-oriented, not byte-oriented.

    See: TABLE 3.9 Optional parameters for the CCITTFaxDecode filter
    """

    @staticmethod
    def _get_parameters(parameters, rows):
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
    def decode(data, decodeParms=None, height=0):
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


def decode_stream_data(stream):
    from .generic import NameObject

    filters = stream.get(SA.FILTER, ())

    if len(filters) and not isinstance(filters[0], NameObject):
        # we have a single filter instance
        filters = (filters,)
    data = stream._data
    # If there is not data to decode we should not try to decode the data.
    if data:
        for filterType in filters:
            if filterType == FT.FLATE_DECODE or filterType == FTA.FL:
                data = FlateDecode.decode(data, stream.get(SA.DECODE_PARMS))
            elif filterType == FT.ASCII_HEX_DECODE or filterType == FTA.AHx:
                data = ASCIIHexDecode.decode(data)
            elif filterType == FT.LZW_DECODE or filterType == FTA.LZW:
                data = LZWDecode.decode(data, stream.get(SA.DECODE_PARMS))
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


def decodeStreamData(stream):
    warnings.warn(
        DEPR_MSG.format("decodeStreamData", "decode_stream_data"),
        PendingDeprecationWarning,
        stacklevel=2,
    )
    return decode_stream_data(stream)


def _xobj_to_image(x_object_obj):
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
    data = x_object_obj.get_data()
    if x_object_obj[IA.COLOR_SPACE] == ColorSpaces.DEVICE_RGB:
        mode = "RGB"
    else:
        mode = "P"
    extension = None
    if SA.FILTER in x_object_obj:
        if x_object_obj[SA.FILTER] == FT.FLATE_DECODE:
            extension = ".png"
            img = Image.frombytes(mode, size, data)
            if G.S_MASK in x_object_obj:  # add alpha channel
                alpha = Image.frombytes("L", size, x_object_obj[G.S_MASK].get_data())
                img.putalpha(alpha)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            data = img_byte_arr.getvalue()
        elif x_object_obj[SA.FILTER] in (
            [FT.LZW_DECODE],
            [FT.ASCII_85_DECODE],
            [FT.CCITT_FAX_DECODE],
        ):
            from PyPDF2._utils import b_

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
