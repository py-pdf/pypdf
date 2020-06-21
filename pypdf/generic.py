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
Implementation of generic PDF objects (dictionary, number, string, and so on).
"""

import codecs
import decimal
import math
import re
import uuid
import warnings
from io import BytesIO

from pypdf.utils import *
from pypdf.utils import pypdfBytes as b_, pypdfUnicode as u_

__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

ObjectPrefix = b_('/<[tf(n%')
NumberSigns = b_('+-')
IndirectPattern = re.compile(b_(r"[+-]?(\d+)\s+(\d+)\s+R[^a-zA-Z]"))


def readObject(stream, pdf):
    tok = stream.read(1)
    stream.seek(-1, 1)  # reset to start
    idx = ObjectPrefix.find(tok)

    if idx == 0:  # name object
        return NameObject.readFromStream(stream, pdf)
    elif idx == 1:  # hexadecimal string OR dictionary
        peek = stream.read(2)
        stream.seek(-2, 1)  # reset to start

        if peek == b_('<<'):
            return DictionaryObject.readFromStream(stream, pdf)
        else:
            return readHexStringFromStream(stream)
    elif idx == 2:  # array object
        return ArrayObject.readFromStream(stream, pdf)
    elif idx == 3 or idx == 4:  # boolean object
        return BooleanObject.readFromStream(stream)
    elif idx == 5:  # string object
        return readStringFromStream(stream)
    elif idx == 6:  # null object
        return NullObject.readFromStream(stream)
    elif idx == 7:  # comment
        while tok not in (b_('\r'), b_('\n')):
            tok = stream.read(1)
            # Prevents an infinite loop by raising an error if the stream is at
            # the EOF
            if len(tok) <= 0:
                raise PdfStreamError("File ended unexpectedly.")
        tok = readNonWhitespace(stream)
        stream.seek(-1, 1)

        return readObject(stream, pdf)
    else:  # number object OR indirect reference
        peek = stream.read(20)
        stream.seek(-len(peek), 1)  # reset to start

        if IndirectPattern.match(peek) is not None:
            return IndirectObject.readFromStream(stream, pdf)
        else:
            return NumberObject.readFromStream(stream)


class PdfObject(object):
    def getObject(self):
        """Resolves indirect references."""
        return self


# TO-DO Add __repr_() implementations to the *Object classes
class NullObject(PdfObject):
    def writeToStream(self, stream, encryption_key):
        stream.write(b_("null"))

    @staticmethod
    def readFromStream(stream):
        null_text = stream.read(4)

        if null_text != b_("null"):
            raise PdfReadError("Could not read Null object")

        return NullObject()


class BooleanObject(PdfObject):
    def __init__(self, value):
        self.value = value

    def writeToStream(self, stream, encryption_key):
        if self.value:
            stream.write(b_("true"))
        else:
            stream.write(b_("false"))

    @staticmethod
    def readFromStream(stream):
        word = stream.read(4)

        if word == b_("true"):
            return BooleanObject(True)
        elif word == b_("fals"):
            stream.read(1)

            return BooleanObject(False)
        else:
            raise PdfReadError('Could not read Boolean object')


class ArrayObject(list, PdfObject):
    def writeToStream(self, stream, encryption_key):
        stream.write(b_("["))

        for data in self:
            stream.write(b_(" "))
            data.writeToStream(stream, encryption_key)

        stream.write(b_(" ]"))

    @staticmethod
    def readFromStream(stream, pdf):
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
            arr.append(readObject(stream, pdf))

        return arr


class IndirectObject(PdfObject):
    def __init__(self, idnum, generation, pdf):
        """
        Represents an indirect generic object whose declaration in the File
        Body is something like

        ``123 0 obj``\n
        ``...``\n
        ``endobj``

        :param idnum: identifying number of this indirect reference.
        :param generation: generation number, used for marking batch updates.
        :param pdf: the :class:`PdfFileReader<pdf.PdfFileReader>` or
            :class:`PdfFileWriter<pdf.PdfFileWriter>` instance associated with
            this object.
        """
        self.idnum = idnum
        self.generation = generation
        self.pdf = pdf

    def getObject(self):
        return self.pdf.getObject(self).getObject()

    def __repr__(self):
        return "IndirectObject(%r, %r)" % (self.idnum, self.generation)

    def __eq__(self, other):
        return (
                other is not None and
                isinstance(other, IndirectObject) and
                self.idnum == other.idnum and
                self.generation == other.generation and
                self.pdf is other.pdf
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def writeToStream(self, stream, encryption_key):
        stream.write(b_("%s %s R" % (self.idnum, self.generation)))

    @staticmethod
    def readFromStream(stream, pdf):
        idnum = b_("")

        while True:
            tok = stream.read(1)
            if not tok:
                # stream has truncated prematurely
                raise PdfStreamError("Stream has ended unexpectedly")
            if tok.isspace():
                break
            idnum += tok

        generation = b_("")

        while True:
            tok = stream.read(1)

            if not tok:
                # stream has truncated prematurely
                raise PdfStreamError("Stream has ended unexpectedly")
            if tok.isspace():
                if not generation:
                    continue
                break

            generation += tok

        r = readNonWhitespace(stream)

        if r != b_("R"):
            raise PdfReadError(
                "Error reading indirect object reference at byte %s" %
                hexStr(stream.tell())
            )

        return IndirectObject(int(idnum), int(generation), pdf)


class FloatObject(decimal.Decimal, PdfObject):
    def __new__(cls, value="0", context=None):
        try:
            return decimal.Decimal.__new__(
                cls, pypdfStr(value), context
            )
        except:
            return decimal.Decimal.__new__(cls, str(value))

    def __repr__(self):
        if self == self.to_integral():
            return str(self.quantize(decimal.Decimal(1)))
        else:
            # Standard formatting adds useless extraneous zeros.
            o = "%.5f" % self
            # Remove the zeros.
            while o and o[-1] == '0':
                o = o[:-1]
            return o

    def asNumeric(self):
        return float(b_(repr(self)))

    def writeToStream(self, stream, encryption_key):
        stream.write(b_(repr(self)))


class NumberObject(int, PdfObject):
    NumberPattern = re.compile(b_('[^+-.0-9]'))
    ByteDot = b_(".")

    def __new__(cls, value):
        val = int(value)
        try:
            return int.__new__(cls, val)
        except OverflowError:
            return int.__new__(cls, 0)

    def asNumeric(self):
        return int(b_(repr(self)))

    def writeToStream(self, stream, encryption_key):
        stream.write(b_(repr(self)))

    @staticmethod
    def readFromStream(stream):
        num = readUntilRegex(stream, NumberObject.NumberPattern)

        if num.find(NumberObject.ByteDot) != -1:
            return FloatObject(num)
        else:
            return NumberObject(num)


def createStringObject(string):
    """
    Given a string (either a ``str`` or ``unicode``), create a
    :class:`ByteStringObject<ByteStringObject>` or a
    :class:`TextStringObject<TextStringObject>` to represent the string.
    """
    if isinstance(string, string_type):
        return TextStringObject(string)
    elif isinstance(string, bytes_type):
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
                retval = TextStringObject(decodePdfDocEncoding(string))
                retval.autodetect_pdfdocencoding = True

                return retval
        except UnicodeDecodeError:
            return ByteStringObject(string)
    else:
        raise TypeError("createStringObject() should have str or unicode arg")


def readHexStringFromStream(stream):
    stream.read(1)
    txt = ""
    x = b_("")

    while True:
        tok = readNonWhitespace(stream)
        if not tok:
            # stream has truncated prematurely
            raise PdfStreamError("Stream has ended unexpectedly")
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
            # stream has truncated prematurely
            raise PdfStreamError("Stream has ended unexpectedly")
        if tok == b_("("):
            parens += 1
        elif tok == b_(")"):
            parens -= 1
            if parens == 0:
                break
        elif tok == b_("\\"):
            tok = stream.read(1)
            escape_dict = {
                b_("n"): b_("\n"), b_("r"): b_("\r"), b_("t"): b_("\t"),
                b_("b"): b_("\b"), b_("f"): b_("\f"), b_("c"): b_("\c"),
                b_("("): b_("("), b_(")"): b_(")"), b_("/"): b_("/"),
                b_("\\"): b_("\\"), b_(" "): b_(" "), b_("/"): b_("/"),
                b_("%"): b_("%"), b_("<"): b_("<"), b_(">"): b_(">"),
                b_("["): b_("["), b_("]"): b_("]"), b_("#"): b_("#"),
                b_("_"): b_("_"), b_("&"): b_("&"), b_('$'): b_('$'),
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
                    for i in range(2):
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

                    if not tok in b_("\n\r"):
                        stream.seek(-1, 1)
                    # Then don't add anything to the actual string, since this
                    # line break was escaped:
                    tok = b_('')
                else:
                    raise PdfReadError(
                        r"Unexpected escaped string: %s" % tok
                    )
        txt += tok

    return createStringObject(txt)


class ByteStringObject(bytes_type, PdfObject):
    """
    Represents a string object where the text encoding could not be determined.
    This occurs quite often, as the PDF spec doesn't provide an alternate way
    to represent strings -- for example, the encryption data stored in files
    (like /O) is clearly not text, but is still stored in a ``String`` object).
    """
    # For compatibility with TextStringObject.original_bytes.  This method
    # returns self.
    original_bytes = property(lambda self: self)

    def writeToStream(self, stream, encryption_key):
        bytearr = self

        if encryption_key:
            bytearr = RC4Encrypt(encryption_key, bytearr)

        stream.write(b_("<"))
        stream.write(b_(hexEncode(bytearr)))
        stream.write(b_(">"))


class TextStringObject(string_type, PdfObject):
    """
    Represents a ``str`` object that has been decoded into a real ``unicode``
    string. If read from a PDF document, this string appeared to match the
    PDFDocEncoding, or contained a UTF-16BE BOM mark to cause UTF-16 decoding
    to occur.
    """
    autodetect_pdfdocencoding = False
    autodetect_utf16 = False

    # It is occasionally possible that a text string object gets created where
    # a byte string object was expected due to the autodetection mechanism --
    # if that occurs, this "original_bytes" property can be used to
    # back-calculate what the original encoded bytes were.
    original_bytes = property(lambda self: self.getOriginalBytes())

    def getOriginalBytes(self):
        # We're a text string object, but the library is trying to get our raw
        # bytes.  This can happen if we auto-detected this string as text, but
        # we were wrong.  It's pretty common.  Return the original bytes that
        # would have been used to create this object, based upon the autodetect
        # method.
        if self.autodetect_utf16:
            return codecs.BOM_UTF16_BE + self.encode("utf-16be")
        elif self.autodetect_pdfdocencoding:
            return encodePdfDocEncoding(self)
        else:
            raise Exception("no information about original bytes")

    def writeToStream(self, stream, encryption_key):
        # Try to write the string out as a PDFDocEncoding encoded string.  It's
        # nicer to look at in the PDF file.  Sadly, we take a performance hit
        # here for trying...
        try:
            bytearr = encodePdfDocEncoding(self)
        except UnicodeEncodeError:
            bytearr = codecs.BOM_UTF16_BE + self.encode("utf-16be")

        if encryption_key:
            bytearr = RC4Encrypt(encryption_key, bytearr)
            obj = ByteStringObject(bytearr)
            obj.writeToStream(stream, None)
        else:
            stream.write(b_("("))

            for c in bytearr:
                if not pypdfChr(c).isalnum() and pypdfChr(c) != ' ':
                    stream.write(b_("\\%03o" % pypdfOrd(c)))
                else:
                    stream.write(b_(pypdfChr(c)))

            stream.write(b_(")"))


class NameObject(str, PdfObject):
    delimiterPattern = re.compile(b_(r"\s+|[\(\)<>\[\]{}/%]"))
    surfix = b_("/")

    def writeToStream(self, stream, encryption_key):
        stream.write(b_(self))

    @staticmethod
    def readFromStream(stream, pdf):
        debug = False

        if debug:
            print((stream.tell()))

        name = stream.read(1)

        if name != NameObject.surfix:
            raise PdfReadError("name read error")

        name += readUntilRegex(
            stream, NameObject.delimiterPattern, ignore_eof=True
        )

        if debug:
            print(name)
        try:
            return NameObject(name.decode('utf-8'))
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            # Name objects should represent irregular characters
            # with a '#' followed by the symbol's hex number
            if not pdf.strict:
                warnings.warn(
                    "Illegal character in Name Object", PdfReadWarning
                )
                return NameObject(name)
            else:
                raise PdfReadError("Illegal character in Name Object")


class DictionaryObject(dict, PdfObject):
    def rawGet(self, key):
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
        return dict.__getitem__(self, key).getObject()

    def getXmpMetadata(self):
        """
        Retrieves XMP (Extensible Metadata Platform) data relevant to this
        object, if available.

        Added in v1.12, will exist for all future v1.x releases.

        :return: a :class:`XmpInformation<xmp.XmpInformation>` instance that
        can be used to access XMP metadata from the document.  Can also return
        ``None`` if no metadata was found on the document root.
        """
        metadata = self.get("/Metadata", None)

        if metadata is None:
            return None

        metadata = metadata.getObject()
        from . import xmp

        if not isinstance(metadata, xmp.XmpInformation):
            metadata = xmp.XmpInformation(metadata)
            self[NameObject("/Metadata")] = metadata

        return metadata

    xmpMetadata = property(getXmpMetadata)
    """
    Read-only property that accesses the
    :meth:`getXmpData<DictionaryObject.getxmpData>` function.

    Added in v1.12, will exist for all future v1.x releases.
    """

    def writeToStream(self, stream, encryption_key):
        stream.write(b_("<<\n"))

        for key, value in list(self.items()):
            key.writeToStream(stream, encryption_key)
            stream.write(b_(" "))
            value.writeToStream(stream, encryption_key)
            stream.write(b_("\n"))

        stream.write(b_(">>"))

    @staticmethod
    def readFromStream(stream, pdf):
        debug = False
        data = {}
        buff = stream.read(2)

        if buff != b_("<<"):
            raise PdfReadError(
                "Dictionary read error at byte %s: stream must begin with '<<'"
                % hexStr(stream.tell())
            )

        while True:
            tok = readNonWhitespace(stream)

            if tok == b_('\x00'):
                continue
            elif tok == b_('%'):
                stream.seek(-1, 1)
                skipOverComment(stream)
                continue
            if not tok:
                # stream has truncated prematurely
                raise PdfStreamError("Stream has ended unexpectedly")

            if debug:
                print("Tok:", tok)

            if tok == b_(">"):
                stream.read(1)
                break

            stream.seek(-1, 1)
            key = readObject(stream, pdf)
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            value = readObject(stream, pdf)

            if not data.get(key):
                data[key] = value
            elif pdf.strict:
                # multiple definitions of key not permitted
                raise PdfReadError(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (hexStr(stream.tell()), key)
                )
            else:
                warnings.warn(
                    "Multiple definitions in dictionary at byte %s for key %s"
                    % (hexStr(stream.tell()), key), PdfReadWarning
                )

        pos = stream.tell()
        s = readNonWhitespace(stream)

        if s == b_('s') and stream.read(5) == b_('tream'):
            eol = stream.read(1)
            # Odd PDF file output has spaces after 'stream' keyword but before
            # EOL. Patch provided by Danial Sandler
            while eol == b_(' '):
                eol = stream.read(1)
            assert eol in (b_("\n"), b_("\r"))

            if eol == b_("\r"):
                # read \n after
                if stream.read(1)  != b_('\n'):
                    stream.seek(-1, 1)

            # this is a stream object, not a dictionary
            assert "/Length" in data
            length = data["/Length"]

            if debug:
                print(data)
            if isinstance(length, IndirectObject):
                t = stream.tell()
                length = pdf.getObject(length)
                stream.seek(t, 0)
            data["__streamdata__"] = stream.read(length)

            if debug:
                print("here")
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
                        "Unable to find 'endstream' marker after stream at "
                        "byte %s." % hexStr(stream.tell())
                    )
        else:
            stream.seek(pos, 0)
        if "__streamdata__" in data:
            return StreamObject.initializeFromDictionary(data)
        else:
            retval = DictionaryObject()
            retval.update(data)

            return retval


class TreeObject(DictionaryObject):
    def __init__(self):
        DictionaryObject.__init__()

    def hasChildren(self):
        return '/First' in self

    def __iter__(self):
        return self.children()

    def children(self):
        if not self.hasChildren():
            raise StopIteration

        child = self['/First']
        while True:
            yield child
            if child == self['/Last']:
                raise StopIteration
            child = child['/Next']

    def addChild(self, child, pdf):
        childObj = child.getObject()
        child = pdf.getReference(childObj)
        assert isinstance(child, IndirectObject)

        if '/First' not in self:
            self[NameObject('/First')] = child
            self[NameObject('/Count')] = NumberObject(0)
            prev = None
        else:
            prev = self['/Last']

        self[NameObject('/Last')] = child
        self[NameObject('/Count')] = NumberObject(
            self[NameObject('/Count')] + 1
        )

        if prev:
            prevRef = pdf.getReference(prev)
            assert isinstance(prevRef, IndirectObject)
            childObj[NameObject('/Prev')] = prevRef
            prev[NameObject('/Next')] = child

        parentRef = pdf.getReference(self)
        assert isinstance(parentRef, IndirectObject)
        childObj[NameObject('/Parent')] = parentRef

    def removeChild(self, child):
        childObj = child.getObject()

        if NameObject('/Parent') not in childObj:
            raise ValueError("Removed child does not appear to be a tree item")
        elif childObj[NameObject('/Parent')] != self:
            raise ValueError("Removed child is not a member of this tree")

        found = False
        prevRef = None
        prev = None
        curRef = self[NameObject('/First')]
        cur = curRef.getObject()
        lastRef = self[NameObject('/Last')]
        last = lastRef.getObject()

        while cur is not None:
            if cur == childObj:
                if prev is None:
                    if NameObject('/Next') in cur:
                        # Removing first tree node
                        nextRef = cur[NameObject('/Next')]
                        next = nextRef.getObject()
                        del next[NameObject('/Prev')]
                        self[NameObject('/First')] = nextRef
                        self[NameObject('/Count')] =\
                            self[NameObject('/Count')] - 1

                    else:
                        # Removing only tree node
                        assert self[NameObject('/Count')] == 1
                        del self[NameObject('/Count')]
                        del self[NameObject('/First')]
                        if NameObject('/Last') in self:
                            del self[NameObject('/Last')]
                else:
                    if NameObject('/Next') in cur:
                        # Removing middle tree node
                        nextRef = cur[NameObject('/Next')]
                        next = nextRef.getObject()
                        next[NameObject('/Prev')] = prevRef
                        prev[NameObject('/Next')] = nextRef
                        self[NameObject('/Count')] =\
                            self[NameObject('/Count')] - 1
                    else:
                        # Removing last tree node
                        assert cur == last
                        del prev[NameObject('/Next')]
                        self[NameObject('/Last')] = prevRef
                        self[NameObject('/Count')] =\
                            self[NameObject('/Count')] - 1
                found = True
                break

            prevRef = curRef
            prev = cur
            if NameObject('/Next') in cur:
                curRef = cur[NameObject('/Next')]
                cur = curRef.getObject()
            else:
                curRef = None
                cur = None

        if not found:
            raise ValueError("Removal couldn't find item in tree")

        del childObj[NameObject('/Parent')]
        if NameObject('/Next') in childObj:
            del childObj[NameObject('/Next')]
        if NameObject('/Prev') in childObj:
            del childObj[NameObject('/Prev')]

    def emptyTree(self):
        for child in self:
            childObj = child.getObject()
            del childObj[NameObject('/Parent')]
            if NameObject('/Next') in childObj:
                del childObj[NameObject('/Next')]
            if NameObject('/Prev') in childObj:
                del childObj[NameObject('/Prev')]

        if NameObject('/Count') in self:
            del self[NameObject('/Count')]
        if NameObject('/First') in self:
            del self[NameObject('/First')]
        if NameObject('/Last') in self:
            del self[NameObject('/Last')]


class StreamObject(DictionaryObject):
    def __init__(self):
        super(StreamObject, self).__init__()
        self._data = None
        self.decodedSelf = None

    def writeToStream(self, stream, encryption_key):
        self[NameObject("/Length")] = NumberObject(len(self._data))
        DictionaryObject.writeToStream(self, stream, encryption_key)
        del self["/Length"]
        stream.write(b_("\nstream\n"))
        data = self._data

        if encryption_key:
            data = RC4Encrypt(encryption_key, data)

        stream.write(data)
        stream.write(b_("\nendstream"))

    @staticmethod
    def initializeFromDictionary(data):
        if "/Filter" in data:
            if data.get("/Type") == "/ObjStm":
                retval = ObjectStream()
            else:
                retval = EncodedStreamObject()
        else:
            retval = DecodedStreamObject()

        retval._data = data["__streamdata__"]
        del data["__streamdata__"]
        del data["/Length"]
        retval.update(data)

        return retval

    def flateEncode(self):
        from pypdf.filters import FlateCodec

        if "/Filter" in self:
            f = self["/Filter"]

            if isinstance(f, ArrayObject):
                f.insert(0, NameObject("/FlateDecode"))
            else:
                newf = ArrayObject()
                newf.append(NameObject("/FlateDecode"))
                newf.append(f)
                f = newf
        else:
            f = NameObject("/FlateDecode")

        retval = EncodedStreamObject()
        retval[NameObject("/Filter")] = f
        retval._data = FlateCodec.encode(self._data)

        return retval


class EncodedStreamObject(StreamObject):
    def __init__(self):
        super(EncodedStreamObject, self).__init__()
        self.decodedSelf = None

    def getData(self):
        from pypdf.filters import decodeStreamData

        if self.decodedSelf:
            # Cached version of decoded object
            return self.decodedSelf.getData()
        else:
            # Create decoded object
            decoded = DecodedStreamObject()
            decoded._data = decodeStreamData(self)

            for key, value in list(self.items()):
                if not key in ("/Length", "/Filter", "/DecodeParms"):
                    decoded[key] = value

            self.decodedSelf = decoded

            return decoded._data

    def setData(self, data):
        raise NotImplementedError(
            "Creating EncodedStreamObject is not currently supported"
        )


class DecodedStreamObject(StreamObject):
    def __init__(self):
        super(DecodedStreamObject, self).__init__()

    def getData(self):
        return self._data

    def setData(self, data):
        self._data = data


class ContentStream(DecodedStreamObject):
    def __init__(self, stream, pdf):
        super(ContentStream, self).__init__()
        self.pdf = pdf
        self.operations = []
        # stream may be a StreamObject or an ArrayObject containing
        # multiple StreamObjects to be cat'd together.
        stream = stream.getObject()

        if isinstance(stream, ArrayObject):
            data = b_("")
            for s in stream:
                data += b_(s.getObject().getData())
            stream = BytesIO(b_(data))
        else:
            stream = BytesIO(b_(stream.getData()))

        self.__parseContentStream(stream)

    def __parseContentStream(self, stream):
        stream.seek(0, 0)
        operands = []

        while True:
            peek = readNonWhitespace(stream)

            if peek == b_('') or pypdfOrd(peek) == 0:
                break

            stream.seek(-1, 1)
            if peek.isalpha() or peek == b_("'") or peek == b_('"'):
                operator = readUntilRegex(
                    stream, NameObject.delimiterPattern, True
                )
                if operator == b_("BI"):
                    # Begin inline image - a completely different parsing
                    # mechanism is required
                    assert operands == []
                    ii = self._readInlineImage(stream)
                    self.operations.append((ii, b_("INLINE IMAGE")))
                else:
                    self.operations.append((operands, operator))
                    operands = []
            elif peek == b_('%'):
                # If we encounter a comment in the content stream, we have to
                # handle it here.  Typically, readObject will handle
                # encountering a comment -- but readObject assumes that
                # following the comment must be the object we're trying to
                # read.  In this case, it could be an operator instead.
                while peek not in (b_('\r'), b_('\n')):
                    peek = stream.read(1)
            else:
                operands.append(readObject(stream, None))

    def _readInlineImage(self, stream):
        # Begin reading just after the "BI" - begin image
        # First read the dictionary of settings.
        settings = DictionaryObject()

        while True:
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)

            if tok == b_("I"):
                # "ID" - begin of image data
                break

            key = readObject(stream, self.pdf)
            tok = readNonWhitespace(stream)
            stream.seek(-1, 1)
            value = readObject(stream, self.pdf)
            settings[key] = value

        # Left at beginning of ID
        tmp = stream.read(3)
        assert tmp[:2] == b_("ID")
        data = b_("")

        while True:
            # Read the inline image, while checking for EI (End Image) operator
            tok = stream.read(1)

            if tok == b_("E"):
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
                        data += info
                else:
                    stream.seek(-1, 1)
                    data += tok
            else:
                data += tok

        return {"settings": settings, "data": data}

    def _getData(self):
        newdata = BytesIO()

        for operands, operator in self.operations:
            if operator == b_("INLINE IMAGE"):
                newdata.write(b_("BI"))
                dicttext = BytesIO()
                operands["settings"].writeToStream(dicttext, None)
                newdata.write(dicttext.getvalue()[2:-2])
                newdata.write(b_("ID "))
                newdata.write(operands["data"])
                newdata.write(b_("EI"))
            else:
                for op in operands:
                    op.writeToStream(newdata, None)
                    newdata.write(b_(" "))

                newdata.write(b_(operator))

            newdata.write(b_("\n"))

        return newdata.getvalue()

    def _setData(self, value):
        if value:
            self.__parseContentStream(BytesIO(b_(value)))

    _data = property(_getData, _setData)


class ObjectStream(EncodedStreamObject):
    DATA_HEADER_RE = re.compile(b"(?:\d+\s)+")
    """
    Regex to match pairs of ids and offset numbers in the first part of an
    object stream data.
    """

    def __init__(self):
        """
        Class intended to provide simplified access to some of object streams'
        properties.
        """
        super(ObjectStream, self).__init__()

    @property
    def objectIds(self):
        """
        :return: an iterable containing a sequence of object ids sorted
            according to their appearance order, stored in the object stream
            header.
        """
        match = self.DATA_HEADER_RE.match(self.getData())
        output = [int(n) for n in match.group().split()]

        if (len(output) % 2) != 0:
            raise PdfReadError(
                "Object stream header must contain an even list of numbers"
            )

        return tuple(output[i] for i in range(0, len(output), 2))


class DocumentInformation(DictionaryObject):
    """
    A class representing the basic document metadata provided in a PDF File.
    This class is accessible through
    :meth:`documentInfo()<pypdf.PdfFileReader.documentInfo()>`

    All text properties of the document metadata have
    *two* properties, e.g. author and author_raw. The non-raw property will
    always return a ``TextStringObject``, making it ideal for a case where
    the metadata is being displayed. The raw property can sometimes return
    a ``ByteStringObject``, if PyPDF was unable to decode the string's
    text encoding; this requires additional safety in the caller and
    therefore is not as commonly accessed.
    """

    def __init__(self):
        DictionaryObject.__init__(self)

    def getText(self, key):
        retval = self.get(key, None)

        if isinstance(retval, TextStringObject):
            return retval

        return None

    title = property(lambda self: self.getText("/Title"))
    """
    Read-only property accessing the document's **title**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the title is not specified.
    """

    title_raw = property(lambda self: self.get("/Title"))
    """The "raw" version of title; can return a ``ByteStringObject``."""

    author = property(lambda self: self.getText("/Author"))
    """
    Read-only property accessing the document's **author**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the author is not specified.
    """

    author_raw = property(lambda self: self.get("/Author"))
    """The "raw" version of author; can return a ``ByteStringObject``."""

    subject = property(lambda self: self.getText("/Subject"))
    """
    Read-only property accessing the document's **subject**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the subject is not specified.
    """

    subject_raw = property(lambda self: self.get("/Subject"))
    """The "raw" version of subject; can return a ``ByteStringObject``."""

    creator = property(lambda self: self.getText("/Creator"))
    """
    Read-only property accessing the document's **creator**. If the
    document was converted to PDF from another format, this is the name of the
    application (e.g. OpenOffice) that created the original document from
    which it was converted. Returns a unicode string (``TextStringObject``)
    or ``None`` if the creator is not specified.
    """

    creator_raw = property(lambda self: self.get("/Creator"))
    """The "raw" version of creator; can return a ``ByteStringObject``."""

    producer = property(lambda self: self.getText("/Producer"))
    """
    Read-only property accessing the document's **producer**.
    If the document was converted to PDF from another format, this is
    the name of the application (for example, OSX Quartz) that converted
    it to PDF. Returns a unicode string (``TextStringObject``)
    or ``None`` if the producer is not specified.
    """

    producer_raw = property(lambda self: self.get("/Producer"))
    """The "raw" version of producer; can return a ``ByteStringObject``."""
    
    keywords = property(lambda self: self.getText("/Keywords"))
    """
    Read-only property accessing the document's **keywords**.
    Returns a unicode string (``TextStringObject``) or ``None``
    if the keywords are not specified.
    """

    keywords_raw = property(lambda self: self.get("/Keywords"))
    """The "raw" version of keywords; can return a ``ByteStringObject``."""

class RectangleObject(ArrayObject):
    """
    This class is used to represent *page boxes* in PyPDF. These boxes
    include:

        * :attr:`artBox<pypdf.generic.PageObject.artBox>`
        * :attr:`bleedBox<pypdf.generic.PageObject.bleedBox>`
        * :attr:`cropBox<pypdf.generic.PageObject.cropBox>`
        * :attr:`mediaBox<pypdf.generic.PageObject.mediaBox>`
        * :attr:`trimBox<pypdf.generic.PageObject.trimBox>`
    """
    def __init__(self, arr):
        # Must have four points
        assert len(arr) == 4
        # Automatically convert arr[x] into NumberObject(arr[x]) if necessary
        ArrayObject.__init__(self, [self.ensureIsNumber(x) for x in arr])

    def ensureIsNumber(self, value):
        if not isinstance(value, (NumberObject, FloatObject)):
            value = FloatObject(value)
        return value

    def __repr__(self):
        return "RectangleObject(%s)" % repr(list(self))

    def getLowerLeft_x(self):
        return self[0]

    def getLowerLeft_y(self):
        return self[1]

    def getUpperRight_x(self):
        return self[2]

    def getUpperRight_y(self):
        return self[3]

    def getUpperLeft_x(self):
        return self.getLowerLeft_x()

    def getUpperLeft_y(self):
        return self.getUpperRight_y()

    def getLowerRight_x(self):
        return self.getUpperRight_x()

    def getLowerRight_y(self):
        return self.getLowerLeft_y()

    def getLowerLeft(self):
        return self.getLowerLeft_x(), self.getLowerLeft_y()

    def getLowerRight(self):
        return self.getLowerRight_x(), self.getLowerRight_y()

    def getUpperLeft(self):
        return self.getUpperLeft_x(), self.getUpperLeft_y()

    def getUpperRight(self):
        return self.getUpperRight_x(), self.getUpperRight_y()

    def setLowerLeft(self, value):
        self[0], self[1] = [self.ensureIsNumber(x) for x in value]

    def setLowerRight(self, value):
        self[2], self[1] = [self.ensureIsNumber(x) for x in value]

    def setUpperLeft(self, value):
        self[0], self[3] = [self.ensureIsNumber(x) for x in value]

    def setUpperRight(self, value):
        self[2], self[3] = [self.ensureIsNumber(x) for x in value]

    def getWidth(self):
        return self.getUpperRight_x() - self.getLowerLeft_x()

    def getHeight(self):
        return self.getUpperRight_y() - self.getLowerLeft_y()

    lowerLeft = property(getLowerLeft, setLowerLeft)
    """
    Property to read and modify the lower left coordinate of this box
    in (x,y) form.
    """

    lowerRight = property(getLowerRight, setLowerRight)
    """
    Property to read and modify the lower right coordinate of this box
    in (x,y) form.
    """

    upperLeft = property(getUpperLeft, setUpperLeft)
    """
    Property to read and modify the upper left coordinate of this box
    in (x,y) form.
    """

    upperRight = property(getUpperRight, setUpperRight)
    """
    Property to read and modify the upper right coordinate of this box
    in (x,y) form.
    """


def getRectangle(self, name, defaults):
    retval = self.get(name)

    if isinstance(retval, RectangleObject):
        return retval
    if retval is None:
        for d in defaults:
            retval = self.get(d)
            if retval is not None:
                break
    if isinstance(retval, IndirectObject):
        retval = self.pdf.getObject(retval)

    retval = RectangleObject(retval)
    setRectangle(self, name, retval)

    return retval


def setRectangle(self, name, value):
    if not isinstance(name, NameObject):
        name = NameObject(name)
    self[name] = value


def deleteRectangle(self, name):
    del self[name]


def createRectangleAccessor(name, fallback):
    return property(
        lambda self: getRectangle(self, name, fallback),
        lambda self, value: setRectangle(self, name, value),
        lambda self: deleteRectangle(self, name)
    )


class PageObject(DictionaryObject):
    """
    This class represents a single page within a PDF file.  Typically this
    object will be created by accessing the
    :meth:`getPage()<pypdf.PdfFileReader.getPage>` method of the
    :class:`PdfFileReader<pypdf.PdfFileReader>` class, but it is
    also possible to create an empty page with the
    :meth:`createBlankPage()<PageObject.createBlankPage>` static method.

    :param pdf: PDF file the page belongs to.
    :param indirectRef: Stores the original indirect reference to
        this object in its source PDF
    """
    def __init__(self, pdf=None, indirectRef=None):
        DictionaryObject.__init__(self)
        self.pdf = pdf
        self.indirectRef = indirectRef

    @staticmethod
    def createBlankPage(pdf=None, width=None, height=None):
        """
        Returns a new blank page.
        If ``width`` or ``height`` is ``None``, try to get the page size from
        the last page of *pdf*.

        :param pdf: PDF file the page belongs to
        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :return: the new blank page:
        :rtype: :class:`PageObject<PageObject>`
        :raises PageSizeNotDefinedError: if ``pdf`` is ``None`` or contains
            no page
        """
        page = PageObject(pdf)

        # Creates a new page (cnf. PDF Reference 7.7.3.3)
        page.__setitem__(NameObject('/Type'), NameObject('/Page'))
        page.__setitem__(NameObject('/Parent'), NullObject())
        page.__setitem__(NameObject('/Resources'), DictionaryObject())

        if width is None or height is None:
            if pdf is not None and pdf.numPages > 0:
                lastpage = pdf.getPage(pdf.numPages - 1)
                width = lastpage.mediaBox.getWidth()
                height = lastpage.mediaBox.getHeight()
            else:
                raise PageSizeNotDefinedError()
        page.__setitem__(
            NameObject('/MediaBox'), RectangleObject([0, 0, width, height])
        )

        return page

    def rotateClockwise(self, angle):
        """
        Rotates a page clockwise by increments of 90 degrees.

        :param int angle: Angle to rotate the page.  Must be an increment of 90
            deg.
        """
        assert angle % 90 == 0
        self._rotate(angle)
        return self

    def rotateCounterClockwise(self, angle):
        """
        Rotates a page counter-clockwise by increments of 90 degrees.

        :param int angle: Angle to rotate the page.  Must be an increment
            of 90 deg.
        """
        assert angle % 90 == 0
        self._rotate(-angle)
        return self

    def _rotate(self, angle):
        rotateObj = self.get("/Rotate", 0)
        currentAngle = rotateObj if isinstance(rotateObj, int) else \
            rotateObj.getObject()
        self[NameObject("/Rotate")] = NumberObject(currentAngle + angle)

    @staticmethod
    def _mergeResources(res1, res2, resource):
        newRes = DictionaryObject()
        newRes.update(res1.get(resource, DictionaryObject()).getObject())
        page2Res = res2.get(resource, DictionaryObject()).getObject()
        renameRes = {}

        for key in list(page2Res.keys()):
            if key in newRes and newRes.rawGet(key) != page2Res.rawGet(key):
                newname = NameObject(key + str(uuid.uuid4()))
                renameRes[key] = newname
                newRes[newname] = page2Res[key]
            elif key not in newRes:
                newRes[key] = page2Res.rawGet(key)

        return newRes, renameRes

    @staticmethod
    def _contentStreamRename(stream, rename, pdf):
        if not rename:
            return stream

        stream = ContentStream(stream, pdf)

        for operands, operator in stream.operations:
            for i in range(len(operands)):
                op = operands[i]
                if isinstance(op, NameObject):
                    operands[i] = rename.get(op, op)

        return stream

    @staticmethod
    def _pushPopGS(contents, pdf):
        # Adds a graphics state "push" and "pop" to the beginning and end of a
        # content stream.  This isolates it from changes such as transformation
        # matrices.
        stream = ContentStream(contents, pdf)
        stream.operations.insert(0, [[], "q"])
        stream.operations.append([[], "Q"])

        return stream

    @staticmethod
    def _addTransformationMatrix(contents, pdf, ctm):
        # Adds transformation matrix at the beginning of the given contents
        # stream.
        a, b, c, d, e, f = ctm
        contents = ContentStream(contents, pdf)
        contents.operations.insert(
            0, [[FloatObject(a), FloatObject(b), FloatObject(c),
                 FloatObject(d), FloatObject(e), FloatObject(f)], " cm"]
        )

        return contents

    def getContents(self):
        """
        Accesses the page contents.

        :return: the ``/Contents`` object, or ``None`` if it doesn't exist.
            ``/Contents`` is optional, as described in PDF Reference  7.7.3.3
        """
        if "/Contents" in self:
            return self["/Contents"].getObject()
        else:
            return None

    def mergePage(self, page2):
        """
        Merges the content streams of two pages into one.  Resource references
        (i.e. fonts) are maintained from both pages.  The mediabox/cropbox/etc
        of this page are not altered.  The parameter page's content stream will
        be added to the end of this page's content stream, meaning that it will
        be drawn after, or "on top" of this page.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        """
        self._mergePage(page2)

    def _mergePage(self, page2, page2transformation=None, ctm=None,
                   expand=False):
        # First we work on merging the resource dictionaries.  This allows us
        # to find out what symbols in the content streams we might need to
        # rename.
        newResources = DictionaryObject()
        rename = {}
        originalResources = self["/Resources"].getObject()
        page2Resources = page2["/Resources"].getObject()
        newAnnots = ArrayObject()

        for page in (self, page2):
            if "/Annots" in page:
                annots = page["/Annots"]
                if isinstance(annots, ArrayObject):
                    for ref in annots:
                        newAnnots.append(ref)

        for res in ("/ExtGState", "/Font", "/XObject", "/ColorSpace",
                    "/Pattern", "/Shading", "/Properties"):
            new, newrename = PageObject._mergeResources(
                originalResources, page2Resources, res
            )
            if new:
                newResources[NameObject(res)] = new
                rename.update(newrename)

        # Combine /ProcSet sets.
        newResources[NameObject("/ProcSet")] = ArrayObject(
            frozenset(
                originalResources.get("/ProcSet", ArrayObject()).getObject()
            ).union(
                frozenset(
                    page2Resources.get("/ProcSet", ArrayObject()).getObject()
                )
            )
        )

        newContentArray = ArrayObject()

        originalContent = self.getContents()

        if originalContent is not None:
            newContentArray.append(PageObject._pushPopGS(
                originalContent, self.pdf))

        page2Content = page2.getContents()

        if page2Content is not None:
            if page2transformation is not None:
                page2Content = page2transformation(page2Content)
            page2Content = PageObject._contentStreamRename(
                page2Content, rename, self.pdf)
            page2Content = PageObject._pushPopGS(page2Content, self.pdf)
            newContentArray.append(page2Content)

        # If expanding the page to fit a new page, calculate the new media box
        # size
        if expand:
            corners1 = [self.mediaBox.getLowerLeft_x().asNumeric(),
                        self.mediaBox.getLowerLeft_y().asNumeric(),
                        self.mediaBox.getUpperRight_x().asNumeric(),
                        self.mediaBox.getUpperRight_y().asNumeric()]
            corners2 = [page2.mediaBox.getLowerLeft_x().asNumeric(),
                        page2.mediaBox.getLowerLeft_y().asNumeric(),
                        page2.mediaBox.getUpperLeft_x().asNumeric(),
                        page2.mediaBox.getUpperLeft_y().asNumeric(),
                        page2.mediaBox.getUpperRight_x().asNumeric(),
                        page2.mediaBox.getUpperRight_y().asNumeric(),
                        page2.mediaBox.getLowerRight_x().asNumeric(),
                        page2.mediaBox.getLowerRight_y().asNumeric()]
            if ctm is not None:
                ctm = [float(x) for x in ctm]
                new_x = [ctm[0]*corners2[i] + ctm[2]*corners2[i+1] + ctm[4]
                         for i in range(0, 8, 2)]
                new_y = [ctm[1]*corners2[i] + ctm[3]*corners2[i+1] + ctm[5]
                         for i in range(0, 8, 2)]
            else:
                new_x = corners2[0:8:2]
                new_y = corners2[1:8:2]

            lowerleft = [min(new_x), min(new_y)]
            upperright = [max(new_x), max(new_y)]
            lowerleft = [min(corners1[0], lowerleft[0]), min(corners1[1],
                                                             lowerleft[1])]
            upperright = [max(corners1[2], upperright[0]), max(corners1[3],
                                                               upperright[1])]

            self.mediaBox.setLowerLeft(lowerleft)
            self.mediaBox.setUpperRight(upperright)

        self[NameObject('/Contents')] = ContentStream(newContentArray,
                                                      self.pdf)
        self[NameObject('/Resources')] = newResources
        self[NameObject('/Annots')] = newAnnots

    def mergeTransformedPage(self, page2, ctm, expand=False):
        """
        This is similar to mergePage, but a transformation matrix is
        applied to the merged stream.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param tuple ctm: a 6-element tuple containing the operands of the
            transformation matrix
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        self._mergePage(
            page2, lambda page2Content: PageObject._addTransformationMatrix(
                page2Content, page2.pdf, ctm), ctm, expand
        )

    def mergeScaledPage(self, page2, scale, expand=False):
        """
        This is similar to mergePage, but the stream to be merged is scaled
        by appling a transformation matrix.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float scale: The scaling factor
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        # CTM to scale : [ sx 0 0 sy 0 0 ]
        return self.mergeTransformedPage(
            page2, (scale, 0, 0, scale, 0, 0), expand
        )

    def mergeRotatedPage(self, page2, rotation, expand=False):
        """
        This is similar to mergePage, but the stream to be merged is rotated
        by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float rotation: The angle of the rotation, in degrees
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        rotation = math.radians(rotation)

        return self.mergeTransformedPage(
            page2, (math.cos(rotation), math.sin(rotation),
                    -math.sin(rotation), math.cos(rotation), 0, 0), expand
        )

    def mergeTranslatedPage(self, page2, tx, ty, expand=False):
        """
        This is similar to ``mergePage``, but the stream to be merged is
        translated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis.
        :param float ty: The translation on Y axis.
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        return self.mergeTransformedPage(page2, (1,  0, 0,  1, tx, ty), expand)

    def mergeRotatedTranslatedPage(
            self, page2, rotation, tx, ty, expand=False
    ):
        """
        This is similar to mergePage, but the stream to be merged is rotated
        and translated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis.
        :param float ty: The translation on Y axis.
        :param float rotation: The angle of the rotation, in degrees.
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """

        translation = [[1, 0, 0], [0, 1, 0], [-tx, -ty, 1]]
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1]
        ]
        rtranslation = [
            [1, 0, 0], [0, 1, 0], [tx, ty, 1]
        ]
        ctm = matrixMultiply(translation, rotating)
        ctm = matrixMultiply(ctm, rtranslation)

        return self.mergeTransformedPage(
            page2,
            (ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]),
            expand
        )

    def mergeRotatedScaledPage(self, page2, rotation, scale, expand=False):
        """
        This is similar to mergePage, but the stream to be merged is rotated
        and scaled by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float rotation: The angle of the rotation, in degrees.
        :param float scale: The scaling factor.
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1]
        ]
        scaling = [
            [scale, 0, 0], [0, scale, 0], [0, 0, 1]
        ]
        ctm = matrixMultiply(rotating, scaling)

        return self.mergeTransformedPage(
            page2,
            (ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]),
            expand
        )

    def mergeScaledTranslatedPage(self, page2, scale, tx, ty, expand=False):
        """
        This is similar to mergePage, but the stream to be merged is translated
        and scaled by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float scale: The scaling factor.
        :param float tx: The translation on X axis.
        :param float ty: The translation on Y axis.
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """

        translation = [
            [1, 0, 0], [0, 1, 0], [tx, ty, 1]
        ]
        scaling = [
            [scale, 0, 0], [0, scale, 0], [0, 0, 1]
        ]
        ctm = matrixMultiply(scaling, translation)

        return self.mergeTransformedPage(
            page2,
            (ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]),
            expand
        )

    def mergeRotatedScaledTranslatedPage(
            self, page2, rotation, scale, tx, ty, expand=False
    ):
        """
        This is similar to mergePage, but the stream to be merged is
        translated, rotated and scaled by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis.
        :param float ty: The translation on Y axis.
        :param float rotation: The angle of the rotation, in degrees.
        :param float scale: The scaling factor.
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        translation = [
            [1, 0, 0], [0, 1, 0], [tx, ty, 1]
        ]
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1]
        ]
        scaling = [
            [scale, 0, 0], [0, scale, 0], [0, 0, 1]
        ]
        ctm = matrixMultiply(rotating, scaling)
        ctm = matrixMultiply(ctm, translation)

        return self.mergeTransformedPage(
            page2,
            (ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]),
            expand
        )

    def addTransformation(self, ctm):
        """
        Applies a transformation matrix to the page.

        :param tuple ctm: A 6-element tuple containing the operands of the
            transformation matrix.
        """
        originalContent = self.getContents()

        if originalContent is not None:
            newContent = PageObject._addTransformationMatrix(
                originalContent, self.pdf, ctm)
            newContent = PageObject._pushPopGS(newContent, self.pdf)
            self[NameObject('/Contents')] = newContent

    def scale(self, sx, sy):
        """
        Scales a page by the given factors by appling a transformation
        matrix to its content and updating the page size.

        :param float sx: The scaling factor on horizontal axis.
        :param float sy: The scaling factor on vertical axis.
        """
        self.addTransformation((sx, 0, 0,  sy, 0,  0))
        self.mediaBox = RectangleObject([
            float(self.mediaBox.getLowerLeft_x()) * sx,
            float(self.mediaBox.getLowerLeft_y()) * sy,
            float(self.mediaBox.getUpperRight_x()) * sx,
            float(self.mediaBox.getUpperRight_y()) * sy]
        )

        if "/VP" in self:
            viewport = self["/VP"]

            if isinstance(viewport, ArrayObject):
                bbox = viewport[0]["/BBox"]
            else:
                bbox = viewport["/BBox"]

            scaled_bbox = RectangleObject([
                float(bbox[0]) * sx, float(bbox[1]) * sy, float(bbox[2]) * sx,
                float(bbox[3]) * sy]
            )

            if isinstance(viewport, ArrayObject):
                self[NameObject("/VP")][NumberObject(0)][NameObject("/BBox")] \
                    = scaled_bbox
            else:
                self[NameObject("/VP")][NameObject("/BBox")] = scaled_bbox

    def scaleBy(self, factor):
        """
        Scales a page by the given factor by appling a transformation
        matrix to its content and updating the page size.

        :param float factor: The scaling factor (for both X and Y axis).
        """
        self.scale(factor, factor)

    def scaleTo(self, width, height):
        """
        Scales a page to the specified dimentions by appling a
        transformation matrix to its content and updating the page size.

        :param float width: The new width.
        :param float height: The new heigth.
        """
        sx = width / float(self.mediaBox.getUpperRight_x() -
                           self.mediaBox.getLowerLeft_x())
        sy = height / float(self.mediaBox.getUpperRight_y() -
                            self.mediaBox.getLowerLeft_y())
        self.scale(sx, sy)

    def compressContentStreams(self):
        """
        Compresses the size of this page by joining all content streams and
        applying a FlateDecode filter.

        However, it is possible that this function will perform no action if
        content stream compression becomes "automatic" for some reason.
        """
        content = self.getContents()

        if content is not None:
            if not isinstance(content, ContentStream):
                content = ContentStream(content, self.pdf)
            self[NameObject("/Contents")] = content.flateEncode()

    def extractText(self):
        """
        Locate all text drawing commands, in the order they are provided in the
        content stream, and extract the text.  This works well for some PDF
        files, but poorly for others, depending on the generator used.  This
        will be refined in the future.  Do not rely on the order of text coming
        out of this function, as it will change if this function is made more
        sophisticated.

        :return: a unicode string object.
        """
        text = pypdfUnicode("")
        content = self["/Contents"].getObject()

        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pdf)

        # Note: we check all strings are TextStringObjects.  ByteStringObjects
        # are strings where the byte->string encoding was unknown, so adding
        # them to the text here would be gibberish.
        for operands, operator in content.operations:
            if operator == b_("Tj"):
                _text = operands[0]

                if isinstance(_text, TextStringObject):
                    text += _text
                    text += "\n"
            elif operator == b_("T*"):
                text += "\n"
            elif operator == b_("'"):
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == b_('"'):
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == b_("TJ"):
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += i
                text += "\n"

        return text

    mediaBox = createRectangleAccessor("/MediaBox", ())
    """
    A :class:`RectangleObject<pypdf.generic.RectangleObject>`, expressed in
    default user space units, defining the boundaries of the physical medium on
    which the page is intended to be displayed or printed.
    """

    cropBox = createRectangleAccessor("/CropBox", ("/MediaBox",))
    """
    A :class:`RectangleObject<pypdf.generic.RectangleObject>`, expressed in
    default user space units, defining the visible region of default user
    space.  When the page is displayed or printed, its contents are to be
    clipped (cropped) to this rectangle and then imposed on the output medium
    in some implementation-defined manner.  Default value: same as
    :attr:`mediaBox<mediaBox>`.
    """

    bleedBox = createRectangleAccessor("/BleedBox", ("/CropBox", "/MediaBox"))
    """
    A :class:`RectangleObject<pypdf.generic.RectangleObject>`, expressed in
    default user space units, defining the region to which the contents of the
    page should be clipped when output in a production enviroment.
    """

    trimBox = createRectangleAccessor("/TrimBox", ("/CropBox", "/MediaBox"))
    """
    A :class:`RectangleObject<pypdf.generic.RectangleObject>`, expressed in
    default user space units, defining the intended dimensions of the finished
    page after trimming.
    """

    artBox = createRectangleAccessor("/ArtBox", ("/CropBox", "/MediaBox"))
    """
    A :class:`RectangleObject<pypdf.generic.RectangleObject>`, expressed in
    default user space units, defining the extent of the page's meaningful
    content as intended by the page's creator.
    """


class Field(TreeObject):
    """
    A class representing a field dictionary. This class is accessed through
    :meth:`getFields()<pypdf.PdfFileReader.getFields>`
    """
    def __init__(self, data):
        DictionaryObject.__init__(self)
        attributes = ("/FT", "/Parent", "/Kids", "/T", "/TU", "/TM", "/Ff",
                      "/V", "/DV", "/AA")
        for attr in attributes:
            try:
                self[NameObject(attr)] = data[attr]
            except KeyError:
                pass

    fieldType = property(lambda self: self.get("/FT"))
    """
    Read-only property accessing the type of this field.
    """

    parent = property(lambda self: self.get("/Parent"))
    """
    Read-only property accessing the parent of this field.
    """

    kids = property(lambda self: self.get("/Kids"))
    """
    Read-only property accessing the kids of this field.
    """

    name = property(lambda self: self.get("/T"))
    """
    Read-only property accessing the name of this field.
    """

    altName = property(lambda self: self.get("/TU"))
    """
    Read-only property accessing the alternate name of this field.
    """

    mappingName = property(lambda self: self.get("/TM"))
    """
    Read-only property accessing the mapping name of this field. This
    name is used by PyPDF as a key in the dictionary returned by
    :meth:`getFields<pypdf.PdfFileReader.getFields>`.
    """

    flags = property(lambda self: self.get("/Ff"))
    """
    Read-only property accessing the field flags, specifying various
    characteristics of the field (see Table 8.70 of the PDF 1.7 reference).
    """

    value = property(lambda self: self.get("/V"))
    """
    Read-only property accessing the value of this field. Format
    varies based on field type.
    """

    defaultValue = property(lambda self: self.get("/DV"))
    """
    Read-only property accessing the default value of this field.
    """

    additionalActions = property(lambda self: self.get("/AA"))
    """
    Read-only property accessing the additional actions dictionary.
    This dictionary defines the field's behavior in response to trigger events.
    See Section 8.5.2 of the PDF 1.7 reference.
    """


class Destination(TreeObject):
    """
    A class representing a destination within a PDF file.
    See section 8.2.1 of the PDF 1.6 reference.

    :param str title: Title of this destination.
    :param int page: Page number of this destination.
    :param str typ: How the destination is displayed.
    :param args: Additional arguments may be necessary depending on the type.
    :raises PdfReadError: If destination type is invalid.

    Valid ``typ`` arguments (see PDF spec for details):
             /Fit       No additional arguments
             /XYZ       [left] [top] [zoomFactor]
             /FitH      [top]
             /FitV      [left]
             /FitR      [left] [bottom] [right] [top]
             /FitB      No additional arguments
             /FitBH     [top]
             /FitBV     [left]
    """
    def __init__(self, title, page, typ, *args):
        DictionaryObject.__init__(self)
        self[NameObject("/Title")] = title
        self[NameObject("/Page")] = page
        self[NameObject("/Type")] = typ

        # from table 8.2 of the PDF 1.7 reference.
        if typ == "/XYZ":
            (self[NameObject("/Left")], self[NameObject("/Top")],
                self[NameObject("/Zoom")]) = args
        elif typ == "/FitR":
            (self[NameObject("/Left")], self[NameObject("/Bottom")],
                self[NameObject("/Right")], self[NameObject("/Top")]) = args
        elif typ in ["/FitH", "/FitBH"]:
            self[NameObject("/Top")], = args
        elif typ in ["/FitV", "/FitBV"]:
            self[NameObject("/Left")], = args
        elif typ in ["/Fit", "/FitB"]:
            pass
        else:
            raise PdfReadError("Unknown Destination Type: %r" % typ)

    def getDestArray(self):
        return ArrayObject(
            [self.rawGet('/Page'), self['/Type']] + [
                self[x] for x in
                ['/Left', '/Bottom', '/Right', '/Top', '/Zoom'] if x in self
            ])

    def writeToStream(self, stream, encryption_key):
        stream.write(b_("<<\n"))
        key = NameObject('/D')
        key.writeToStream(stream, encryption_key)
        stream.write(b_(" "))
        value = self.getDestArray()
        value.writeToStream(stream, encryption_key)

        key = NameObject("/S")
        key.writeToStream(stream, encryption_key)
        stream.write(b_(" "))
        value = NameObject("/GoTo")
        value.writeToStream(stream, encryption_key)

        stream.write(b_("\n"))
        stream.write(b_(">>"))

    title = property(lambda self: self.get("/Title"))
    """
    Read-only property accessing the destination title.

    :rtype: ``str``
    """

    page = property(lambda self: self.get("/Page"))
    """
    Read-only property accessing the destination page number.

    :rtype: ``int``
    """

    typ = property(lambda self: self.get("/Type"))
    """
    Read-only property accessing the destination type.

    :rtype: ``str``
    """

    zoom = property(lambda self: self.get("/Zoom", None))
    """
    Read-only property accessing the zoom factor.

    :rtype: ``int``, or ``None`` if not available.
    """

    left = property(lambda self: self.get("/Left", None))
    """
    Read-only property accessing the left horizontal coordinate.

    :rtype: ``int``, or ``None`` if not available.
    """

    right = property(lambda self: self.get("/Right", None))
    """
    Read-only property accessing the right horizontal coordinate.

    :rtype: ``int``, or ``None`` if not available.
    """

    top = property(lambda self: self.get("/Top", None))
    """
    Read-only property accessing the top vertical coordinate.

    :rtype: ``int``, or ``None`` if not available.
    """

    bottom = property(lambda self: self.get("/Bottom", None))
    """
    Read-only property accessing the bottom vertical coordinate.

    :rtype: ``int``, or ``None`` if not available.
    """


class Bookmark(Destination):
    def writeToStream(self, stream, encryption_key):
        stream.write(b_("<<\n"))

        for key in [NameObject(x) for x in [
            '/Title', '/Parent', '/First', '/Last', '/Next', '/Prev'
        ] if x in self]:
            key.writeToStream(stream, encryption_key)
            stream.write(b_(" "))
            value = self.rawGet(key)
            value.writeToStream(stream, encryption_key)
            stream.write(b_("\n"))

        key = NameObject('/Dest')
        key.writeToStream(stream, encryption_key)
        stream.write(b_(" "))
        value = self.getDestArray()
        value.writeToStream(stream, encryption_key)
        stream.write(b_("\n"))
        stream.write(b_(">>"))


def encodePdfDocEncoding(unicodeStr):
    retval = b_('')

    for c in unicodeStr:
        try:
            retval += b_(chr(_pdfDocEncoding_rev[c]))
        except KeyError:
            raise UnicodeEncodeError(
                "pdfdocencoding", c, -1, -1,
                "does not exist in translation table"
            )

    return retval


def decodePdfDocEncoding(byteArray):
    retval = u_('')

    for b in byteArray:
        c = _pdfDocEncoding[pypdfOrd(b)]

        if c == u_('\u0000'):
            raise UnicodeDecodeError(
                "pdfdocencoding", pypdfBytearray(b), -1, -1,
                "does not exist in translation table"
            )

        retval += c

    return retval


_pdfDocEncoding = (
    u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'),
    u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'),
    u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'),
    u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'),
    u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u0000'), u_('\u02d8'),
    u_('\u02c7'), u_('\u02c6'), u_('\u02d9'), u_('\u02dd'), u_('\u02db'),
    u_('\u02da'), u_('\u02dc'), u_('\u0020'), u_('\u0021'), u_('\u0022'),
    u_('\u0023'), u_('\u0024'), u_('\u0025'), u_('\u0026'), u_('\u0027'),
    u_('\u0028'), u_('\u0029'), u_('\u002a'), u_('\u002b'), u_('\u002c'),
    u_('\u002d'), u_('\u002e'), u_('\u002f'), u_('\u0030'), u_('\u0031'),
    u_('\u0032'), u_('\u0033'), u_('\u0034'), u_('\u0035'), u_('\u0036'),
    u_('\u0037'), u_('\u0038'), u_('\u0039'), u_('\u003a'), u_('\u003b'),
    u_('\u003c'), u_('\u003d'), u_('\u003e'), u_('\u003f'), u_('\u0040'),
    u_('\u0041'), u_('\u0042'), u_('\u0043'), u_('\u0044'), u_('\u0045'),
    u_('\u0046'), u_('\u0047'), u_('\u0048'), u_('\u0049'), u_('\u004a'),
    u_('\u004b'), u_('\u004c'), u_('\u004d'), u_('\u004e'), u_('\u004f'),
    u_('\u0050'), u_('\u0051'), u_('\u0052'), u_('\u0053'), u_('\u0054'),
    u_('\u0055'), u_('\u0056'), u_('\u0057'), u_('\u0058'), u_('\u0059'),
    u_('\u005a'), u_('\u005b'), u_('\u005c'), u_('\u005d'), u_('\u005e'),
    u_('\u005f'), u_('\u0060'), u_('\u0061'), u_('\u0062'), u_('\u0063'),
    u_('\u0064'), u_('\u0065'), u_('\u0066'), u_('\u0067'), u_('\u0068'),
    u_('\u0069'), u_('\u006a'), u_('\u006b'), u_('\u006c'), u_('\u006d'),
    u_('\u006e'), u_('\u006f'), u_('\u0070'), u_('\u0071'), u_('\u0072'),
    u_('\u0073'), u_('\u0074'), u_('\u0075'), u_('\u0076'), u_('\u0077'),
    u_('\u0078'), u_('\u0079'), u_('\u007a'), u_('\u007b'), u_('\u007c'),
    u_('\u007d'), u_('\u007e'), u_('\u0000'), u_('\u2022'), u_('\u2020'),
    u_('\u2021'), u_('\u2026'), u_('\u2014'), u_('\u2013'), u_('\u0192'),
    u_('\u2044'), u_('\u2039'), u_('\u203a'), u_('\u2212'), u_('\u2030'),
    u_('\u201e'), u_('\u201c'), u_('\u201d'), u_('\u2018'), u_('\u2019'),
    u_('\u201a'), u_('\u2122'), u_('\ufb01'), u_('\ufb02'), u_('\u0141'),
    u_('\u0152'), u_('\u0160'), u_('\u0178'), u_('\u017d'), u_('\u0131'),
    u_('\u0142'), u_('\u0153'), u_('\u0161'), u_('\u017e'), u_('\u0000'),
    u_('\u20ac'), u_('\u00a1'), u_('\u00a2'), u_('\u00a3'), u_('\u00a4'),
    u_('\u00a5'), u_('\u00a6'), u_('\u00a7'), u_('\u00a8'), u_('\u00a9'),
    u_('\u00aa'), u_('\u00ab'), u_('\u00ac'), u_('\u0000'), u_('\u00ae'),
    u_('\u00af'), u_('\u00b0'), u_('\u00b1'), u_('\u00b2'), u_('\u00b3'),
    u_('\u00b4'), u_('\u00b5'), u_('\u00b6'), u_('\u00b7'), u_('\u00b8'),
    u_('\u00b9'), u_('\u00ba'), u_('\u00bb'), u_('\u00bc'), u_('\u00bd'),
    u_('\u00be'), u_('\u00bf'), u_('\u00c0'), u_('\u00c1'), u_('\u00c2'),
    u_('\u00c3'), u_('\u00c4'), u_('\u00c5'), u_('\u00c6'), u_('\u00c7'),
    u_('\u00c8'), u_('\u00c9'), u_('\u00ca'), u_('\u00cb'), u_('\u00cc'),
    u_('\u00cd'), u_('\u00ce'), u_('\u00cf'), u_('\u00d0'), u_('\u00d1'),
    u_('\u00d2'), u_('\u00d3'), u_('\u00d4'), u_('\u00d5'), u_('\u00d6'),
    u_('\u00d7'), u_('\u00d8'), u_('\u00d9'), u_('\u00da'), u_('\u00db'),
    u_('\u00dc'), u_('\u00dd'), u_('\u00de'), u_('\u00df'), u_('\u00e0'),
    u_('\u00e1'), u_('\u00e2'), u_('\u00e3'), u_('\u00e4'), u_('\u00e5'),
    u_('\u00e6'), u_('\u00e7'), u_('\u00e8'), u_('\u00e9'), u_('\u00ea'),
    u_('\u00eb'), u_('\u00ec'), u_('\u00ed'), u_('\u00ee'), u_('\u00ef'),
    u_('\u00f0'), u_('\u00f1'), u_('\u00f2'), u_('\u00f3'), u_('\u00f4'),
    u_('\u00f5'), u_('\u00f6'), u_('\u00f7'), u_('\u00f8'), u_('\u00f9'),
    u_('\u00fa'), u_('\u00fb'), u_('\u00fc'), u_('\u00fd'), u_('\u00fe'),
    u_('\u00ff')
)

assert len(_pdfDocEncoding) == 256

_pdfDocEncoding_rev = {}

for i in range(256):
    char = _pdfDocEncoding[i]

    if char == u_("\u0000"):
        continue

    assert char not in _pdfDocEncoding_rev

    _pdfDocEncoding_rev[char] = i
