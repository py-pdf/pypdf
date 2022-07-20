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


"""
Implementation of generic PDF objects (dictionary, number, string, and so on).
"""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

import codecs
import decimal
import logging
import re
import sys
import warnings
from sys import version_info

from PyPDF2._security import RC4_encrypt
from PyPDF2._utils import DEPR_MSG
from PyPDF2.constants import FilterTypes as FT
from PyPDF2.constants import StreamAttributes as SA
from PyPDF2.errors import (
    STREAM_TRUNCATED_PREMATURELY,
    PdfReadError,
    PdfReadWarning,
    PdfStreamError,
)

from . import _utils, filters
from ._utils import b_, chr_, ord_, readNonWhitespace, skipOverComment, u_

if version_info < (3, 0):
    from cStringIO import StringIO

    BytesIO = StringIO
else:
    from io import BytesIO, StringIO

logger = logging.getLogger(__name__)
ObjectPrefix = b_("/<[tf(n%")
NumberSigns = b_("+-")
IndirectPattern = re.compile(b_(r"[+-]?(\d+)\s+(\d+)\s+R[^a-zA-Z]"))


def read_object(stream, pdf):
    tok = stream.read(1)
    stream.seek(-1, 1)  # reset to start
    idx = ObjectPrefix.find(tok)
    if idx == 0:
        return NameObject.read_from_stream(stream, pdf)
    elif idx == 1:
        # hexadecimal string OR dictionary
        peek = stream.read(2)
        stream.seek(-2, 1)  # reset to start

        if peek == b_("<<"):
            return DictionaryObject.read_from_stream(stream, pdf)
        else:
            return readHexStringFromStream(stream)
    elif idx == 2:
        return ArrayObject.read_from_stream(stream, pdf)
    elif idx == 3 or idx == 4:
        return BooleanObject.read_from_stream(stream)
    elif idx == 5:
        return readStringFromStream(stream)
    elif idx == 6:
        return NullObject.read_from_stream(stream)
    elif idx == 7:
        # comment
        while tok not in (b_("\r"), b_("\n")):
            tok = stream.read(1)
            # Prevents an infinite loop by raising an error if the stream is at
            # the EOF
            if len(tok) <= 0:
                raise PdfStreamError("File ended unexpectedly.")
        tok = readNonWhitespace(stream)
        stream.seek(-1, 1)
        return read_object(stream, pdf)
    else:
        # number object OR indirect reference
        peek = stream.read(20)
        stream.seek(-len(peek), 1)  # reset to start
        if IndirectPattern.match(peek) is not None:
            return IndirectObject.read_from_stream(stream, pdf)
        else:
            return NumberObject.read_from_stream(stream)


def readObject(stream, pdf):
    warnings.warn(
        "readObject will be deprecated with PyPDF2 2.0.0, use read_object instead",
        PendingDeprecationWarning,
        stacklevel=2,
    )
    return read_object(stream, pdf)


class PdfObject(object):
    def get_object(self):
        """Resolve indirect references."""
        return self

    def getObject(self):
        warnings.warn(
            "getObject will be removed in PyPDF2 2.0.0. Use get_object instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_object()


class NullObject(PdfObject):
    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("null"))

    @staticmethod
    def read_from_stream(stream):
        nulltxt = stream.read(4)
        if nulltxt != b_("null"):
            raise PdfReadError("Could not read Null object")
        return NullObject()

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def readFromStream(stream):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return NullObject.read_from_stream(stream)


class BooleanObject(PdfObject):
    def __init__(self, value):
        self.value = value

    def write_to_stream(self, stream, encryption_key):
        if self.value:
            stream.write(b_("true"))
        else:
            stream.write(b_("false"))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream):
        word = stream.read(4)
        if word == b_("true"):
            return BooleanObject(True)
        elif word == b_("fals"):
            stream.read(1)
            return BooleanObject(False)
        else:
            raise PdfReadError("Could not read Boolean object")

    @staticmethod
    def readFromStream(stream):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return BooleanObject.read_from_stream(stream)


class ArrayObject(list, PdfObject):
    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("["))
        for data in self:
            stream.write(b_(" "))
            data.write_to_stream(stream, encryption_key)
        stream.write(b_(" ]"))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream, pdf):
        arr = ArrayObject()
        tmp = stream.read(1)
        if tmp != b_("["):
            raise PdfReadError("Could not read array")
        while True:
            # skip leading whitespace
            tok = stream.read(1)
            while tok.isspace():
                tok = stream.read(1)
            stream.seek(-1, 1)
            # check for array ending
            peekahead = stream.read(1)
            if peekahead == b_("]"):
                break
            stream.seek(-1, 1)
            # read and append obj
            arr.append(read_object(stream, pdf))
        return arr

    @staticmethod
    def readFromStream(stream, pdf):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return ArrayObject.read_from_stream(stream, pdf)


class IndirectObject(PdfObject):
    def __init__(self, idnum, generation, pdf):
        self.idnum = idnum
        self.generation = generation
        self.pdf = pdf

    def get_object(self):
        return self.pdf.get_object(self).get_object()

    def __repr__(self):
        return "IndirectObject(%r, %r)" % (self.idnum, self.generation)

    def __eq__(self, other):
        return (
            other is not None
            and isinstance(other, IndirectObject)
            and self.idnum == other.idnum
            and self.generation == other.generation
            and self.pdf is other.pdf
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("%s %s R" % (self.idnum, self.generation)))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream, pdf):
        idnum = b_("")
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                break
            idnum += tok
        generation = b_("")
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                if not generation:
                    continue
                break
            generation += tok
        r = readNonWhitespace(stream)
        if r != b_("R"):
            raise PdfReadError(
                "Error reading indirect object reference at byte %s"
                % _utils.hexStr(stream.tell())
            )
        return IndirectObject(int(idnum), int(generation), pdf)

    @staticmethod
    def readFromStream(stream, pdf):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return IndirectObject.read_from_stream(stream, pdf)


class FloatObject(decimal.Decimal, PdfObject):
    def __new__(cls, value="0", context=None):
        try:
            return decimal.Decimal.__new__(cls, _utils.str_(value), context)
        except Exception:
            try:
                return decimal.Decimal.__new__(cls, str(value))
            except decimal.InvalidOperation:
                # If this isn't a valid decimal (happens in malformed PDFs)
                # fallback to 0
                logger.warning("Invalid FloatObject {}".format(value))
                return decimal.Decimal.__new__(cls, "0")

    def __repr__(self):
        if self == self.to_integral():
            return str(self.quantize(decimal.Decimal(1)))
        else:
            # Standard formatting adds useless extraneous zeros.
            o = "%.5f" % self
            # Remove the zeros.
            while o and o[-1] == "0":
                o = o[:-1]
            return o

    def as_numeric(self):
        return float(b_(repr(self)))

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_(repr(self)))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)


class NumberObject(int, PdfObject):
    NumberPattern = re.compile(b_("[^+-.0-9]"))
    ByteDot = b_(".")

    def __new__(cls, value):
        val = int(value)
        try:
            return int.__new__(cls, val)
        except OverflowError:
            return int.__new__(cls, 0)

    def as_numeric(self):
        return int(b_(repr(self)))

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_(repr(self)))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream):
        num = _utils.readUntilRegex(stream, NumberObject.NumberPattern)
        if num.find(NumberObject.ByteDot) != -1:
            return FloatObject(num)
        else:
            return NumberObject(num)

    @staticmethod
    def readFromStream(stream):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return NumberObject.read_from_stream(stream)


def createStringObject(string):
    """
    Given a string (either a "str" or "unicode"), create a ByteStringObject or a
    TextStringObject to represent the string.
    """
    if isinstance(string, _utils.string_type):
        return TextStringObject(string)
    elif isinstance(string, _utils.bytes_type):
        try:
            if string.startswith(codecs.BOM_UTF16_BE):
                retval = TextStringObject(string.decode("utf-16"))
                retval.autodetect_utf16 = True
                return retval
            else:
                # This is probably a big performance hit here, but we need to
                # convert string objects into the text/unicode-aware version if
                # possible... and the only way to check if that's possible is
                # to try.  Some strings are strings, some are just byte arrays.
                retval = TextStringObject(decode_pdfdocencoding(string))
                retval.autodetect_pdfdocencoding = True
                return retval
        except UnicodeDecodeError:
            return ByteStringObject(string)
    else:
        raise TypeError("createStringObject should have str or unicode arg")


def readHexStringFromStream(stream):
    stream.read(1)
    txt = ""
    x = b_("")
    while True:
        tok = readNonWhitespace(stream)
        if not tok:
            raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
        if tok == b_(">"):
            break
        x += tok
        if len(x) == 2:
            txt += chr(int(x, base=16))
            x = b_("")
    if len(x) == 1:
        x += b_("0")
    if len(x) == 2:
        txt += chr(int(x, base=16))
    return createStringObject(b_(txt))


def readStringFromStream(stream):
    tok = stream.read(1)
    parens = 1
    txt = b_("")
    while True:
        tok = stream.read(1)
        if not tok:
            raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
        if tok == b_("("):
            parens += 1
        elif tok == b_(")"):
            parens -= 1
            if parens == 0:
                break
        elif tok == b_("\\"):
            tok = stream.read(1)
            escape_dict = {
                b_("n"): b_("\n"),
                b_("r"): b_("\r"),
                b_("t"): b_("\t"),
                b_("b"): b_("\b"),
                b_("f"): b_("\f"),
                b_("c"): b_(r"\c"),
                b_("("): b_("("),
                b_(")"): b_(")"),
                b_("/"): b_("/"),
                b_("\\"): b_("\\"),
                b_(" "): b_(" "),
                b_("/"): b_("/"),
                b_("%"): b_("%"),
                b_("<"): b_("<"),
                b_(">"): b_(">"),
                b_("["): b_("["),
                b_("]"): b_("]"),
                b_("#"): b_("#"),
                b_("_"): b_("_"),
                b_("&"): b_("&"),
                b_("$"): b_("$"),
            }
            try:
                tok = escape_dict[tok]
            except KeyError:
                if tok.isdigit():
                    # "The number ddd may consist of one, two, or three
                    # octal digits; high-order overflow shall be ignored.
                    # Three octal digits shall be used, with leading zeros
                    # as needed, if the next character of the string is also
                    # a digit." (PDF reference 7.3.4.2, p 16)
                    for _ in range(2):
                        ntok = stream.read(1)
                        if ntok.isdigit():
                            tok += ntok
                        else:
                            break
                    tok = b_(chr(int(tok, base=8)))
                elif tok in b_("\n\r"):
                    # This case is  hit when a backslash followed by a line
                    # break occurs.  If it's a multi-char EOL, consume the
                    # second character:
                    tok = stream.read(1)
                    if tok not in b_("\n\r"):
                        stream.seek(-1, 1)
                    # Then don't add anything to the actual string, since this
                    # line break was escaped:
                    tok = b_("")
                else:
                    msg = r"Unexpected escaped string: {}".format(tok.decode("utf8"))
                    # if.strict: PdfReadError(msg)
                    logger.warning(msg)
        txt += tok
    return createStringObject(txt)


class ByteStringObject(_utils.bytes_type, PdfObject):  # type: ignore
    """
    Represents a string object where the text encoding could not be determined.
    This occurs quite often, as the PDF spec doesn't provide an alternate way to
    represent strings -- for example, the encryption data stored in files (like
    /O) is clearly not text, but is still stored in a "String" object.
    """

    @property
    def original_bytes(self):
        """For compatibility with TextStringObject.original_bytes."""
        return self

    def write_to_stream(self, stream, encryption_key):
        bytearr = self
        if encryption_key:
            bytearr = RC4_encrypt(encryption_key, bytearr)
        stream.write(b_("<"))
        stream.write(_utils.hexencode(bytearr))
        stream.write(b_(">"))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)


class TextStringObject(_utils.string_type, PdfObject):  # type: ignore
    """
    Represents a string object that has been decoded into a real unicode string.
    If read from a PDF document, this string appeared to match the
    PDFDocEncoding, or contained a UTF-16BE BOM mark to cause UTF-16 decoding to
    occur.
    """

    autodetect_pdfdocencoding = False
    autodetect_utf16 = False

    @property
    def original_bytes(self):
        """
        It is occasionally possible that a text string object gets created where
        a byte string object was expected due to the autodetection mechanism --
        if that occurs, this "original_bytes" property can be used to
        back-calculate what the original encoded bytes were.
        """
        return self.get_original_bytes()

    def get_original_bytes(self):
        # We're a text string object, but the library is trying to get our raw
        # bytes.  This can happen if we auto-detected this string as text, but
        # we were wrong.  It's pretty common.  Return the original bytes that
        # would have been used to create this object, based upon the autodetect
        # method.
        if self.autodetect_utf16:
            return codecs.BOM_UTF16_BE + self.encode("utf-16be")
        elif self.autodetect_pdfdocencoding:
            return encode_pdfdocencoding(self)
        else:
            raise Exception("no information about original bytes")

    def write_to_stream(self, stream, encryption_key):
        # Try to write the string out as a PDFDocEncoding encoded string.  It's
        # nicer to look at in the PDF file.  Sadly, we take a performance hit
        # here for trying...
        try:
            bytearr = encode_pdfdocencoding(self)
        except UnicodeEncodeError:
            bytearr = codecs.BOM_UTF16_BE + self.encode("utf-16be")
        if encryption_key:
            bytearr = RC4_encrypt(encryption_key, bytearr)
            obj = ByteStringObject(bytearr)
            obj.write_to_stream(stream, None)
        else:
            stream.write(b_("("))
            for c in bytearr:
                if not chr_(c).isalnum() and c != b_(" "):
                    stream.write(b_("\\%03o" % ord_(c)))
                else:
                    stream.write(b_(chr_(c)))
            stream.write(b_(")"))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)


class NameObject(str, PdfObject):
    delimiterPattern = re.compile(b_(r"\s+|[\(\)<>\[\]{}/%]"))
    surfix = b_("/")

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_(self))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream, pdf):
        name = stream.read(1)
        if name != NameObject.surfix:
            raise PdfReadError("name read error")
        name += _utils.readUntilRegex(
            stream, NameObject.delimiterPattern, ignore_eof=True
        )
        try:
            try:
                ret = name.decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                ret = name.decode("gbk")
            return NameObject(ret)
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Name objects should represent irregular characters
            # with a '#' followed by the symbol's hex number
            if not pdf.strict:
                warnings.warn("Illegal character in Name Object", _utils.PdfReadWarning)
                return NameObject(name)
            else:
                raise PdfReadError("Illegal character in Name Object")

    @staticmethod
    def readFromStream(stream, pdf):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return NameObject.read_from_stream(stream, pdf)


class DictionaryObject(dict, PdfObject):
    def raw_get(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not isinstance(key, PdfObject):
            raise ValueError("key must be PdfObject")
        if not isinstance(value, PdfObject):
            raise ValueError("value must be PdfObject")
        return dict.__setitem__(self, key, value)

    def setdefault(self, key, value=None):
        if not isinstance(key, PdfObject):
            raise ValueError("key must be PdfObject")
        if not isinstance(value, PdfObject):
            raise ValueError("value must be PdfObject")
        return dict.setdefault(self, key, value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key).get_object()

    @property
    def xmp_metadata(self):
        """
        Retrieve XMP (Extensible Metadata Platform) data relevant to the
        this object, if available.

        Stability: Added in v1.12, will exist for all future v1.x releases.
        @return Returns a {@link #xmp.XmpInformation XmlInformation} instance
        that can be used to access XMP metadata from the document.  Can also
        return None if no metadata was found on the document root.
        """
        metadata = self.get("/Metadata", None)
        if metadata is None:
            return None
        metadata = metadata.get_object()
        from . import xmp

        if not isinstance(metadata, xmp.XmpInformation):
            metadata = xmp.XmpInformation(metadata)
            self[NameObject("/Metadata")] = metadata
        return metadata

    def getXmpMetadata(self):  # XmpInformation
        """
        .. deprecated:: 1.28.3
            Use :meth:`xmp_metadata` instead.
        """
        warnings.warn(
            "getXmpMetadata will be removed in PyPDF2 2.0.0. "
            "Use xmp_metadata instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.xmp_metadata

    @property
    def xmpMetadata(self):
        """
        .. deprecated:: 1.28.3
            Use :meth:`xmp_metadata` instead.
        """
        warnings.warn(
            "xmpMetadata will be removed in PyPDF2 2.0.0. Use xmp_metadata instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.xmp_metadata

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("<<\n"))
        for key, value in list(self.items()):
            key.write_to_stream(stream, encryption_key)
            stream.write(b_(" "))
            value.write_to_stream(stream, encryption_key)
            stream.write(b_("\n"))
        stream.write(b_(">>"))

    def writeToStream(self, stream, encryption_key):
        warnings.warn(
            "writeToStream will be removed in PyPDF2 2.0.0. "
            "Use write_to_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream, pdf):
        tmp = stream.read(2)
        if tmp != b_("<<"):
            raise PdfReadError(
                "Dictionary read error at byte %s: stream must begin with '<<'"
                % _utils.hexStr(stream.tell())
            )
        data = {}
        while True:
            tok = readNonWhitespace(stream)
            if tok == b_("\x00"):
                continue
            elif tok == b_("%"):
                stream.seek(-1, 1)
                skipOverComment(stream)
                continue
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)

            if tok == b_(">"):
                stream.read(1)
                break
            stream.seek(-1, 1)
            key = read_object(stream, pdf)
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            value = read_object(stream, pdf)
            if not data.get(key):
                data[key] = value
            elif pdf.strict:
                # multiple definitions of key not permitted
                raise PdfReadError(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (_utils.hexStr(stream.tell()), key)
                )
            else:
                warnings.warn(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (_utils.hexStr(stream.tell()), key),
                    PdfReadWarning,
                )

        pos = stream.tell()
        s = readNonWhitespace(stream)
        if s == b_("s") and stream.read(5) == b_("tream"):
            eol = stream.read(1)
            # odd PDF file output has spaces after 'stream' keyword but before EOL.
            # patch provided by Danial Sandler
            while eol == b_(" "):
                eol = stream.read(1)
            if eol not in (b_("\n"), b_("\r")):
                raise PdfStreamError("Stream data must be followed by a newline")
            if eol == b_("\r"):
                # read \n after
                if stream.read(1) != b_("\n"):
                    stream.seek(-1, 1)
            # this is a stream object, not a dictionary
            if SA.LENGTH not in data:
                raise PdfStreamError("Stream length not defined")
            length = data[SA.LENGTH]
            if isinstance(length, IndirectObject):
                t = stream.tell()
                length = pdf.get_object(length)
                stream.seek(t, 0)
            data["__streamdata__"] = stream.read(length)
            e = readNonWhitespace(stream)
            ndstream = stream.read(8)
            if (e + ndstream) != b_("endstream"):
                # (sigh) - the odd PDF file has a length that is too long, so
                # we need to read backwards to find the "endstream" ending.
                # ReportLab (unknown version) generates files with this bug,
                # and Python users into PDF files tend to be our audience.
                # we need to do this to correct the streamdata and chop off
                # an extra character.
                pos = stream.tell()
                stream.seek(-10, 1)
                end = stream.read(9)
                if end == b_("endstream"):
                    # we found it by looking back one character further.
                    data["__streamdata__"] = data["__streamdata__"][:-1]
                else:
                    stream.seek(pos, 0)
                    raise PdfReadError(
                        "Unable to find 'endstream' marker after stream at byte %s."
                        % _utils.hexStr(stream.tell())
                    )
        else:
            stream.seek(pos, 0)
        if "__streamdata__" in data:
            return StreamObject.initializeFromDictionary(data)
        else:
            retval = DictionaryObject()
            retval.update(data)
            return retval

    @staticmethod
    def readFromStream(stream, pdf):
        warnings.warn(
            "readFromStream will be removed in PyPDF2 2.0.0. "
            "Use read_from_stream instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return DictionaryObject.read_from_stream(stream, pdf)


class TreeObject(DictionaryObject):
    def __init__(self):
        DictionaryObject.__init__(self)

    def hasChildren(self):
        return "/First" in self

    def __iter__(self):
        return self.children()

    def children(self):
        if not self.hasChildren():
            if sys.version_info >= (3, 5):  # PEP 479
                return
            else:
                raise StopIteration

        child = self["/First"]
        while True:
            yield child
            if child == self["/Last"]:
                if sys.version_info >= (3, 5):  # PEP 479
                    return
                else:
                    raise StopIteration
            child = child["/Next"]

    def addChild(self, child, pdf):
        warnings.warn(
            DEPR_MSG.format("addChild", "add_child"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.add_child(child, pdf)

    def add_child(self, child, pdf):  # PdfReader
        child_obj = child.get_object()
        child = pdf.getReference(child_obj)
        assert isinstance(child, IndirectObject)

        if "/First" not in self:
            self[NameObject("/First")] = child
            self[NameObject("/Count")] = NumberObject(0)
            prev = None
        else:
            prev = self["/Last"]

        self[NameObject("/Last")] = child
        self[NameObject("/Count")] = NumberObject(self[NameObject("/Count")] + 1)

        if prev:
            prev_ref = pdf.getReference(prev)
            assert isinstance(prev_ref, IndirectObject)
            child_obj[NameObject("/Prev")] = prev_ref
            prev[NameObject("/Next")] = child

        parent_ref = pdf.getReference(self)
        assert isinstance(parent_ref, IndirectObject)
        child_obj[NameObject("/Parent")] = parent_ref

    def removeChild(self, child):
        warnings.warn(
            DEPR_MSG.format("removeChild", "remove_child"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.remove_child(child)

    def remove_child(self, child):
        child_obj = child.get_object()

        if NameObject("/Parent") not in child_obj:
            raise ValueError("Removed child does not appear to be a tree item")
        elif child_obj[NameObject("/Parent")] != self:
            raise ValueError("Removed child is not a member of this tree")

        found = False
        prev_ref = None
        prev = None
        cur_ref = self[NameObject("/First")]
        cur = cur_ref.get_object()
        last_ref = self[NameObject("/Last")]
        last = last_ref.get_object()
        while cur is not None:
            if cur == child_obj:
                if prev is None:
                    if NameObject("/Next") in cur:
                        # Removing first tree node
                        next_ref = cur[NameObject("/Next")]
                        next = next_ref.get_object()
                        del next[NameObject("/Prev")]
                        self[NameObject("/First")] = next_ref
                        self[NameObject("/Count")] = self[NameObject("/Count")] - 1

                    else:
                        # Removing only tree node
                        assert self[NameObject("/Count")] == 1
                        del self[NameObject("/Count")]
                        del self[NameObject("/First")]
                        if NameObject("/Last") in self:
                            del self[NameObject("/Last")]
                else:
                    if NameObject("/Next") in cur:
                        # Removing middle tree node
                        next_ref = cur[NameObject("/Next")]
                        next = next_ref.get_object()
                        next[NameObject("/Prev")] = prev_ref
                        prev[NameObject("/Next")] = next_ref
                        self[NameObject("/Count")] = self[NameObject("/Count")] - 1
                    else:
                        # Removing last tree node
                        assert cur == last
                        del prev[NameObject("/Next")]
                        self[NameObject("/Last")] = prev_ref
                        self[NameObject("/Count")] = self[NameObject("/Count")] - 1
                found = True
                break

            prev_ref = cur_ref
            prev = cur
            if NameObject("/Next") in cur:
                cur_ref = cur[NameObject("/Next")]
                cur = cur_ref.get_object()
            else:
                cur_ref = None
                cur = None

        if not found:
            raise ValueError("Removal couldn't find item in tree")

        del child_obj[NameObject("/Parent")]
        if NameObject("/Next") in child_obj:
            del child_obj[NameObject("/Next")]
        if NameObject("/Prev") in child_obj:
            del child_obj[NameObject("/Prev")]

    def emptyTree(self):
        for child in self:
            child_obj = child.get_object()
            del child_obj[NameObject("/Parent")]
            if NameObject("/Next") in child_obj:
                del child_obj[NameObject("/Next")]
            if NameObject("/Prev") in child_obj:
                del child_obj[NameObject("/Prev")]

        if NameObject("/Count") in self:
            del self[NameObject("/Count")]
        if NameObject("/First") in self:
            del self[NameObject("/First")]
        if NameObject("/Last") in self:
            del self[NameObject("/Last")]


class StreamObject(DictionaryObject):
    def __init__(self):
        self._data = None
        self.decoded_self = None

    @property
    def decodedSelf(self):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.decoded_self

    @decodedSelf.setter
    def decodedSelf(self, value):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.decoded_self = value

    def write_to_stream(self, stream, encryption_key):
        self[NameObject(SA.LENGTH)] = NumberObject(len(self._data))
        DictionaryObject.write_to_stream(self, stream, encryption_key)
        del self[SA.LENGTH]
        stream.write(b_("\nstream\n"))
        data = self._data
        if encryption_key:
            data = RC4_encrypt(encryption_key, data)
        stream.write(data)
        stream.write(b_("\nendstream"))

    @staticmethod
    def initializeFromDictionary(data):
        if SA.FILTER in data:
            retval = EncodedStreamObject()
        else:
            retval = DecodedStreamObject()
        retval._data = data["__streamdata__"]
        del data["__streamdata__"]
        del data[SA.LENGTH]
        retval.update(data)
        return retval

    def flateEncode(self):
        warnings.warn(
            DEPR_MSG.format("flateEncode", "flate_encode"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.flate_encode()

    def flate_encode(self):
        if SA.FILTER in self:
            f = self[SA.FILTER]
            if isinstance(f, ArrayObject):
                f.insert(0, NameObject(FT.FLATE_DECODE))
            else:
                newf = ArrayObject()
                newf.append(NameObject("/FlateDecode"))
                newf.append(f)
                f = newf
        else:
            f = NameObject("/FlateDecode")
        retval = EncodedStreamObject()
        retval[NameObject(SA.FILTER)] = f
        retval._data = filters.FlateDecode.encode(self._data)
        return retval


class DecodedStreamObject(StreamObject):
    def get_data(self):
        return self._data

    def set_data(self, data):
        self._data = data

    def getData(self):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._data

    def setData(self, data):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.set_data(data)


class EncodedStreamObject(StreamObject):
    def __init__(self):
        self.decoded_self = None

    @property
    def decodedSelf(self):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.decoded_self

    @decodedSelf.setter
    def decodedSelf(self, value):
        warnings.warn(
            DEPR_MSG.format("decodedSelf", "decoded_self"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.decoded_self = value

    def get_data(self):
        if self.decoded_self:
            # cached version of decoded object
            return self.decoded_self.get_data()
        else:
            # create decoded object
            decoded = DecodedStreamObject()

            decoded._data = filters.decode_stream_data(self)
            for key, value in list(self.items()):
                if key not in (SA.LENGTH, SA.FILTER, SA.DECODE_PARMS):
                    decoded[key] = value
            self.decoded_self = decoded
            return decoded._data

    def getData(self):
        warnings.warn(
            DEPR_MSG.format("getData", "get_data"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_data()

    def set_data(self, data):
        raise PdfReadError("Creating EncodedStreamObject is not currently supported")

    def setData(self, data):
        warnings.warn(
            DEPR_MSG.format("setData", "set_data"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.set_data(data)


class ContentStream(DecodedStreamObject):
    def __init__(self, stream, pdf):
        self.pdf = pdf
        self.operations = []
        # stream may be a StreamObject or an ArrayObject containing
        # multiple StreamObjects to be cat'd together.
        stream = stream.get_object()
        if isinstance(stream, ArrayObject):
            data = b_("")
            for s in stream:
                data += b_(s.get_object().get_data())
            stream = BytesIO(b_(data))
        else:
            stream = BytesIO(b_(stream.get_data()))
        self.__parseContentStream(stream)

    def __parseContentStream(self, stream):
        # file("f:\\tmp.txt", "w").write(stream.read())
        stream.seek(0, 0)
        operands = []
        while True:
            peek = readNonWhitespace(stream)
            if peek == b_("") or ord_(peek) == 0:
                break
            stream.seek(-1, 1)
            if peek.isalpha() or peek == b_("'") or peek == b_('"'):
                operator = _utils.readUntilRegex(
                    stream, NameObject.delimiterPattern, True
                )
                if operator == b_("BI"):
                    # begin inline image - a completely different parsing
                    # mechanism is required, of course... thanks buddy...
                    assert operands == []
                    ii = self._readInlineImage(stream)
                    self.operations.append((ii, b_("INLINE IMAGE")))
                else:
                    self.operations.append((operands, operator))
                    operands = []
            elif peek == b_("%"):
                # If we encounter a comment in the content stream, we have to
                # handle it here.  Typically, readObject will handle
                # encountering a comment -- but readObject assumes that
                # following the comment must be the object we're trying to
                # read.  In this case, it could be an operator instead.
                while peek not in (b_("\r"), b_("\n")):
                    peek = stream.read(1)
            else:
                operands.append(read_object(stream, None))

    def _readInlineImage(self, stream):
        # begin reading just after the "BI" - begin image
        # first read the dictionary of settings.
        settings = DictionaryObject()
        while True:
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            if tok == b_("I"):
                # "ID" - begin of image data
                break
            key = read_object(stream, self.pdf)
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            value = read_object(stream, self.pdf)
            settings[key] = value
        # left at beginning of ID
        tmp = stream.read(3)
        assert tmp[:2] == b_("ID")
        data = BytesIO()
        # Read the inline image, while checking for EI (End Image) operator.
        while True:
            # Read 8 kB at a time and check if the chunk contains the E operator.
            buf = stream.read(8192)
            # We have reached the end of the stream, but haven't found the EI operator.
            if not buf:
                raise PdfReadError("Unexpected end of stream")
            loc = buf.find(b_("E"))

            if loc == -1:
                data.write(buf)
            else:
                # Write out everything before the E.
                data.write(buf[0:loc])

                # Seek back in the stream to read the E next.
                stream.seek(loc - len(buf), 1)
                tok = stream.read(1)
                # Check for End Image
                tok2 = stream.read(1)
                if tok2 == b_("I"):
                    # Data can contain EI, so check for the Q operator.
                    tok3 = stream.read(1)
                    info = tok + tok2
                    # We need to find whitespace between EI and Q.
                    has_q_whitespace = False
                    while tok3 in _utils.WHITESPACES:
                        has_q_whitespace = True
                        info += tok3
                        tok3 = stream.read(1)
                    if tok3 == b_("Q") and has_q_whitespace:
                        stream.seek(-1, 1)
                        break
                    else:
                        stream.seek(-1, 1)
                        data.write(info)
                else:
                    stream.seek(-1, 1)
                    data.write(tok)
        return {"settings": settings, "data": data.getvalue()}

    def _getData(self):
        newdata = BytesIO()
        for operands, operator in self.operations:
            if operator == b_("INLINE IMAGE"):
                newdata.write(b_("BI"))
                dicttext = BytesIO()
                operands["settings"].write_to_stream(dicttext, None)
                newdata.write(dicttext.getvalue()[2:-2])
                newdata.write(b_("ID "))
                newdata.write(operands["data"])
                newdata.write(b_("EI"))
            else:
                for op in operands:
                    op.write_to_stream(newdata, None)
                    newdata.write(b_(" "))
                newdata.write(b_(operator))
            newdata.write(b_("\n"))
        return newdata.getvalue()

    def _setData(self, value):
        self.__parseContentStream(BytesIO(b_(value)))

    _data = property(_getData, _setData)


class RectangleObject(ArrayObject):
    """
    This class is used to represent *page boxes* in PyPDF2. These boxes include:

        * :attr:`artbox <PyPDF2._page.PageObject.artbox>`
        * :attr:`bleedbox <PyPDF2._page.PageObject.bleedbox>`
        * :attr:`cropbox <PyPDF2._page.PageObject.cropbox>`
        * :attr:`mediabox <PyPDF2._page.PageObject.mediabox>`
        * :attr:`trimbox <PyPDF2._page.PageObject.trimbox>`
    """

    def __init__(self, arr):
        # must have four points
        assert len(arr) == 4
        # automatically convert arr[x] into NumberObject(arr[x]) if necessary
        ArrayObject.__init__(self, [self._ensure_is_number(x) for x in arr])

    def _ensure_is_number(self, value):
        if not isinstance(value, (NumberObject, FloatObject)):
            value = FloatObject(value)
        return value

    def ensureIsNumber(self, value):
        warnings.warn(
            "ensureIsNumber will be removed in PyPDF2 2.0.0. ",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._ensure_is_number(value)

    def __repr__(self):
        return "RectangleObject(%s)" % repr(list(self))

    @property
    def left(self):
        return self[0]

    @property
    def bottom(self):
        return self[1]

    @property
    def right(self):
        return self[2]

    @property
    def top(self):
        return self[3]

    def getLowerLeft_x(self):
        warnings.warn(
            DEPR_MSG.format("getLowerLeft_x", "left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.left

    def getLowerLeft_y(self):
        warnings.warn(
            DEPR_MSG.format("getLowerLeft_y", "bottom"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.bottom

    def getUpperRight_x(self):
        warnings.warn(
            DEPR_MSG.format("getUpperRight_x", "right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.right

    def getUpperRight_y(self):
        warnings.warn(
            DEPR_MSG.format("getUpperRight_y", "top"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.top

    def getUpperLeft_x(self):
        warnings.warn(
            DEPR_MSG.format("getUpperLeft_x", "left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.left

    def getUpperLeft_y(self):
        warnings.warn(
            DEPR_MSG.format("getUpperLeft_y", "top"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.top

    def getLowerRight_x(self):
        warnings.warn(
            DEPR_MSG.format("getLowerRight_x", "right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.right

    def getLowerRight_y(self):
        warnings.warn(
            DEPR_MSG.format("getLowerRight_y", "bottom"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.bottom

    @property
    def lower_left(self):
        """
        Property to read and modify the lower left coordinate of this box
        in (x,y) form.
        """
        return self.left, self.bottom

    @lower_left.setter
    def lower_left(self, value):
        self[0], self[1] = [self._ensure_is_number(x) for x in value]

    @property
    def lower_right(self):
        """
        Property to read and modify the lower right coordinate of this box
        in (x,y) form.
        """
        return self.right, self.bottom

    @lower_right.setter
    def lower_right(self, value):
        self[2], self[1] = [self._ensure_is_number(x) for x in value]

    @property
    def upper_left(self):
        """
        Property to read and modify the upper left coordinate of this box
        in (x,y) form.
        """
        return self.left, self.top

    @upper_left.setter
    def upper_left(self, value):
        self[0], self[3] = [self._ensure_is_number(x) for x in value]

    @property
    def upper_right(self):
        """
        Property to read and modify the upper right coordinate of this box
        in (x,y) form.
        """
        return self.right, self.top

    @upper_right.setter
    def upper_right(self, value):
        self[2], self[3] = [self._ensure_is_number(x) for x in value]

    def getLowerLeft(self):
        warnings.warn(
            DEPR_MSG.format("getLowerLeft", "lower_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.lower_left

    def getLowerRight(self):
        warnings.warn(
            DEPR_MSG.format("getLowerRight", "lower_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.lower_right

    def getUpperLeft(self):
        warnings.warn(
            DEPR_MSG.format("getUpperLeft", "upper_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.upper_left

    def getUpperRight(self):
        warnings.warn(
            DEPR_MSG.format("getUpperRight", "upper_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.upper_right

    def setLowerLeft(self, value):
        warnings.warn(
            DEPR_MSG.format("setLowerLeft", "lower_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.lower_left = value

    def setLowerRight(self, value):
        warnings.warn(
            DEPR_MSG.format("setLowerRight", "lower_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self[2], self[1] = [self._ensure_is_number(x) for x in value]

    def setUpperLeft(self, value):
        warnings.warn(
            DEPR_MSG.format("setUpperLeft", "upper_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self[0], self[3] = [self._ensure_is_number(x) for x in value]

    def setUpperRight(self, value):
        warnings.warn(
            DEPR_MSG.format("setUpperRight", "upper_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self[2], self[3] = [self._ensure_is_number(x) for x in value]

    @property
    def width(self):
        return self.right - self.left

    def getWidth(self):
        warnings.warn(DEPR_MSG.format("getWidth", "width"), DeprecationWarning)
        return self.width

    @property
    def height(self):
        return self.top - self.bottom

    def getHeight(self):
        warnings.warn(DEPR_MSG.format("getHeight", "height"), DeprecationWarning)
        return self.height

    @property
    def lowerLeft(self):
        warnings.warn(
            DEPR_MSG.format("lowerLeft", "lower_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.lower_left

    @lowerLeft.setter
    def lowerLeft(self, value):
        warnings.warn(
            DEPR_MSG.format("lowerLeft", "lower_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.lower_left = value

    @property
    def lowerRight(self):
        warnings.warn(
            DEPR_MSG.format("lowerRight", "lower_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.lower_right

    @lowerRight.setter
    def lowerRight(self, value):
        warnings.warn(
            DEPR_MSG.format("lowerRight", "lower_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.lower_right = value

    @property
    def upperLeft(self):
        warnings.warn(
            DEPR_MSG.format("upperLeft", "upper_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.upper_left

    @upperLeft.setter
    def upperLeft(self, value):
        warnings.warn(
            DEPR_MSG.format("upperLeft", "upper_left"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.upper_left = value

    @property
    def upperRight(self):
        warnings.warn(
            DEPR_MSG.format("upperRight", "upper_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.upper_right

    @upperRight.setter
    def upperRight(self, value):
        warnings.warn(
            DEPR_MSG.format("upperRight", "upper_right"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.upper_right = value


class Field(TreeObject):
    """
    A class representing a field dictionary. This class is accessed through
    :meth:`get_fields()<PyPDF2.PdfReader.get_fields>`
    """

    def __init__(self, data):
        DictionaryObject.__init__(self)
        attributes = (
            "/FT",
            "/Parent",
            "/Kids",
            "/T",
            "/TU",
            "/TM",
            "/Ff",
            "/V",
            "/DV",
            "/AA",
        )
        for attr in attributes:
            try:
                self[NameObject(attr)] = data[attr]
            except KeyError:
                pass

    @property
    def field_type(self):
        """Read-only property accessing the type of this field."""
        return self.get("/FT")

    @property
    def fieldType(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`field_type` instead.
        """
        warnings.warn(
            "fieldType will be removed in PyPDF2 2.0.0. "
            "Use the field_type property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.field_type

    @property
    def parent(self):
        """Read-only property accessing the parent of this field."""
        return self.get("/Parent")

    @property
    def kids(self):
        """Read-only property accessing the kids of this field."""
        return self.get("/Kids")

    @property
    def name(self):
        """Read-only property accessing the name of this field."""
        return self.get("/T")

    @property
    def alternate_name(self):
        """Read-only property accessing the alternate name of this field."""
        return self.get("/TU")

    @property
    def altName(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`alternate_name` instead.
        """
        warnings.warn(
            "altName will be removed in PyPDF2 2.0.0. "
            "Use the alternate_name property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.alternate_name

    @property
    def mapping_name(self):
        """
        Read-only property accessing the mapping name of this field. This
        name is used by PyPDF2 as a key in the dictionary returned by
        :meth:`get_fields()<PyPDF2.PdfReader.get_fields>`
        """
        return self.get("/TM")

    @property
    def mappingName(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`mapping_name` instead.
        """
        warnings.warn(
            "mappingName will be removed in PyPDF2 2.0.0. "
            "Use the mapping_name property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.mapping_name

    @property
    def flags(self):
        """
        Read-only property accessing the field flags, specifying various
        characteristics of the field (see Table 8.70 of the PDF 1.7 reference).
        """
        return self.get("/Ff")

    @property
    def value(self):
        """
        Read-only property accessing the value of this field. Format
        varies based on field type.
        """
        return self.get("/V")

    @property
    def default_value(self):
        """Read-only property accessing the default value of this field."""
        return self.get("/DV")

    @property
    def defaultValue(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`default_value` instead.
        """
        warnings.warn(
            "defaultValue will be removed in PyPDF2 2.0.0. "
            "Use the default_value property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.default_value

    @property
    def additional_actions(self):
        """
        Read-only property accessing the additional actions dictionary.
        This dictionary defines the field's behavior in response to trigger events.
        See Section 8.5.2 of the PDF 1.7 reference.
        """
        self.get("/AA")

    @property
    def additionalActions(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`additional_actions` instead.
        """
        warnings.warn(
            "additionalActions will be removed in PyPDF2 2.0.0. "
            "Use the additional_actions property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.additional_actions


class Destination(TreeObject):
    """
    A class representing a destination within a PDF file.
    See section 8.2.1 of the PDF 1.6 reference.

    :param str title: Title of this destination.
    :param IndirectObject page: Reference to the page of this destination. Should
        be an instance of :class:`IndirectObject<PyPDF2.generic.IndirectObject>`.
    :param str typ: How the destination is displayed.
    :param args: Additional arguments may be necessary depending on the type.
    :raises PdfReadError: If destination type is invalid.

    .. list-table:: Valid ``typ`` arguments (see PDF spec for details)
       :widths: 50 50

       * - /Fit
         - No additional arguments
       * - /XYZ
         - [left] [top] [zoomFactor]
       * - /FitH
         - [top]
       * - /FitV
         - [left]
       * - /FitR
         - [left] [bottom] [right] [top]
       * - /FitB
         - No additional arguments
       * - /FitBH
         - [top]
       * - /FitBV
         - [left]
    """

    def __init__(self, title, page, typ, *args):
        DictionaryObject.__init__(self)
        self[NameObject("/Title")] = title
        self[NameObject("/Page")] = page
        self[NameObject("/Type")] = typ

        from PyPDF2.constants import TypArguments as TA
        from PyPDF2.constants import TypFitArguments as TF

        # from table 8.2 of the PDF 1.7 reference.
        if typ == "/XYZ":
            (
                self[NameObject(TA.LEFT)],
                self[NameObject(TA.TOP)],
                self[NameObject("/Zoom")],
            ) = args
        elif typ == TF.FIT_R:
            (
                self[NameObject(TA.LEFT)],
                self[NameObject(TA.BOTTOM)],
                self[NameObject(TA.RIGHT)],
                self[NameObject(TA.TOP)],
            ) = args
        elif typ in [TF.FIT_H, TF.FIT_BH]:
            (self[NameObject(TA.TOP)],) = args
        elif typ in [TF.FIT_V, TF.FIT_BV]:
            (self[NameObject(TA.LEFT)],) = args
        elif typ in [TF.FIT, TF.FIT_B]:
            pass
        else:
            raise PdfReadError("Unknown Destination Type: %r" % typ)

    @property
    def dest_array(self):
        return ArrayObject(
            [self.raw_get("/Page"), self["/Type"]]
            + [
                self[x]
                for x in ["/Left", "/Bottom", "/Right", "/Top", "/Zoom"]
                if x in self
            ]
        )

    def getDestArray(self):
        """
        .. deprecated:: 1.28.3
            Use :py:attr:`dest_array` instead.
        """
        warnings.warn(
            "getDestArray will be removed in PyPDF2 2.0.0. "
            "Use the dest_array property instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.dest_array

    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("<<\n"))
        key = NameObject("/D")
        key.write_to_stream(stream, encryption_key)
        stream.write(b_(" "))
        value = self.dest_array
        value.write_to_stream(stream, encryption_key)

        key = NameObject("/S")
        key.write_to_stream(stream, encryption_key)
        stream.write(b_(" "))
        value = NameObject("/GoTo")
        value.write_to_stream(stream, encryption_key)

        stream.write(b_("\n"))
        stream.write(b_(">>"))

    @property
    def title(self):
        """
        Read-only property accessing the destination title.

        :rtype: str
        """
        return self.get("/Title")

    @property
    def page(self):
        """
        Read-only property accessing the destination page number.

        :rtype: int
        """
        return self.get("/Page")

    @property
    def typ(self):
        """
        Read-only property accessing the destination type.

        :rtype: str
        """
        return self.get("/Type")

    @property
    def zoom(self):
        """
        Read-only property accessing the zoom factor.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Zoom", None)

    @property
    def left(self):
        """
        Read-only property accessing the left horizontal coordinate.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Left", None)

    @property
    def right(self):
        """
        Read-only property accessing the right horizontal coordinate.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Right", None)

    @property
    def top(self):
        """
        Read-only property accessing the top vertical coordinate.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Top", None)

    @property
    def bottom(self):
        """
        Read-only property accessing the bottom vertical coordinate.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Bottom", None)


class Bookmark(Destination):
    def write_to_stream(self, stream, encryption_key):
        stream.write(b_("<<\n"))
        for key in [
            NameObject(x)
            for x in ["/Title", "/Parent", "/First", "/Last", "/Next", "/Prev"]
            if x in self
        ]:
            key.write_to_stream(stream, encryption_key)
            stream.write(b_(" "))
            value = self.raw_get(key)
            value.write_to_stream(stream, encryption_key)
            stream.write(b_("\n"))
        key = NameObject("/Dest")
        key.write_to_stream(stream, encryption_key)
        stream.write(b_(" "))
        value = self.dest_array
        value.write_to_stream(stream, encryption_key)
        stream.write(b_("\n"))
        stream.write(b_(">>"))


def encode_pdfdocencoding(unicode_string):
    retval = b_("")
    for c in unicode_string:
        try:
            retval += b_(chr(_pdfDocEncoding_rev[c]))
        except KeyError:
            raise UnicodeEncodeError(
                "pdfdocencoding", c, -1, -1, "does not exist in translation table"
            )
    return retval


def decode_pdfdocencoding(byte_array):
    retval = u_("")
    for b in byte_array:
        c = _pdfDocEncoding[ord_(b)]
        if c == u_("\u0000"):
            raise UnicodeDecodeError(
                "pdfdocencoding",
                _utils.barray(b),
                -1,
                -1,
                "does not exist in translation table",
            )
        retval += c
    return retval


# PDFDocEncoding Character Set: Table D.2 of PDF Reference 1.7
# C.1 Predefined encodings sorted by character name of another PDF reference
# Some indices have '\u0000' although they should have something else:
# 22: should be '\u0017'
_pdfDocEncoding = (
    u_("\u0000"),
    u_("\u0001"),
    u_("\u0002"),
    u_("\u0003"),
    u_("\u0004"),
    u_("\u0005"),
    u_("\u0006"),
    u_("\u0007"),  #  0 -  7
    u_("\u0008"),
    u_("\u0009"),
    u_("\u000a"),
    u_("\u000b"),
    u_("\u000c"),
    u_("\u000d"),
    u_("\u000e"),
    u_("\u000f"),  #  8 - 15
    u_("\u0010"),
    u_("\u0011"),
    u_("\u0012"),
    u_("\u0013"),
    u_("\u0014"),
    u_("\u0015"),
    u_("\u0000"),
    u_("\u0017"),  # 16 - 23
    u_("\u02d8"),
    u_("\u02c7"),
    u_("\u02c6"),
    u_("\u02d9"),
    u_("\u02dd"),
    u_("\u02db"),
    u_("\u02da"),
    u_("\u02dc"),  # 24 - 31
    u_("\u0020"),
    u_("\u0021"),
    u_("\u0022"),
    u_("\u0023"),
    u_("\u0024"),
    u_("\u0025"),
    u_("\u0026"),
    u_("\u0027"),  # 32 - 39
    u_("\u0028"),
    u_("\u0029"),
    u_("\u002a"),
    u_("\u002b"),
    u_("\u002c"),
    u_("\u002d"),
    u_("\u002e"),
    u_("\u002f"),  # 40 - 47
    u_("\u0030"),
    u_("\u0031"),
    u_("\u0032"),
    u_("\u0033"),
    u_("\u0034"),
    u_("\u0035"),
    u_("\u0036"),
    u_("\u0037"),  # 48 - 55
    u_("\u0038"),
    u_("\u0039"),
    u_("\u003a"),
    u_("\u003b"),
    u_("\u003c"),
    u_("\u003d"),
    u_("\u003e"),
    u_("\u003f"),  # 56 - 63
    u_("\u0040"),
    u_("\u0041"),
    u_("\u0042"),
    u_("\u0043"),
    u_("\u0044"),
    u_("\u0045"),
    u_("\u0046"),
    u_("\u0047"),  # 64 - 71
    u_("\u0048"),
    u_("\u0049"),
    u_("\u004a"),
    u_("\u004b"),
    u_("\u004c"),
    u_("\u004d"),
    u_("\u004e"),
    u_("\u004f"),  # 72 - 79
    u_("\u0050"),
    u_("\u0051"),
    u_("\u0052"),
    u_("\u0053"),
    u_("\u0054"),
    u_("\u0055"),
    u_("\u0056"),
    u_("\u0057"),  # 80 - 87
    u_("\u0058"),
    u_("\u0059"),
    u_("\u005a"),
    u_("\u005b"),
    u_("\u005c"),
    u_("\u005d"),
    u_("\u005e"),
    u_("\u005f"),  # 88 - 95
    u_("\u0060"),
    u_("\u0061"),
    u_("\u0062"),
    u_("\u0063"),
    u_("\u0064"),
    u_("\u0065"),
    u_("\u0066"),
    u_("\u0067"),  # 96 - 103
    u_("\u0068"),
    u_("\u0069"),
    u_("\u006a"),
    u_("\u006b"),
    u_("\u006c"),
    u_("\u006d"),
    u_("\u006e"),
    u_("\u006f"),  # 104 - 111
    u_("\u0070"),
    u_("\u0071"),
    u_("\u0072"),
    u_("\u0073"),
    u_("\u0074"),
    u_("\u0075"),
    u_("\u0076"),
    u_("\u0077"),  # 112 - 119
    u_("\u0078"),
    u_("\u0079"),
    u_("\u007a"),
    u_("\u007b"),
    u_("\u007c"),
    u_("\u007d"),
    u_("\u007e"),
    u_("\u0000"),  # 120 - 127
    u_("\u2022"),
    u_("\u2020"),
    u_("\u2021"),
    u_("\u2026"),
    u_("\u2014"),
    u_("\u2013"),
    u_("\u0192"),
    u_("\u2044"),  # 128 - 135
    u_("\u2039"),
    u_("\u203a"),
    u_("\u2212"),
    u_("\u2030"),
    u_("\u201e"),
    u_("\u201c"),
    u_("\u201d"),
    u_("\u2018"),  # 136 - 143
    u_("\u2019"),
    u_("\u201a"),
    u_("\u2122"),
    u_("\ufb01"),
    u_("\ufb02"),
    u_("\u0141"),
    u_("\u0152"),
    u_("\u0160"),  # 144 - 151
    u_("\u0178"),
    u_("\u017d"),
    u_("\u0131"),
    u_("\u0142"),
    u_("\u0153"),
    u_("\u0161"),
    u_("\u017e"),
    u_("\u0000"),  # 152 - 159
    u_("\u20ac"),
    u_("\u00a1"),
    u_("\u00a2"),
    u_("\u00a3"),
    u_("\u00a4"),
    u_("\u00a5"),
    u_("\u00a6"),
    u_("\u00a7"),  # 160 - 167
    u_("\u00a8"),
    u_("\u00a9"),
    u_("\u00aa"),
    u_("\u00ab"),
    u_("\u00ac"),
    u_("\u0000"),
    u_("\u00ae"),
    u_("\u00af"),  # 168 - 175
    u_("\u00b0"),
    u_("\u00b1"),
    u_("\u00b2"),
    u_("\u00b3"),
    u_("\u00b4"),
    u_("\u00b5"),
    u_("\u00b6"),
    u_("\u00b7"),  # 176 - 183
    u_("\u00b8"),
    u_("\u00b9"),
    u_("\u00ba"),
    u_("\u00bb"),
    u_("\u00bc"),
    u_("\u00bd"),
    u_("\u00be"),
    u_("\u00bf"),  # 184 - 191
    u_("\u00c0"),
    u_("\u00c1"),
    u_("\u00c2"),
    u_("\u00c3"),
    u_("\u00c4"),
    u_("\u00c5"),
    u_("\u00c6"),
    u_("\u00c7"),  # 192 - 199
    u_("\u00c8"),
    u_("\u00c9"),
    u_("\u00ca"),
    u_("\u00cb"),
    u_("\u00cc"),
    u_("\u00cd"),
    u_("\u00ce"),
    u_("\u00cf"),  # 200 - 207
    u_("\u00d0"),
    u_("\u00d1"),
    u_("\u00d2"),
    u_("\u00d3"),
    u_("\u00d4"),
    u_("\u00d5"),
    u_("\u00d6"),
    u_("\u00d7"),  # 208 - 215
    u_("\u00d8"),
    u_("\u00d9"),
    u_("\u00da"),
    u_("\u00db"),
    u_("\u00dc"),
    u_("\u00dd"),
    u_("\u00de"),
    u_("\u00df"),  # 216 - 223
    u_("\u00e0"),
    u_("\u00e1"),
    u_("\u00e2"),
    u_("\u00e3"),
    u_("\u00e4"),
    u_("\u00e5"),
    u_("\u00e6"),
    u_("\u00e7"),  # 224 - 231
    u_("\u00e8"),
    u_("\u00e9"),
    u_("\u00ea"),
    u_("\u00eb"),
    u_("\u00ec"),
    u_("\u00ed"),
    u_("\u00ee"),
    u_("\u00ef"),  # 232 - 239
    u_("\u00f0"),
    u_("\u00f1"),
    u_("\u00f2"),
    u_("\u00f3"),
    u_("\u00f4"),
    u_("\u00f5"),
    u_("\u00f6"),
    u_("\u00f7"),  # 240 - 247
    u_("\u00f8"),
    u_("\u00f9"),
    u_("\u00fa"),
    u_("\u00fb"),
    u_("\u00fc"),
    u_("\u00fd"),
    u_("\u00fe"),
    u_("\u00ff"),  # 248 - 255
)

assert len(_pdfDocEncoding) == 256

_pdfDocEncoding_rev = {}
for i in range(256):
    char = _pdfDocEncoding[i]
    if char == u_("\u0000"):
        continue
    assert char not in _pdfDocEncoding_rev, (
        str(char) + " at " + str(i) + " already at " + str(_pdfDocEncoding_rev[char])
    )
    _pdfDocEncoding_rev[char] = i
