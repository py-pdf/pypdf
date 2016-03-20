from PyPDF2 import PdfFileMerger

# initiate a PdfFileMerger object in memory
merger = PdfFileMerger()

# remember to open files in READ-BINARY mode only
input1 = open("document1.pdf", "rb")
input2 = open("document2.pdf", "rb")
input3 = open("document3.pdf", "rb")

# with clause to ensure proper closing of file handles
with input1, input2, input3:
	# reading from input1 (i.e. document1.pdf) add the first 3 pages to the
	# merger object
	merger.append(fileobj = input1, pages = (0,3))

	# at position = 2 (beginning after the second page), reading from input2
	# insert the first 1 pages
	merger.merge(position = 2, fileobj = input2, pages = (0,1))
	# NOTE: the use of 'merge' method of PdfFileMerger when position of
	# document to be inserted is not the end

	# append entire input3 document at the end of merger object
	merger.append(input3)

# Write merger object to an output PDF document
with open("document-output.pdf", "wb") as outputFile:
	merger.write(outputFile)
