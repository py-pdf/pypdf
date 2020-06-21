#!/usr/bin/python3
"""
   test/demo program that copy alll comments from multiples pdf into one command line:
   PDFCommentsMerge [-d] [-o output.pdf] [input1.pdf] ... [inputN.pdf]
   -d: open Excel output at the end of extraction
   -o: prode the output Excel name/path ; if not present the file is created
       in temp folder named "FullCommented **input1**.pdf"
    if no parameters (mainly for idle test), the pdf filenames re asked for
    empty to finish
"""
import sys
import os
import pypdf as PDF;
    

if sys.argv[0].upper().find("PYTHON.EXE")>=0:
    del sys.argv[0]
del sys.argv[0] # to ignore called program

displayOutput=('-d' in sys.argv) or ('idlelib.run' in sys.modules)
try:
    del sys.argv[sys.argv.index('-d')]
except:
    pass


if (len(sys.argv)==0) or (('-o' in sys.argv) and (len(sys.argv)<=2)) :
    print(globals()['__doc__'])
    while True:
        t=input("pdf file to scan:")
        if t=='':break
        sys.argv.append(t)

if '-o' in sys.argv:
    i=sys.argv.index('-o')
    outFile=sys.argv[i+1]
    del sys.argv[i]
    del sys.argv[i]
else:
    tempFolder=os.environ['TEMP'].replace('\\','/')
    if tempFolder[-1]!='/' : tempFolder+='/'
    outFile=tempFolder+"FullCommented "+os.path.splitext(os.path.split(sys.argv[0])[-1])[0]+'.pdf'

pdfO=PDF.PdfFileWriter(None,PDF.PdfFileReader(sys.argv[0]))
del sys.argv[0]

pdfS=[]
for f in sys.argv:
    pdfS.append(PDF.PdfFileReader(f))
    #check if decryption is required ; normally not required
    if pdfS[-1].isEncrypted: pdfS[-1].decrypt('')

#we assume that all the documents are commenting the same original document
for i in range(pdfO.numPages):
    po=pdfO.getPage(i)
    for pdfin in pdfS:
        pdfO.addCommentsFromPage(i,pdfin.getPage(i))

pdfO.write(outFile)
if displayOutput:
    os.startfile(outFile)
