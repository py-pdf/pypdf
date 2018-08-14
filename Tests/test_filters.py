# -*- coding: utf-8 -*-
"""
Performs unit tests for filters.py.

TO-DO Add license notice, if any.
"""
import string
import sys
import unittest
from itertools import product as cartesian_product

from PyPDF4.filters import FlateDecode, ASCIIHexDecode, ASCII85Decode, \
    LZWDecode
from PyPDF4.utils import PdfReadError, PdfStreamError, hexencode


class FlateDecodeTestCase(unittest.TestCase):
    """
    Tests expected results and edge cases of FlateDecode.
    """
    @classmethod
    def setUpClass(cls):
        cls.filter_inputs = (
            "", '', """""",
            string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, string.digits, string.hexdigits,
            string.punctuation, string.whitespace,  # Add more...
        )

        # TO-DO Is this check, with specific regard to sys.version_info, OK?
        # Note: bytes() is not supported in Python 2
        if sys.version_info > (3, 0):
            cls.filter_inputs = tuple(
                bytes(s, "ASCII") for s in cls.filter_inputs
            )

    def test_expected_results(self):
        """
        Tests FlateDecode decode() and encode() methods.
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
            hexencode(string.whitespace) + ">",
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
        Tests when no EOD character is present, ensuring an exception is raised
        """
        inputs = ("", '', """""", '''''')

        for i in inputs:
            with self.assertRaises(PdfStreamError):
                ASCIIHexDecode.decode(i)


class ASCII85DecodeTestCase(unittest.TestCase):
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
        From ISO 32000 (2008) §7.4.3:
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
    def test_decode(self):
        inputs = (
            "\x80\x0B\x60\x50\x22\x0C\x0C\x85\x01",
            "\x54\x68\x69\x73\x20\x82\x20\x61\x20\x73\x61\x6d\x70\x6c\x65\x20"
            "\x74\x65\x78\x74\x88\x74\x72\x69\x6e\x67\x20\x49\x27\x64\x20\x6c"
            "\x69\x6b\x8e\x74\x6f\x20\x65\x6e\x63\x6f\x64\x65\x85\x01",
        )
        exp_outputs = (
            "-----A---B",
            "This is a sample text string I'd like to encode",
        )

        for o, i in zip(exp_outputs, inputs):
            self.assertEqual(
                o, LZWDecode.decode(i),
                "Input = %s\tExp. output = %s"
            )


if __name__ == "__main__":
    unittest.main(FlateDecodeTestCase)
