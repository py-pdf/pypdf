"""
Tests the ``pypdf/generic.py`` module.
"""
import io
from os.path import abspath, dirname, join, pardir
import sys
import unittest

from pypdf.generic import IndirectObject, ObjectStream, TextStringObject
from pypdf.pdf import PdfFileReader

# Configure path environment
PROJECT_ROOT = abspath(join(dirname(__file__), pardir))
TESTS_DATA_ROOT = join(PROJECT_ROOT, "tests", "fixture_data")

sys.path.append(PROJECT_ROOT)


class ObjectStreamTestCase(unittest.TestCase):
    """ [EXPLAIN THIS.] """

    def test_object_ids(self):
        """
        Tests the ``ObjectStream.objectIds()`` method.
        """
        exp_results = (
            (8, 3, 10, 2, 1, 11, 13, 15, 4, 19, 5, 20, 6, 21, 17),
            (
                644,
                642,
                646,
                647,
                648,
                122,
                119,
                120,
                121,
                124,
                179,
                232,
                327,
                467,
                478,
                519,
                568,
                573,
                580,
                586,
                592,
                598,
                603,
                611,
                616,
                623,
                629,
                634,
            ),
        )
        # Files we know to have Object Streams within
        input_data = (
            # (filename, id, generation number)
            ("crazyones.pdf", 9, 0),
            ("GeoBase_NHNC1_Data_Model_UML_EN.pdf", 645, 0),
        )

        for o__, d__ in zip(exp_results, input_data):
            filepath = join(TESTS_DATA_ROOT, d__[0])
            r__ = PdfFileReader(filepath)
            ref = IndirectObject(d__[1], d__[2], r__)
            obj_stm = r__.getObject(ref)

            r__.close()

            self.assertIsInstance(obj_stm, ObjectStream)
            self.assertTupleEqual(tuple(o__), tuple(obj_stm.objectIds))


class TextStringObjectTestCase(unittest.TestCase):
    """ [EXPLAIN THIS.] """

    @staticmethod
    def _get_output_bytes_for_string(input_string):
        stream = io.BytesIO()
        text_string_object = TextStringObject(input_string)
        text_string_object.writeToStream(stream, encryption_key=None)
        stream_output = stream.getvalue()
        return stream_output

    def test_write_to_stream(self):
        """
        Tests the ``TextStringObject.writeToStream()`` method.
        """

        output_for_lowercase_letter = self._get_output_bytes_for_string("k")
        self.assertEqual(output_for_lowercase_letter, b"(k)")

        output_for_uppercase_letter = self._get_output_bytes_for_string("K")
        self.assertEqual(output_for_uppercase_letter, b"(K)")

        output_for_digit = self._get_output_bytes_for_string("7")
        self.assertEqual(output_for_digit, b"(7)")

        output_for_space = self._get_output_bytes_for_string(" ")
        self.assertEqual(output_for_space, b"( )")

        output_for_opening_parentheses = self._get_output_bytes_for_string("(")
        self.assertEqual(output_for_opening_parentheses, b"(\\050)")

        output_for_backslash = self._get_output_bytes_for_string("\\")
        self.assertEqual(output_for_backslash, b"(\\134)")


if __name__ == "__main__":
    unittest.main()
