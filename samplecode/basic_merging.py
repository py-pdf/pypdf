from pypdf4 import PdfFileMerger

merger = PdfFileMerger()

# Make it dependent on makesimple.py, so as to not manually create .pdf
# files
input1 = open("simple1.pdf", "rb")
input2 = open("simple2.pdf", "rb")
input3 = open("simple3.pdf", "rb")

# Add the first 3 pages of input1 document to output
merger.append(fileobj=input1, pages=(0, 3))

# Insert the first page of input2 into the output beginning after the second
# page
merger.merge(position=2, fileobj=input2, pages=(0, 1))

# Append entire input3 document to the end of the output document
merger.append(input3)

# Write to an output PDF document
output = open("MergedPDF.pdf", "wb")
merger.write(output)
