.. pypdf documentation main file, created by
   sphinx-quickstart on Thu Apr  7 20:13:19 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pypdf
=================

pypdf is a `free <https://en.wikipedia.org/wiki/Free_software>`_ and open
source pure-python PDF library capable of splitting,
merging, cropping, and transforming the pages of PDF files. It can also add
custom data, viewing options, and passwords to PDF files.
pypdf can retrieve text and metadata from PDFs as well.

See `pdfly <https://github.com/py-pdf/pdfly>`_ for a CLI application that uses pypdf to interact with PDFs.

You can contribute to `pypdf on GitHub <https://github.com/py-pdf/pypdf>`_.

.. toctree::
   :caption: User Guide
   :maxdepth: 1

   user/installation
   user/migration-1-to-2
   user/robustness
   user/suppress-warnings
   user/metadata
   user/extract-text
   user/post-processing-in-text-extraction
   user/extract-images
   user/extract-attachments
   user/encryption-decryption
   user/merging-pdfs
   user/cropping-and-transforming
   user/reading-pdf-annotations
   user/adding-pdf-annotations
   user/add-watermark
   user/add-javascript
   user/viewer-preferences
   user/forms
   user/streaming-data
   user/file-size
   user/pdf-version-support
   user/pdfa-compliance


.. toctree::
   :caption: API Reference
   :maxdepth: 1

   modules/PdfReader
   modules/PdfWriter
   modules/Destination
   modules/DocumentInformation
   modules/Field
   modules/Fit
   modules/PageObject
   modules/PageRange
   modules/PaperSize
   modules/RectangleObject
   modules/Transformation
   modules/XmpInformation
   modules/annotations
   modules/constants
   modules/errors
   modules/generic
   modules/PdfDocCommon

.. toctree::
   :caption: Developer Guide
   :maxdepth: 1

   dev/intro
   dev/pdf-format
   dev/pypdf-parsing
   dev/pypdf-writing
   dev/cmaps
   dev/deprecations
   dev/documentation
   dev/testing
   dev/releasing

.. toctree::
   :caption: About pypdf
   :maxdepth: 1

   meta/CHANGELOG
   meta/changelog-v1
   meta/project-governance
   meta/taking-ownership
   meta/history
   meta/CONTRIBUTORS
   meta/scope-of-pypdf
   meta/comparisons
   meta/faq

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
