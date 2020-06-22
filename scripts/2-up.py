from __future__ import print_function

import os
from os.path import abspath, dirname, join
import sys

from pypdf import PdfFileReader, PdfFileWriter

PROJECT_ROOT = abspath(join(dirname(__file__), os.pardir, os.pardir))
sys.path.append(PROJECT_ROOT)


# TO-DO Decide which one of the two halves below to keep
def main():
    if len(sys.argv) != 3:
        print("usage: python 2-up.py input_file output_file")
        sys.exit(1)

    print("2-up input " + sys.argv[1])

    input1 = PdfFileReader(open(sys.argv[1], "rb"))
    output = PdfFileWriter()

    for iter in range(0, input1.numPages - 1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter + 1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(), 0, True)
        output.addPage(lhs)
        print(str(iter) + " "),
        sys.stdout.flush()

    print("writing " + sys.argv[2])
    output_stream = open(sys.argv[2], "wb")
    output.write()
    print("done.")


if __name__ == "__main__":
    main()


def main():
    if len(sys.argv) != 3:
        print("usage: python 2-up.py input_file output_file")
        sys.exit(1)

    print("2-up input " + sys.argv[1])
    input1 = PdfFileReader(open(sys.argv[1], "rb"))
    output = PdfFileWriter()

    for i in range(0, input1.numPages - 1, 2):
        lhs = input1.getPage(i)
        rhs = input1.getPage(i + 1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(), 0, True)
        output.addPage(lhs)
        print(str(i) + " "),
        sys.stdout.flush()

    print("writing " + sys.argv[2])
    output_stream = open(sys.argv[2], "wb")
    output.write()
    print("done.")


if __name__ == "__main__":
    main()
