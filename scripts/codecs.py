"""
Encodes/decodes data fed from the command line with PyPDF codecs.
"""
import argparse

from sys import argv, path, stderr
from os.path import abspath, dirname, join, pardir

PROJECT_ROOT = abspath(
    join(dirname(__file__), pardir)
)
path.append(PROJECT_ROOT)

from pypdf4.filters import *

__version__ = "0.1.0"
CODECS = {
    "flate": FlateCodec, "asciihex": ASCIIHexCodec, "lzw": LZWCodec,
    "ascii85": ASCII85Codec, "dct": DCTCodec, "jpx": JPXCodec,
    "ccittfax": CCITTFaxCodec
}
# TO-DO Add a list command
ENCODE, DECODE = ("encode", "decode")
ACTIONS = (ENCODE, DECODE)


def main():
    parser = argparse.ArgumentParser(
        description="Encodes/decodes some data fed in with PyPDF codecs",
        epilog="Version %s" % __version__
    )

    # When not specified, the default action= keyword is "store"
    parser.add_argument(
        "action", choices=ACTIONS, help="The action to perform"
    )
    parser.add_argument("data", help="Data to either encode or decode")
    parser.add_argument(
        "-f", "--file", dest="isfile", action="store_const", const=True,
        help="Whether the argument provided to DATA should be interpreted as a"
        " file path"
    )
    parser.add_argument(
        "-c", "--codec", choices=CODECS.keys(), required=True,
        help="The codec to encode/decode with"
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    args = parser.parse_args()
    codec = CODECS[args.codec]

    if args.isfile:
        try:
            with open(args.data, "rb") as infile:
                data = infile.read()
        except IOError as e:
            print(e, file=stderr)
            exit(1)
    else:
        data = args.data.encode("LATIN1")

    # TO-DO If the output is in bytes form, strip the b'' characters from the
    # output
    if args.action == ENCODE:
        print(codec.encode(data))
    elif args.action == DECODE:
        print(codec.decode(data))
    else:
        print("Unsupported action %s" % args.action, file=stderr)
        exit(1)


if __name__ == "__main__":
    main()
