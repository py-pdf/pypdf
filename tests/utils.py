"""
File containing utils intended to be used in unit testing rather than the
internal project codebase.
"""


def intToBitstring(n__, fill=8):
    """
    Turns an integer ``n`` into its corresponding textual bit representation.

    :param fill: number of zeros to pad the bit representation with.
    :raises TypeError: if n is not an integer.
    """
    if not isinstance(n__, int):
        raise TypeError("n must be an integer")

    return ("{bits:0>%db}" % fill).format(bits=n__)


def bitstringToInt(b__):
    """Performs the reverse of ``intToBitstring()``."""
    if not isinstance(b__, str):
        raise TypeError("Expected str, got %s" % b__.__class__)
    if not set(b__).issubset({"0", "1"}):
        raise ValueError("b must be a string containing only 0's and 1's")

    result, bitlen = 0, len(b__)

    for index, i in enumerate(b__):
        if i == "1":
            result += 2 ** (bitlen - index - 1)

    return result
