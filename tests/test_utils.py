import string
import unittest

from pypdf4.utils import hexEncode
from tests.utils import intToBitstring, bitstringToInt


class UtilsTestCase(unittest.TestCase):
    """
    UtilsTestCase is intended to test the code utilities in utils.py.
    """
    def testHexEncode(self):
        inputs = (
            string.ascii_lowercase, string.ascii_uppercase,
            string.ascii_letters, " \t\n\r\x0b\x0c",
            # All the characters from \x00 to \xff in ascending order
            '\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10'
            '\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#'
            '$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`ab'
            'cdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87'
            '\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97'
            '\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7'
            '\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7'
            '\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7'
            '\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7'
            '\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7'
            '\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7'
            '\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
        )
        expOutputs = (
            "6162636465666768696a6b6c6d6e6f707172737475767778797a",
            "4142434445464748494a4b4c4d4e4f505152535455565758595a",
            "6162636465666768696a6b6c6d6e6f707172737475767778797a4142434445464"
            "748494a4b4c4d4e4f505152535455565758595a", "20090a0d0b0c",
            "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f2"
            "02122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f40"
            "4142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606"
            "162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f8081"
            "82838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a"
            "2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2"
            "c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e"
            "3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
        )

        for o, i in zip(expOutputs, inputs):
            self.assertEqual(o, hexEncode(i))


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
