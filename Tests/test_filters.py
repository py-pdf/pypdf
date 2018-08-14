"""
Performs unit tests for filters.py.

TO-DO Add license notice, if any.
"""
import string
import sys
import unittest

from itertools import product as cartesian_product
from unittest import skip

from PyPDF4.filters import FlateDecode, ASCIIHexDecode
from PyPDF4.utils import PdfReadError, PdfStreamError


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
            "30313233343536373839616263646566414243444546>", "20090a0d0b0c>",
        )
        expected_outputs = (
            "", string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, string.digits, string.digits,
            string.hexdigits, string.whitespace
        )

        for i, o in zip(inputs, expected_outputs):
            self.assertEqual(
                ASCIIHexDecode.decode(i), o,
                msg="i = %s" % i
            )
            # print(
            #     "ASCIIHexDecode.decode(%s) == %s" % (i, ASCIIHexDecode.decode(i))
            # )


    def test_no_eod(self):
        """
        Tests when no EOD character is present, ensuring an exception is raised
        """
        inputs = ("", '', """""", '''''')

        for i in inputs:
            with self.assertRaises(PdfStreamError):
                ASCIIHexDecode.decode(i)


if __name__ == "__main__":
    unittest.main(FlateDecodeTestCase)
