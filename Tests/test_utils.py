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
        exp_outputs = inputs = range(2 ** 12 + 1)

        for o, i in zip(exp_outputs, inputs):
            self.assertEqual(
                o, bitstringToInt(intToBitstring(i))
            )

    def testBitstringToInt(self):
        inputs = (
            "00000000", "",
            "00000001", "1",
            "01010101", "1010101",
            "10101010",
            "11111111",
            "100000000", "0100000000", "00100000000", "000100000000",
            "100000001", "0100000001", "00100000001", "000100000001",
        )
        exp_outputs = (
            0, 0,
            1, 1,
            85, 85,
            170,
            255,
            256, 256, 256, 256,
            257, 257, 257, 257,
        )

        for o, b in zip(exp_outputs, inputs):
            self.assertEqual(
                o, bitstringToInt(b)
            )


if __name__ == "__main__":
    unittest.main()
