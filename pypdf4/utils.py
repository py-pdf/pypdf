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
Utility functions for PDF library.
"""
import sys

from binascii import hexlify

try:
    import __builtin__ as builtins
except ImportError:  # Py3
    import builtins

__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"


xrange_fn = getattr(builtins, "xrange", range)
_basestring = getattr(builtins, "basestring", str)

bytes_type = type(bytes())  # Works the same in Python 2.X and 3.X
string_type = getattr(builtins, "unicode", str)
int_types = (int, long) if sys.version_info[0] < 3 else (int,)


# Make basic type tests more consistent
def isString(s):
    """Test if arg is a string. Compatible with Python 2 and 3."""
    return isinstance(s, _basestring)


def isInt(n):
    """Test if arg is an int. Compatible with Python 2 and 3."""
    return isinstance(n, int_types)


def isBytes(b):
    """Test if arg is a bytes instance. Compatible with Python 2 and 3."""
    return isinstance(b, bytes_type)


#custom implementation of warnings.formatwarning
def formatWarning(message, category, filename, lineno, line=None):
    file = filename.replace("/", "\\").rsplit("\\", 1)[1]  # find the file name
    return "%s: %s [%s:%s]\n" % (category.__name__, message, file, lineno)


def readUntilWhitespace(stream, maxchars=None):
    """
    Reads non-whitespace characters and returns them.
    Stops upon encountering whitespace or when maxchars is reached.
    """
    txt = pypdfBytes("")

    while True:
        tok = stream.read(1)

        if tok.isspace() or not tok:
            break

        txt += tok
        if len(txt) == maxchars:
            break

    return txt


def readNonWhitespace(stream):
    """
    Finds and reads the next non-whitespace character (ignores whitespace).
    """
    tok = WHITESPACES[0]

    while tok in WHITESPACES:
        tok = stream.read(1)

    return tok


def skipOverWhitespace(stream):
    """
    Similar to readNonWhitespace, but returns a Boolean if more than
    one whitespace character was read.
    """
    tok = WHITESPACES[0]
    cnt = 0

    while tok in WHITESPACES:
        tok = stream.read(1)
        cnt+=1

    return cnt > 1


def skipOverComment(stream):
    tok = stream.read(1)
    stream.seek(-1, 1)

    if tok == pypdfBytes('%'):
        while tok not in (pypdfBytes('\n'), pypdfBytes('\r')):
            tok = stream.read(1)


def readUntilRegex(stream, regex, ignore_eof=False):
    """
    Reads until the regular expression pattern matched (ignore the match)
    Raise PdfStreamError on premature end-of-file.
    :param bool ignore_eof: If true, ignore end-of-line and return immediately
    """
    name = pypdfBytes('')

    while True:
        tok = stream.read(16)

        if not tok:
            # stream has truncated prematurely
            if ignore_eof == True:
                return name
            else:
                raise PdfStreamError("Stream has ended unexpectedly")
        m = regex.search(tok)
        if m is not None:
            name += tok[:m.start()]
            stream.seek(m.start()-len(tok), 1)
            break
        name += tok

    return name


class ConvertFunctionsToVirtualList(object):
    def __init__(self, lengthFunction, getFunction):
        self.lengthFunction = lengthFunction
        self.getFunction = getFunction

    def __len__(self):
        return self.lengthFunction()

    def __getitem__(self, index):
        if isinstance(index, slice):
            indices = xrange_fn(*index.indices(len(self)))
            cls = type(self)
            return cls(indices.__len__, lambda idx: self[indices[idx]])
        if not isInt(index):
            raise TypeError("sequence indices must be integers")

        len_self = len(self)

        if index < 0:
            # support negative indexes
            index = len_self + index
        if index < 0 or index >= len_self:
            raise IndexError("sequence index out of range")

        return self.getFunction(index)


def RC4Encrypt(key, plaintext):
    S = [i for i in range(256)]
    j = 0

    for i in range(256):
        j = (j + S[i] + pypdfOrd(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    i, j = 0, 0
    retval = []

    for x in range(len(plaintext)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = S[(S[i] + S[j]) % 256]
        retval.append(pypdfBytes(chr(pypdfOrd(plaintext[x]) ^ t)))

    return pypdfBytes("").join(retval)


def matrixMultiply(a, b):
    return [[sum([float(i) * float(j)
                  for i, j in zip(row, col)]
                ) for col in zip(*b)]
            for row in a]


def markLocation(stream):
    """Creates text file showing current location in context."""
    # Mainly for debugging
    RADIUS = 5000
    stream.seek(-RADIUS, 1)
    outputDoc = open('PyPDF4_pdfLocation.txt', 'w')
    outputDoc.write(stream.read(RADIUS))
    outputDoc.write('HERE')
    outputDoc.write(stream.read(RADIUS))
    outputDoc.close()
    stream.seek(-RADIUS, 1)


class PyPdfError(Exception):
    pass


class PdfReadError(PyPdfError):
    pass


class PageSizeNotDefinedError(PyPdfError):
    pass


class PdfReadWarning(UserWarning):
    pass


class PdfStreamError(PdfReadError):
    pass


if sys.version_info[0] < 3:
    pypdfBytes = lambda s: s
else:
    def pypdfBytes(s):
        if isinstance(s, bytes):  # In Python 2, bytes is str
            return s
        else:
            return s.encode('LATIN-1')

pypdfBytes.__doc__ = """
Abstracts the conversion from ``str`` to ``bytes`` over versions 2.7.x and
3 of Python.
"""


def pypdfUnicode(s):
    """
    Encodes a string ``s`` according to the Unicode character set (default for
    Python 3).
    :param s: a ``str`` instance.
    :rtype: ``unicode`` for Python 2, ``str`` for Python 3.
    """
    if sys.version_info[0] < 3:
        return unicode(s, 'unicode_escape')
    else:
        return s


def pypdfStr(b):
    """
    Abstracts the conversion from bytes to string over versions 2.7.x and
    3 of Python.
    """
    if sys.version_info[0] < 3:
        return b
    else:
        if isinstance(b, bytes):
            return b.decode("LATIN1")
        else:
            return b


def pypdfOrd(b):
    """
    Abstracts the conversion from a single-character string to the
    corresponding integer value over versions 2.7.x and 3 of Python.
    """
    # In case of bugs, try to look here! Should the condition be brought like
    # it used to be in the comment below?
    # if sys.version_info[0] < 3 or type(b) == str:
    # (``str is bytes == True`` in Python 2)
    if isinstance(b, str):
        return ord(b)
    elif sys.version_info < (3, 0) and isinstance(b, unicode):
        return ord(b)
    # TO-DO The code below should be changed (b could be ANYTHING!) but I have
    # no idea of what (and how much) previous code could be depending on this
    # behavior
    else:
        return b


def pypdfChr(c):
    """
    Abstracts the conversion from a single byte to the corresponding ASCII
    character over versions 2.7.x and 3 of Python.
    """
    if sys.version_info[0] < 3:
        return c
    else:
        return chr(c)


def pypdfBytearray(b):
    """
    Abstracts the conversion from a ``bytes`` variable to a ``bytearray`` value
    over versions 2.7.x and 3 of Python.
    """
    if sys.version_info[0] < 3:
        return b
    else:
        return bytearray(b)


def hexEncode(s):
    """
    Abstracts the conversion from a LATIN 1 string to an hex-valued string
    representation of the former over versions 2.7.x and 3 of Python.

    :param str s: a ``str`` to convert from LATIN 1 to an hexadecimal string
        representation.
    :return: a hex-valued string, e.g. ``hexEncode("$A'") == "244127"``.
    :rtype: str
    """
    if sys.version_info < (3, 0):
        return s.encode('hex')
    else:
        if isinstance(s, str):
            s = s.encode("LATIN1")

        # The output is in the set of "0123456789ABCDEF" characters. Using the
        # ASCII decoder is a safeguard against anomalies, albeit unlikely
        return hexlify(s).decode("ASCII")


def hexStr(num):
    return hex(num).replace('L', '')


WHITESPACES = [pypdfBytes(x) for x in [' ', '\n', '\r', '\t', '\x00']]


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
