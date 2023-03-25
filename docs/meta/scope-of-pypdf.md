# Scope of pypdf

What features should pypdf have and which features will it never have?

pypdf aims at making interactions with PDF documents simpler. Core tasks that
pypdf can perform are:

* Document manipulation: Splitting, merging, cropping, and transforming the pages of PDF files
* Data Extraction: Extract text and metadata from PDF documents
* Security: Decrypt / encrypt PDF documents

Typical indicators that something should be done by pypdf:

* The task needs in-depth knowledge of the PDF format
* It currently requires a lot of code or even is impossible to do with pypdf
* It's neither mentioned in "belongs in user code" nor in "out of scope"
* It already is in the issue list with the [is-feature tag](https://github.com/py-pdf/pypdf/labels/is-feature).

## Belongs in user code

Here are a few indicators that a feature belongs into users code (and not into pypdf):

1. The use-case is very specific. Most people will not encounter the same need.
2. It can be done without knowledge of the PDF specification
3. It cannot be done without (non-pdf) domain knowledge. Anything that is
   specific to your industry.

## Out of scope

While this list is infinitely long, there are a few topics that are asked
multiple times.

Those topics are out of scope for pypdf. They will never be part of pypdf:

1. **Optical Character Recognition (OCR)**: OCR is about extracting text from
   images. That is very different from the kind of text extraction pypdf is
   doing. Please note that images can be within PDF documents. In the case of
   scanned documents, the whole page is an image. Some scanners automatically
   execute OCR and add a text-layer behind the scanned page. That is something
   pypdf can use, if it's present. As a rule-of-thumb: If you cannot mark/copy
   the text, it's likely an image. A noteworthy open source OCR project is
   [tesseract](https://github.com/tesseract-ocr/tesseract).
2. **Format Conversion**: Converting docx / HTML to PDF or PDF to those formats.
   You might want to have a look at [`pdfkit`](https://pypi.org/project/pdfkit/)
   and similar projects.

Out of scope for the moment, but might be added if there are enough contributors:

* **Digital Signature Support** ([reference
  ticket](https://github.com/py-pdf/pypdf/issues/302)): Cryptography is
  complicated. It's important to get it right. pypdf currently doesn't have
  enough active contributors to properly add digital signautre support. For the
  moment, [pyhanko](https://pypi.org/project/pyHanko/) seems to be the best
  choice.
* **PDF Generation from Scratch**: pypdf can manipulate existing PDF documents,
  add annotations, combine / split / crop / transform. It can add blank pages.
  But if you want to generate invoices, you might want to have a look at
  [`reportlab`](https://pypi.org/project/reportlab/) /
  [`fpdf2`](https://pypi.org/project/fpdf2/) or document conversion tools like
  [`pdfkit`](https://pypi.org/project/pdfkit/).
* **Replacing words within a PDF**: [Extracting text from PDF is hard](https://pypdf.readthedocs.io/en/stable/user/extract-text.html#why-text-extraction-is-hard).
   Replacing text in a reliable way is even harder.
