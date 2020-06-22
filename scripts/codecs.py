#!/usr/bin/env python3
# TO-DO Add license notice
"""
Encodes/decodes data fed from the command line with PyPDF codecs.

Although PyPDF4 mandates Python 2 support as well, only Python 3 is supported
by this script.
"""
import argparse
from os.path import abspath, dirname, join, pardir
from sys import exit, path, stderr

from pypdf.filters import *

PROJECT_ROOT = abspath(join(dirname(__file__), pardir))
path.append(PROJECT_ROOT)


__version__ = "0.3.0"
CODECS = {
    "flate": FlateCodec,
    "asciihex": ASCIIHexCodec,
    "lzw": LZWCodec,
    "ascii85": ASCII85Codec,
    "dct": DCTCodec,
    "jpx": JPXCodec,
    "ccittfax": CCITTFaxCodec,
}

ENCODE, DECODE, LIST = ("encode", "decode", "list")
CODEC_ACTIONS = (ENCODE, DECODE)
VIEW_ACTIONS = (LIST,)


def main():
    """
    :return: exit status of program (``0`` with no errors, ``1`` with a generic
        error).
    """
    parser = argparse.ArgumentParser(
        description="Encodes/decodes some data fed in with PyPDF codecs",
        epilog="Version %s" % __version__,
    )
    subparsers = parser.add_subparsers(title="Commands", dest="action")
    codec_parser = subparsers.add_parser(
        ENCODE, aliases=(DECODE,), help="Encode/decode data"
    )
    _list_parser = subparsers.add_parser(LIST, help="List available codecs")

    subparsers.required = True
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    codec_parser.add_argument("data", help="Data to either encode or decode")
    # TO-DO Add chained list of encoders/decoders support (like
    # ASCIIHexDecode(LZWDecode(data))).
    codec_parser.add_argument(
        "-c",
        "--codec",
        choices=CODECS.keys(),
        required=True,
        help="The codec to encode/decode with",
    )
    codec_parser.add_argument(
        "-f",
        "--file",
        dest="isfile",
        action="store_const",
        const=True,
        help="Whether the argument provided to DATA should be interpreted as a"
        " file path",
    )

    args = parser.parse_args()

    # TO-DO Find a proper way of writing bytes directly to the console (perhaps
    # throught bytes streams?). Decoded byte strings are not enough reliable.
    if args.action in CODEC_ACTIONS:
        codec = CODECS[args.codec]

        if args.isfile:
            try:
                with open(args.data, "rb") as instream:
                    data = instream.read()
            except IOError as e:
                print(e, file=stderr)
                return 1
        else:
            data = args.data.encode("LATIN1")

        if args.action == ENCODE:
            data = codec.encode(data)
        elif args.action == DECODE:
            data = codec.decode(data)

        if isinstance(data, bytes):
            data = data.decode("LATIN1")

        print(data)
    elif args.action == LIST:
        print("Available codecs:", *CODECS.keys(), sep="\n\t")
    else:
        print("Unrecognized action", args.action, file=stderr)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
