# PyPDF2 Sample Code Folder

This folder contains demonstrations of just a few of PyPDF2's many features.


## `basic_features.py`

Sample code that demonstrates:

* Getting metadata from a PDF.
* Copying a PDF, one page at a time, and performing different operations on each page (resize, rotate, add a watermark).
* Encrypting a PDF.
* Adding javascript that runs when the PDF is opened.


## `basic_merging.py`

Sample code that demonstrates merging together three PDFs into one, picking and choosing which pages appear in which order.
Selected pages can be added to the end of the output PDF being built, or inserted in the middle.


## `make_simple.py`

Sample code to make a few simple PDF files of various page counts.


## `make_simple.sh`

An example shell script that does the exact same thing as `makesimple.py`,
but by  using the `ps2pdf` script on the command line.


To contribute more...

Feel free to add any type of PDF file or sample code, either by

	1) sending it via email to PyPDF2@phaseit.net
	2) including it in a pull request on GitHub