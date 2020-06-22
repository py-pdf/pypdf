# Copyright 2018 Acsor <nildexo@yandex.com>
# Copyright 2019 Kurt McKee <contactme@kurtmckee.org>
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

import io
import re
import string
import unittest

import pytest

import pypdf.utils
from tests.utils import bitstringToInt, intToBitstring

# Establish the bytes/str/unicode types.
try:
    unicode
except NameError:
    # Python 3
    bytes_type = bytes
    str_type = str
    unicode_type = str
else:
    # Python 2
    bytes_type = str
    str_type = str
    unicode_type = unicode


class UtilsTestCase(unittest.TestCase):
    """
    UtilsTestCase is intended to test the code utilities in utils.py.
    """

    def testHexEncode(self):
        inputs = (
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.ascii_letters,
            " \t\n\r\x0b\x0c",
            # All the characters from \x00 to \xff in ascending order
            "\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10"
            '\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#'
            "$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`ab"
            "cdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87"
            "\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97"
            "\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7"
            "\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7"
            "\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7"
            "\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7"
            "\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7"
            "\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7"
            "\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff",
        )
        expOutputs = (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a",
            "4142434445464748494a4b4c4d4e4f505152535455565758595a",
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464"
            "748494a4b4c4d4e4f505152535455565758595a",
            "20090a0d0b0c",
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2"
            "02122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f40"
            "4142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606"
            "162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f8081"
            "82838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a"
            "2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2"
            "c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e"
            "3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff",
        )

        for o, i in zip(expOutputs, inputs):
            self.assertEqual(o, pypdf.utils.hexEncode(i))

    def testPairs(self):
        """
        Tests ``utils.pairs()``.
        """
        inputs = (range(0), range(6), range(10))
        expOutputs = (
            tuple(),
            ((0, 1), (2, 3), (4, 5)),
            ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9)),
        )

        for o, i in zip(expOutputs, inputs):
            self.assertTupleEqual(o, tuple(pypdf.utils.pairs(i)))

    def testPairsException(self):
        """
        Tests ``utils.pairs()`` when it is fed unaccepted values.
        """
        inputs = (range(1), range(5), range(11), range(111))

        for i in inputs:
            with self.assertRaises(ValueError):
                list(pypdf.utils.pairs(i))


class TestUtilsTestCase(unittest.TestCase):
    """
    TestUtilsTestCase is intended to test test-related utils functions, not
    project-wide ones.
    """

    def testIntToBitstringToInt(self):
        """
        Ensures that bitstringToInt(intToBitsring(input)) == input.
        """
        inputs = range(2 ** 12 + 1)

        for i in inputs:
            self.assertEqual(i, bitstringToInt(intToBitstring(i)))

    def testBitstringToInt(self):
        """
        Ensures that bitstringToInt() produces the expected result from some
        of its possible inputs.
        """
        inputs = (
            "00000000",
            "",
            "00000001",
            "1",
            "01010101",
            "1010101",
            "10101010",
            "11111111",
            "100000000",
            "0100000000",
            "00100000000",
            "000100000000",
            "100000001",
            "0100000001",
            "00100000001",
            "000100000001",
        )
        expOutputs = (
            0,
            0,
            1,
            1,
            85,
            85,
            170,
            255,
            256,
            256,
            256,
            256,
            257,
            257,
            257,
            257,
        )

        for o, b in zip(expOutputs, inputs):
            self.assertEqual(o, bitstringToInt(b))


@pytest.mark.parametrize(
    "arg, expected",
    (
        (u"str", True),
        ("str", True),
        (123, False),
        # I *think* that the function behaves incorrectly here.
        #
        # Python 2 support ends in 2020, but for now, I think that is_string()
        # should return False for Python 2 `bytes` and `str` objects, and only
        # `unicode` objects should return True.
        #
        # If this gets fixed, this additional test parameter will need
        # to be uncommented:
        #
        # (b'bytes', False)
    ),
)
def testIsString(arg, expected):
    assert pypdf.utils.isString(arg) == expected


@pytest.mark.parametrize(
    "arg, expected", ((123, True), (1 << 100, True), (123.123, False), ("str", False),)
)
def testIsInt(arg, expected):
    assert pypdf.utils.isInt(arg) == expected


@pytest.mark.parametrize(
    "arg, expected",
    (
        (b"bytes", True),
        (u"bytes".encode("utf8"), True),
        (u"str", False),
        (b"str".decode("utf8"), False),
        (10, False),
    ),
)
def testIsBytes(arg, expected):
    assert pypdf.utils.isBytes(arg) == expected


@pytest.mark.parametrize(
    "data, maxchars, expected_value, expected_tell",
    (
        (b"", None, b"", 0),
        (b"abcdef", None, b"abcdef", 6),
        (b"abcdef", 3, b"abc", 3),
        (b"abc def", None, b"abc", 4),
    ),
)
def testReadUntilWhitespace(data, maxchars, expected_value, expected_tell):
    stream = io.BytesIO(data)
    assert pypdf.utils.readUntilWhitespace(stream, maxchars) == expected_value
    assert stream.tell() == expected_tell


@pytest.mark.parametrize(
    "data, expected_value, expected_tell",
    ((b"", b"", 0), (b"      ", b"", 6), (b"   a   ", b"a", 4),),
)
def testReadNonWhitespace(data, expected_value, expected_tell):
    stream = io.BytesIO(data)
    assert pypdf.utils.readNonWhitespace(stream) == expected_value
    assert stream.tell() == expected_tell


@pytest.mark.parametrize(
    "data, expected_result, expected_tell",
    (
        (b"", False, 0),
        (b"      ", True, 6),
        (b"a   ", False, 1),
        (b" a   ", True, 2),
        (b"  a   ", True, 3),
    ),
)
def testSkipOverWhitespace(data, expected_result, expected_tell):
    stream = io.BytesIO(data)
    assert pypdf.utils.skipOverWhitespace(stream) == expected_result
    assert stream.tell() == expected_tell


@pytest.mark.parametrize(
    "data, expected_tell",
    ((b"", 0), (b" ", 0), (b"a", 0), (b"%a\n\r", 3), (b"%a\r\n", 3), (b"%aa\r", 4),),
)
def testSkipOverComments(data, expected_tell):
    stream = io.BytesIO(data)
    pypdf.utils.skipOverComment(stream)
    assert stream.tell() == expected_tell


@pytest.mark.parametrize(
    "data, pattern, expected_value, expected_tell",
    (
        (b"", b"123", b"", 0),
        (b"abc123def", b"123", b"abc", 3),
        (b"abcdef", b"123", b"abcdef", 6),
    ),
)
def testReadUntilRegex(data, pattern, expected_value, expected_tell):
    stream = io.BytesIO(data)
    regex = re.compile(pattern)
    assert pypdf.utils.readUntilRegex(stream, regex, ignore_eof=True) == expected_value
    assert stream.tell() == expected_tell


def testReadUntilRegexException():
    stream = io.BytesIO(b"abcdef")
    regex = re.compile(b"123")
    with pytest.raises(pypdf.utils.PdfStreamError):
        pypdf.utils.readUntilRegex(stream, regex, ignore_eof=False)


def testMatrixMultiply():
    matrix1 = [
        [1, 2],
        [3, 4],
    ]
    matrix2 = [
        [2, 3],
        [5, 7],
    ]
    expected_result = [
        [12, 17],
        [26, 37],
    ]
    assert pypdf.utils.matrixMultiply(matrix1, matrix2) == expected_result


@pytest.mark.parametrize(
    "arg, expected_value",
    ((b"a", b"a"), (b"a"[0], b"a"), ("a", b"a"), (u"a", b"a"), (97, b"a"),),
)
def testPypdfBytes(arg, expected_value):
    value = pypdf.utils.pypdfBytes(arg)
    assert value == expected_value
    assert isinstance(value, bytes_type)


@pytest.mark.parametrize(
    "arg, expected_value", ((b"abc", "abc"), ("abc", "abc"), (u"abc", "abc"),)
)
def testPypdfStr(arg, expected_value):
    value = pypdf.utils.pypdfStr(arg)
    assert value == expected_value
    assert isinstance(value, str_type)


@pytest.mark.parametrize(
    "arg, expected_value",
    (
        (b"abc", u"abc"),
        ("abc", u"abc"),
        (u"abc", u"abc"),
        (b"\\u0061bc", u"abc"),
        (u"\\u0061bc", u"\\u0061bc"),
    ),
)
def testPypdfUnicode(arg, expected_value):
    value = pypdf.utils.pypdfUnicode(arg)
    assert value == expected_value
    assert isinstance(value, unicode_type)


@pytest.mark.parametrize(
    "arg, expected_value",
    (
        (b"a", 97),
        (b"a"[0], 97),
        ("a", 97),
        ("a"[0], 97),
        (u"a", 97),
        (u"a"[0], 97),
        (97, 97),
    ),
)
def testPypdfOrd(arg, expected_value):
    value = pypdf.utils.pypdfOrd(arg)
    assert value == expected_value
    assert isinstance(value, int)


@pytest.mark.parametrize(
    "arg, expected_value", ((97, "a"), (b"a", "a"), ("a", "a"), (u"a", "a"),)
)
def testPypdfChr(arg, expected_value):
    value = pypdf.utils.pypdfChr(arg)
    assert value == expected_value
    assert isinstance(value, str_type)


@pytest.mark.parametrize(
    "arg, expected_value", ((0x1, "0x1"), (1 << 100, "0x10000000000000000000000000"),)
)
def testHexStr(arg, expected_value):
    value = pypdf.utils.hexStr(arg)
    assert value == expected_value
    assert isinstance(value, str_type)


def testRC4Encode():
    crypto_text = pypdf.utils.RC4Encrypt("def", "abc")
    assert crypto_text == b"\x9e\xa6\xef"
    assert isinstance(crypto_text, bytes)


@pytest.mark.parametrize(
    "filename", (r"path/to/filename", r"path\to\filename", r"filename",)
)
def testFormatWarning(filename):
    args = ("message", Warning, filename, "lineno", "line")
    warning = pypdf.utils.formatWarning(*args)
    assert warning == "Warning: message [filename:lineno]\n"


def testWhitespaces():
    whitespaces = {b" ", b"\n", b"\r", b"\t", b"\x00"}
    assert whitespaces == set(pypdf.utils.WHITESPACES)
    for character in pypdf.utils.WHITESPACES:
        assert isinstance(character, bytes_type)
