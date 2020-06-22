# -*- coding: utf-8 -*-
"""
Performs unit tests for filters.py.

TO-DO Add license notice, if any.
"""
from itertools import product as cartesian_product
from math import floor, log
from os.path import abspath, dirname, join
import string
import sys
import unittest

import pytest

from pypdf.filters import (
    ASCII85Codec,
    ASCIIHexCodec,
    CCITTFaxCodec,
    DCTCodec,
    FlateCodec,
    LZWCodec,
    decodeStreamData,
)
from pypdf.generic import EncodedStreamObject, IndirectObject
from pypdf.pdf import PdfFileReader
from pypdf.utils import PdfReadError, PdfStreamError, hexEncode
from tests.utils import intToBitstring

TESTS_ROOT = abspath(dirname(__file__))
TEST_DATA_ROOT = join(TESTS_ROOT, "fixture_data")


# Establish bytes/str/unicode types.
try:
    unicode
except NameError:
    # Python 3
    bytes_type = bytes
    str_type = str
    unicode_type = str
else:
    # Python 2
    bytes_type = bytes
    str_type = str
    unicode_type = unicode


class FlateCodecTestCase(unittest.TestCase):
    """
    Tests expected results and edge cases of FlateCodec.
    """

    @classmethod
    def setUpClass(cls):
        cls.filterInputs = [
            "",
            "",
            """""",
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.ascii_letters,
            string.digits,
            string.hexdigits,
            string.punctuation,
            string.whitespace,  # Add more...
        ]
        for f__ in ("TheHappyPrince.txt",):
            with open(join(TEST_DATA_ROOT, f__)) as infile:
                cls.filterInputs.append(infile.read())

        cls.filterInputs = tuple(s.encode("latin1") for s in cls.filterInputs)

    def testExpectedResults(self):
        """
        Tests FlateCodec decode() and encode() methods.

        TO-DO Test the result with the omitted predictor values.
        """
        codec = FlateCodec()
        predictors = [1]  # , 10, 11, 12, 13, 14, 15]

        for predictor, s__ in cartesian_product(predictors, self.filterInputs):
            self.assertEqual(
                s__,
                codec.decode(codec.encode(s__), {"/Predictor": predictor}),
                "(predictor, s__) = (%d, %s)" % (predictor, s__),
            )

    def testInvalidPredictors(self):
        """
        Inputs a series of invalid predictor values (outside the
        {1, 2} U [10, 15] range) checking that ``PdfReadError`` is raised.
        """
        codec = FlateCodec()
        predictors = tuple(set(range(-20, 21)) - {1, 2, 10, 11, 12, 13, 14, 15})

        for predictor, s__ in cartesian_product(predictors, self.filterInputs):
            with self.assertRaises(
                PdfReadError,  # pylint: disable=bad-continuation
                msg="(predictor, input) = (%d, %s)"  # pylint: disable=bad-continuation
                % (predictor, s__),  # pylint: disable=bad-continuation
            ):
                codec.decode(codec.encode(s__), {"/Predictor": predictor})


class ASCIIHexCodecTestCase(unittest.TestCase):
    """
    Tests primarily the decode() method of ASCIIHexCodec.
    """

    @classmethod
    def setUpClass(cls):
        cls.filterInputs = (
            "",
            "",
            """""",
            ">",
            ">>",
            ">>>",
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.ascii_letters,
            string.digits,
            string.hexdigits,
            string.punctuation,
            string.whitespace,  # Add more...
        )

    def testExpectedResults(self):
        """
        Feeds a bunch of values to ``ASCIIHexCodec.decode()`` and ensures that
        the correct output is returned.

        TO-DO What is decode() supposed to do for such inputs as ">>", ">>>" or
        any other not terminated by ">"? (For the latter case, an exception
        is currently raised.)
        """
        inputs = (
            ">",
            "6162636465666768696a6b6c6d6e6f707172737475767778797a>",
            "4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464"
            "748494a4b4c4d4e4f505152535455565758595a>",
            "30313233343536373839>",
            "3  031323334353637   3839>",  # Same as previous, but whitespaced
            "30313233343536373839616263646566414243444546>",
            hexEncode(string.whitespace) + ">",
        )
        expected_outputs = (
            "",
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.ascii_letters,
            string.digits,
            string.digits,
            string.hexdigits,
            string.whitespace,
        )

        for o__, i in zip(expected_outputs, inputs):
            self.assertEqual(
                o__,
                ASCIIHexCodec.decode(i),
                "Expected = %s\tReceived = %s"
                % (repr(o__), repr(ASCIIHexCodec.decode(i))),
            )

    def testNoEod(self):
        """
        Tests when no EOD character is present, ensuring an exception is
        raised.
        """
        inputs = ("", "", """""", """""")

        for i in inputs:
            with self.assertRaises(PdfStreamError):
                ASCIIHexCodec.decode(i)


class ASCII85CodecTestCase(unittest.TestCase):
    """
    Tests the ``decode()`` method of ``ASCII85Codec``.
    """

    def testEncodeDecode(self):
        """
        Verifies that decode(encode(data)) == data, with encode() and decode()
        from ASCII85Codec.
        """
        e__, d__ = ASCII85Codec.encode, ASCII85Codec.decode
        inputs = [
            string.ascii_lowercase.encode("ascii"),
            string.ascii_uppercase.encode("ascii"),
            string.ascii_letters.encode("ascii"),
            string.whitespace.encode("ascii"),
            b"\x00\x00\x00\x00",
            2 * b"\x00\x00\x00\x00",
        ]

        for filename in ("TheHappyPrince.txt",):
            with open(join(TEST_DATA_ROOT, filename), "rb") as infile:
                inputs.append(infile.read())

        for i in inputs:
            if sys.version_info > (3, 0) and isinstance(i, str):
                # The Python 3 version of decode() returns a bytes instance
                exp = i.encode("LATIN1")
            else:
                exp = i

            self.assertEqual(exp, d__(e__(i)))

    def testWithOverflow(self):
        """ [EXPLAIN THIS.] """
        inputs = (
            v__ + "~>"
            for v__ in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f"
            "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a"
            "\x1b\x1c\x1d\x1e\x1fvwxy{|}~\x7f\x80\x81\x82"
            "\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d"
            "\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98"
            "\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬"
            "\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇ"
        )

        for i in inputs:
            with self.assertRaises(ValueError, msg="char = " + repr(i)):
                ASCII85Codec.decode(i)

    def testFiveZeroBytes(self):
        """
        From ISO 32000 (2008) sect. 7.4.3:
        «As a special case, if all five bytes are 0, they shall be represented
        by the character with code 122 (z) instead of by five exclamation
        points (!!!!!).»
        """
        inputs = (b"z~>", b"zz~>", b"zzz~>")
        exp_outputs = (
            b"\x00\x00\x00\x00",
            b"\x00\x00\x00\x00" * 2,
            b"\x00\x00\x00\x00" * 3,
        )

        self.assertEqual(ASCII85Codec.decode(b"!!!!!~>"), ASCII85Codec.decode(b"z~>"))

        for o__, i in zip(exp_outputs, inputs):
            self.assertEqual(o__, ASCII85Codec.decode(i))


class LZWCodecTestCase(unittest.TestCase):
    """
    Tests the ``LZWCodec.decode()`` method by means of a LZW Encoder built
    specifically for testing it.
    """

    def testWriteCode(self):
        """
        Tests that the memorization of bit values performed by ``_writeCode()``
        as a contiguous bit-stream works as intended.
        """
        self.maxDiff = None
        e__ = LZWCodec.Encoder("")
        e__.output = list()

        inputs = range(2 ** 8, 2 ** 12 - 1)
        e__.bitspercode = int(floor(log(inputs[0], 2))) + 1
        exp_output = "".join(intToBitstring(n__, floor(log(n__, 2))) for n__ in inputs)

        for i in inputs:
            if floor(log(i, 2)) + 1 > e__.bitspercode:
                e__.bitspercode += 1

            e__._writeCode(i)

        self.assertEqual(
            exp_output, "".join(intToBitstring(n__) for n__ in e__.output)[: e__.bitpos]
        )

    def testReadCode(self):
        """
        Tests that the interpretation of bit values performed by
        ``_readCode()`` as a contiguous bit-stream works as intended.
        """
        inputs = bytearray(range(256))
        d__ = LZWCodec.Decoder(inputs)
        exp_output_stream = "".join(intToBitstring(b__) for b__ in inputs)
        curr = 0
        # TODO:  this deserves to be an assignment expression.
        code = d__._readCode()

        while code != -1:
            if curr + d__.bitspercode >= len(exp_output_stream):
                exp_output = exp_output_stream[curr:] + "0" * (
                    (curr + d__.bitspercode) - len(exp_output_stream)
                )
            else:
                exp_output = exp_output_stream[curr : curr + d__.bitspercode]

            self.assertEqual(
                exp_output,
                intToBitstring(code, d__.bitspercode),
                msg="(curr, code) = (%d, %d)" % (curr, code),
            )

            curr += d__.bitspercode
            code = d__._readCode()

    def testEncodeDecode(self):
        """
        Ensures that the ``decode(encode(data))`` concatenation equals data,
        where data can be an arbitrary byte stream.
        """
        self.maxDiff = None
        inputs = [
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.whitespace,
            string.ascii_letters,
            2000 * string.ascii_letters,
        ]

        if sys.version_info > (3, 0):
            for index, e in enumerate(inputs):
                inputs[index] = e.encode("LATIN1")

        for f__ in (
            "Hamlet.txt",  # pylint: disable=bad-continuation
            "TheHappyPrince.txt",  # pylint: disable=bad-continuation
        ):
            with open(join(TEST_DATA_ROOT, f__), "rb") as infile:
                # TO-DO If we approach the number of read bytes to 10K the
                # codec stops working correctly. This is a bug to fix!
                inputs.append(infile.read())

        for b__ in inputs:
            e__ = LZWCodec.Encoder(b__)
            d__ = LZWCodec.Decoder(e__.encode())

            # self.assertEqual(b__, d__.decode())


class DecodeStreamDataTestCase(unittest.TestCase):
    """
    Test case intended to test the
    :meth:`decodeStreamData<filters.decodeStreamData>` method. If functions by
    querying known object references, asking ``decodeStreamData()`` to decode
    their stream content and check the decoded value against what would be
    produced by the filter that is known to be used.
    """

    def testDecodeStreamData(self):
        """ Stores PDF files infos and the coordinates of stream objects. We
            don't care if we need to open a new file stream for each obj.
            reference -- unit tests don't have to be efficient
        """
        this_dir = join(TEST_DATA_ROOT, self.testDecodeStreamData.__name__)
        filters = (
            # (filter type, filename, id, gen. number)
            (FlateCodec, "FlateDecode.pdf", 4, 0),
            (FlateCodec, "FlateDecode.pdf", 8, 0),
            (FlateCodec, "FlateDecode.pdf", 9, 0),
            # TO-DO No PDF files found with this type of encoding, get them.
            # (ASCIIHexCodec, "ASCIIHexDecode.pdf", ?, ?)
            (LZWCodec, "LZWDecode.pdf", 209, 0),
            (LZWCodec, "LZWDecode.pdf", 210, 0),
            (LZWCodec, "LZWDecode.pdf", 211, 0),
            (ASCII85Codec, "ASCII85Decode.pdf", 5, 0),
            (ASCII85Codec, "ASCII85Decode.pdf", 6, 0),
            (DCTCodec, "DCTDecode.pdf", 4, 0),
            # TO-DO No PDF files found with this type of encoding, get them.
            # (JPXCodec, "JPXDecode.pdf", ?, ?)
            (CCITTFaxCodec, "CCITTFaxDecode.pdf", 46, 0),
        )

        for f__ in filters:
            with open(join(this_dir, f__[1]), "rb") as infile:
                reader = PdfFileReader(infile)
                ref = IndirectObject(f__[2], f__[3], reader)
                stream = reader.getObject(ref)

                # Ensures that the PdfFileReader reads a stream object
                self.assertEqual(EncodedStreamObject, type(stream))

                # print("Running with %s!" % f[0].__name__)
                if f__[0] is CCITTFaxCodec:
                    self.assertEqual(
                        f__[0].decode(
                            stream._data,
                            stream.get("/DecodeParms"),
                            stream.get("/Height"),
                        ),
                        decodeStreamData(stream),
                    )
                else:
                    self.assertEqual(
                        f__[0].decode(stream._data, stream.get("/DecodeParms")),
                        decodeStreamData(stream),
                    )


@pytest.mark.parametrize(
    "data, expected_value, exception",
    (
        (b"<~~>", b"", None),  # Empty input
        (b"<~@:E^~>", b"abc", None),  # Basic decoding
        (u"<~@:E^~>", b"abc", None),  # Handle a str (or unicode) object
        (b"<~@: E^~>", b"abc", None),  # Ignore whitespace
        (b"<~z~>", b"\x00\x00\x00\x00", None),  # Handle 'z'
        (b"~>", b"", None),  # No initial '<~'
        (b"@:E^~>", b"abc", None),  # No initial '<~'
        (b"", None, ValueError),  # Choke on missing '~>'
        (b">", None, ValueError),  # Choke on missing '~>'
        (b"<~<~~>", None, ValueError),  # Don't double-skip '<~'
        (b"<~~~>", None, ValueError),  # Choke on bare '~'
        (b"<~aazaa~>", None, ValueError),  # Choke on mid-group 'z'
        (u"<~\x80~>", None, ValueError),  # Choke on non-ASCII characters
    ),
)
def test_ascii85_decode(data, expected_value, exception):
    """ [EXPLAIN THIS.] """
    if exception:
        with pytest.raises(exception):
            ASCII85Codec.decode(data)
    else:
        value = ASCII85Codec.decode(data)
        assert value == expected_value
        assert isinstance(value, bytes_type)


@pytest.mark.parametrize(
    "data, expected_value",
    (
        (b"", b"<~~>"),
        (b"abc", b"<~@:E^~>"),
        (b"\x00", b"<~!!~>"),
        (b"\xff", b"<~rr~>"),
        (b"\x00\x00\x00\x00", b"<~z~>"),
    ),
)
def testASCII85Encode(data, expected_value):
    """ [EXPLAIN THIS.] """
    value = ASCII85Codec.encode(data)
    assert value == expected_value
    assert isinstance(value, bytes_type)
