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
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

from codecs import getencoder
from io import BufferedReader, BufferedWriter, BytesIO, FileIO
from typing import Any, Dict, List, Optional, Union, overload

from .errors import STREAM_TRUNCATED_PREMATURELY, PdfStreamError

bytes_type = type(bytes())  # Works the same in Python 2.X and 3.X
StreamType = Union[BytesIO, BufferedReader, BufferedWriter, FileIO]
StrByteType = Union[str, StreamType]


def readUntilWhitespace(stream: StreamType, maxchars: Optional[int] = None) -> bytes:
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


def readNonWhitespace(stream: StreamType) -> bytes:
    """
    Finds and reads the next non-whitespace character (ignores whitespace).
    """
    tok = WHITESPACES[0]
    while tok in WHITESPACES:
        tok = stream.read(1)
    return tok


def skipOverWhitespace(stream: StreamType) -> bool:
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


def skipOverComment(stream: StreamType) -> None:
    tok = stream.read(1)
    stream.seek(-1, 1)
    if tok == b_("%"):
        while tok not in (b_("\n"), b_("\r")):
            tok = stream.read(1)


def readUntilRegex(stream: StreamType, regex: Any, ignore_eof: bool = False) -> bytes:
    """
    Reads until the regular expression pattern matched (ignore the match)
    :raises PdfStreamError: on premature end-of-file
    :param bool ignore_eof: If true, ignore end-of-line and return immediately
    :param regex: re.Pattern
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


def RC4_encrypt(key: Union[str, bytes], plaintext: bytes) -> bytes:
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + ord_(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]
    i, j = 0, 0
    retval = []
    for x in range(len(plaintext)):
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        t = S[(S[i] + S[j]) % 256]
        retval.append(b_(chr(ord_(plaintext[x]) ^ t)))
    return b_("").join(retval)


def matrixMultiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    return [
        [sum(float(i) * float(j) for i, j in zip(row, col)) for col in zip(*b)]
        for row in a
    ]


def markLocation(stream: StreamType) -> None:
    """Creates text file showing current location in context."""
    # Mainly for debugging
    radius = 5000
    stream.seek(-radius, 1)
    with open("PyPDF2_pdfLocation.txt", "wb") as output_fh:
        output_fh.write(stream.read(radius))
        output_fh.write(b"HERE")
        output_fh.write(stream.read(radius))
    stream.seek(-radius, 1)


B_CACHE: Dict[Union[str, bytes], bytes] = {}


def b_(s: Union[str, bytes]) -> bytes:
    bc = B_CACHE
    if s in bc:
        return bc[s]
    if isinstance(s, bytes):
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


@overload
def str_(b: str) -> str:
    ...


@overload
def str_(b: bytes) -> str:
    ...


def str_(b: Union[str, bytes]) -> str:
    if isinstance(b, bytes):
        return b.decode("latin-1")
    else:
        return b


@overload
def ord_(b: str) -> int:
    ...


@overload
def ord_(b: bytes) -> bytes:
    ...


@overload
def ord_(b: int) -> int:
    ...


def ord_(b: Union[int, str, bytes]) -> Union[int, bytes]:
    if isinstance(b, str):
        return ord(b)
    else:
        return b


def hexencode(b: bytes) -> bytes:

    coder = getencoder("hex_codec")
    coded = coder(b)  # type: ignore
    return coded[0]


def hexStr(num: int) -> str:
    return hex(num).replace("L", "")


WHITESPACES = [b_(x) for x in [" ", "\n", "\r", "\t", "\x00"]]


def paethPredictor(left: int, up: int, up_left: int) -> int:
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
