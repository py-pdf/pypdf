# -*- coding: utf-8 -*-
"""
Performs unit tests for filters.py.

TO-DO Add license notice, if any.
"""
import string
import sys
import unittest
from itertools import product as cartesian_product
from math import ceil, floor, log
from os.path import join
from unittest import skip

from PyPDF4.filters import FlateDecode, ASCIIHexDecode, ASCII85Decode, \
    LZWDecode
from PyPDF4.utils import PdfReadError, PdfStreamError, hexEncode
from Tests.utils import intToBitstring, bitstringToInt


TEST_DATA_DIR = join("Tests", "TestData")


class FlateDecodeTestCase(unittest.TestCase):
    """
    Tests expected results and edge cases of FlateDecode.
    """
    @classmethod
    def setUpClass(cls):
        cls.filter_inputs = [
            "", '', """""",
            string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, string.digits, string.hexdigits,
            string.punctuation, string.whitespace,  # Add more...
        ]
        for f in ("TheHappyPrince.txt", ):
            with open(join(TEST_DATA_DIR, f)) as infile:
                cls.filter_inputs.append(infile.read())

        cls.filter_inputs = tuple(
            s.encode("latin1") for s in cls.filter_inputs
        )

    def test_expected_results(self):
        """
        Tests FlateDecode decode() and encode() methods.

        TO-DO Test the result with the omitted predictor values.
        """
        codec = FlateDecode()
        predictors = [1]  # , 10, 11, 12, 13, 14, 15]

        for predictor, s in cartesian_product(predictors, self.filter_inputs):
            self.assertEqual(
                s, codec.decode(codec.encode(s), {"/Predictor": predictor}),
                "(predictor, s) = (%d, %s)" % (predictor, s)
            )

    def test_unsupported_predictor(self):
        """
        Inputs an unsupported predictor (outside the [10, 15] range) checking
        that PdfReadError() is raised. Once this predictor support is updated
        in the future, this test case may be removed.
        """
        codec = FlateDecode()
        predictors = (-10, -1, 0, 9, 16, 20, 100)

        for predictor, s in cartesian_product(predictors, self.filter_inputs):
            with self.assertRaises(
                    PdfReadError,
                    msg="(predictor, input) = (%d, %s)" % (predictor, s),
            ):
                codec.decode(codec.encode(s), {"/Predictor": predictor})


class ASCIIHexDecodeTestCase(unittest.TestCase):
    """
    Tests primarily the decode() method of ASCIIHexDecode.
    """
    @classmethod
    def setUpClass(cls):
        cls.filter_inputs = (
            "", '', """""",
            ">", ">>", ">>>",
            string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, string.digits, string.hexdigits,
            string.punctuation, string.whitespace,  # Add more...
        )

    def test_expected_results(self):
        """
        Feeds a bunch of values to ASCIIHexDecode.decode() and ensures the
        correct output is returned.

        TO-DO What is decode() supposed to do for such inputs as ">>", ">>>" or
        any other not terminated by ">"? (For the latter case, an exception
        is currently raised.)
        """
        inputs = (
            ">", "6162636465666768696a6b6c6d6e6f707172737475767778797a>",
            "4142434445464748494a4b4c4d4e4f505152535455565758595a>",
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464"
            "748494a4b4c4d4e4f505152535455565758595a>",
            "30313233343536373839>",
            "3  031323334353637   3839>",  # Same as previous, but whitespaced
            "30313233343536373839616263646566414243444546>",
            hexEncode(string.whitespace) + ">",
        )
        expected_outputs = (
            "", string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, string.digits, string.digits,
            string.hexdigits, string.whitespace
        )

        for o, i in zip(expected_outputs, inputs):
            self.assertEqual(
                o, ASCIIHexDecode.decode(i),
                "Expected = %s\tReceived = %s" %
                (repr(o), repr(ASCIIHexDecode.decode(i)))
            )

    def test_no_eod(self):
        """
        Tests when no EOD character is present, ensuring an exception is
        raised.
        """
        inputs = ("", '', """""", '''''')

        for i in inputs:
            with self.assertRaises(PdfStreamError):
                ASCIIHexDecode.decode(i)


class ASCII85DecodeTestCase(unittest.TestCase):
    """
    Tests the decode() method of ASCII85Decode.

    TO-DO A proper input-expected output test case is missing and should be
    added.
    """
    def test_with_overflow(self):
        inputs = (
            v + "~>" for v in '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0e\x0f'
                              '\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a'
                              '\x1b\x1c\x1d\x1e\x1fvwxy{|}~\x7f\x80\x81\x82'
                              '\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d'
                              '\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98'
                              '\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0¡¢£¤¥¦§¨©ª«¬'
                              '\xad®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇ'
        )

        for i in inputs:
            with self.assertRaises(ValueError, msg="char = " + repr(i)):
                ASCII85Decode.decode(i)

    def test_five_zero_bytes(self):
        """
        From ISO 32000 (2008) sect. 7.4.3:
        «As a special case, if all five bytes are 0, they shall be represented
        by the character with code 122 (z) instead of by five exclamation
        points (!!!!!).»
        """
        inputs = ("z", "zz", "zzz")
        exp_outputs = (
            b"\x00\x00\x00\x00", b"\x00\x00\x00\x00" * 2,
            b"\x00\x00\x00\x00" * 3,
        )

        self.assertEqual(
            ASCII85Decode.decode("!!!!!"), ASCII85Decode.decode("z")
        )

        for o, i in zip(exp_outputs, inputs):
            self.assertEqual(
                o, ASCII85Decode.decode(i)
            )


class LZWDecodeTestCase(unittest.TestCase):
    """
    Tests the LZWDecode.decode() method by means of a LZW Encoder built
    specifically for testing it.
    """
    def test_write_code(self):
        """
        Tests that the memorization of byte values performed by _writeCode()
        as a contiguous bit-stream works as intended.
        """
        self.maxDiff = None
        e = LZWDecode.Encoder(None)
        e.result = list()

        inputs = range(2 ** 8, 2 ** 12 - 1)
        e.bitspercode = int(floor(log(inputs[0], 2))) + 1
        exp_output = "".join(
            intToBitstring(n, floor(log(n, 2))) for n in inputs
        )

        for i in inputs:
            if floor(log(i, 2)) + 1 > e.bitspercode:
                e.bitspercode += 1

            e._writeCode(i)

        self.assertEqual(
            exp_output,
            "".join(intToBitstring(n) for n in e.result)[:e.bitpos]
        )

    def test_encode_decode(self):
        """
        Ensures that the decode(encode(data)) concatenation equals data, where
        data can be an arbitrary byte stream.
        """
        inputs = [
            string.ascii_lowercase, string.ascii_uppercase, string.whitespace,
            string.ascii_letters, "AABBCCDDEEFFGGHHIIJJKKLLMMNNOOPPQQRRSSTTT",
        ]

        for f in ("TheHappyPrince.txt", ):
            with open(join(TEST_DATA_DIR, f)) as infile:
                inputs.append(infile.read())

        for t in inputs:
            self.assertEqual(
                t, LZWDecode.decode(LZWDecode.encode(t))
            )


if __name__ == "__main__":
    unittest.main()
