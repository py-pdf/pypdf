[![PyPI version](https://badge.fury.io/py/PyPDF2.svg)](https://badge.fury.io/py/PyPDF2)
[![Python Support](https://img.shields.io/pypi/pyversions/PyPDF2.svg)](https://pypi.org/project/PyPDF2/)
[![](https://img.shields.io/badge/-documentation-green)](https://pypdf2.readthedocs.io/en/latest/)
![GitHub last commit](https://img.shields.io/github/last-commit/py-pdf/PyPDF2)
[![codecov](https://codecov.io/gh/py-pdf/PyPDF2/branch/main/graph/badge.svg?token=id42cGNZ5Z)](https://codecov.io/gh/py-pdf/PyPDF2)

# PyPDF2

PyPDF2 is a free and open-source pure-python PDF library capable of splitting,
[merging](https://pypdf2.readthedocs.io/en/latest/user/merging-pdfs.html),
[cropping, and transforming](https://pypdf2.readthedocs.io/en/latest/user/cropping-and-transforming.html)
the pages of PDF files. It can also add
custom data, viewing options, and
[passwords](https://pypdf2.readthedocs.io/en/latest/user/encryption-decryption.html)
to PDF files. PyPDF2 can
[retrieve text](https://pypdf2.readthedocs.io/en/latest/user/extract-text.html)
and
[metadata](https://pypdf2.readthedocs.io/en/latest/user/metadata.html)
from PDFs as well.


## Installation

You can install PyPDF2 via pip:

```
pip install PyPDF2
```

## Usage

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("example.pdf")
number_of_pages = reader.numPages
page = reader.pages[0]
text = page.extractText()
```

PyPDF2 can do a lot more, e.g. splitting, merging, reading and creating
annotations, decrypting and encrypting, and more.

Please see [the documentation](https://pypdf2.readthedocs.io/en/latest/)
and [`Scripts`](https://github.com/py-pdf/PyPDF2/tree/main/Scripts) for
more usage examples!

A lot of questions are asked and answered
[on StackOverflow](https://stackoverflow.com/questions/tagged/pypdf2).

## Contributions

Maintaining PyPDF2 is a collaborative effort. You can support PyPDF2 by writing
documentation, helping to narrow down issues, and adding code.

### Q&A

The experience PyPDF2 users have covers the whole range from beginners who
want to make their live easier to experts who developed software before PDF
existed. You can contribute to the PyPDF2 community by answering questions
on [StackOverflow](https://stackoverflow.com/questions/tagged/pypdf2),
helping in [discussions](https://github.com/py-pdf/PyPDF2/discussions),
and asking users who report issues for [MCVE](https://stackoverflow.com/help/minimal-reproducible-example)'s (Code + example PDF!).


### Issues

A good bug ticket includes a MCVE - a minimal complete verifiable example.
For PyPDF2, this means that you must upload a PDF that causes the bug to occur
as well as the code you're executing with all of the output. Use
`print(PyPDF2.__version__)` to tell us which version you're using.

### Code

All code contributions are welcome, but smaller ones have a better chance to
get included in a timely manner. Adding unit tests for new features or test
cases for bugs you've fixed help us to ensure that the Pull Request (PR) is fine.

PyPDF2 includes a test suite which can be executed with `pytest`:

```bash
$ pytest
========================= test session starts =========================
platform linux -- Python 3.6.15, pytest-7.0.1, pluggy-1.0.0
rootdir: /home/moose/Github/Martin/PyPDF2
plugins: cov-3.0.0
collected 57 items

Tests/test_basic_features.py ..                                 [  3%]
Tests/test_merger.py .                                          [  5%]
Tests/test_page.py .                                            [  7%]
Tests/test_pagerange.py .......                                 [ 19%]
Tests/test_reader.py ..........                                 [ 36%]
Tests/test_utils.py ......................                      [ 75%]
Tests/test_workflows.py ..........                              [ 92%]
Tests/test_writer.py ..                                         [ 96%]
Tests/test_xmp.py ..                                            [100%]

========================= 57 passed in 1.06s ==========================
```
