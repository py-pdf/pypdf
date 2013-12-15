from PyPDF2 import PdfFileWriter, PdfFileReader
import sys
import math

def main():
    print ("2-up on " + sys.argv[1])
    input1 = PdfFileReader(open(sys.argv[1], "rb"))
    output = PdfFileWriter()
    for iter in range (0, input1.getNumPages()-1, 2):
        lhs = input1.getPage(iter)
        rhs = input1.getPage(iter+1)
        lhs.mergeTranslatedPage(rhs, lhs.mediaBox.getUpperRight_x(),0, True)
        output.addPage(lhs)
        print (str(iter) + " "),
        sys.stdout.flush()

    # print(" imposed array: " + str(pagesInOrder))
    print("writing file")
    outputStream = file(sys.argv[2], "wb")
    output.write(outputStream)
    print("done.")

if __name__ == "__main__":
    main()


