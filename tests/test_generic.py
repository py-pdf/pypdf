"""
Tests the ``pypdf/generic.py`` module.
"""
import sys
import unittest

from os.path import abspath, dirname, join, pardir

# Configure path environment
PROJECT_ROOT = abspath(
    join(dirname(__file__), pardir)
)
TESTS_DATA_ROOT = join(PROJECT_ROOT, "tests", "fixture_data")

sys.path.append(PROJECT_ROOT)

from pypdf.pdf import PdfFileReader
from pypdf.generic import IndirectObject, ObjectStream


class ObjectStreamTestCase(unittest.TestCase):
    def testObjectIds(self):
        """
        Tests the ``ObjectStream.objectIds()`` method.
        """
        expResults = (
            (8, 3, 10, 2, 1, 11, 13, 15, 4, 19, 5, 20, 6, 21, 17),
        )
        # Files we know to have Object Streams within
        inputData = (
            # (filename, id, generationNumber)
            ("crazyones.pdf", 9, 0),
        )

        for o, d in zip(expResults, inputData):
            filepath = join(TESTS_DATA_ROOT, d[0])
            r = PdfFileReader(filepath)
            ref = IndirectObject(d[1], d[2], r)
            objStm = r.getObject(ref)

            self.assertIsInstance(objStm, ObjectStream)
            self.assertTupleEqual(tuple(objStm.objectIds), tuple(o))


if __name__ == "__main__":
    unittest.main()