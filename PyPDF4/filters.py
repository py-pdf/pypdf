# -*- coding: UTF-8 -*-
# vim: sw=4:expandtab:foldmethod=marker
#
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
"""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

import math
import struct
from sys import version_info

from .utils import PdfReadError, pypdfOrd, paethPredictor, PdfStreamError

if version_info < (3, 0):
    from cStringIO import StringIO
else:
    from io import StringIO

try:
    import zlib

    def decompress(data):
        return zlib.decompress(data)

    def compress(data):
        return zlib.compress(data)
except ImportError:
    # Unable to import zlib.  Attempt to use the System.IO.Compression
    # library from the .NET framework. (IronPython only)
    import System
    from System import IO, Array

    def _string_to_bytearr(buf):
        retval = Array.CreateInstance(System.Byte, len(buf))

        for i in range(len(buf)):    # pylint: disable=consider-using-enumerate
            retval[i] = ord(buf[i])

        return retval

    def _bytearr_to_string(these_bytes):
        retval = ""

        for i in range(these_bytes.Length):
            retval += chr(these_bytes[i])

        return retval

    def _read_bytes(stream):
        ms = IO.MemoryStream()
        buf = Array.CreateInstance(System.Byte, 2048)

        while True:
            these_bytes = stream.Read(buf, 0, buf.Length)

            if these_bytes == 0:
                break
            else:
                ms.Write(buf, 0, these_bytes)

        retval = ms.ToArray()
        ms.Close()

        return retval

    def decompress(data):
        these_bytes = _string_to_bytearr(data)
        ms = IO.MemoryStream()
        ms.Write(bytes, 0, these_bytes.Length)
        ms.Position = 0  # fseek 0
        gz = IO.Compression.DeflateStream(
            ms, IO.Compression.CompressionMode.Decompress
        )
        these_bytes = _read_bytes(gz)
        retval = _bytearr_to_string(these_bytes)
        gz.Close()
        return retval

    def compress(data):
        these_bytes = _string_to_bytearr(data)
        ms = IO.MemoryStream()
        gz = IO.Compression.DeflateStream(
            ms, IO.Compression.CompressionMode.Compress, True
        )
        gz.Write(these_bytes, 0, these_bytes.Length)
        gz.Close()
        ms.Position = 0  # fseek 0
        these_bytes = ms.ToArray()
        retval = _bytearr_to_string(these_bytes)
        ms.Close()
        return retval


class FlateDecode(object):
    @staticmethod
    def decode(data, decodeParms):    # pylint: disable=too-many-locals, too-many-branches
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
                predictor = decodeParms.get("/Predictor", 1)
            except AttributeError:
                pass    # Usually an array with a null object was read

        # predictor 1 == no predictor
        if predictor != 1:
            # The /Columns param. has 1 as the default value; see ISO 32000,
            # §7.4.4.3 LZWDecode and FlateDecode Parameters, Table 8
            columns = decodeParms.get("/Columns", 1)

            # PNG prediction:
            if 10 <= predictor <= 15:
                output = StringIO()
                # PNG prediction can vary from row to row
                row_length = columns + 1
                assert len(data) % row_length == 0
                prev_rowdata = (0, ) * row_length

                for row in range(len(data) // row_length):
                    rowdata = [
                        pypdfOrd(x) for x in
                        data[(row*row_length):((row+1)*row_length)]
                    ]
                    filterByte = rowdata[0]

                    if filterByte == 0:
                        pass
                    elif filterByte == 1:
                        for i in range(2, row_length):
                            rowdata[i] = (rowdata[i] + rowdata[i-1]) % 256
                    elif filterByte == 2:
                        for i in range(1, row_length):
                            rowdata[i] = (rowdata[i] + prev_rowdata[i]) % 256
                    elif filterByte == 3:
                        for i in range(1, row_length):
                            left = rowdata[i - 1] if i > 1 else 0
                            floor = math.floor(left + prev_rowdata[i])/2
                            rowdata[i] = (rowdata[i] + int(floor)) % 256
                    elif filterByte == 4:
                        for i in range(1, row_length):
                            left = rowdata[i - 1] if i > 1 else 0
                            up = prev_rowdata[i]
                            up_left = prev_rowdata[i - 1] if i > 1 else 0
                            paeth = paethPredictor(left, up, up_left)
                            rowdata[i] = (rowdata[i] + paeth) % 256
                    else:
                        # Unsupported PNG filter
                        raise PdfReadError(
                            "Unsupported PNG filter %r" % filterByte
                        )
                    prev_rowdata = rowdata
                    output.write(''.join([chr(x) for x in rowdata[1:]]))

                data = output.getvalue()
            else:
                # unsupported predictor
                raise PdfReadError(
                    "Unsupported flatedecode predictor %r" % predictor
                )

        return data

    @staticmethod
    def encode(data):
        return compress(data)


class ASCIIHexDecode(object):
    """
        The ASCIIHexDecode filter decodes data that has been encoded in ASCII
        hexadecimal form into a base-7 ASCII format.
    """
    @staticmethod
    def decode(data, decode_parms=None):
        """
        :param data: a str sequence of hexadecimal-encoded values to be
            converted into a base-7 ASCII string
        :return: a string conversion in base-7 ASCII, where each of its values
            v is such that 0 <= ord(v) <= 127.
        """
        retval = ""
        hex_pair = ""
        eod_found = False

        for c in data:
            if c == ">":
                # If the filter encounters the EOD marker after reading an odd
                # number of hexadecimal digits, it shall behave as if a 0
                # (zero) followed the last digit - from ISO 32000 specification
                if len(hex_pair) == 1:
                    hex_pair += "0"
                    retval += chr(int(hex_pair, base=16))
                    hex_pair = ""

                eod_found = True
                break
            elif c.isspace():
                continue

            hex_pair += c

            if len(hex_pair) == 2:
                retval += chr(int(hex_pair, base=16))
                hex_pair = ""

        if not eod_found:
            raise PdfStreamError("Ending character '>' not found in stream")

        assert hex_pair == ""

        return retval

    def encode(self):
        pass


# pylint: disable=too-few-public-methods
class LZWDecode(object):
    """
    For a reference of the LZW algorithm consult ISO 32000, section 7.4.4 or
    Section 13 of "TIFF 6.0 Specification" for a more detailed discussion.
    """
    class Encoder(object):
        """
        LZWDecode.Encoder is primarily employed for testing purposes and its
        implementation doesn't (yet) cover all the little facets present in
        the ISO standard.
        """
        MAX_ENTRIES = 2 ** 12

        def __init__(self, data):
            """
            :param data: a str or byte string to encode with LZW.
            """
            self.data = data
            self.bitspercode = None
            # self.table maps buffer values to their progressive indices
            self.table = None
            # self.result stores the contiguous stream of bits in form of ints
            self.result = None
            # The location of the next bit we are going to write to
            self.bitpos = 0

            self.resetTable()

        def resetTable(self):
            """
            Brings the pattern-to-code-value table to default values.
            """
            self.bitspercode = 9

            self.table = {
                chr(n): n for n in range(256)
            }
            self.table[256] = len(self.table)
            self.table[257] = len(self.table)

        def encode(self):
            """
            Encodes the data passed in to __init__() according to the LZW
            specification.
            """
            self.result = list()
            buffer = str()
            self._writeCode(self.table[256])

            for c in self.data:
                if buffer + c in self.table.keys():
                    buffer += c
                else:
                    # Write the code of buffer to the codetext
                    self._writeCode(self.table[buffer])
                    self._addCodeToTable(buffer + c)

                    buffer = c

            self._writeCode(self.table[buffer])
            self._writeCode(self.table[257])

            # This results in an automatic assertion of the values of
            # self.result, since for each v one of them, 0 <= v <= 255
            return bytearray(self.result)

        def _writeCode(self, code):
            """
            Tricky implementation method that serves in the conversion from
            usually higher-than-eight-bit values (input in code as
            integers) to a stream of bits. The serialization is performed by
            writing into a list of integer values.

            :param code: an integer value whose bit stream will be serialized
                inside self.result.
            """
            bytesAlloc = int(
                math.ceil(float(self.bitpos + self.bitspercode) / 8)
            ) - len(self.result)
            self.result.extend([0] * bytesAlloc)
            bitsWritten = 0
            relbitpos = self.bitpos % 8
            bytepos = int(math.floor(self.bitpos / 8))

            while (self.bitspercode - bitsWritten) > 0:
                self.result[bytepos] |= (
                    ((code << bitsWritten) >> (self.bitspercode - 8)) & 0xFF
                ) >> relbitpos

                bitsWritten += min(
                    8 - relbitpos, self.bitspercode - bitsWritten
                )
                relbitpos = (self.bitpos + bitsWritten) % 8
                bytepos = int(math.floor((self.bitpos + bitsWritten) / 8))

            self.bitpos += self.bitspercode

        def _addCodeToTable(self, value):
            if len(self.table) > (2 ** self.bitspercode) - 1:
                self.bitspercode += 1
            elif len(self.table) > LZWDecode.Encoder.MAX_ENTRIES:
                self.resetTable()
                self._writeCode(256)

            self.table[value] = len(self.table)

    # pylint: disable=too-many-instance-attributes
    class Decoder(object):
        """
        Decodes a stream of data encoded according to LZW.
        """
        def __init__(self, data):
            """
            :param data: a string or byte string.
            """
            self.STOP = 257
            self.CLEARDICT = 256
            self.data = data
            self.bytepos = 0
            self.bitpos = 0
            self.dict = [""] * 4096

            for i in range(256):
                self.dict[i] = chr(i)

            self.resetDict()

        def resetDict(self):
            self.dictlen = 258
            self.bitspercode = 9

        def nextCode(self):
            fillbits = self.bitspercode
            value = 0

            while fillbits > 0:
                if self.bytepos >= len(self.data):
                    return -1

                nextbits = pypdfOrd(self.data[self.bytepos])
                bitsfromhere = 8 - self.bitpos

                if bitsfromhere > fillbits:
                    bitsfromhere = fillbits

                value |= (
                        ((nextbits >> (8 - self.bitpos - bitsfromhere)) &
                         (0xff >> (8 - bitsfromhere))) <<
                        (fillbits - bitsfromhere)
                )
                fillbits -= bitsfromhere
                self.bitpos += bitsfromhere

                if self.bitpos >= 8:
                    self.bitpos = 0
                    self.bytepos = self.bytepos + 1

            return value

        def decode(self):
            """
            TIFF 6.0 specification explains in sufficient details the steps
            to implement the LZW encode() and decode() algorithms.
            """
            cW = self.CLEARDICT
            baos = ""

            while True:
                pW = cW
                cW = self.nextCode()

                if cW == -1:
                    raise PdfReadError("Missed the stop code in LZWDecode")
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
                    if (self.dictlen >= (1 << self.bitspercode) - 1 and
                            self.bitspercode < 12):
                        self.bitspercode += 1

            return baos

    @staticmethod
    def encode(data, decodeParms=None):
        return LZWDecode.Encoder(data).encode()

    @staticmethod
    def decode(data, decode_params=None):
        return LZWDecode.Decoder(data).decode()


# pylint: disable=too-few-public-methods
class ASCII85Decode(object):
    """
    Decodes string ASCII85-encoded data into a byte format.
    """
    # pylint: disable=too-many-branches, too-many-statements, too-many-locals
    @staticmethod
    def encode(data, decode_parms=None):
        """
        Encodes chunks of 4-byte sequences of textual or bytes data according
        to the base-85 ASCII encoding algorithm.

        :param data: a str or byte sequence of values.
        :return: ASCII85-encoded data in bytes format (equal to str in Python
            2).
        """
        result = str()
        filler = "\x00" if type(data) is str else b"\x00"

        if type(data) not in (str, bytes):
            raise TypeError(
                "Expected str or bytes type for data, got %s instead" %
                type(data)
            )

        for group in range(int(math.ceil(len(data) / 4.0))):
            decimalRepr = 0
            ascii85 = str()
            groupWidth = min(4, len(data) - 4 * group)

            if groupWidth < 4:
                data = data + (4 - groupWidth) * filler

            for byte in range(4):
                decimalRepr +=\
                    pypdfOrd(data[4 * group + byte]) << 8 * (4 - byte - 1)

            # If all bytes are 0, we turn them into a single 'z' character
            if decimalRepr == 0 and groupWidth == 4:
                ascii85 = "z"
            else:
                for i in range(5):
                    ascii85 = chr(decimalRepr % 85 + 33) + ascii85
                    decimalRepr = int(decimalRepr / 85.0)

            # In case of a partial group of four bytes, the standard says:
            # «Finally, it shall write only the first n + 1 characters of the
            # resulting group of 5.» - ISO 32000 (2008), sec. 7.4.3
            result += ascii85[:min(5, groupWidth + 1)]

        return (result + "~>").encode("LATIN1")

    @staticmethod
    def decode(data, decode_parms=None):
        """
        Decodes binary (bytes or str) data previously encoded in ASCII85.

        :param data: a str or bytes sequence of ASCII85-encoded characters.
        :return: bytes for Python 3, str for Python 2.

        TO-DO Add check for missing '~>' EOD marker.
        """
        group_index = b = 0
        out = bytearray()

        if isinstance(data, bytes):
            data = data.decode("LATIN1")
        elif not isinstance(data, str):
            raise TypeError(
                "data is of %s type, expected str or bytes" %
                data.__class__.__name__
            )

        for index, c in enumerate(data):
            byte = ord(c)

            # 33 == ord('!') and 117 == ord('u')
            if 33 <= byte <= 117:
                group_index += 1
                b = b * 85 + (byte - 33)

                if group_index == 5:
                    out += struct.pack(b'>L', b)
                    group_index = b = 0
            # 122 == ord('z')
            elif byte == 122:
                assert group_index == 0
                out.extend(b"\x00\x00\x00\x00")
            # 126 == ord('~') and 62 == ord('>')
            elif byte == 126 and data[index + 1] == '>':
                if group_index:
                    for _ in range(5 - group_index):
                        b = b * 85 + 84
                    out += struct.pack(b'>L', b)[:group_index - 1]

                break
            else:
                raise ValueError("Value '%c' not recognized" % c)

        return bytes(out)


# pylint: disable=too-few-public-methods
class DCTDecode(object):
    @staticmethod
    def decode(data, decode_params=None):
        """
        TO-DO Implement this filter.
        """
        return data


class JPXDecode(object):    # pylint: disable=too-few-public-methods
    @staticmethod
    def decode(data, decode_parms=None):
        """
        TO-DO Implement this filter.
        """
        return data


class CCITTFaxDecode(object):    # pylint: disable=too-few-public-methods
    @staticmethod
    def decode(data, decode_parms=None, height=0):
        if decode_parms:
            if decode_parms.get("/K", 1) == -1:
                CCITTgroup = 4
            else:
                CCITTgroup = 3

        width = decode_parms["/Columns"]
        imgSize = len(data)
        tiffHeaderStruct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
        tiffHeader = struct.pack(
            tiffHeaderStruct,
            b'II',  # Byte order indication: Little endian
            42,  # Version number (always 42)
            8,  # Offset to first IFD
            8,  # Number of tags in IFD
            256, 4, 1, width,  # ImageWidth, LONG, 1, width
            257, 4, 1, height,  # ImageLength, LONG, 1, length
            258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
            # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
            259, 3, 1, CCITTgroup,
            262, 3, 1, 0,  # Thresholding, SHORT, 1, 0 = WhiteIsZero
            # StripOffsets, LONG, 1, length of header
            273, 4, 1, struct.calcsize(tiffHeaderStruct),
            278, 4, 1, height,  # RowsPerStrip, LONG, 1, length
            279, 4, 1, imgSize,  # StripByteCounts, LONG, 1, size of image
            0  # last IFD
        )

        # TO-DO Finish implementing (the code above only adds header infos.)

        return tiffHeader + data


# pylint: disable=too-many-branches
def decodeStreamData(stream):
    from .generic import NameObject
    filters = stream.get("/Filter", ())

    if filters and not isinstance(filters[0], NameObject):
        # we have a single filter instance
        filters = (filters,)

    data = stream._data

    # If there is not data to decode we should not try to decode the data.
    if data:
        for filterType in filters:
            if filterType in ["/FlateDecode", "/Fl"]:
                data = FlateDecode.decode(data, stream.get("/DecodeParms"))
            elif filterType in ["/ASCIIHexDecode", "/AHx"]:
                data = ASCIIHexDecode.decode(data)
            elif filterType in ["/LZWDecode", "/LZW"]:
                data = LZWDecode.decode(data, stream.get("/DecodeParms"))
            elif filterType in ["/ASCII85Decode", "/A85"]:
                data = ASCII85Decode.decode(data)
            elif filterType == "/DCTDecode":
                data = DCTDecode.decode(data)
            elif filterType == "/JPXDecode":
                data = JPXDecode.decode(data)
            elif filterType == "/CCITTFaxDecode":
                height = stream.get("/Height", ())
                data = CCITTFaxDecode.decode(
                    data, stream.get("/DecodeParms"), height
                )
            elif filterType == "/Crypt":
                decodeParams = stream.get("/DecodeParams", {})

                if "/Name" not in decodeParams and "/Type" not in decodeParams:
                    pass
                else:
                    raise NotImplementedError(
                        "/Crypt filter with /Name or /Type not supported yet"
                    )
            else:
                # unsupported filter
                raise NotImplementedError("unsupported filter %s" % filterType)

    return data
