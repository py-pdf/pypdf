PyPDF2 vs X
===========

PyPDF2 was created with the aim to be a strict successor of pyPdf: it did
everything pyPdf did, but more.

PyPDF2 is largely about metadata:
PyPDF2 manages metadata, merges PDF instances, and so on.

PyMuPDF and PikePDF
-------------------
`PyMuPDF <https://pypi.org/project/PyMuPDF/>`__ is a Python binding to
`MuPDF <https://mupdf.com/>`__ and
`PikePDF <https://pypi.org/project/pikepdf/>`__ is the Python binding to
`QPDF <https://github.com/qpdf/qpdf>`_.

While both are excellent libraries for various use-cases, using them is not
always possible even when they support the use-case. Both of them are powered
by C libraries which makes installation harder and might cause security concerns.
For MuPDF you might also need to buy a commercial license.

A core feature of PyPDF2 is that it's pure Python. That means there is no
C dependency. It has been used for over 10 years and for this reason a lot of
support via StackOverflow and examples on the internet.

pyPDF
-----
PyPDF2 was forked from pyPDF. pyPDF has been unmaintained for a long time.

PyPDF3 and PyPDF4
-----------------
Developing and maintaining open source software is extremely time-intensive
and in the case of PyPDF2 not paid at all. Having a continuous support is hard.

PyPDF2 was initially released in 2012 on PyPI and received releases until 2016.
From 2016 to 2022 there was no update - but people were still using it.

As PyPDF2 is open source, there were attempts to fork it and continue the
development. PyPDF3 was first released in 2018 and still receives updates.
PyPDF4 has only one release from 2018.

I, Martin Thoma, the current maintainer of PyPDF2, hope that we can bring the
community back to one path of development. Let's see.
