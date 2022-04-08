[![PyPI version](https://badge.fury.io/py/PyPDF2.svg)](https://badge.fury.io/py/PyPDF2)
[![Python Support](https://img.shields.io/pypi/pyversions/PyPDF2.svg)](https://pypi.org/project/PyPDF2/)
[![](https://img.shields.io/badge/-documentation-green)](https://pythonhosted.org/PyPDF2/)
![GitHub last commit](https://img.shields.io/github/last-commit/py-pdf/PyPDF2)

# PyPDF2

PyPDF2 is a pure-python PDF library capable of
splitting, merging together, cropping, and transforming
the pages of PDF files. It can also add custom
data, viewing options, and passwords to PDF files.
It can retrieve text and metadata from PDFs as well
as merge entire files together.

[Homepage](http://py-pdf.github.io/PyPDF2/)



## Installation

To install via pip:

```
pip install PyPDF2
```

## Examples

Please see the `Sample_Code` folder.

## FAQ

A lot of questions are asked [on StackOverflow](https://stackoverflow.com/questions/tagged/pypdf2).

## Contributions

Maintaining PyPDF2 is a collaborative effort. You can support PyPDF2 by writing
documentation, helping to narrow down issues, and adding code.


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
$ pytest .
============================= test session starts ==============================
platform linux -- Python 3.10.2, pytest-7.0.1, pluggy-1.0.0
rootdir: /home/moose/Github/PyPDF2
plugins: mccabe-2.0, icdiff-0.5, cov-3.0.0, timeout-2.1.0
collected 29 items

Tests/test_basic_features.py .                                           [  3%]
Tests/test_merger.py .                                                   [  6%]
Tests/test_reader.py .........                                           [ 37%]
Tests/test_utils.py .....                                                [ 55%]
Tests/test_workflows.py ...........                                      [ 93%]
Tests/test_xmp.py ..                                                     [100%]

============================== 29 passed in 0.29s ==============================
```
