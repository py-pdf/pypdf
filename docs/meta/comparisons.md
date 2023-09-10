# pypdf vs X

pypdf is a [free] and open source pure-python PDF library capable of
splitting, merging, cropping, and transforming the pages of PDF files.
It can also add custom data, viewing options, and passwords to PDF
files. pypdf can retrieve text and metadata from PDFs as well.

## PyMuPDF and PikePDF

[PyMuPDF] is a Python binding to [MuPDF] and [PikePDF] is the Python
binding to [QPDF].

While both are excellent libraries for various use-cases, using them is
not always possible even when they support the use-case. Both of them
are powered by C libraries which makes installation harder and might
cause security concerns. For MuPDF you might also need to buy a
commercial license.

A core feature of pypdf is that it's pure Python. That means there is
no C dependency. It has been used for over 10 years and for this reason
a lot of support via StackOverflow and examples on the internet.

## pypdf

PyPDF2 was merged back into `pypdf`. The development continues at `pypdf`.

## PyPDF3 and PyPDF4

Developing and maintaining open source software is extremely
time-intensive and in the case of pypdf not paid at all. Having a
continuous support is hard.

pypdf was initially released in 2012 on PyPI and received releases
until 2016. From 2016 to 2022 there was no update - but people were
still using it.

As pypdf is free software, there were attempts to fork it and continue
the development. PyPDF3 was first released in 2018 and still receives
updates. PyPDF4 has only one release from 2018.

I (Martin Thoma, the current maintainer of pypdf and PyPDF2), hope that we can
bring the community back to one path of development. I deprecated PyPDF2 in
favor of pypdf already and pypdf has now more features and a cleaner interface
than PyPDF2. See [history of pypdf](history.md).

  [free]: https://en.wikipedia.org/wiki/Free_software
  [PyMuPDF]: https://pypi.org/project/PyMuPDF/
  [MuPDF]: https://mupdf.com/
  [PikePDF]: https://pypi.org/project/pikepdf/
  [QPDF]: https://github.com/qpdf/qpdf


## pdfminer.six and pdfplumber

[`pdfminer.six`](https://pypi.org/project/pdfminer.six/) is capable of
extracting the [font size](https://stackoverflow.com/a/69962459/562769)
/ font weight (bold-ness). It has no capabilities for writing PDF files.

[`pdfplumber`](https://pypi.org/project/pdfplumber/) is a library focused on extracting data from PDF documents. Since `pdfplumber` is built on top of `pdfminer.six`, there are **no capabilities of exporting or modifying a PDF file** (see [#440 (discussions)](https://github.com/jsvine/pdfplumber/discussions/440#discussioncomment-803880)). However, `pdfplumber` is capable of converting a PDF file into an image, [draw lines and rectangles on the image](https://github.com/jsvine/pdfplumber#drawing-methods), and save it as an image file. Please note that the image conversion is done via ImageMagick (see [`pdfplumber`'s documentation](https://github.com/jsvine/pdfplumber#visual-debugging)).

The `pdfplumber` community is active in answering questions and the library is maintained as of May 2023.

## pdfrw / pdfrw2

I don't have experience with any of those libraries. Please add a
comparison if you know pypdf and [`pdfrw`](https://pypi.org/project/pdfrw/)!

Please be aware that there is also
[`pdfminer`](https://pypi.org/project/pdfminer/) which is not maintained.
Then there is [`pdfrw2`](https://pypi.org/project/pdfrw2/) which doesn't have
a large community behind it.

## Document Generation

There are (Python) [tools to generate PDF documents](https://github.com/py-pdf/awesome-pdf#generators).
pypdf is not one of them.


## CLI applications

pypdf is a pure Python PDF library. If you're looking for an application which
you can use from the terminal, give [`pdfly`](https://pdfly.readthedocs.io/en/latest/)
a shot.
