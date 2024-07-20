# Frequently Asked Questions

## How is pypdf related to PyPDF2?

PyPDF2 was a fork from the original pyPdf. After several years, the fork was
merged back into `pypdf` (now all lowercase).

## Which Python versions are supported?

pypdf 3.0+ supports Python 3.6 and later.
PyPDF2 2.0+ supports Python 3.6 and later.
PyPDF2 1.27.10 supported Python 2.7 to 3.10.

  [Matthew]: https://github.com/mstamy2
  [source]: https://github.com/py-pdf/PyPDF2/commit/24b270d876518d15773224b5d0d6c2206db29f64#commitcomment-5038317
  [this sort of thing]: https://github.com/py-pdf/PyPDF2/issues/24
  [GitHub issue]: https://github.com/py-pdf/PyPDF2/issues

## Who uses pypdf?

pyPdf is vendored [into](https://github.com/Buyanbat/XacCRM/tree/ee78e8df967182f661b6494a86444501e7d89c8f/report/pyPdf) [several](https://github.com/MyBook/calibre/tree/ca1efe3c21f6553e096dab745b3cdeb36244a5a9/src/pyPdf) [projects](https://github.com/Giacomo-De-Florio-Dev/Make_Your_PDF_Safe/tree/ec439f92243d12d54ae024668792470c6b40ee96/MakeYourPDFsafe_V1.3/PyPDF2). That
means the code of pyPdf was copied into that project.

Projects that depend on pypdf:

* [Camelot](https://github.com/camelot-dev/camelot): A Python library to extract tabular data from PDFs
* [edi](https://github.com/OCA/edi): Electronic Data Interchange modules
* [amazon-textract-textractor](https://github.com/aws-samples/amazon-textract-textractor/blob/42444b08c672607eadbdcd64f3c5adb2d85383de/helper/setup.py): Analyze documents with Amazon Textract and generate output in multiple formats.
* [maigret](https://github.com/soxoj/maigret): Collect a dossier on a person by username from thousands of sites
* [deda](https://github.com/dfd-tud/deda): tracking Dots Extraction, Decoding and Anonymisation toolkit
* [opencanary](https://github.com/thinkst/opencanary)
* Document Conversions
  * [rst2pdf](https://github.com/rst2pdf/rst2pdf)
  * [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf)
  * [doc2text](https://github.com/jlsutherland/doc2text)
* [pdfalyzer](https://pypi.org/project/pdfalyzer/): A PDF analysis tool for visualizing the inner tree-like data structure of a PDF in spectacularly large and colorful diagrams as well as scanning the binary streams embedded in the PDF for hidden potentially malicious content.

## How do I cite pypdf?

In BibTeX format:

```
@misc{pypdf,
 title         = {The {pypdf} library},
 author        = {Mathieu Fenniak and
                  Matthew Stamy and
                  pubpub-zz and
                  Martin Thoma and
                  Matthew Peveler and
                  exiledkingcc and {pypdf Contributors}},
 year          = {2024},
 url           = {https://pypi.org/project/pypdf/}
 note          = {See https://pypdf.readthedocs.io/en/latest/meta/CONTRIBUTORS.html for all contributors}
}
```

## Which License does pypdf use?

`pypdf` uses the [BSD-3-Clause license](https://en.wikipedia.org/wiki/BSD_licenses#3-clause), see the LICENSE file.
