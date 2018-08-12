"""
Adds unit tests for filters.py.

TO-DO Add license notice, if any.
"""
import string
import sys
import unittest

from itertools import product as cartesian_product

from PyPDF4.filters import FlateDecode
from PyPDF4.utils import PdfReadError


class FlateDecodeTestCase(unittest.TestCase):
    """
    Tests expected results and edge cases of FlateDecode.
    """
    @classmethod
    def setUpClass(cls):
        cls.filter_inputs = (
            # "", '', """""",
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


if __name__ == "__main__":
    unittest.main(FlateDecodeTestCase)
