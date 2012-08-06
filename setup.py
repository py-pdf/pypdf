#!/usr/bin/env python

from distutils.core import setup
try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py

long_description = """
A Pure-Python library built as a PDF toolkit.  It is capable of:
    
- extracting document information (title, author, ...),
- splitting documents page by page,
- merging documents page by page,
- cropping pages,
- merging multiple pages into a single page,
- encrypting and decrypting PDF files.

By being Pure-Python, it should run on any Python platform without any
dependencies on external libraries.  It can also work entirely on StringIO
objects rather than file streams, allowing for PDF manipulation in memory.
It is therefore a useful tool for websites that manage or manipulate PDFs.
"""

setup(
        name="PyPDF2",
        version="1.15",
        description="PDF toolkit",
        long_description=long_description,
        author="Mathieu Fenniak",
        author_email="biziqe@mathieu.fenniak.net",
        maintainer="Phaseit, Inc.",
        maintainer_email="PyPDF2@phaseit.net",
        url="http://knowah.github.com/PyPDF2",
        download_url="http://github.com/knowah/PyPDF2/tarball/master",
        classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        packages=["PyPDF2"],
        cmdclass = {'build_py': build_py},
    )

