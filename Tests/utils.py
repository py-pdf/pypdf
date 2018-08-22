def intToBitstring(n, fill=8):
    """
    Turns an integer n into its corresponding bit representation.

    :param fill: number of zeros to pad the bit representation with.
    :raises TypeError: if n is not an integer.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")

    return ("{bits:0>%db}" % fill).format(bits=n)


def bitstringToInt(b):
    """Performs the reverse of intToBitstring()."""
    if not isinstance(b, str):
        raise TypeError("Expected str, got %s" % b.__class__)
    if not set(b).issubset({"0", "1"}):
        raise ValueError("b must be a string containing only 0's and 1's")

    result, bitlen = 0, len(b)

    for index, i in enumerate(b):
        if i == "1":
            result += 2 ** (bitlen - index - 1)

    return result
