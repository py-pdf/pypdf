# Original Copyright (c) 2006, Mathieu Fenniak
# Modified by Chris Johnson and others
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
from io import BytesIO
from sys import version_info
import zlib

from .constants import CcittFaxDecodeParameters as CCITT
from .constants import ColorSpaces
from .constants import FilterTypeAbbreviations as FTA
from .constants import FilterTypes as FT
from .constants import ImageAttributes as IA
from .constants import LzwFilterParameters as LZW
from .constants import StreamAttributes as SA
from .errors import PdfReadError


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
    """zipped object with optional png pre-compression"""
    
    @staticmethod
    def decode(data, decodeParms):
        """
        :param data: flate-encoded data.
        :param decodeParms: a dictionary of values, understanding the
            "/Predictor":<int> key only
        :return: the flate-decoded data.
        """
        data = decompress(data)
        if decodeParms is None:
            return data

        # apply additional (probably PNG based) decoding
        try:
            predictor = decodeParms.get("/Predictor", 1)
        except AttributeError:
            # no predictor - usually an array with a null object was read
            predictor = 1

        if predictor == 1:
            return data

        if predictor >= 10 and predictor <= 15:
            # PNG prediction.  Can vary from row to row and each row
            # starts with a one byte indicator followed by n bytes of
            # picture elements (not necessarily one for RGB)

            columns = decodeParms.get("/Columns")
            bpc = decodeParms.get("/BitsPerComponent")
            colors = decodeParms.get("/Colors")
            try:
                rowlength = (
                    int(bpc * colors * columns / 8) + 1
                    if bpc is not None
                    else columns + 1
                )
            except Exception:
                # error here is the  result of a badly formed stream or
                # previous parser error
                print("FlateDecode error in decode parms handling ")
                raise

            assert len(data) % rowlength == 0

            output = BytesIO()
            prev_rowdata = bytes(rowlength)
            for row in range(len(data) // rowlength):

                rowdata = bytearray(data[(row * rowlength) : ((row + 1) * rowlength)])

                filterByte = rowdata[0]
                if filterByte == 0:
                    pass
                elif filterByte == 1:
                    for i in range(2, rowlength):
                        rowdata[i] = (rowdata[i] + rowdata[i - 1]) % 256
                elif filterByte == 2:
                    for i in range(1, rowlength):
                        rowdata[i] = (rowdata[i] + prev_rowdata[i]) % 256
                elif filterByte == 3:
                    for i in range(1, rowlength):
                        left = rowdata[i - 1] if i > 1 else 0
                        floor = math.floor(left + prev_rowdata[i]) / 2
                        rowdata[i] = (rowdata[i] + int(floor)) % 256
                elif filterByte == 4:
                    for i in range(1, rowlength):
                        left = rowdata[i - 1] if i > 1 else 0
                        up = prev_rowdata[i]
                        up_left = prev_rowdata[i - 1] if i > 1 else 0
                        paeth = paethPredictor(left, up, up_left)
                        rowdata[i] = (rowdata[i] + paeth) % 256
                else:
                    # unsupported PNG filter
                    raise PdfReadError("Unsupported PNG filter %r" % filterByte)
                prev_rowdata = rowdata
                output.write(rowdata[1:])

            data = output.getvalue()
        else:
            # unsupported predictor
            raise PdfReadError("Unsupported flatedecode predictor %r" % predictor)
        return data


    @staticmethod
    def encode(data):
        return compress(data)


class ASCIIHexDecode(object):
    # this does not work in Python 3
    #
    def decode(data, decodeParms=None):
        retval = ""
        char = ""
        x = 0
        while True:
            c = data[x]
            if c == ">":
                break
            elif c.isspace():
                x += 1
                continue
            char += c
            if len(char) == 2:
                retval += chr(int(char, base=16))
                char = ""
            x += 1
        assert char == ""
        return retval

    decode = staticmethod(decode)

    def encode(data):
        return compress(data)

    encode = staticmethod(encode)


class LZWDecode(object):
    """Taken from:
    http://www.java2s.com/Open-Source/Java-Document/PDF/PDF-Renderer/com/sun/pdfview/decode/LZWDecode.java.htm
    """

    class decoder(object):
        def __init__(self, data):
            self.STOP = 257
            self.CLEARDICT = 256
            self.data = data
            self.bytepos = 0
            self.bitpos = 0
            self.dict = [bytes([i]) if i < 256 else b"" for i in range(4096)]
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

                nextbits = self.data[self.bytepos]
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
            http://www.rasip.fer.hr/research/compress/algorithms/fund/lz/lzw.html
            and the PDFReference

            :rtype: bytes
            """
            cW = self.CLEARDICT
            baos = b""  # output is bytestring for Python 3
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
                        p = self.dict[pW] + self.dict[cW][:1]
                        self.dict[self.dictlen] = p
                        self.dictlen += 1
                    else:
                        p = self.dict[pW] + self.dict[pW][:1]
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
        return LZWDecode.decoder(data).decode()


class ASCII85Decode(object):
    """Decodes string ASCII85-encoded data into a byte format.
       Python 3 standard library can be used here
    """

    @staticmethod
    def decode(data, decodeParms=None):
        if version_info < (3, 0):
            retval = ""
            group = []
            x = 0
            hit_eod = False
            # remove all whitespace from data
            data = [y for y in data if y not in " \n\r\t"]
            while not hit_eod:
                c = data[x]
                if len(retval) == 0 and c == "<" and data[x + 1] == "~":
                    x += 2
                    continue
                # elif c.isspace():
                #    x += 1
                #    continue
                elif c == b"z":
                    assert len(group) == 0
                    retval += "\x00\x00\x00\x00"
                    x += 1
                    continue
                elif c == b"~" and data[x + 1] == b">":
                    if len(group) != 0:
                        # cannot have a final group of just 1 char
                        assert len(group) > 1
                        cnt = len(group) - 1
                        group += [85, 85, 85]
                        hit_eod = cnt
                    else:
                        break
                else:
                    c = ord(c) - 33
                    assert c >= 0 and c < 85
                    group += [c]
                if len(group) >= 5:
                    b = (
                        group[0] * (85**4)
                        + group[1] * (85**3)
                        + group[2] * (85**2)
                        + group[3] * 85
                        + group[4]
                    )
                    assert b < (2**32 - 1)
                    c4 = chr((b >> 0) % 256)
                    c3 = chr((b >> 8) % 256)
                    c2 = chr((b >> 16) % 256)
                    c1 = chr(b >> 24)
                    retval += c1 + c2 + c3 + c4
                    if hit_eod:
                        retval = retval[: -4 + hit_eod]
                    group = []
                x += 1
            return retval
        else:
            if isinstance(data, str):
                data = data.encode("ascii")
            n = b = 0
            out = bytearray()
            for c in data:
                if ord("!") <= c and c <= ord("u"):
                    n += 1
                    b = b * 85 + (c - 33)
                    if n == 5:
                        out += struct.pack(b">L", b)
                        n = b = 0
                elif c == ord("z"):
                    assert n == 0
                    out += b"\0\0\0\0"
                elif c == ord("~"):
                    if n:
                        for _ in range(5 - n):
                            b = b * 85 + 84
                        out += struct.pack(b">L", b)[: n - 1]
                    break
            return bytes(out)

    decode = staticmethod(decode)


class DCTDecode(object):
    @staticmethod
    def decode(data, decodeParms=None):
        return data


class JPXDecode(object):
    @staticmethod
    def decode(data, decodeParms=None):
        return data


class CCITTFaxDecode(object):
    @staticmethod
    def decode(data, decodeParms=None, height=0):
        if decodeParms:
            if decodeParms.get("/K", 1) == -1:
                CCITTgroup = 4
            else:
                CCITTgroup = 3

        width = decodeParms["/Columns"]
        imgSize = len(data)
        tiff_header_struct = "<" + "2s" + "h" + "l" + "h" + "hhll" * 8 + "h"
        tiffHeader = struct.pack(
            tiff_header_struct,
            b"II",  # Byte order indication: Little endian
            42,  # Version number (always 42)
            8,  # Offset to first IFD
            8,  # Number of tags in IFD
            256,
            4,
            1,
            width,  # ImageWidth, LONG, 1, width
            257,
            4,
            1,
            height,  # ImageLength, LONG, 1, length
            258,
            3,
            1,
            1,  # BitsPerSample, SHORT, 1, 1
            259,
            3,
            1,
            CCITTgroup,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
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
            height,  # RowsPerStrip, LONG, 1, length
            279,
            4,
            1,
            imgSize,  # StripByteCounts, LONG, 1, size of image
            0,  # last IFD
        )

        return tiffHeader + data


def decodeStreamData(stream):
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
                # unsupported filter
                raise NotImplementedError("unsupported filter %s" % filterType)
    return data


# change the transitions to character string
#
class Fax(object):

    # class constants     # type(self).tableV
    tableV = [(None, None, None) for i in range(8192)]
    tableW = [(None, None, None) for i in range(8192)]
    tableB = [(None, None, None) for i in range(8192)]

    modeU = "U"  # uncompressed
    modeV = "V"  # 2D mode
    modeBlack = "B"
    modeWhite = "W"
    modeFinished = "Z"

    def initialize(self, cols, rows, stripsize):
        self.Result = b""
        self.linect = 0

        self.bitpos = 0
        self.bytepos = 0
        # bitmap lines and columns
        self.Columns = cols
        self.Rows = rows
        self.K = stripsize
        # current and reference line transitions (positions of each w,b,w,b run
        self.Result = b""
        self.currentPos = 0
        self.cT = [None for j in range(self.Columns + 1)]
        self.cTP = 0
        self.cT[0] = 0
        self.rT = [None for i in range(self.Columns)]
        self.rT[0] = 0
        self.rTP = 0  # spec suggests that this should be -1 but I think first white run starts with first pel
        self.currentMode = None
        self.startingMode = None

    def decode(self, stream, DecodeParms):

        print("fax decode:stream length {} parms {}".format(len(stream), DecodeParms))
        self.initialize(
            DecodeParms["/Columns"], DecodeParms["/Rows"], DecodeParms["/K"]
        )
        if self.K >= 0:
            print("Cannot handle G3 compression yet")
            return
        self.Process(stream)
        return self.Result

    def __init__(self):
        # print("Initializing instance and class variables" )
        self.currentMode = None
        self.startingMode = None
        self.Result = b""
        self.bitpos = 0
        self.bytepos = 0
        self.LoadTables(type(self).tableV, type(self).tableB, type(self).tableW)

    def getbits(self, data, fillbits):
        value = 0
        while fillbits > 0:
            nextbits = data[self.bytepos]
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

    def flush_line(self):
        pixW = b"\xff\xff\xff"
        pixB = b"\x00\x00\x00"
        Ssave = self.cT[self.cTP]
        self.cT[self.cTP] = self.Columns
        linedata = b"".join(
            [
                [pixB, pixW][i % 2] * (self.cT[i] - self.cT[i - 1])
                for i in range(1, self.cTP + 1)
            ]
        )
        self.Result += linedata
        self.linect += 1
        self.cT[self.cTP] = Ssave

        self.rT = list(self.cT)
        for i in range(self.cTP, len(self.cT)):
            self.rT[i] = None
        self.rTP = 0
        self.cTP = 0
        self.currentPos = 0

    def switch_uncompressed(self, p):
        print("uncompressed mode", end=" ")
        pass

    def copy_down(self, p):

        while True:
            if self.rT[self.rTP] is None:
                break
            if self.rT[self.rTP] >= self.currentPos:
                break
            self.rTP += 2

        if self.rT[self.rTP] is None:
            self.flush_line()

        print("v{}".format(p), end=" ")
        self.cT[self.cTP] = self.rT[self.rTP] + p
        self.currentPos = self.cT[self.cTP]
        self.cTP += 1
        self.rTP += 1

    def do_pass(self, p):
        self.rTP += 2
        self.currentPos = self.rT[self.rTP]

    def switch_horizontal(self, p):

        # Horizontal mode consists of two runs
        # white and black or black and white
        # they may extend beyond existing transitions on the reference line
        #  H    next mode    black   white
        #  white             end     black
        #  black             white   end

        self.currentPos = self.currentPos + 0
        self.startingMode = [self.modeBlack, self.modeWhite][self.cTP % 2]
        self.currentMode = self.startingMode

    def rle_black(self, p):
        self.rle(p)

    def rle_white(self, p):
        self.rle(p)

    def rle(self, p):

        self.currentPos += p
        if p > 63:
            return
        if self.currentPos >= self.Columns:
            tPos = self.currentPos - self.Columns
            self.flush_line()
            self.currentPos = tPos
            self.cTP = 0

            if self.rT[self.rTP] <= self.cT[self.cTP]:
                self.rTP += 1
            else:
                pass

        self.cT[self.cTP] = self.currentPos
        self.cTP += 1

        if self.currentMode != self.startingMode:
            self.currentMode = self.rle_end
        elif self.currentMode == self.modeBlack:
            self.currentMode = self.modeWhite
        elif self.currentMode == self.modeWhite:
            self.currentMode = self.modeBlack
        else:
            raise PdfReadError("Fax decode mode error")

    def rle_end(self, p):

        assert self.currentPos < self.Columns
        while True:
            if self.rT[self.rTP] is None:
                break
            if self.rT[self.rTP] >= self.currentPos:
                break
            self.rTP += 2
        self.currentMode = self.modeV

    def pterm(self, p):
        self.flush_line()
        # print( 'Fax {} bytes'.format( len(self.Result)) )
        # print( 'that is {} lines'.format( len(self.Result) / 3 / self.Columns ) )
        # print( 'count of lines as we went along ' , self.linect )
        self.currentMode = self.modeFinished

    def AddEntry(self, tableX, bits, op, opa):

        bita = bits + "0000000000000"
        bitz = bits + "1111111111111"

        valmin = 0
        valmax = 0
        for i in range(13):
            valmin = valmin * 2 + (bita[i] == "1")
            valmax = valmax * 2 + (bitz[i] == "1")

        for t in range(valmin, valmax + 1):
            tableX[t] = (len(bits), op, opa)

    def LoadTables(self, tableV, tableB, tableW):
        AddEntry = self.AddEntry

        AddEntry(tableV, "0000001111", self.switch_uncompressed, 0)
        AddEntry(tableV, "0000010", self.copy_down, -3)
        AddEntry(tableV, "0000011", self.copy_down, +3)
        AddEntry(tableV, "000010", self.copy_down, -2)
        AddEntry(tableV, "000011", self.copy_down, 2)
        AddEntry(tableV, "0001", self.do_pass, 0)  # Pass
        AddEntry(tableV, "010", self.copy_down, -1)  # a1 to the left of b1 by 1
        AddEntry(tableV, "011", self.copy_down, +1)  # a1 to the right of b1 by 1
        AddEntry(tableV, "1", self.copy_down, 0)  # a1 under b1  a1b1=0
        AddEntry(
            tableV, "001", self.switch_horizontal, 0
        )  # horrizontal e.g run length doding for #White and then black
        AddEntry(tableW, "00000010", self.rle_white, 29)
        AddEntry(tableW, "00000011", self.rle_white, 30)
        AddEntry(tableW, "00000100", self.rle_white, 45)
        AddEntry(tableW, "00000101", self.rle_white, 46)
        AddEntry(tableW, "0000011", self.rle_white, 22)
        AddEntry(tableW, "0000100", self.rle_white, 23)
        AddEntry(tableW, "00001010", self.rle_white, 47)
        AddEntry(tableW, "00001011", self.rle_white, 48)
        AddEntry(tableW, "000011", self.rle_white, 13)
        AddEntry(tableW, "0001000", self.rle_white, 20)
        AddEntry(tableW, "00010010", self.rle_white, 33)
        AddEntry(tableW, "00010011", self.rle_white, 34)
        AddEntry(tableW, "00010100", self.rle_white, 35)
        AddEntry(tableW, "00010101", self.rle_white, 36)
        AddEntry(tableW, "00010110", self.rle_white, 37)
        AddEntry(tableW, "00010111", self.rle_white, 38)
        AddEntry(tableW, "0001100", self.rle_white, 19)
        AddEntry(tableW, "00011010", self.rle_white, 31)
        AddEntry(tableW, "00011011", self.rle_white, 32)
        AddEntry(tableW, "000111", self.rle_white, 1)
        AddEntry(tableW, "001000", self.rle_white, 12)
        AddEntry(tableW, "00100100", self.rle_white, 53)
        AddEntry(tableW, "00100101", self.rle_white, 54)
        AddEntry(tableW, "0010011", self.rle_white, 26)
        AddEntry(tableW, "00101000", self.rle_white, 39)
        AddEntry(tableW, "00101001", self.rle_white, 40)
        AddEntry(tableW, "00101010", self.rle_white, 41)
        AddEntry(tableW, "00101011", self.rle_white, 42)
        AddEntry(tableW, "00101100", self.rle_white, 43)
        AddEntry(tableW, "00101101", self.rle_white, 44)
        AddEntry(tableW, "0010111", self.rle_white, 21)
        AddEntry(tableW, "0011000", self.rle_white, 28)
        AddEntry(tableW, "00110010", self.rle_white, 61)
        AddEntry(tableW, "00110011", self.rle_white, 62)
        AddEntry(tableW, "00110100", self.rle_white, 63)
        AddEntry(tableW, "00110101", self.rle_white, 00)
        AddEntry(tableW, "00111", self.rle_white, 10)
        AddEntry(tableW, "01000", self.rle_white, 11)
        AddEntry(tableW, "0100100", self.rle_white, 27)
        AddEntry(tableW, "01001010", self.rle_white, 59)
        AddEntry(tableW, "01001011", self.rle_white, 60)
        AddEntry(tableW, "0100111", self.rle_white, 18)
        AddEntry(tableW, "0101000", self.rle_white, 24)
        AddEntry(tableW, "01010010", self.rle_white, 49)
        AddEntry(tableW, "01010011", self.rle_white, 50)
        AddEntry(tableW, "01010100", self.rle_white, 51)
        AddEntry(tableW, "01010101", self.rle_white, 52)
        AddEntry(tableW, "0101011", self.rle_white, 25)
        AddEntry(tableW, "01011000", self.rle_white, 55)
        AddEntry(tableW, "01011001", self.rle_white, 56)
        AddEntry(tableW, "01011010", self.rle_white, 57)
        AddEntry(tableW, "01011011", self.rle_white, 58)
        AddEntry(tableW, "0111", self.rle_white, 2)
        AddEntry(tableW, "1000", self.rle_white, 3)
        AddEntry(tableW, "10011", self.rle_white, 8)
        AddEntry(tableW, "10100", self.rle_white, 9)
        AddEntry(tableW, "101010", self.rle_white, 16)
        AddEntry(tableW, "101011", self.rle_white, 17)
        AddEntry(tableW, "1011", self.rle_white, 4)
        AddEntry(tableW, "1100", self.rle_white, 5)
        AddEntry(tableW, "110100", self.rle_white, 14)
        AddEntry(tableW, "110101", self.rle_white, 15)
        AddEntry(tableW, "1110", self.rle_white, 6)
        AddEntry(tableW, "1111", self.rle_white, 7)
        #
        AddEntry(tableW, "11011", self.rle_white, 64)
        AddEntry(tableW, "10010", self.rle_white, 128)
        AddEntry(tableW, "010111", self.rle_white, 192)
        AddEntry(tableW, "0110111", self.rle_white, 256)
        AddEntry(tableW, "00110110", self.rle_white, 320)
        AddEntry(tableW, "00110111", self.rle_white, 384)
        AddEntry(tableW, "01100100", self.rle_white, 448)
        AddEntry(tableW, "01100101", self.rle_white, 512)
        AddEntry(tableW, "01101000", self.rle_white, 576)
        AddEntry(tableW, "01100111", self.rle_white, 640)
        AddEntry(tableW, "011001100", self.rle_white, 704)
        AddEntry(tableW, "011001101", self.rle_white, 768)
        AddEntry(tableW, "011010010", self.rle_white, 832)
        AddEntry(tableW, "011010011", self.rle_white, 896)
        AddEntry(tableW, "011010100", self.rle_white, 960)
        AddEntry(tableW, "011010101", self.rle_white, 1024)
        AddEntry(tableW, "011010110", self.rle_white, 1088)
        AddEntry(tableW, "011010111", self.rle_white, 1152)
        AddEntry(tableW, "011011000", self.rle_white, 1216)
        AddEntry(tableW, "011011001", self.rle_white, 1280)
        AddEntry(tableW, "011011010", self.rle_white, 1344)
        AddEntry(tableW, "011011011", self.rle_white, 1408)
        AddEntry(tableW, "010011000", self.rle_white, 1472)
        AddEntry(tableW, "010011001", self.rle_white, 1536)
        AddEntry(tableW, "010011010", self.rle_white, 1600)
        AddEntry(tableW, "011000", self.rle_white, 1664)
        AddEntry(tableW, "010011011", self.rle_white, 1728)

        AddEntry(tableW, "00000001000", self.rle_white, 1792)
        AddEntry(tableW, "00000001100", self.rle_white, 1856)
        AddEntry(tableW, "00000001101", self.rle_white, 1920)
        AddEntry(tableW, "000000010010", self.rle_white, 1984)
        AddEntry(tableW, "000000010011", self.rle_white, 2048)
        AddEntry(tableW, "000000010100", self.rle_white, 2112)
        AddEntry(tableW, "000000010101", self.rle_white, 2176)
        AddEntry(tableW, "000000010110", self.rle_white, 2240)
        AddEntry(tableW, "000000010111", self.rle_white, 2304)
        AddEntry(tableW, "000000011100", self.rle_white, 2368)
        AddEntry(tableW, "000000011101", self.rle_white, 2432)
        AddEntry(tableW, "000000011110", self.rle_white, 2496)
        AddEntry(tableW, "000000011111", self.rle_white, 2560)

        AddEntry(tableB, "0000001000", self.rle_black, 18)
        AddEntry(tableB, "000000100100", self.rle_black, 52)
        AddEntry(tableB, "000000100111", self.rle_black, 55)
        AddEntry(tableB, "000000101000", self.rle_black, 56)
        AddEntry(tableB, "000000101011", self.rle_black, 59)
        AddEntry(tableB, "000000101100", self.rle_black, 60)
        AddEntry(tableB, "00000010111", self.rle_black, 24)
        AddEntry(tableB, "00000011000", self.rle_black, 25)
        AddEntry(tableB, "000000110111", self.rle_black, 53)
        AddEntry(tableB, "000000111000", self.rle_black, 54)
        AddEntry(tableB, "00000100", self.rle_black, 13)
        AddEntry(tableB, "00000101000", self.rle_black, 23)
        AddEntry(tableB, "000001010010", self.rle_black, 50)
        AddEntry(tableB, "000001010011", self.rle_black, 51)
        AddEntry(tableB, "000001010100", self.rle_black, 44)
        AddEntry(tableB, "000001010101", self.rle_black, 45)
        AddEntry(tableB, "000001010110", self.rle_black, 46)
        AddEntry(tableB, "000001010111", self.rle_black, 47)
        AddEntry(tableB, "000001011000", self.rle_black, 57)
        AddEntry(tableB, "000001011001", self.rle_black, 58)
        AddEntry(tableB, "000001011010", self.rle_black, 61)
        AddEntry(tableB, "0000010111", self.rle_black, 16)
        AddEntry(tableB, "0000011000", self.rle_black, 17)
        AddEntry(tableB, "000001100100", self.rle_black, 48)
        AddEntry(tableB, "000001100101", self.rle_black, 49)
        AddEntry(tableB, "000001100110", self.rle_black, 62)
        AddEntry(tableB, "000001100111", self.rle_black, 63)
        AddEntry(tableB, "000001101000", self.rle_black, 30)
        AddEntry(tableB, "000001101001", self.rle_black, 31)
        AddEntry(tableB, "000001101010", self.rle_black, 32)
        AddEntry(tableB, "000001101011", self.rle_black, 33)
        AddEntry(tableB, "000001101100", self.rle_black, 40)
        AddEntry(tableB, "000001101101", self.rle_black, 41)
        AddEntry(tableB, "00000110111", self.rle_black, 22)
        AddEntry(tableB, "00000111", self.rle_black, 14)
        AddEntry(tableB, "0000100", self.rle_black, 10)
        AddEntry(tableB, "0000101", self.rle_black, 11)
        AddEntry(tableB, "000011000", self.rle_black, 15)
        AddEntry(tableB, "000011001010", self.rle_black, 26)
        AddEntry(tableB, "000011001011", self.rle_black, 27)
        AddEntry(tableB, "000011001100", self.rle_black, 28)
        AddEntry(tableB, "000011001101", self.rle_black, 29)
        AddEntry(tableB, "00001100111", self.rle_black, 19)
        AddEntry(tableB, "00001101000", self.rle_black, 20)
        AddEntry(tableB, "000011010010", self.rle_black, 34)
        AddEntry(tableB, "000011010011", self.rle_black, 35)
        AddEntry(tableB, "000011010100", self.rle_black, 36)
        AddEntry(tableB, "000011010101", self.rle_black, 37)
        AddEntry(tableB, "000011010110", self.rle_black, 38)
        AddEntry(tableB, "000011010111", self.rle_black, 39)
        AddEntry(tableB, "00001101100", self.rle_black, 21)
        AddEntry(tableB, "000011011010", self.rle_black, 42)
        AddEntry(tableB, "000011011011", self.rle_black, 43)
        AddEntry(tableB, "0000110111", self.rle_black, 00)
        AddEntry(tableB, "0000111", self.rle_black, 12)
        AddEntry(tableB, "000100", self.rle_black, 9)
        AddEntry(tableB, "000101", self.rle_black, 8)
        AddEntry(tableB, "00011", self.rle_black, 7)
        AddEntry(tableB, "0010", self.rle_black, 6)
        AddEntry(tableB, "0011", self.rle_black, 5)
        AddEntry(tableB, "010", self.rle_black, 1)
        AddEntry(tableB, "011", self.rle_black, 4)
        AddEntry(tableB, "10", self.rle_black, 3)
        AddEntry(tableB, "11", self.rle_black, 2)

        AddEntry(tableB, "000011001000", self.rle_black, 128)
        AddEntry(tableB, "000011001001", self.rle_black, 192)
        AddEntry(tableB, "000001011011", self.rle_black, 256)
        AddEntry(tableB, "000000110011", self.rle_black, 320)
        AddEntry(tableB, "000000110100", self.rle_black, 384)
        AddEntry(tableB, "000000110101", self.rle_black, 448)
        AddEntry(tableB, "0000001101100", self.rle_black, 512)
        AddEntry(tableB, "0000001101101", self.rle_black, 576)
        AddEntry(tableB, "0000001001010", self.rle_black, 640)
        AddEntry(tableB, "0000001001011", self.rle_black, 704)
        AddEntry(tableB, "0000001001100", self.rle_black, 768)
        AddEntry(tableB, "0000001001101", self.rle_black, 832)
        AddEntry(tableB, "0000001110010", self.rle_black, 896)
        AddEntry(tableB, "0000001110011", self.rle_black, 960)
        AddEntry(tableB, "0000001110100", self.rle_black, 1024)
        AddEntry(tableB, "0000001110101", self.rle_black, 1088)
        AddEntry(tableB, "0000001110110", self.rle_black, 1152)
        AddEntry(tableB, "0000001110111", self.rle_black, 1216)
        AddEntry(tableB, "0000001010010", self.rle_black, 1280)
        AddEntry(tableB, "0000001010011", self.rle_black, 1344)
        AddEntry(tableB, "0000001010100", self.rle_black, 1408)
        AddEntry(tableB, "0000001010101", self.rle_black, 1472)
        AddEntry(tableB, "0000001011010", self.rle_black, 1536)
        AddEntry(tableB, "0000001011011", self.rle_black, 1600)
        AddEntry(tableB, "0000001100100", self.rle_black, 1664)
        AddEntry(tableB, "0000001100101", self.rle_black, 1728)

        AddEntry(tableB, "00000001000", self.rle_black, 1792)
        AddEntry(tableB, "00000001100", self.rle_black, 1856)
        AddEntry(tableB, "00000001101", self.rle_black, 1920)
        AddEntry(tableB, "000000010010", self.rle_black, 1984)
        AddEntry(tableB, "000000010011", self.rle_black, 2048)
        AddEntry(tableB, "000000010100", self.rle_black, 2112)
        AddEntry(tableB, "000000010101", self.rle_black, 2176)
        AddEntry(tableB, "000000010110", self.rle_black, 2240)
        AddEntry(tableB, "000000010111", self.rle_black, 2304)
        AddEntry(tableB, "000000011100", self.rle_black, 2368)
        AddEntry(tableB, "000000011101", self.rle_black, 2432)
        AddEntry(tableB, "000000011110", self.rle_black, 2496)
        AddEntry(tableB, "000000011111", self.rle_black, 2560)

        AddEntry(tableV, "0000000000010", self.pterm, 0)
        AddEntry(tableW, "0000000000010", self.pterm, 0)
        AddEntry(tableB, "0000000000010", self.pterm, 0)

    def Process(self, stream):
        self.currentMode = self.modeV
        nextbits = self.getbits(stream, 13)
        while self.bytepos < len(stream):
            if self.currentMode == self.modeFinished:
                print("CCITT decode finished")
                print(
                    "Data len {} = {} rows ".format(
                        len(self.Result), len(self.Result) / 3 / self.Columns
                    )
                )
                return self.Result

            if self.currentMode == self.modeU:
                print("cannot handle uncompresssed mode")
            if self.currentMode == self.modeV:
                (code_len, operator, operand) = self.tableV[nextbits]
            elif self.currentMode == self.modeWhite:
                (code_len, operator, operand) = self.tableW[nextbits]
            elif self.currentMode == self.modeBlack:
                (code_len, operator, operand) = self.tableB[nextbits]
            if operator is None:
                print("None!!!")
            else:
                operator(operand)
            if self.currentMode == self.rle_end:
                self.rle_end(1)

            nextbits = nextbits << (code_len)
            nextbits = nextbits & 0x1FFF
            nextbits = nextbits + self.getbits(stream, code_len)

        return self.Result


def paethPredictor(left, up, up_left):
    p = left + up - up_left
    dist_left = abs(p - left)
    dist_up = abs(p - up)
    dist_up_left = abs(p - up_left)

    if dist_left <= dist_up and dist_left <= dist_up_left:
        return left
    elif dist_up <= dist_up_left:
        return up
    else:
        return up_left
