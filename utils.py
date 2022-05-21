# Original Copyright 2006, Mathieu Fenniak
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


import sys

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


# Make basic type tests more consistent
def isString(s):
    """Test if arg is a string. Compatible with Python 2 and 3."""
    return isinstance(s, _basestring)


def isInt(n):
    """Test if arg is an int. Compatible with Python 2 and 3."""
    return isinstance(n, int_types)


def isBytes(b):
    """Test if arg is a bytes instance. Compatible with Python 2 and 3."""
    import warnings
    warnings.warn("PyPDF2.utils.isBytes will be deprecated", DeprecationWarning)
    return isinstance(b, bytes_type)


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


def RC4_encrypt(key, plaintext):
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


def matrixMultiply(a, b):
    return [
        [sum([float(i) * float(j) for i, j in zip(row, col)]) for col in zip(*b)]
        for row in a
    ]


def markLocation(stream):
    """Creates text file showing current location in context."""
    # Mainly for debugging
    RADIUS = 5000
    stream.seek(-RADIUS, 1)
    with open("PyPDF2_pdfLocation.txt", "wb") as output_fh:
        output_fh.write(stream.read(RADIUS))
        output_fh.write(b"HERE")
        output_fh.write(stream.read(RADIUS))
    stream.seek(-RADIUS, 1)


if sys.version_info[0] < 3:
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


def glyph2unicode(obj):
    glyph2uni = dict()
    glyph2uni["/A"] = "\u0041"
    glyph2uni["/AE"] = "\u00C6"
    glyph2uni["/AEacute"] = "\u01FC"
    glyph2uni["/Aacute"] = "\u00C1"
    glyph2uni["/Abreve"] = "\u0102"
    glyph2uni["/Acircumflex"] = "\u00C2"
    glyph2uni["/Adieresis"] = "\u00C4"
    glyph2uni["/Agrave"] = "\u00C0"
    glyph2uni["/Alpha"] = "\u0391"
    glyph2uni["/Alphatonos"] = "\u0386"
    glyph2uni["/Amacron"] = "\u0100"
    glyph2uni["/Aogonek"] = "\u0104"
    glyph2uni["/Aring"] = "\u00C5"
    glyph2uni["/Aringacute"] = "\u01FA"
    glyph2uni["/Atilde"] = "\u00C3"
    glyph2uni["/B"] = "\u0042"
    glyph2uni["/Beta"] = "\u0392"
    glyph2uni["/C"] = "\u0043"
    glyph2uni["/Cacute"] = "\u0106"
    glyph2uni["/Ccaron"] = "\u010C"
    glyph2uni["/Ccedilla"] = "\u00C7"
    glyph2uni["/Ccircumflex"] = "\u0108"
    glyph2uni["/Cdotaccent"] = "\u010A"
    glyph2uni["/Chi"] = "\u03A7"
    glyph2uni["/D"] = "\u0044"
    glyph2uni["/Dcaron"] = "\u010E"
    glyph2uni["/Dcroat"] = "\u0110"
    glyph2uni["/Delta"] = "\u2206"
    glyph2uni["/E"] = "\u0045"
    glyph2uni["/Eacute"] = "\u00C9"
    glyph2uni["/Ebreve"] = "\u0114"
    glyph2uni["/Ecaron"] = "\u011A"
    glyph2uni["/Ecircumflex"] = "\u00CA"
    glyph2uni["/Edieresis"] = "\u00CB"
    glyph2uni["/Edotaccent"] = "\u0116"
    glyph2uni["/Egrave"] = "\u00C8"
    glyph2uni["/Emacron"] = "\u0112"
    glyph2uni["/Eng"] = "\u014A"
    glyph2uni["/Eogonek"] = "\u0118"
    glyph2uni["/Epsilon"] = "\u0395"
    glyph2uni["/Epsilontonos"] = "\u0388"
    glyph2uni["/Eta"] = "\u0397"
    glyph2uni["/Etatonos"] = "\u0389"
    glyph2uni["/Eth"] = "\u00D0"
    glyph2uni["/Euro"] = "\u20AC"
    glyph2uni["/F"] = "\u0046"
    glyph2uni["/G"] = "\u0047"
    glyph2uni["/Gamma"] = "\u0393"
    glyph2uni["/Gbreve"] = "\u011E"
    glyph2uni["/Gcaron"] = "\u01E6"
    glyph2uni["/Gcircumflex"] = "\u011C"
    glyph2uni["/Gdotaccent"] = "\u0120"
    glyph2uni["/H"] = "\u0048"
    glyph2uni["/H18533"] = "\u25CF"
    glyph2uni["/H18543"] = "\u25AA"
    glyph2uni["/H18551"] = "\u25AB"
    glyph2uni["/H22073"] = "\u25A1"
    glyph2uni["/Hbar"] = "\u0126"
    glyph2uni["/Hcircumflex"] = "\u0124"
    glyph2uni["/I"] = "\u0049"
    glyph2uni["/IJ"] = "\u0132"
    glyph2uni["/Iacute"] = "\u00CD"
    glyph2uni["/Ibreve"] = "\u012C"
    glyph2uni["/Icircumflex"] = "\u00CE"
    glyph2uni["/Idieresis"] = "\u00CF"
    glyph2uni["/Idotaccent"] = "\u0130"
    glyph2uni["/Ifraktur"] = "\u2111"
    glyph2uni["/Igrave"] = "\u00CC"
    glyph2uni["/Imacron"] = "\u012A"
    glyph2uni["/Iogonek"] = "\u012E"
    glyph2uni["/Iota"] = "\u0399"
    glyph2uni["/Iotadieresis"] = "\u03AA"
    glyph2uni["/Iotatonos"] = "\u038A"
    glyph2uni["/Itilde"] = "\u0128"
    glyph2uni["/J"] = "\u004A"
    glyph2uni["/Jcircumflex"] = "\u0134"
    glyph2uni["/K"] = "\u004B"
    glyph2uni["/Kappa"] = "\u039A"
    glyph2uni["/L"] = "\u004C"
    glyph2uni["/Lacute"] = "\u0139"
    glyph2uni["/Lambda"] = "\u039B"
    glyph2uni["/Lcaron"] = "\u013D"
    glyph2uni["/Ldot"] = "\u013F"
    glyph2uni["/Lslash"] = "\u0141"
    glyph2uni["/M"] = "\u004D"
    glyph2uni["/Mu"] = "\u039C"
    glyph2uni["/N"] = "\u004E"
    glyph2uni["/Nacute"] = "\u0143"
    glyph2uni["/Ncaron"] = "\u0147"
    glyph2uni["/Ntilde"] = "\u00D1"
    glyph2uni["/Nu"] = "\u039D"
    glyph2uni["/O"] = "\u004F"
    glyph2uni["/OE"] = "\u0152"
    glyph2uni["/Oacute"] = "\u00D3"
    glyph2uni["/Obreve"] = "\u014E"
    glyph2uni["/Ocircumflex"] = "\u00D4"
    glyph2uni["/Odieresis"] = "\u00D6"
    glyph2uni["/Ograve"] = "\u00D2"
    glyph2uni["/Ohorn"] = "\u01A0"
    glyph2uni["/Ohungarumlaut"] = "\u0150"
    glyph2uni["/Omacron"] = "\u014C"
    glyph2uni["/Omega"] = "\u2126"
    glyph2uni["/Omegatonos"] = "\u038F"
    glyph2uni["/Omicron"] = "\u039F"
    glyph2uni["/Omicrontonos"] = "\u038C"
    glyph2uni["/Oslash"] = "\u00D8"
    glyph2uni["/Oslashacute"] = "\u01FE"
    glyph2uni["/Otilde"] = "\u00D5"
    glyph2uni["/P"] = "\u0050"
    glyph2uni["/Phi"] = "\u03A6"
    glyph2uni["/Pi"] = "\u03A0"
    glyph2uni["/Psi"] = "\u03A8"
    glyph2uni["/Q"] = "\u0051"
    glyph2uni["/R"] = "\u0052"
    glyph2uni["/Racute"] = "\u0154"
    glyph2uni["/Rcaron"] = "\u0158"
    glyph2uni["/Rfraktur"] = "\u211C"
    glyph2uni["/Rho"] = "\u03A1"
    glyph2uni["/S"] = "\u0053"
    glyph2uni["/SF010000"] = "\u250C"
    glyph2uni["/SF020000"] = "\u2514"
    glyph2uni["/SF030000"] = "\u2510"
    glyph2uni["/SF040000"] = "\u2518"
    glyph2uni["/SF050000"] = "\u253C"
    glyph2uni["/SF060000"] = "\u252C"
    glyph2uni["/SF070000"] = "\u2534"
    glyph2uni["/SF080000"] = "\u251C"
    glyph2uni["/SF090000"] = "\u2524"
    glyph2uni["/SF100000"] = "\u2500"
    glyph2uni["/SF110000"] = "\u2502"
    glyph2uni["/SF190000"] = "\u2561"
    glyph2uni["/SF200000"] = "\u2562"
    glyph2uni["/SF210000"] = "\u2556"
    glyph2uni["/SF220000"] = "\u2555"
    glyph2uni["/SF230000"] = "\u2563"
    glyph2uni["/SF240000"] = "\u2551"
    glyph2uni["/SF250000"] = "\u2557"
    glyph2uni["/SF260000"] = "\u255D"
    glyph2uni["/SF270000"] = "\u255C"
    glyph2uni["/SF280000"] = "\u255B"
    glyph2uni["/SF360000"] = "\u255E"
    glyph2uni["/SF370000"] = "\u255F"
    glyph2uni["/SF380000"] = "\u255A"
    glyph2uni["/SF390000"] = "\u2554"
    glyph2uni["/SF400000"] = "\u2569"
    glyph2uni["/SF410000"] = "\u2566"
    glyph2uni["/SF420000"] = "\u2560"
    glyph2uni["/SF430000"] = "\u2550"
    glyph2uni["/SF440000"] = "\u256C"
    glyph2uni["/SF450000"] = "\u2567"
    glyph2uni["/SF460000"] = "\u2568"
    glyph2uni["/SF470000"] = "\u2564"
    glyph2uni["/SF480000"] = "\u2565"
    glyph2uni["/SF490000"] = "\u2559"
    glyph2uni["/SF500000"] = "\u2558"
    glyph2uni["/SF510000"] = "\u2552"
    glyph2uni["/SF520000"] = "\u2553"
    glyph2uni["/SF530000"] = "\u256B"
    glyph2uni["/SF540000"] = "\u256A"
    glyph2uni["/Sacute"] = "\u015A"
    glyph2uni["/Scaron"] = "\u0160"
    glyph2uni["/Scedilla"] = "\u015E"
    glyph2uni["/Scircumflex"] = "\u015C"
    glyph2uni["/Sigma"] = "\u03A3"
    glyph2uni["/T"] = "\u0054"
    glyph2uni["/Tau"] = "\u03A4"
    glyph2uni["/Tbar"] = "\u0166"
    glyph2uni["/Tcaron"] = "\u0164"
    glyph2uni["/Theta"] = "\u0398"
    glyph2uni["/Thorn"] = "\u00DE"
    glyph2uni["/U"] = "\u0055"
    glyph2uni["/Uacute"] = "\u00DA"
    glyph2uni["/Ubreve"] = "\u016C"
    glyph2uni["/Ucircumflex"] = "\u00DB"
    glyph2uni["/Udieresis"] = "\u00DC"
    glyph2uni["/Ugrave"] = "\u00D9"
    glyph2uni["/Uhorn"] = "\u01AF"
    glyph2uni["/Uhungarumlaut"] = "\u0170"
    glyph2uni["/Umacron"] = "\u016A"
    glyph2uni["/Uogonek"] = "\u0172"
    glyph2uni["/Upsilon"] = "\u03A5"
    glyph2uni["/Upsilon1"] = "\u03D2"
    glyph2uni["/Upsilondieresis"] = "\u03AB"
    glyph2uni["/Upsilontonos"] = "\u038E"
    glyph2uni["/Uring"] = "\u016E"
    glyph2uni["/Utilde"] = "\u0168"
    glyph2uni["/V"] = "\u0056"
    glyph2uni["/W"] = "\u0057"
    glyph2uni["/Wacute"] = "\u1E82"
    glyph2uni["/Wcircumflex"] = "\u0174"
    glyph2uni["/Wdieresis"] = "\u1E84"
    glyph2uni["/Wgrave"] = "\u1E80"
    glyph2uni["/X"] = "\u0058"
    glyph2uni["/Xi"] = "\u039E"
    glyph2uni["/Y"] = "\u0059"
    glyph2uni["/Yacute"] = "\u00DD"
    glyph2uni["/Ycircumflex"] = "\u0176"
    glyph2uni["/Ydieresis"] = "\u0178"
    glyph2uni["/Ygrave"] = "\u1EF2"
    glyph2uni["/Z"] = "\u005A"
    glyph2uni["/Zacute"] = "\u0179"
    glyph2uni["/Zcaron"] = "\u017D"
    glyph2uni["/Zdotaccent"] = "\u017B"
    glyph2uni["/Zeta"] = "\u0396"
    glyph2uni["/a"] = "\u0061"
    glyph2uni["/aacute"] = "\u00E1"
    glyph2uni["/abreve"] = "\u0103"
    glyph2uni["/acircumflex"] = "\u00E2"
    glyph2uni["/acute"] = "\u00B4"
    glyph2uni["/acutecomb"] = "\u0301"
    glyph2uni["/adieresis"] = "\u00E4"
    glyph2uni["/ae"] = "\u00E6"
    glyph2uni["/aeacute"] = "\u01FD"
    glyph2uni["/agrave"] = "\u00E0"
    glyph2uni["/aleph"] = "\u2135"
    glyph2uni["/alpha"] = "\u03B1"
    glyph2uni["/alphatonos"] = "\u03AC"
    glyph2uni["/amacron"] = "\u0101"
    glyph2uni["/ampersand"] = "\u0026"
    glyph2uni["/angle"] = "\u2220"
    glyph2uni["/angleleft"] = "\u2329"
    glyph2uni["/angleright"] = "\u232A"
    glyph2uni["/anoteleia"] = "\u0387"
    glyph2uni["/aogonek"] = "\u0105"
    glyph2uni["/approxequal"] = "\u2248"
    glyph2uni["/aring"] = "\u00E5"
    glyph2uni["/aringacute"] = "\u01FB"
    glyph2uni["/arrowboth"] = "\u2194"
    glyph2uni["/arrowdblboth"] = "\u21D4"
    glyph2uni["/arrowdbldown"] = "\u21D3"
    glyph2uni["/arrowdblleft"] = "\u21D0"
    glyph2uni["/arrowdblright"] = "\u21D2"
    glyph2uni["/arrowdblup"] = "\u21D1"
    glyph2uni["/arrowdown"] = "\u2193"
    glyph2uni["/arrowleft"] = "\u2190"
    glyph2uni["/arrowright"] = "\u2192"
    glyph2uni["/arrowup"] = "\u2191"
    glyph2uni["/arrowupdn"] = "\u2195"
    glyph2uni["/arrowupdnbse"] = "\u21A8"
    glyph2uni["/asciicircum"] = "\u005E"
    glyph2uni["/asciitilde"] = "\u007E"
    glyph2uni["/asterisk"] = "\u002A"
    glyph2uni["/asteriskmath"] = "\u2217"
    glyph2uni["/at"] = "\u0040"
    glyph2uni["/atilde"] = "\u00E3"
    glyph2uni["/b"] = "\u0062"
    glyph2uni["/backslash"] = "\u005C"
    glyph2uni["/bar"] = "\u007C"
    glyph2uni["/beta"] = "\u03B2"
    glyph2uni["/block"] = "\u2588"
    glyph2uni["/braceleft"] = "\u007B"
    glyph2uni["/braceright"] = "\u007D"
    glyph2uni["/bracketleft"] = "\u005B"
    glyph2uni["/bracketright"] = "\u005D"
    glyph2uni["/breve"] = "\u02D8"
    glyph2uni["/brokenbar"] = "\u00A6"
    glyph2uni["/bullet"] = "\u2022"
    glyph2uni["/c"] = "\u0063"
    glyph2uni["/cacute"] = "\u0107"
    glyph2uni["/caron"] = "\u02C7"
    glyph2uni["/carriagereturn"] = "\u21B5"
    glyph2uni["/ccaron"] = "\u010D"
    glyph2uni["/ccedilla"] = "\u00E7"
    glyph2uni["/ccircumflex"] = "\u0109"
    glyph2uni["/cdotaccent"] = "\u010B"
    glyph2uni["/cedilla"] = "\u00B8"
    glyph2uni["/cent"] = "\u00A2"
    glyph2uni["/chi"] = "\u03C7"
    glyph2uni["/circle"] = "\u25CB"
    glyph2uni["/circlemultiply"] = "\u2297"
    glyph2uni["/circleplus"] = "\u2295"
    glyph2uni["/circumflex"] = "\u02C6"
    glyph2uni["/club"] = "\u2663"
    glyph2uni["/colon"] = "\u003A"
    glyph2uni["/colonmonetary"] = "\u20A1"
    glyph2uni["/comma"] = "\u002C"
    glyph2uni["/congruent"] = "\u2245"
    glyph2uni["/copyright"] = "\u00A9"
    glyph2uni["/currency"] = "\u00A4"
    glyph2uni["/d"] = "\u0064"
    glyph2uni["/dagger"] = "\u2020"
    glyph2uni["/daggerdbl"] = "\u2021"
    glyph2uni["/dcaron"] = "\u010F"
    glyph2uni["/dcroat"] = "\u0111"
    glyph2uni["/degree"] = "\u00B0"
    glyph2uni["/delta"] = "\u03B4"
    glyph2uni["/diamond"] = "\u2666"
    glyph2uni["/dieresis"] = "\u00A8"
    glyph2uni["/dieresistonos"] = "\u0385"
    glyph2uni["/divide"] = "\u00F7"
    glyph2uni["/dkshade"] = "\u2593"
    glyph2uni["/dnblock"] = "\u2584"
    glyph2uni["/dollar"] = "\u0024"
    glyph2uni["/dong"] = "\u20AB"
    glyph2uni["/dotaccent"] = "\u02D9"
    glyph2uni["/dotbelowcomb"] = "\u0323"
    glyph2uni["/dotlessi"] = "\u0131"
    glyph2uni["/dotmath"] = "\u22C5"
    glyph2uni["/e"] = "\u0065"
    glyph2uni["/eacute"] = "\u00E9"
    glyph2uni["/ebreve"] = "\u0115"
    glyph2uni["/ecaron"] = "\u011B"
    glyph2uni["/ecircumflex"] = "\u00EA"
    glyph2uni["/edieresis"] = "\u00EB"
    glyph2uni["/edotaccent"] = "\u0117"
    glyph2uni["/egrave"] = "\u00E8"
    glyph2uni["/eight"] = "\u0038"
    glyph2uni["/element"] = "\u2208"
    glyph2uni["/ellipsis"] = "\u2026"
    glyph2uni["/emacron"] = "\u0113"
    glyph2uni["/emdash"] = "\u2014"
    glyph2uni["/emptyset"] = "\u2205"
    glyph2uni["/endash"] = "\u2013"
    glyph2uni["/eng"] = "\u014B"
    glyph2uni["/eogonek"] = "\u0119"
    glyph2uni["/epsilon"] = "\u03B5"
    glyph2uni["/epsilontonos"] = "\u03AD"
    glyph2uni["/equal"] = "\u003D"
    glyph2uni["/equivalence"] = "\u2261"
    glyph2uni["/estimated"] = "\u212E"
    glyph2uni["/eta"] = "\u03B7"
    glyph2uni["/etatonos"] = "\u03AE"
    glyph2uni["/eth"] = "\u00F0"
    glyph2uni["/exclam"] = "\u0021"
    glyph2uni["/exclamdbl"] = "\u203C"
    glyph2uni["/exclamdown"] = "\u00A1"
    glyph2uni["/existential"] = "\u2203"
    glyph2uni["/f"] = "\u0066"
    glyph2uni["/female"] = "\u2640"
    glyph2uni["/figuredash"] = "\u2012"
    glyph2uni["/filledbox"] = "\u25A0"
    glyph2uni["/filledrect"] = "\u25AC"
    glyph2uni["/five"] = "\u0035"
    glyph2uni["/fiveeighths"] = "\u215D"
    glyph2uni["/florin"] = "\u0192"
    glyph2uni["/four"] = "\u0034"
    glyph2uni["/fraction"] = "\u2044"
    glyph2uni["/franc"] = "\u20A3"
    glyph2uni["/g"] = "\u0067"
    glyph2uni["/gamma"] = "\u03B3"
    glyph2uni["/gbreve"] = "\u011F"
    glyph2uni["/gcaron"] = "\u01E7"
    glyph2uni["/gcircumflex"] = "\u011D"
    glyph2uni["/gdotaccent"] = "\u0121"
    glyph2uni["/germandbls"] = "\u00DF"
    glyph2uni["/gradient"] = "\u2207"
    glyph2uni["/grave"] = "\u0060"
    glyph2uni["/gravecomb"] = "\u0300"
    glyph2uni["/greater"] = "\u003E"
    glyph2uni["/greaterequal"] = "\u2265"
    glyph2uni["/guillemotleft"] = "\u00AB"
    glyph2uni["/guillemotright"] = "\u00BB"
    glyph2uni["/guilsinglleft"] = "\u2039"
    glyph2uni["/guilsinglright"] = "\u203A"
    glyph2uni["/h"] = "\u0068"
    glyph2uni["/hbar"] = "\u0127"
    glyph2uni["/hcircumflex"] = "\u0125"
    glyph2uni["/heart"] = "\u2665"
    glyph2uni["/hookabovecomb"] = "\u0309"
    glyph2uni["/house"] = "\u2302"
    glyph2uni["/hungarumlaut"] = "\u02DD"
    glyph2uni["/hyphen"] = "\u002D"
    glyph2uni["/i"] = "\u0069"
    glyph2uni["/iacute"] = "\u00ED"
    glyph2uni["/ibreve"] = "\u012D"
    glyph2uni["/icircumflex"] = "\u00EE"
    glyph2uni["/idieresis"] = "\u00EF"
    glyph2uni["/igrave"] = "\u00EC"
    glyph2uni["/ij"] = "\u0133"
    glyph2uni["/imacron"] = "\u012B"
    glyph2uni["/infinity"] = "\u221E"
    glyph2uni["/integral"] = "\u222B"
    glyph2uni["/integralbt"] = "\u2321"
    glyph2uni["/integraltp"] = "\u2320"
    glyph2uni["/intersection"] = "\u2229"
    glyph2uni["/invbullet"] = "\u25D8"
    glyph2uni["/invcircle"] = "\u25D9"
    glyph2uni["/invsmileface"] = "\u263B"
    glyph2uni["/iogonek"] = "\u012F"
    glyph2uni["/iota"] = "\u03B9"
    glyph2uni["/iotadieresis"] = "\u03CA"
    glyph2uni["/iotadieresistonos"] = "\u0390"
    glyph2uni["/iotatonos"] = "\u03AF"
    glyph2uni["/itilde"] = "\u0129"
    glyph2uni["/j"] = "\u006A"
    glyph2uni["/jcircumflex"] = "\u0135"
    glyph2uni["/k"] = "\u006B"
    glyph2uni["/kappa"] = "\u03BA"
    glyph2uni["/kgreenlandic"] = "\u0138"
    glyph2uni["/l"] = "\u006C"
    glyph2uni["/lacute"] = "\u013A"
    glyph2uni["/lambda"] = "\u03BB"
    glyph2uni["/lcaron"] = "\u013E"
    glyph2uni["/ldot"] = "\u0140"
    glyph2uni["/less"] = "\u003C"
    glyph2uni["/lessequal"] = "\u2264"
    glyph2uni["/lfblock"] = "\u258C"
    glyph2uni["/lira"] = "\u20A4"
    glyph2uni["/logicaland"] = "\u2227"
    glyph2uni["/logicalnot"] = "\u00AC"
    glyph2uni["/logicalor"] = "\u2228"
    glyph2uni["/longs"] = "\u017F"
    glyph2uni["/lozenge"] = "\u25CA"
    glyph2uni["/lslash"] = "\u0142"
    glyph2uni["/ltshade"] = "\u2591"
    glyph2uni["/m"] = "\u006D"
    glyph2uni["/macron"] = "\u00AF"
    glyph2uni["/male"] = "\u2642"
    glyph2uni["/minus"] = "\u2212"
    glyph2uni["/minute"] = "\u2032"
    glyph2uni["/mu"] = "\u00B5"
    glyph2uni["/multiply"] = "\u00D7"
    glyph2uni["/musicalnote"] = "\u266A"
    glyph2uni["/musicalnotedbl"] = "\u266B"
    glyph2uni["/n"] = "\u006E"
    glyph2uni["/nacute"] = "\u0144"
    glyph2uni["/napostrophe"] = "\u0149"
    glyph2uni["/ncaron"] = "\u0148"
    glyph2uni["/nine"] = "\u0039"
    glyph2uni["/notelement"] = "\u2209"
    glyph2uni["/notequal"] = "\u2260"
    glyph2uni["/notsubset"] = "\u2284"
    glyph2uni["/ntilde"] = "\u00F1"
    glyph2uni["/nu"] = "\u03BD"
    glyph2uni["/numbersign"] = "\u0023"
    glyph2uni["/o"] = "\u006F"
    glyph2uni["/oacute"] = "\u00F3"
    glyph2uni["/obreve"] = "\u014F"
    glyph2uni["/ocircumflex"] = "\u00F4"
    glyph2uni["/odieresis"] = "\u00F6"
    glyph2uni["/oe"] = "\u0153"
    glyph2uni["/ogonek"] = "\u02DB"
    glyph2uni["/ograve"] = "\u00F2"
    glyph2uni["/ohorn"] = "\u01A1"
    glyph2uni["/ohungarumlaut"] = "\u0151"
    glyph2uni["/omacron"] = "\u014D"
    glyph2uni["/omega"] = "\u03C9"
    glyph2uni["/omega1"] = "\u03D6"
    glyph2uni["/omegatonos"] = "\u03CE"
    glyph2uni["/omicron"] = "\u03BF"
    glyph2uni["/omicrontonos"] = "\u03CC"
    glyph2uni["/one"] = "\u0031"
    glyph2uni["/onedotenleader"] = "\u2024"
    glyph2uni["/oneeighth"] = "\u215B"
    glyph2uni["/onehalf"] = "\u00BD"
    glyph2uni["/onequarter"] = "\u00BC"
    glyph2uni["/onethird"] = "\u2153"
    glyph2uni["/openbullet"] = "\u25E6"
    glyph2uni["/ordfeminine"] = "\u00AA"
    glyph2uni["/ordmasculine"] = "\u00BA"
    glyph2uni["/orthogonal"] = "\u221F"
    glyph2uni["/oslash"] = "\u00F8"
    glyph2uni["/oslashacute"] = "\u01FF"
    glyph2uni["/otilde"] = "\u00F5"
    glyph2uni["/p"] = "\u0070"
    glyph2uni["/paragraph"] = "\u00B6"
    glyph2uni["/parenleft"] = "\u0028"
    glyph2uni["/parenright"] = "\u0029"
    glyph2uni["/partialdiff"] = "\u2202"
    glyph2uni["/percent"] = "\u0025"
    glyph2uni["/period"] = "\u002E"
    glyph2uni["/periodcentered"] = "\u00B7"
    glyph2uni["/perpendicular"] = "\u22A5"
    glyph2uni["/perthousand"] = "\u2030"
    glyph2uni["/peseta"] = "\u20A7"
    glyph2uni["/phi"] = "\u03C6"
    glyph2uni["/phi1"] = "\u03D5"
    glyph2uni["/pi"] = "\u03C0"
    glyph2uni["/plus"] = "\u002B"
    glyph2uni["/plusminus"] = "\u00B1"
    glyph2uni["/prescription"] = "\u211E"
    glyph2uni["/product"] = "\u220F"
    glyph2uni["/propersubset"] = "\u2282"
    glyph2uni["/propersuperset"] = "\u2283"
    glyph2uni["/proportional"] = "\u221D"
    glyph2uni["/psi"] = "\u03C8"
    glyph2uni["/q"] = "\u0071"
    glyph2uni["/question"] = "\u003F"
    glyph2uni["/questiondown"] = "\u00BF"
    glyph2uni["/quotedbl"] = "\u0022"
    glyph2uni["/quotedblbase"] = "\u201E"
    glyph2uni["/quotedblleft"] = "\u201C"
    glyph2uni["/quotedblright"] = "\u201D"
    glyph2uni["/quoteleft"] = "\u2018"
    glyph2uni["/quotereversed"] = "\u201B"
    glyph2uni["/quoteright"] = "\u2019"
    glyph2uni["/quotesinglbase"] = "\u201A"
    glyph2uni["/quotesingle"] = "\u0027"
    glyph2uni["/r"] = "\u0072"
    glyph2uni["/racute"] = "\u0155"
    glyph2uni["/radical"] = "\u221A"
    glyph2uni["/rcaron"] = "\u0159"
    glyph2uni["/reflexsubset"] = "\u2286"
    glyph2uni["/reflexsuperset"] = "\u2287"
    glyph2uni["/registered"] = "\u00AE"
    glyph2uni["/revlogicalnot"] = "\u2310"
    glyph2uni["/rho"] = "\u03C1"
    glyph2uni["/ring"] = "\u02DA"
    glyph2uni["/rtblock"] = "\u2590"
    glyph2uni["/s"] = "\u0073"
    glyph2uni["/sacute"] = "\u015B"
    glyph2uni["/scaron"] = "\u0161"
    glyph2uni["/scedilla"] = "\u015F"
    glyph2uni["/scircumflex"] = "\u015D"
    glyph2uni["/second"] = "\u2033"
    glyph2uni["/section"] = "\u00A7"
    glyph2uni["/semicolon"] = "\u003B"
    glyph2uni["/seven"] = "\u0037"
    glyph2uni["/seveneighths"] = "\u215E"
    glyph2uni["/shade"] = "\u2592"
    glyph2uni["/sigma"] = "\u03C3"
    glyph2uni["/sigma1"] = "\u03C2"
    glyph2uni["/similar"] = "\u223C"
    glyph2uni["/six"] = "\u0036"
    glyph2uni["/slash"] = "\u002F"
    glyph2uni["/smileface"] = "\u263A"
    glyph2uni["/space"] = "\u0020"
    glyph2uni["/spade"] = "\u2660"
    glyph2uni["/sterling"] = "\u00A3"
    glyph2uni["/suchthat"] = "\u220B"
    glyph2uni["/summation"] = "\u2211"
    glyph2uni["/sun"] = "\u263C"
    glyph2uni["/t"] = "\u0074"
    glyph2uni["/tau"] = "\u03C4"
    glyph2uni["/tbar"] = "\u0167"
    glyph2uni["/tcaron"] = "\u0165"
    glyph2uni["/therefore"] = "\u2234"
    glyph2uni["/theta"] = "\u03B8"
    glyph2uni["/theta1"] = "\u03D1"
    glyph2uni["/thorn"] = "\u00FE"
    glyph2uni["/three"] = "\u0033"
    glyph2uni["/threeeighths"] = "\u215C"
    glyph2uni["/threequarters"] = "\u00BE"
    glyph2uni["/tilde"] = "\u02DC"
    glyph2uni["/tildecomb"] = "\u0303"
    glyph2uni["/tonos"] = "\u0384"
    glyph2uni["/trademark"] = "\u2122"
    glyph2uni["/triagdn"] = "\u25BC"
    glyph2uni["/triaglf"] = "\u25C4"
    glyph2uni["/triagrt"] = "\u25BA"
    glyph2uni["/triagup"] = "\u25B2"
    glyph2uni["/two"] = "\u0032"
    glyph2uni["/twodotenleader"] = "\u2025"
    glyph2uni["/twothirds"] = "\u2154"
    glyph2uni["/u"] = "\u0075"
    glyph2uni["/uacute"] = "\u00FA"
    glyph2uni["/ubreve"] = "\u016D"
    glyph2uni["/ucircumflex"] = "\u00FB"
    glyph2uni["/udieresis"] = "\u00FC"
    glyph2uni["/ugrave"] = "\u00F9"
    glyph2uni["/uhorn"] = "\u01B0"
    glyph2uni["/uhungarumlaut"] = "\u0171"
    glyph2uni["/umacron"] = "\u016B"
    glyph2uni["/underscore"] = "\u005F"
    glyph2uni["/underscoredbl"] = "\u2017"
    glyph2uni["/union"] = "\u222A"
    glyph2uni["/universal"] = "\u2200"
    glyph2uni["/uogonek"] = "\u0173"
    glyph2uni["/upblock"] = "\u2580"
    glyph2uni["/upsilon"] = "\u03C5"
    glyph2uni["/upsilondieresis"] = "\u03CB"
    glyph2uni["/upsilondieresistonos"] = "\u03B0"
    glyph2uni["/upsilontonos"] = "\u03CD"
    glyph2uni["/uring"] = "\u016F"
    glyph2uni["/utilde"] = "\u0169"
    glyph2uni["/v"] = "\u0076"
    glyph2uni["/w"] = "\u0077"
    glyph2uni["/wacute"] = "\u1E83"
    glyph2uni["/wcircumflex"] = "\u0175"
    glyph2uni["/wdieresis"] = "\u1E85"
    glyph2uni["/weierstrass"] = "\u2118"
    glyph2uni["/wgrave"] = "\u1E81"
    glyph2uni["/x"] = "\u0078"
    glyph2uni["/xi"] = "\u03BE"
    glyph2uni["/y"] = "\u0079"
    glyph2uni["/yacute"] = "\u00FD"
    glyph2uni["/ycircumflex"] = "\u0177"
    glyph2uni["/ydieresis"] = "\u00FF"
    glyph2uni["/yen"] = "\u00A5"
    glyph2uni["/ygrave"] = "\u1EF3"
    glyph2uni["/z"] = "\u007A"
    glyph2uni["/zacute"] = "\u017A"
    glyph2uni["/zcaron"] = "\u017E"
    glyph2uni["/zdotaccent"] = "\u017C"
    glyph2uni["/zero"] = "\u0030"
    glyph2uni["/zeta"] = "\u03B6"

    if isinstance(obj, bytes):
        obj = obj.decode_pdfdocencoding(obj)
    try:
        return glyph2uni[obj]
    except KeyError:
        return ""


def paethPredictor(left, up, up_left):
    # this is only used in png compression / decompression
    # so I believe that the code should be put there
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


# end of source
