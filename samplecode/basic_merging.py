#!/usr/bin/env python
"""
Merges three PDF documents input from the command line.
"""
from __future__ import print_function

from os import pardir
from sys import argv, path

from os.path import abspath, dirname, join

SAMPLE_CODE_ROOT = dirname(__file__)
SAMPLE_PDF_ROOT = join(SAMPLE_CODE_ROOT, "pdfsamples")

path.append(
    abspath(join(SAMPLE_CODE_ROOT, pardir))
)

from pypdf4 import PdfFileReader, PdfFileMerger

FLAG_HELP = {"-h", "--help"}
USAGE = """\
Merges three PDF documents input from the command line.

%(progname)s: <PDF 1> <PDF 2> <PDF 3> [output filename]
%(progname)s: [-h | --help]
""" % {"progname": argv[0]}


def main():
    requiredPages = 3
    output = "PyPDF-Merging-Output.pdf"

    if set(argv) & FLAG_HELP:
        print(USAGE)
        exit(0)
    elif len(argv) < 4:
        print(USAGE)
        exit(1)
    else:
        files = [f.strip() for f in argv[1:4]]

        if len(argv) > 4:
            output = argv[4].strip()

    reader1 = PdfFileReader(files[0])
    merger = PdfFileMerger()

    if reader1.numPages < requiredPages:
        print(
            "File 1 requires %d pages, but it has just %d" %
            (requiredPages, reader1.numPages)
        )
        exit(1)

    input1 = open(files[0], "rb")
    input2 = open(files[1], "rb")
    input3 = open(files[2], "rb")

    # Add the first 3 pages of input1 to output
    merger.append(fileobj=input1, pages=(0, 3))

    # Insert the first page of input2 into the output beginning after the
    # second page
    merger.merge(position=2, fileobj=input2, pages=(0, 1))

    # Append entire input3 document to the end of the output document
    merger.append(input3)

    # Write to an output PDF document
    with open(output, "wb") as outputStream:
        merger.write(outputStream)

    print("Output successfully written to", output)


if __name__ == "__main__":
    main()
