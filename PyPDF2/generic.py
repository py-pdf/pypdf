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
import warnings
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

from ._utils import (
    WHITESPACES,
    StreamType,
    b_,
    bytes_type,
    deprecate_no_replacement,
    deprecate_with_replacement,
    hex_str,
    hexencode,
    ord_,
    read_non_whitespace,
    read_until_regex,
    skip_over_comment,
    str_,
)
from .constants import FilterTypes as FT
from .constants import StreamAttributes as SA
from .constants import TypArguments as TA
from .constants import TypFitArguments as TF
from .errors import (
    STREAM_TRUNCATED_PREMATURELY,
    PdfReadError,
    PdfReadWarning,
    PdfStreamError,
)

logger = logging.getLogger(__name__)
ObjectPrefix = b_("/<[tf(n%")
NumberSigns = b_("+-")
IndirectPattern = re.compile(b_(r"[+-]?(\d+)\s+(\d+)\s+R[^a-zA-Z]"))


class PdfObject:
    def get_object(self) -> Optional["PdfObject"]:
        """Resolve indirect references."""
        return self

    def getObject(self) -> Optional["PdfObject"]:  # pragma: no cover
        deprecate_with_replacement("getObject", "get_object")
        return self.get_object()

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        raise NotImplementedError


class NullObject(PdfObject):
    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_("null"))

    @staticmethod
    def read_from_stream(stream: StreamType) -> "NullObject":
        nulltxt = stream.read(4)
        if nulltxt != b_("null"):
            raise PdfReadError("Could not read Null object")
        return NullObject()

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def readFromStream(stream: StreamType) -> "NullObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return NullObject.read_from_stream(stream)


class BooleanObject(PdfObject):
    def __init__(self, value: Any) -> None:
        self.value = value

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, BooleanObject):
            return self.value == __o.value
        elif isinstance(__o, bool):
            return self.value == __o
        else:
            return False

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        if self.value:
            stream.write(b_("true"))
        else:
            stream.write(b_("false"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream: StreamType) -> "BooleanObject":
        word = stream.read(4)
        if word == b_("true"):
            return BooleanObject(True)
        elif word == b_("fals"):
            stream.read(1)
            return BooleanObject(False)
        else:
            raise PdfReadError("Could not read Boolean object")

    @staticmethod
    def readFromStream(stream: StreamType) -> "BooleanObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return BooleanObject.read_from_stream(stream)


class ArrayObject(list, PdfObject):
    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_("["))
        for data in self:
            stream.write(b_(" "))
            data.write_to_stream(stream, encryption_key)
        stream.write(b_(" ]"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(
        stream: StreamType,
        pdf: Any,
        forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
    ) -> "ArrayObject":  # PdfReader
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
            arr.append(read_object(stream, pdf, forced_encoding))
        return arr

    @staticmethod
    def readFromStream(
        stream: StreamType, pdf: Any  # PdfReader
    ) -> "ArrayObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return ArrayObject.read_from_stream(stream, pdf)


class IndirectObject(PdfObject):
    def __init__(self, idnum: int, generation: int, pdf: Any) -> None:  # PdfReader
        self.idnum = idnum
        self.generation = generation
        self.pdf = pdf

    def get_object(self) -> Optional[PdfObject]:
        return self.pdf.get_object(self).get_object()

    def __repr__(self) -> str:
        return f"IndirectObject({self.idnum!r}, {self.generation!r})"

    def __eq__(self, other: Any) -> bool:
        return (
            other is not None
            and isinstance(other, IndirectObject)
            and self.idnum == other.idnum
            and self.generation == other.generation
            and self.pdf is other.pdf
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_(f"{self.idnum} {self.generation} R"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream: StreamType, pdf: Any) -> "IndirectObject":  # PdfReader
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
        r = read_non_whitespace(stream)
        if r != b_("R"):
            raise PdfReadError(
                "Error reading indirect object reference at byte %s"
                % hex_str(stream.tell())
            )
        return IndirectObject(int(idnum), int(generation), pdf)

    @staticmethod
    def readFromStream(
        stream: StreamType, pdf: Any  # PdfReader
    ) -> "IndirectObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return IndirectObject.read_from_stream(stream, pdf)


class FloatObject(decimal.Decimal, PdfObject):
    def __new__(
        cls, value: Union[str, Any] = "0", context: Optional[Any] = None
    ) -> "FloatObject":
        try:
            return decimal.Decimal.__new__(cls, str_(value), context)
        except Exception:
            try:
                return decimal.Decimal.__new__(cls, str(value))
            except decimal.InvalidOperation:
                # If this isn't a valid decimal (happens in malformed PDFs)
                # fallback to 0
                logger.warning(f"Invalid FloatObject {value}")
                return decimal.Decimal.__new__(cls, "0")

    def __repr__(self) -> str:
        if self == self.to_integral():
            return str(self.quantize(decimal.Decimal(1)))
        else:
            # Standard formatting adds useless extraneous zeros.
            o = "%.5f" % self
            # Remove the zeros.
            while o and o[-1] == "0":
                o = o[:-1]
            return o

    def as_numeric(self) -> float:
        return float(b_(repr(self)))

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_(repr(self)))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)


class NumberObject(int, PdfObject):
    NumberPattern = re.compile(b_("[^+-.0-9]"))
    ByteDot = b_(".")

    def __new__(cls, value: Any) -> "NumberObject":
        val = int(value)
        try:
            return int.__new__(cls, val)
        except OverflowError:
            return int.__new__(cls, 0)

    def as_numeric(self) -> int:
        return int(b_(repr(self)))

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_(repr(self)))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream: StreamType) -> Union["NumberObject", FloatObject]:
        num = read_until_regex(stream, NumberObject.NumberPattern)
        if num.find(NumberObject.ByteDot) != -1:
            return FloatObject(num)
        else:
            return NumberObject(num)

    @staticmethod
    def readFromStream(
        stream: StreamType,
    ) -> Union["NumberObject", FloatObject]:  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return NumberObject.read_from_stream(stream)


def readHexStringFromStream(  # TODO: PEP8
    stream: StreamType,
) -> Union["TextStringObject", "ByteStringObject"]:
    stream.read(1)
    txt = ""
    x = b_("")
    while True:
        tok = read_non_whitespace(stream)
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


def readStringFromStream(  # TODO: PEP8
    stream: StreamType,
    forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
) -> Union["TextStringObject", "ByteStringObject"]:
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
    return createStringObject(txt, forced_encoding)


class ByteStringObject(bytes_type, PdfObject):  # type: ignore
    """
    Represents a string object where the text encoding could not be determined.
    This occurs quite often, as the PDF spec doesn't provide an alternate way to
    represent strings -- for example, the encryption data stored in files (like
    /O) is clearly not text, but is still stored in a "String" object.
    """

    @property
    def original_bytes(self) -> bytes:
        """For compatibility with TextStringObject.original_bytes."""
        return self

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        bytearr = self
        if encryption_key:
            from ._security import RC4_encrypt

            bytearr = RC4_encrypt(encryption_key, bytearr)  # type: ignore
        stream.write(b_("<"))
        stream.write(hexencode(bytearr))
        stream.write(b_(">"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)


class TextStringObject(str, PdfObject):
    """
    Represents a string object that has been decoded into a real unicode string.
    If read from a PDF document, this string appeared to match the
    PDFDocEncoding, or contained a UTF-16BE BOM mark to cause UTF-16 decoding to
    occur.
    """

    autodetect_pdfdocencoding = False
    autodetect_utf16 = False

    @property
    def original_bytes(self) -> bytes:
        """
        It is occasionally possible that a text string object gets created where
        a byte string object was expected due to the autodetection mechanism --
        if that occurs, this "original_bytes" property can be used to
        back-calculate what the original encoded bytes were.
        """
        return self.get_original_bytes()

    def get_original_bytes(self) -> bytes:
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

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        # Try to write the string out as a PDFDocEncoding encoded string.  It's
        # nicer to look at in the PDF file.  Sadly, we take a performance hit
        # here for trying...
        try:
            bytearr = encode_pdfdocencoding(self)
        except UnicodeEncodeError:
            bytearr = codecs.BOM_UTF16_BE + self.encode("utf-16be")
        if encryption_key:
            from ._security import RC4_encrypt

            bytearr = RC4_encrypt(encryption_key, bytearr)
            obj = ByteStringObject(bytearr)
            obj.write_to_stream(stream, None)
        else:
            stream.write(b_("("))
            for c in bytearr:
                if not chr(c).isalnum() and c != b_(" "):
                    stream.write(b_("\\%03o" % ord_(c)))
                else:
                    stream.write(b_(chr(c)))
            stream.write(b_(")"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)


class NameObject(str, PdfObject):
    delimiter_pattern = re.compile(b_(r"\s+|[\(\)<>\[\]{}/%]"))
    surfix = b_("/")

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_(self))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream: StreamType, pdf: Any) -> "NameObject":  # PdfReader
        name = stream.read(1)
        if name != NameObject.surfix:
            raise PdfReadError("name read error")
        name += read_until_regex(stream, NameObject.delimiter_pattern, ignore_eof=True)
        try:
            try:
                ret = name.decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                ret = name.decode("gbk")
            return NameObject(ret)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # Name objects should represent irregular characters
            # with a '#' followed by the symbol's hex number
            if not pdf.strict:
                warnings.warn("Illegal character in Name Object", PdfReadWarning)
                return NameObject(name)
            else:
                raise PdfReadError("Illegal character in Name Object") from e

    @staticmethod
    def readFromStream(
        stream: StreamType, pdf: Any  # PdfReader
    ) -> "NameObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return NameObject.read_from_stream(stream, pdf)


class DictionaryObject(dict, PdfObject):
    def raw_get(self, key: Any) -> Any:
        return dict.__getitem__(self, key)

    def __setitem__(self, key: Any, value: Any) -> Any:
        if not isinstance(key, PdfObject):
            raise ValueError("key must be PdfObject")
        if not isinstance(value, PdfObject):
            raise ValueError("value must be PdfObject")
        return dict.__setitem__(self, key, value)

    def setdefault(self, key: Any, value: Optional[Any] = None) -> Any:
        if not isinstance(key, PdfObject):
            raise ValueError("key must be PdfObject")
        if not isinstance(value, PdfObject):
            raise ValueError("value must be PdfObject")
        return dict.setdefault(self, key, value)  # type: ignore

    def __getitem__(self, key: Any) -> PdfObject:
        return dict.__getitem__(self, key).get_object()

    @property
    def xmp_metadata(self) -> Optional[PdfObject]:
        """
        Retrieve XMP (Extensible Metadata Platform) data relevant to the
        this object, if available.

        Stability: Added in v1.12, will exist for all future v1.x releases.
        @return Returns a {@link #xmp.XmpInformation XmlInformation} instance
        that can be used to access XMP metadata from the document.  Can also
        return None if no metadata was found on the document root.
        """
        from .xmp import XmpInformation

        metadata = self.get("/Metadata", None)
        if metadata is None:
            return None
        metadata = metadata.get_object()

        if not isinstance(metadata, XmpInformation):
            metadata = XmpInformation(metadata)
            self[NameObject("/Metadata")] = metadata
        return metadata

    def getXmpMetadata(
        self,
    ) -> Optional[PdfObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :meth:`xmp_metadata` instead.
        """
        deprecate_with_replacement("getXmpMetadata", "xmp_metadata")
        return self.xmp_metadata

    @property
    def xmpMetadata(self) -> Optional[PdfObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :meth:`xmp_metadata` instead.
        """
        deprecate_with_replacement("xmpMetadata", "xmp_metadata")
        return self.xmp_metadata

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_("<<\n"))
        for key, value in list(self.items()):
            key.write_to_stream(stream, encryption_key)
            stream.write(b_(" "))
            value.write_to_stream(stream, encryption_key)
            stream.write(b_("\n"))
        stream.write(b_(">>"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(
        stream: StreamType,
        pdf: Any,  # PdfReader
        forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
    ) -> "DictionaryObject":
        def get_next_obj_pos(
            p: int, p1: int, rem_gens: List[int], pdf: Any
        ) -> int:  # PdfReader
            l = pdf.xref[rem_gens[0]]
            for o in l:
                if p1 > l[o] and p < l[o]:
                    p1 = l[o]
            if len(rem_gens) == 1:
                return p1
            else:
                return get_next_obj_pos(p, p1, rem_gens[1:], pdf)

        def read_unsized_from_steam(stream: StreamType, pdf: Any) -> bytes:  # PdfReader
            # we are just pointing at beginning of the stream
            eon = get_next_obj_pos(stream.tell(), 2**32, list(pdf.xref), pdf) - 1
            curr = stream.tell()
            rw = stream.read(eon - stream.tell())
            p = rw.find(b_("endstream"))
            if p < 0:
                raise PdfReadError(
                    f"Unable to find 'endstream' marker for obj starting at {curr}."
                )
            stream.seek(curr + p + 9)
            return rw[: p - 1]

        tmp = stream.read(2)
        if tmp != b_("<<"):
            raise PdfReadError(
                "Dictionary read error at byte %s: stream must begin with '<<'"
                % hex_str(stream.tell())
            )
        data: Dict[Any, Any] = {}
        while True:
            tok = read_non_whitespace(stream)
            if tok == b_("\x00"):
                continue
            elif tok == b_("%"):
                stream.seek(-1, 1)
                skip_over_comment(stream)
                continue
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)

            if tok == b_(">"):
                stream.read(1)
                break
            stream.seek(-1, 1)
            key = read_object(stream, pdf)
            tok = read_non_whitespace(stream)
            stream.seek(-1, 1)
            value = read_object(stream, pdf, forced_encoding)
            if not data.get(key):
                data[key] = value
            elif pdf.strict:
                # multiple definitions of key not permitted
                raise PdfReadError(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (hex_str(stream.tell()), key)
                )
            else:
                warnings.warn(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (hex_str(stream.tell()), key),
                    PdfReadWarning,
                )

        pos = stream.tell()
        s = read_non_whitespace(stream)
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
            pstart = stream.tell()
            data["__streamdata__"] = stream.read(length)
            e = read_non_whitespace(stream)
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
                elif not pdf.strict:
                    stream.seek(pstart, 0)
                    data["__streamdata__"] = read_unsized_from_steam(stream, pdf)
                    pos = stream.tell()
                else:
                    stream.seek(pos, 0)
                    raise PdfReadError(
                        "Unable to find 'endstream' marker after stream at byte %s."
                        % hex_str(stream.tell())
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
    def readFromStream(
        stream: StreamType, pdf: Any  # PdfReader
    ) -> "DictionaryObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return DictionaryObject.read_from_stream(stream, pdf)


class TreeObject(DictionaryObject):
    def __init__(self) -> None:
        DictionaryObject.__init__(self)

    def hasChildren(self) -> bool:
        return "/First" in self

    def __iter__(self) -> Any:
        return self.children()

    def children(self) -> Optional[Any]:
        if not self.hasChildren():
            return

        child = self["/First"]
        while True:
            yield child
            if child == self["/Last"]:
                return
            child = child["/Next"]  # type: ignore

    def addChild(self, child: Any, pdf: Any) -> None:  # pragma: no cover
        deprecate_with_replacement("addChild", "add_child")
        self.add_child(child, pdf)

    def add_child(self, child: Any, pdf: Any) -> None:  # PdfReader
        child_obj = child.get_object()
        child = pdf.get_reference(child_obj)
        assert isinstance(child, IndirectObject)

        if "/First" not in self:
            self[NameObject("/First")] = child
            self[NameObject("/Count")] = NumberObject(0)
            prev = None
        else:
            prev = self["/Last"]

        self[NameObject("/Last")] = child
        self[NameObject("/Count")] = NumberObject(self[NameObject("/Count")] + 1)  # type: ignore

        if prev:
            prev_ref = pdf.get_reference(prev)
            assert isinstance(prev_ref, IndirectObject)
            child_obj[NameObject("/Prev")] = prev_ref
            prev[NameObject("/Next")] = child  # type: ignore

        parent_ref = pdf.get_reference(self)
        assert isinstance(parent_ref, IndirectObject)
        child_obj[NameObject("/Parent")] = parent_ref

    def removeChild(self, child: Any) -> None:  # pragma: no cover
        deprecate_with_replacement("removeChild", "remove_child")
        self.remove_child(child)

    def remove_child(self, child: Any) -> None:
        child_obj = child.get_object()

        if NameObject("/Parent") not in child_obj:
            raise ValueError("Removed child does not appear to be a tree item")
        elif child_obj[NameObject("/Parent")] != self:
            raise ValueError("Removed child is not a member of this tree")

        found = False
        prev_ref = None
        prev = None
        cur_ref: Optional[Any] = self[NameObject("/First")]
        cur: Optional[Dict[str, Any]] = cur_ref.get_object()  # type: ignore
        last_ref = self[NameObject("/Last")]
        last = last_ref.get_object()
        while cur is not None:
            if cur == child_obj:
                if prev is None:
                    if NameObject("/Next") in cur:
                        # Removing first tree node
                        next_ref = cur[NameObject("/Next")]
                        next_obj = next_ref.get_object()
                        del next_obj[NameObject("/Prev")]
                        self[NameObject("/First")] = next_ref
                        self[NameObject("/Count")] -= 1  # type: ignore

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
                        next_obj = next_ref.get_object()
                        next_obj[NameObject("/Prev")] = prev_ref
                        prev[NameObject("/Next")] = next_ref
                        self[NameObject("/Count")] -= 1
                    else:
                        # Removing last tree node
                        assert cur == last
                        del prev[NameObject("/Next")]
                        self[NameObject("/Last")] = prev_ref
                        self[NameObject("/Count")] -= 1
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

    def emptyTree(self) -> None:
        # TODO: Missing rename
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
    def __init__(self) -> None:
        self.__data: Optional[str] = None
        self.decoded_self: Optional[DecodedStreamObject] = None

    @property
    def decodedSelf(self) -> Optional["DecodedStreamObject"]:  # pragma: no cover
        deprecate_with_replacement("decodedSelf", "decoded_self")
        return self.decoded_self

    @decodedSelf.setter
    def decodedSelf(self, value: "DecodedStreamObject") -> None:  # pragma: no cover
        deprecate_with_replacement("decodedSelf", "decoded_self")
        self.decoded_self = value

    @property
    def _data(self) -> Any:
        return self.__data

    @_data.setter
    def _data(self, value: Any) -> None:
        self.__data = value

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        self[NameObject(SA.LENGTH)] = NumberObject(len(self._data))
        DictionaryObject.write_to_stream(self, stream, encryption_key)
        del self[SA.LENGTH]
        stream.write(b_("\nstream\n"))
        data = self._data
        if encryption_key:
            from ._security import RC4_encrypt

            data = RC4_encrypt(encryption_key, data)
        stream.write(data)
        stream.write(b_("\nendstream"))

    @staticmethod
    def initializeFromDictionary(
        data: Dict[str, Any]
    ) -> Union["EncodedStreamObject", "DecodedStreamObject"]:
        retval: Union["EncodedStreamObject", "DecodedStreamObject"]
        if SA.FILTER in data:
            retval = EncodedStreamObject()
        else:
            retval = DecodedStreamObject()
        retval._data = data["__streamdata__"]
        del data["__streamdata__"]
        del data[SA.LENGTH]
        retval.update(data)
        return retval

    def flateEncode(self) -> "EncodedStreamObject":  # pragma: no cover
        deprecate_with_replacement("flateEncode", "flate_encode")
        return self.flate_encode()

    def flate_encode(self) -> "EncodedStreamObject":
        from .filters import FlateDecode

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
        retval._data = FlateDecode.encode(self._data)
        return retval


class DecodedStreamObject(StreamObject):
    def get_data(self) -> Any:
        return self._data

    def set_data(self, data: Any) -> Any:
        self._data = data

    def getData(self) -> Any:  # pragma: no cover
        deprecate_with_replacement("getData", "get_data")
        return self._data

    def setData(self, data: Any) -> None:  # pragma: no cover
        deprecate_with_replacement("setData", "set_data")
        self.set_data(data)


class EncodedStreamObject(StreamObject):
    def __init__(self) -> None:
        self.decoded_self: Optional[DecodedStreamObject] = None

    @property
    def decodedSelf(self) -> Optional["DecodedStreamObject"]:  # pragma: no cover
        deprecate_with_replacement("decodedSelf", "decoded_self")
        return self.decoded_self

    @decodedSelf.setter
    def decodedSelf(self, value: DecodedStreamObject) -> None:  # pragma: no cover
        deprecate_with_replacement("decodedSelf", "decoded_self")
        self.decoded_self = value

    def get_data(self) -> Union[None, str, bytes]:
        from .filters import decodeStreamData

        if self.decoded_self is not None:
            # cached version of decoded object
            return self.decoded_self.get_data()
        else:
            # create decoded object
            decoded = DecodedStreamObject()

            decoded._data = decodeStreamData(self)
            for key, value in list(self.items()):
                if key not in (SA.LENGTH, SA.FILTER, SA.DECODE_PARMS):
                    decoded[key] = value
            self.decoded_self = decoded
            return decoded._data

    def set_data(self, data: Any) -> None:
        raise PdfReadError("Creating EncodedStreamObject is not currently supported")


class ContentStream(DecodedStreamObject):
    def __init__(
        self,
        stream: Any,
        pdf: Any,
        forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
    ) -> None:
        self.pdf = pdf

        # The inner list has two elements:
        #  [0] : List
        #  [1] : str
        self.operations: List[Tuple[Any, Any]] = []

        # stream may be a StreamObject or an ArrayObject containing
        # multiple StreamObjects to be cat'd together.
        stream = stream.get_object()
        if isinstance(stream, ArrayObject):
            data = b_("")
            for s in stream:
                data += b_(s.get_object().get_data())
            stream_bytes = BytesIO(b_(data))
        else:
            stream_data = stream.get_data()
            assert stream_data is not None
            stream_data_bytes = b_(stream_data)
            stream_bytes = BytesIO(stream_data_bytes)
        # self.savstream = stream
        self.forced_encoding = forced_encoding
        self.__parseContentStream(stream_bytes)

    def __parseContentStream(self, stream: StreamType) -> None:
        # file("f:\\tmp.txt", "w").write(stream.read())
        stream.seek(0, 0)
        operands: List[Union[int, str, PdfObject]] = []
        while True:
            peek = read_non_whitespace(stream)
            if peek == b_("") or ord_(peek) == 0:
                break
            stream.seek(-1, 1)
            if peek.isalpha() or peek == b_("'") or peek == b_('"'):
                operator = read_until_regex(stream, NameObject.delimiter_pattern, True)
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
                # handle it here.  Typically, read_object will handle
                # encountering a comment -- but read_object assumes that
                # following the comment must be the object we're trying to
                # read.  In this case, it could be an operator instead.
                while peek not in (b_("\r"), b_("\n")):
                    peek = stream.read(1)
            else:
                operands.append(read_object(stream, None, self.forced_encoding))

    def _readInlineImage(self, stream: StreamType) -> Dict[str, Any]:
        # begin reading just after the "BI" - begin image
        # first read the dictionary of settings.
        settings = DictionaryObject()
        while True:
            tok = read_non_whitespace(stream)
            stream.seek(-1, 1)
            if tok == b_("I"):
                # "ID" - begin of image data
                break
            key = read_object(stream, self.pdf)
            tok = read_non_whitespace(stream)
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
                    while tok3 in WHITESPACES:
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

    @property
    def _data(self) -> bytes:
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

    @_data.setter
    def _data(self, value: Union[str, bytes]) -> None:
        self.__parseContentStream(BytesIO(b_(value)))


def read_object(
    stream: StreamType,
    pdf: Any,  # PdfReader
    forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
) -> Union[PdfObject, int, str, ContentStream]:
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
            return DictionaryObject.read_from_stream(stream, pdf, forced_encoding)
        else:
            return readHexStringFromStream(stream)
    elif idx == 2:
        return ArrayObject.read_from_stream(stream, pdf, forced_encoding)
    elif idx == 3 or idx == 4:
        return BooleanObject.read_from_stream(stream)
    elif idx == 5:
        return readStringFromStream(stream, forced_encoding)
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
        tok = read_non_whitespace(stream)
        stream.seek(-1, 1)
        return read_object(stream, pdf, forced_encoding)
    else:
        # number object OR indirect reference
        peek = stream.read(20)
        stream.seek(-len(peek), 1)  # reset to start
        if IndirectPattern.match(peek) is not None:
            return IndirectObject.read_from_stream(stream, pdf)
        else:
            return NumberObject.read_from_stream(stream)


class RectangleObject(ArrayObject):
    """
    This class is used to represent *page boxes* in PyPDF2. These boxes include:
        * :attr:`artbox <PyPDF2._page.PageObject.artbox>`
        * :attr:`bleedbox <PyPDF2._page.PageObject.bleedbox>`
        * :attr:`cropbox <PyPDF2._page.PageObject.cropbox>`
        * :attr:`mediabox <PyPDF2._page.PageObject.mediabox>`
        * :attr:`trimbox <PyPDF2._page.PageObject.trimbox>`
    """

    def __init__(self, arr: Tuple[float, float, float, float]) -> None:
        # must have four points
        assert len(arr) == 4
        # automatically convert arr[x] into NumberObject(arr[x]) if necessary
        ArrayObject.__init__(self, [self._ensure_is_number(x) for x in arr])  # type: ignore

    def _ensure_is_number(self, value: Any) -> Union[FloatObject, NumberObject]:
        if not isinstance(value, (NumberObject, FloatObject)):
            value = FloatObject(value)
        return value

    def ensureIsNumber(
        self, value: Any
    ) -> Union[FloatObject, NumberObject]:  # pragma: no cover
        deprecate_no_replacement("ensureIsNumber")
        return self._ensure_is_number(value)

    def __repr__(self) -> str:
        return "RectangleObject(%s)" % repr(list(self))

    @property
    def left(self) -> FloatObject:
        return self[0]

    @property
    def bottom(self) -> FloatObject:
        return self[1]

    @property
    def right(self) -> FloatObject:
        return self[2]

    @property
    def top(self) -> FloatObject:
        return self[3]

    def getLowerLeft_x(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getLowerLeft_x", "left")
        return self.left

    def getLowerLeft_y(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getLowerLeft_y", "bottom")
        return self.bottom

    def getUpperRight_x(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getUpperRight_x", "right")
        return self.right

    def getUpperRight_y(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getUpperRight_y", "top")
        return self.top

    def getUpperLeft_x(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getUpperLeft_x", "left")
        return self.left

    def getUpperLeft_y(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getUpperLeft_y", "top")
        return self.top

    def getLowerRight_x(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getLowerRight_x", "right")
        return self.right

    def getLowerRight_y(self) -> FloatObject:  # pragma: no cover
        deprecate_with_replacement("getLowerRight_y", "bottom")
        return self.bottom

    @property
    def lower_left(self) -> Tuple[decimal.Decimal, decimal.Decimal]:
        """
        Property to read and modify the lower left coordinate of this box
        in (x,y) form.
        """
        return self.left, self.bottom

    @lower_left.setter
    def lower_left(self, value: List[Any]) -> None:
        self[0], self[1] = (self._ensure_is_number(x) for x in value)

    @property
    def lower_right(self) -> Tuple[decimal.Decimal, decimal.Decimal]:
        """
        Property to read and modify the lower right coordinate of this box
        in (x,y) form.
        """
        return self.right, self.bottom

    @lower_right.setter
    def lower_right(self, value: List[Any]) -> None:
        self[2], self[1] = (self._ensure_is_number(x) for x in value)

    @property
    def upper_left(self) -> Tuple[decimal.Decimal, decimal.Decimal]:
        """
        Property to read and modify the upper left coordinate of this box
        in (x,y) form.
        """
        return self.left, self.top

    @upper_left.setter
    def upper_left(self, value: List[Any]) -> None:
        self[0], self[3] = (self._ensure_is_number(x) for x in value)

    @property
    def upper_right(self) -> Tuple[decimal.Decimal, decimal.Decimal]:
        """
        Property to read and modify the upper right coordinate of this box
        in (x,y) form.
        """
        return self.right, self.top

    @upper_right.setter
    def upper_right(self, value: List[Any]) -> None:
        self[2], self[3] = (self._ensure_is_number(x) for x in value)

    def getLowerLeft(
        self,
    ) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("getLowerLeft", "lower_left")
        return self.lower_left

    def getLowerRight(
        self,
    ) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("getLowerRight", "lower_right")
        return self.lower_right

    def getUpperLeft(
        self,
    ) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("getUpperLeft", "upper_left")
        return self.upper_left

    def getUpperRight(
        self,
    ) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("getUpperRight", "upper_right")
        return self.upper_right

    def setLowerLeft(self, value: Tuple[float, float]) -> None:  # pragma: no cover
        deprecate_with_replacement("setLowerLeft", "lower_left")
        self.lower_left = value  # type: ignore

    def setLowerRight(self, value: Tuple[float, float]) -> None:  # pragma: no cover
        deprecate_with_replacement("setLowerRight", "lower_right")
        self[2], self[1] = (self._ensure_is_number(x) for x in value)

    def setUpperLeft(self, value: Tuple[float, float]) -> None:  # pragma: no cover
        deprecate_with_replacement("setUpperLeft", "upper_left")
        self[0], self[3] = (self._ensure_is_number(x) for x in value)

    def setUpperRight(self, value: Tuple[float, float]) -> None:  # pragma: no cover
        deprecate_with_replacement("setUpperRight", "upper_right")
        self[2], self[3] = (self._ensure_is_number(x) for x in value)

    @property
    def width(self) -> decimal.Decimal:
        return self.right - self.left

    def getWidth(self) -> decimal.Decimal:  # pragma: no cover
        deprecate_with_replacement("getWidth", "width")
        return self.width

    @property
    def height(self) -> decimal.Decimal:
        return self.top - self.bottom

    def getHeight(self) -> decimal.Decimal:  # pragma: no cover
        deprecate_with_replacement("getHeight", "height")
        return self.height

    @property
    def lowerLeft(self) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("lowerLeft", "lower_left")
        return self.lower_left

    @lowerLeft.setter
    def lowerLeft(
        self, value: Tuple[decimal.Decimal, decimal.Decimal]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("lowerLeft", "lower_left")
        self.lower_left = value

    @property
    def lowerRight(self) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("lowerRight", "lower_right")
        return self.lower_right

    @lowerRight.setter
    def lowerRight(
        self, value: Tuple[decimal.Decimal, decimal.Decimal]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("lowerRight", "lower_right")
        self.lower_right = value

    @property
    def upperLeft(self) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("upperLeft", "upper_left")
        return self.upper_left

    @upperLeft.setter
    def upperLeft(
        self, value: Tuple[decimal.Decimal, decimal.Decimal]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("upperLeft", "upper_left")
        self.upper_left = value

    @property
    def upperRight(self) -> Tuple[decimal.Decimal, decimal.Decimal]:  # pragma: no cover
        deprecate_with_replacement("upperRight", "upper_right")
        return self.upper_right

    @upperRight.setter
    def upperRight(
        self, value: Tuple[decimal.Decimal, decimal.Decimal]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("upperRight", "upper_right")
        self.upper_right = value


class Field(TreeObject):
    """
    A class representing a field dictionary. This class is accessed through
    :meth:`get_fields()<PyPDF2.PdfReader.get_fields>`
    """

    def __init__(self, data: Dict[str, Any]) -> None:
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

    # TABLE 8.69 Entries common to all field dictionaries
    @property
    def field_type(self) -> Optional[NameObject]:
        """Read-only property accessing the type of this field."""
        return self.get("/FT")

    @property
    def fieldType(self) -> Optional[NameObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`field_type` instead.
        """
        deprecate_with_replacement("fieldType", "field_type")
        return self.field_type

    @property
    def parent(self) -> Optional[DictionaryObject]:
        """Read-only property accessing the parent of this field."""
        return self.get("/Parent")

    @property
    def kids(self) -> Optional[ArrayObject]:
        """Read-only property accessing the kids of this field."""
        return self.get("/Kids")

    @property
    def name(self) -> Optional[str]:
        """Read-only property accessing the name of this field."""
        return self.get("/T")

    @property
    def alternate_name(self) -> Optional[str]:
        """Read-only property accessing the alternate name of this field."""
        return self.get("/TU")

    @property
    def altName(self) -> Optional[str]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`alternate_name` instead.
        """
        deprecate_with_replacement("altName", "alternate_name")
        return self.alternate_name

    @property
    def mapping_name(self) -> Optional[str]:
        """
        Read-only property accessing the mapping name of this field. This
        name is used by PyPDF2 as a key in the dictionary returned by
        :meth:`get_fields()<PyPDF2.PdfReader.get_fields>`
        """
        return self.get("/TM")

    @property
    def mappingName(self) -> Optional[str]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`mapping_name` instead.
        """
        deprecate_with_replacement("mappingName", "mapping_name")
        return self.mapping_name

    @property
    def flags(self) -> Optional[int]:
        """
        Read-only property accessing the field flags, specifying various
        characteristics of the field (see Table 8.70 of the PDF 1.7 reference).
        """
        return self.get("/Ff")

    @property
    def value(self) -> Optional[Any]:
        """
        Read-only property accessing the value of this field. Format
        varies based on field type.
        """
        return self.get("/V")

    @property
    def default_value(self) -> Optional[Any]:
        """Read-only property accessing the default value of this field."""
        return self.get("/DV")

    @property
    def defaultValue(self) -> Optional[Any]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`default_value` instead.
        """
        deprecate_with_replacement("defaultValue", "default_value")
        return self.default_value

    @property
    def additional_actions(self) -> Optional[DictionaryObject]:
        """
        Read-only property accessing the additional actions dictionary.
        This dictionary defines the field's behavior in response to trigger events.
        See Section 8.5.2 of the PDF 1.7 reference.
        """
        return self.get("/AA")

    @property
    def additionalActions(self) -> Optional[DictionaryObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`additional_actions` instead.
        """
        deprecate_with_replacement("additionalActions", "additional_actions")
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

    def __init__(
        self,
        title: str,
        page: Union[NumberObject, IndirectObject, NullObject, DictionaryObject],
        typ: Union[str, NumberObject],
        *args: Any,  # ZoomArgType
    ) -> None:
        DictionaryObject.__init__(self)
        self[NameObject("/Title")] = title
        self[NameObject("/Page")] = page
        self[NameObject("/Type")] = typ

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
    def dest_array(self) -> ArrayObject:
        return ArrayObject(
            [self.raw_get("/Page"), self["/Type"]]
            + [
                self[x]
                for x in ["/Left", "/Bottom", "/Right", "/Top", "/Zoom"]
                if x in self
            ]
        )

    def getDestArray(self) -> ArrayObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.3

            Use :py:attr:`dest_array` instead.
        """
        deprecate_with_replacement("getDestArray", "dest_array")
        return self.dest_array

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_("<<\n"))
        key = NameObject("/D")
        key.write_to_stream(stream, encryption_key)
        stream.write(b_(" "))
        value = self.dest_array
        value.write_to_stream(stream, encryption_key)

        key = NameObject("/S")
        key.write_to_stream(stream, encryption_key)
        stream.write(b_(" "))
        value_s = NameObject("/GoTo")
        value_s.write_to_stream(stream, encryption_key)

        stream.write(b_("\n"))
        stream.write(b_(">>"))

    @property
    def title(self) -> Optional[str]:
        """
        Read-only property accessing the destination title.

        :rtype: str
        """
        return self.get("/Title")

    @property
    def page(self) -> Optional[int]:
        """
        Read-only property accessing the destination page number.

        :rtype: int
        """
        return self.get("/Page")

    @property
    def typ(self) -> Optional[str]:
        """
        Read-only property accessing the destination type.

        :rtype: str
        """
        return self.get("/Type")

    @property
    def zoom(self) -> Optional[int]:
        """
        Read-only property accessing the zoom factor.

        :rtype: int, or ``None`` if not available.
        """
        return self.get("/Zoom", None)

    @property
    def left(self) -> Optional[FloatObject]:
        """
        Read-only property accessing the left horizontal coordinate.

        :rtype: float, or ``None`` if not available.
        """
        return self.get("/Left", None)

    @property
    def right(self) -> Optional[FloatObject]:
        """
        Read-only property accessing the right horizontal coordinate.

        :rtype: float, or ``None`` if not available.
        """
        return self.get("/Right", None)

    @property
    def top(self) -> Optional[FloatObject]:
        """
        Read-only property accessing the top vertical coordinate.

        :rtype: float, or ``None`` if not available.
        """
        return self.get("/Top", None)

    @property
    def bottom(self) -> Optional[FloatObject]:
        """
        Read-only property accessing the bottom vertical coordinate.

        :rtype: float, or ``None`` if not available.
        """
        return self.get("/Bottom", None)


class Bookmark(Destination):
    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
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


def createStringObject(
    string: Union[str, bytes],
    forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
) -> Union[TextStringObject, ByteStringObject]:
    """
    Given a string, create a ByteStringObject or a TextStringObject to
    represent the string.

    :param string: A string

    :raises TypeError: If string is not of type str or bytes.
    """
    if isinstance(string, str):
        return TextStringObject(string)
    elif isinstance(string, bytes_type):
        if isinstance(forced_encoding, (list, dict)):
            out = ""
            for x in string:
                try:
                    out += forced_encoding[x]
                except Exception:
                    out += bytes((x,)).decode("charmap")
            return TextStringObject(out)
        elif isinstance(forced_encoding, str):
            return TextStringObject(string.decode(forced_encoding))
        else:
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


def encode_pdfdocencoding(unicode_string: str) -> bytes:
    retval = b_("")
    for c in unicode_string:
        try:
            retval += b_(chr(_pdfdoc_encoding_rev[c]))
        except KeyError:
            raise UnicodeEncodeError(
                "pdfdocencoding", c, -1, -1, "does not exist in translation table"
            )
    return retval


def decode_pdfdocencoding(byte_array: bytes) -> str:
    retval = ""
    for b in byte_array:
        c = _pdfdoc_encoding[ord_(b)]
        if c == "\u0000":
            raise UnicodeDecodeError(
                "pdfdocencoding",
                bytearray(b),
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
_pdfdoc_encoding = [
    "\u0000",
    "\u0001",
    "\u0002",
    "\u0003",
    "\u0004",
    "\u0005",
    "\u0006",
    "\u0007",  # 0 -  7
    "\u0008",
    "\u0009",
    "\u000a",
    "\u000b",
    "\u000c",
    "\u000d",
    "\u000e",
    "\u000f",  # 8 - 15
    "\u0010",
    "\u0011",
    "\u0012",
    "\u0013",
    "\u0014",
    "\u0015",
    "\u0000",
    "\u0017",  # 16 - 23
    "\u02d8",
    "\u02c7",
    "\u02c6",
    "\u02d9",
    "\u02dd",
    "\u02db",
    "\u02da",
    "\u02dc",  # 24 - 31
    "\u0020",
    "\u0021",
    "\u0022",
    "\u0023",
    "\u0024",
    "\u0025",
    "\u0026",
    "\u0027",  # 32 - 39
    "\u0028",
    "\u0029",
    "\u002a",
    "\u002b",
    "\u002c",
    "\u002d",
    "\u002e",
    "\u002f",  # 40 - 47
    "\u0030",
    "\u0031",
    "\u0032",
    "\u0033",
    "\u0034",
    "\u0035",
    "\u0036",
    "\u0037",  # 48 - 55
    "\u0038",
    "\u0039",
    "\u003a",
    "\u003b",
    "\u003c",
    "\u003d",
    "\u003e",
    "\u003f",  # 56 - 63
    "\u0040",
    "\u0041",
    "\u0042",
    "\u0043",
    "\u0044",
    "\u0045",
    "\u0046",
    "\u0047",  # 64 - 71
    "\u0048",
    "\u0049",
    "\u004a",
    "\u004b",
    "\u004c",
    "\u004d",
    "\u004e",
    "\u004f",  # 72 - 79
    "\u0050",
    "\u0051",
    "\u0052",
    "\u0053",
    "\u0054",
    "\u0055",
    "\u0056",
    "\u0057",  # 80 - 87
    "\u0058",
    "\u0059",
    "\u005a",
    "\u005b",
    "\u005c",
    "\u005d",
    "\u005e",
    "\u005f",  # 88 - 95
    "\u0060",
    "\u0061",
    "\u0062",
    "\u0063",
    "\u0064",
    "\u0065",
    "\u0066",
    "\u0067",  # 96 - 103
    "\u0068",
    "\u0069",
    "\u006a",
    "\u006b",
    "\u006c",
    "\u006d",
    "\u006e",
    "\u006f",  # 104 - 111
    "\u0070",
    "\u0071",
    "\u0072",
    "\u0073",
    "\u0074",
    "\u0075",
    "\u0076",
    "\u0077",  # 112 - 119
    "\u0078",
    "\u0079",
    "\u007a",
    "\u007b",
    "\u007c",
    "\u007d",
    "\u007e",
    "\u0000",  # 120 - 127
    "\u2022",
    "\u2020",
    "\u2021",
    "\u2026",
    "\u2014",
    "\u2013",
    "\u0192",
    "\u2044",  # 128 - 135
    "\u2039",
    "\u203a",
    "\u2212",
    "\u2030",
    "\u201e",
    "\u201c",
    "\u201d",
    "\u2018",  # 136 - 143
    "\u2019",
    "\u201a",
    "\u2122",
    "\ufb01",
    "\ufb02",
    "\u0141",
    "\u0152",
    "\u0160",  # 144 - 151
    "\u0178",
    "\u017d",
    "\u0131",
    "\u0142",
    "\u0153",
    "\u0161",
    "\u017e",
    "\u0000",  # 152 - 159
    "\u20ac",
    "\u00a1",
    "\u00a2",
    "\u00a3",
    "\u00a4",
    "\u00a5",
    "\u00a6",
    "\u00a7",  # 160 - 167
    "\u00a8",
    "\u00a9",
    "\u00aa",
    "\u00ab",
    "\u00ac",
    "\u0000",
    "\u00ae",
    "\u00af",  # 168 - 175
    "\u00b0",
    "\u00b1",
    "\u00b2",
    "\u00b3",
    "\u00b4",
    "\u00b5",
    "\u00b6",
    "\u00b7",  # 176 - 183
    "\u00b8",
    "\u00b9",
    "\u00ba",
    "\u00bb",
    "\u00bc",
    "\u00bd",
    "\u00be",
    "\u00bf",  # 184 - 191
    "\u00c0",
    "\u00c1",
    "\u00c2",
    "\u00c3",
    "\u00c4",
    "\u00c5",
    "\u00c6",
    "\u00c7",  # 192 - 199
    "\u00c8",
    "\u00c9",
    "\u00ca",
    "\u00cb",
    "\u00cc",
    "\u00cd",
    "\u00ce",
    "\u00cf",  # 200 - 207
    "\u00d0",
    "\u00d1",
    "\u00d2",
    "\u00d3",
    "\u00d4",
    "\u00d5",
    "\u00d6",
    "\u00d7",  # 208 - 215
    "\u00d8",
    "\u00d9",
    "\u00da",
    "\u00db",
    "\u00dc",
    "\u00dd",
    "\u00de",
    "\u00df",  # 216 - 223
    "\u00e0",
    "\u00e1",
    "\u00e2",
    "\u00e3",
    "\u00e4",
    "\u00e5",
    "\u00e6",
    "\u00e7",  # 224 - 231
    "\u00e8",
    "\u00e9",
    "\u00ea",
    "\u00eb",
    "\u00ec",
    "\u00ed",
    "\u00ee",
    "\u00ef",  # 232 - 239
    "\u00f0",
    "\u00f1",
    "\u00f2",
    "\u00f3",
    "\u00f4",
    "\u00f5",
    "\u00f6",
    "\u00f7",  # 240 - 247
    "\u00f8",
    "\u00f9",
    "\u00fa",
    "\u00fb",
    "\u00fc",
    "\u00fd",
    "\u00fe",
    "\u00ff",  # 248 - 255
]

assert len(_pdfdoc_encoding) == 256


def fill_from_encoding(enc: str) -> List[str]:
    lst: List[str] = []
    for x in range(256):
        try:
            lst += (bytes((x,)).decode(enc),)
        except Exception:
            lst += (chr(x),)
    return lst


_win_encoding = fill_from_encoding("cp1252")
_mac_encoding = fill_from_encoding("mac_roman")
_std_encoding = [
    "\x00",
    "\x01",
    "\x02",
    "\x03",
    "\x04",
    "\x05",
    "\x06",
    "\x07",
    "\x08",
    "\t",
    "\n",
    "\x0b",
    "\x0c",
    "\r",
    "\x0e",
    "\x0f",
    "\x10",
    "\x11",
    "\x12",
    "\x13",
    "\x14",
    "\x15",
    "\x16",
    "\x17",
    "\x18",
    "\x19",
    "\x1a",
    "\x1b",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x1f",
    " ",
    "!",
    '"',
    "#",
    "$",
    "%",
    "&",
    "’",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    ":",
    ";",
    "<",
    "=",
    ">",
    "?",
    "@",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "[",
    "\\",
    "]",
    "^",
    "_",
    "‘",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "{",
    "|",
    "}",
    "~",
    "\x7f",
    "\x80",
    "\x81",
    "\x82",
    "\x83",
    "\x84",
    "\x85",
    "\x86",
    "\x87",
    "\x88",
    "\x89",
    "\x8a",
    "\x8b",
    "\x8c",
    "\x8d",
    "\x8e",
    "\x8f",
    "\x90",
    "\x91",
    "\x92",
    "\x93",
    "\x94",
    "\x95",
    "\x96",
    "\x97",
    "\x98",
    "\x99",
    "\x9a",
    "\x9b",
    "\x9c",
    "\x9d",
    "\x9e",
    "\x9f",
    "\xa0",
    "¡",
    "¢",
    "£",
    "⁄",
    "¥",
    "ƒ",
    "§",
    "¤",
    "'",
    "“",
    "«",
    "‹",
    "›",
    "ﬁ",
    "ﬂ",
    "°",
    "–",
    "†",
    "‡",
    "·",
    "µ",
    "¶",
    "•",
    "‚",
    "„",
    "”",
    "»",
    "…",
    "‰",
    "¾",
    "¿",
    "À",
    "`",
    "´",
    "ˆ",
    "˜",
    "¯",
    "˘",
    "˙",
    "¨",
    "É",
    "˚",
    "¸",
    "Ì",
    "˝",
    "˛",
    "ˇ",
    "—",
    "Ñ",
    "Ò",
    "Ó",
    "Ô",
    "Õ",
    "Ö",
    "×",
    "Ø",
    "Ù",
    "Ú",
    "Û",
    "Ü",
    "Ý",
    "Þ",
    "ß",
    "à",
    "Æ",
    "â",
    "ª",
    "ä",
    "å",
    "æ",
    "ç",
    "Ł",
    "Ø",
    "Œ",
    "º",
    "ì",
    "í",
    "î",
    "ï",
    "ð",
    "æ",
    "ò",
    "ó",
    "ô",
    "ı",
    "ö",
    "÷",
    "ł",
    "ø",
    "œ",
    "ß",
    "ü",
    "ý",
    "þ",
    "ÿ",
]


def rev_encoding(enc: List[str]) -> Dict[str, int]:
    rev: Dict[str, int] = {}
    for i in range(256):
        char = enc[i]
        if char == "\u0000":
            continue
        assert char not in rev, (
            str(char) + " at " + str(i) + " already at " + str(rev[char])
        )
        rev[char] = i
    return rev


_pdfdoc_encoding_rev: Dict[str, int] = rev_encoding(_pdfdoc_encoding)
_win_encoding_rev: Dict[str, int] = rev_encoding(_win_encoding)
_mac_encoding_rev: Dict[str, int] = rev_encoding(_mac_encoding)

charset_encoding: Dict[str, List[str]] = {
    "/StandardCoding": _std_encoding,
    "/WinAnsiEncoding": _win_encoding,
    "/MacRomanEncoding": _mac_encoding,
    "/PDFDocEncoding": _pdfdoc_encoding,
}
