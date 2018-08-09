from PyPDF3 import PdfFileMerger

merger = PdfFileMerger()

input1 = open("document1.pdf", "rb")
input2 = open("document2.pdf", "rb")
input3 = open("document3.pdf", "rb")

# add the first 3 pages of input1 document to output
merger.append(fileobj = input1, pages = (0,3))

# insert the first page of input2 into the output beginning after the second page
merger.merge(position = 2, fileobj = input2, pages = (0,1))

# append entire input3 document to the end of the output document
merger.append(input3)

# Write to an output PDF document
output = open("document-output.pdf", "wb")
merger.write(output)
