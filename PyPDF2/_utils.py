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
Utility functions for the internal use of PyPDF2.

Functions in this module might change their signature or get removed at
any time. They are NOT stable API.
"""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"


import sys
import warnings

# See https://github.com/py-pdf/PyPDF2/issues/779
from PyPDF2.errors import (  # noqa
    STREAM_TRUNCATED_PREMATURELY,
    PageSizeNotDefinedError,
    PdfReadError,
    PdfReadWarning,
    PdfStreamError,
    PyPdfError,
)

try:
    import builtins
    from typing import Dict
except ImportError:  # Py2.7
    import __builtin__ as builtins  # type: ignore


xrange_fn = getattr(builtins, "xrange", range)
_basestring = getattr(builtins, "basestring", str)

bytes_type = type(bytes())  # Works the same in Python 2.X and 3.X
string_type = getattr(builtins, "unicode", str)
int_types = (int, long) if sys.version_info[0] < 3 else (int,)  # type: ignore  # noqa

DEPR_MSG_NO_REPLACEMENT = "{} is deprecated and will be removed in PyPDF2 2.0.0."
DEPR_MSG = "{} is deprecated and will be removed in PyPDF2 2.0.0. Use {} instead."


def _isString(s):
    return isinstance(s, _basestring)


# Make basic type tests more consistent
def isString(s):
    """Test if arg is a string. Compatible with Python 2 and 3."""
    warnings.warn(DEPR_MSG_NO_REPLACEMENT.format("isString"))
    return _isString(s)


def _isInt(n):
    return isinstance(n, int_types)


def isInt(n):
    """Test if arg is an int. Compatible with Python 2 and 3."""
    warnings.warn(DEPR_MSG_NO_REPLACEMENT.format("isInt"))
    return _isInt(n)


def _isBytes(b):
    return isinstance(b, bytes_type)


def isBytes(b):
    """Test if arg is a bytes instance. Compatible with Python 2 and 3."""
    warnings.warn(DEPR_MSG_NO_REPLACEMENT.format("isBytes"))
    return _isBytes(b)


def formatWarning(message, category, filename, lineno, line=None):
    """custom implementation of warnings.formatwarning"""
    file = filename.replace("/", "\\").rsplit("\\", 1)[-1]  # find the file name
    return "%s: %s [%s:%s]\n" % (category.__name__, message, file, lineno)


def readUntilWhitespace(stream, maxchars=None):
    """
    Reads non-whitespace characters and returns them.
    Stops upon encountering whitespace or when maxchars is reached.
    """
    txt = b_("")
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
        cnt += 1
    return cnt > 1


def skipOverComment(stream):
    tok = stream.read(1)
    stream.seek(-1, 1)
    if tok == b_("%"):
        while tok not in (b_("\n"), b_("\r")):
            tok = stream.read(1)


def readUntilRegex(stream, regex, ignore_eof=False):
    """
    Reads until the regular expression pattern matched (ignore the match)
    :raises PdfStreamError: on premature end-of-file
    :param bool ignore_eof: If true, ignore end-of-line and return immediately
    """
    name = b_("")
    while True:
        tok = stream.read(16)
        if not tok:
            # stream has truncated prematurely
            if ignore_eof:
                return name
            else:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
        m = regex.search(tok)
        if m is not None:
            name += tok[: m.start()]
            stream.seek(m.start() - len(tok), 1)
            break
        name += tok
    return name


class _VirtualList(object):
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
        if not _isInt(index):
            raise TypeError("sequence indices must be integers")
        len_self = len(self)
        if index < 0:
            # support negative indexes
            index = len_self + index
        if index < 0 or index >= len_self:
            raise IndexError("sequence index out of range")
        return self.getFunction(index)


class ConvertFunctionsToVirtualList(_VirtualList):
    def __init__(self, lengthFunction, getFunction):
        warnings.warn(
            "ConvertFunctionsToVirtualList will be removed with PyPDF2 2.0.0",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        warnings.warn(DEPR_MSG_NO_REPLACEMENT.format("ConvertFunctionsToVirtualList"))
        super(ConvertFunctionsToVirtualList, self).__init__(lengthFunction, getFunction)


def matrix_multiply(a, b):
    return [
        [sum([float(i) * float(j) for i, j in zip(row, col)]) for col in zip(*b)]
        for row in a
    ]


def matrixMultiply(a, b):
    warnings.warn(
        DEPR_MSG.format("matrixMultiply", "matrix_multiply"), PendingDeprecationWarning
    )
    return matrix_multiply(a, b)


def markLocation(stream):
    """Creates text file showing current location in context."""
    # Mainly for debugging
    radius = 5000
    stream.seek(-radius, 1)
    with open("PyPDF2_pdfLocation.txt", "wb") as output_fh:
        output_fh.write(stream.read(radius))
        output_fh.write(b"HERE")
        output_fh.write(stream.read(radius))
    stream.seek(-radius, 1)


if sys.version_info[0] < 3:
    warnings.warn(
        "Python 3.5 and older support will be dropped with PyPDF2 2.0.0",
        PendingDeprecationWarning,
    )

    def b_(s):
        return s

else:
    B_CACHE = {}  # type: Dict[str, bytes]

    def b_(s):
        bc = B_CACHE
        if s in bc:
            return bc[s]
        if type(s) == bytes:
            return s
        else:
            try:
                r = s.encode("latin-1")
                if len(s) < 2:
                    bc[s] = r
                return r
            except Exception:
                r = s.encode("utf-8")
                if len(s) < 2:
                    bc[s] = r
                return r


def u_(s):
    if sys.version_info[0] < 3:
        return unicode(s, "unicode_escape")  # noqa
    else:
        return s


def str_(b):
    if sys.version_info[0] < 3:
        return b
    else:
        if type(b) == bytes:
            return b.decode("latin-1")
        else:
            return b


def ord_(b):
    if sys.version_info[0] < 3 or type(b) == str:
        return ord(b)
    else:
        return b


def chr_(c):
    if sys.version_info[0] < 3:
        return c
    else:
        return chr(c)


def barray(b):
    if sys.version_info[0] < 3:
        return b
    else:
        return bytearray(b)


def hexencode(b):
    if sys.version_info[0] < 3:
        return b.encode("hex")
    else:
        import codecs

        coder = codecs.getencoder("hex_codec")
        return coder(b)[0]


def hexStr(num):
    return hex(num).replace("L", "")


WHITESPACES = [b_(x) for x in [" ", "\n", "\r", "\t", "\x00"]]


def paeth_predictor(left, up, up_left):
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


def paethPredictor(left, up, up_left):
    warnings.warn(
        DEPR_MSG.format("paethPredictor", "paeth_predictor"), PendingDeprecationWarning
    )
    return paeth_predictor(left, up, up_left)
