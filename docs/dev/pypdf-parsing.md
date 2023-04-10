# How pypdf parses PDF files

pypdf uses {py:class}`PdfReader <pypdf.PdfReader>` to parse PDF files.
The method {py:class}`PdfReader.reader <pypdf.PdfReader.reader>` shows the basic
structure of parsing:

1. Finding and reading the xref tables / trailer
2.
