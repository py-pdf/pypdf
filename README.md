[![PyPI version](https://badge.fury.io/py/pypdf.svg)](https://badge.fury.io/py/pypdf)
[![Python Support](https://img.shields.io/pypi/pyversions/pypdf.svg)](https://pypi.org/project/pypdf/)
[![](https://img.shields.io/badge/-documentation-green)](https://pypdf.readthedocs.io/en/stable/)
[![GitHub last commit](https://img.shields.io/github/last-commit/py-pdf/pypdf)](https://github.com/py-pdf/pypdf)
[![codecov](https://codecov.io/gh/py-pdf/pypdf/branch/main/graph/badge.svg?token=id42cGNZ5Z)](https://codecov.io/gh/py-pdf/pypdf)

# pypdf

pypdf is a free and open-source pure-python PDF library capable of splitting,
[merging](https://pypdf.readthedocs.io/en/stable/user/merging-pdfs.html),
[cropping, and transforming](https://pypdf.readthedocs.io/en/stable/user/cropping-and-transforming.html)
the pages of PDF files. It can also add
custom data, viewing options, and
[passwords](https://pypdf.readthedocs.io/en/stable/user/encryption-decryption.html)
to PDF files. pypdf can
[retrieve text](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
and
[metadata](https://pypdf.readthedocs.io/en/stable/user/metadata.html)
from PDFs as well.

See [pdfly](https://github.com/py-pdf/pdfly) for a CLI application that uses pypdf to interact with PDFs.

## Installation

Install pypdf using pip:

```
pip install pypdf
```

For using pypdf with AES encryption or decryption, install extra dependencies:

```
pip install pypdf[crypto]
```

> **NOTE**: `pypdf` 3.1.0 and above include significant improvements compared to
> previous versions. Please refer to [the migration
> guide](https://pypdf.readthedocs.io/en/latest/user/migration-1-to-2.html) for
> more information.

## Usage

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
```

pypdf can do a lot more, e.g. splitting, merging, reading and creating annotations, decrypting and encrypting. Check out the
[documentation](https://pypdf.readthedocs.io/en/stable/) for additional usage
examples!

For questions and answers, visit
[StackOverflow](https://stackoverflow.com/questions/tagged/pypdf)
(tagged with [pypdf](https://stackoverflow.com/questions/tagged/pypdf)).

## Contributions

Maintaining pypdf is a collaborative effort. You can support the project by
writing documentation, helping to narrow down issues, and submitting code.
See the [CONTRIBUTING.md](https://github.com/py-pdf/pypdf/blob/main/CONTRIBUTING.md) file for more information.

### Q&A

The experience pypdf users have covers the whole range from beginner to expert. You can contribute to the pypdf community by answering questions
on [StackOverflow](https://stackoverflow.com/questions/tagged/pypdf),
helping in [discussions](https://github.com/py-pdf/pypdf/discussions),
and asking users who report issues for [MCVE](https://stackoverflow.com/help/minimal-reproducible-example)'s (Code + example PDF!).


### Issues

A good bug ticket includes a MCVE - a minimal complete verifiable example.
For pypdf, this means that you must upload a PDF that causes the bug to occur
as well as the code you're executing with all of the output. Use
`print(pypdf.__version__)` to tell us which version you're using.

### Code

All code contributions are welcome, but smaller ones have a better chance to
get included in a timely manner. Adding unit tests for new features or test
cases for bugs you've fixed help us to ensure that the Pull Request (PR) is fine.

pypdf includes a test suite which can be executed with `pytest`:

```bash
$ pytest
===================== test session starts =====================
platform linux -- Python 3.6.15, pytest-7.0.1, pluggy-1.0.0
rootdir: /home/moose/GitHub/Martin/pypdf
plugins: cov-3.0.0
collected 233 items

tests/test_basic_features.py ..                         [  0%]
tests/test_constants.py .                               [  1%]
tests/test_filters.py .................x.....           [ 11%]
tests/test_generic.py ................................. [ 25%]
.............                                           [ 30%]
tests/test_javascript.py ..                             [ 31%]
tests/test_merger.py .                                  [ 32%]
tests/test_page.py .........................            [ 42%]
tests/test_pagerange.py ................                [ 49%]
tests/test_papersizes.py ..................             [ 57%]
tests/test_reader.py .................................. [ 72%]
...............                                         [ 78%]
tests/test_utils.py ....................                [ 87%]
tests/test_workflows.py ..........                      [ 91%]
tests/test_writer.py .................                  [ 98%]
tests/test_xmp.py ...                                   [100%]

========== 232 passed, 1 xfailed, 1 warning in 4.52s ==========
```
