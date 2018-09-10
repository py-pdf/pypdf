import sys
import unittest

from unittest import skipIf

from utils import intToBitstring, bitstringToInt


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
            self.assertEqual(
                i, bitstringToInt(intToBitstring(i))
            )

    def testBitstringToInt(self):
        """
        Ensures that bitstringToInt() produces the expected result from some
        of its possible inputs.
        """
        inputs = (
            "00000000", "",
            "00000001", "1",
            "01010101", "1010101",
            "10101010",
            "11111111",
            "100000000", "0100000000", "00100000000", "000100000000",
            "100000001", "0100000001", "00100000001", "000100000001",
        )
        expOutputs = (
            0, 0,
            1, 1,
            85, 85,
            170,
            255,
            256, 256, 256, 256,
            257, 257, 257, 257,
        )

        for o, b in zip(expOutputs, inputs):
            self.assertEqual(
                o, bitstringToInt(b)
            )


if __name__ == "__main__":
    unittest.main()
