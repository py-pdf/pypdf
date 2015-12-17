from PyPDF2 import PdfFileWriter, PdfFileReader
import sys
import math


def main():
    if (len(sys.argv) != 3):
        print("usage: python 2-up.py input_file output_file")
        sys.exit(1)
    print ("2-up input " + sys.argv[1])
    input1 = PdfFileReader(open(sys.argv[1], "rb"))
    output = PdfFileWriter()
    for iter in range (0, input1.getNumPages()-1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter+1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(),0, True)
        output.addPage(lhs)
        print (str(iter) + " "),
        sys.stdout.flush()

    print("writing " + sys.argv[2])
    outputStream = file(sys.argv[2], "wb")
    output.write(outputStream)
    print("done.")

if __name__ == "__main__":
    main()
from PyPDF2 import PdfFileWriter, PdfFileReader
import sys
import math


def main():
    if (len(sys.argv) != 3):
        print("usage: python 2-up.py input_file output_file")
        sys.exit(1)
    print ("2-up input " + sys.argv[1])
    input1 = PdfFileReader(open(sys.argv[1], "rb"))
    output = PdfFileWriter()
    for iter in range (0, input1.getNumPages()-1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter+1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(),0, True)
        output.addPage(lhs)
        print (str(iter) + " "),
        sys.stdout.flush()

    print("writing " + sys.argv[2])
    outputStream = open(sys.argv[2], "wb")
    output.write(outputStream)
    print("done.")

if __name__ == "__main__":
    main()
