"""
Create a booklet-style PDF from a single input.

Pairs of two pages will be put on one page (left and right)

usage: python 2-up.py input_file output_file
"""

import sys

from PyPDF2 import PdfReader, PdfWriter


def main():
    if len(sys.argv) != 3:
        print("usage: python 2-up.py input_file output_file")
        sys.exit(1)
    print("2-up input " + sys.argv[1])
    reader = PdfReader(sys.argv[1])
    writer = PdfWriter()
    for iter in range(0, reader.numPages - 1, 2):
        lhs = reader._get_page(iter)
        rhs = reader._get_page(iter + 1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(), 0, True)
        writer.add_page(lhs)
        print(str(iter) + " "),
        sys.stdout.flush()

    print("writing " + sys.argv[2])
    with open(sys.argv[2], "wb") as fp:
        writer.write(fp)
    print("done.")


if __name__ == "__main__":
    main()
