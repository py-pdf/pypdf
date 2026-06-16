The PageObject Class
--------------------

.. autoclass:: pypdf._page.PageObject
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf._page.VirtualListImages
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf._page.ImageFile
    :members:
    :inherited-members: File
    :undoc-members:

   .. rubric:: Lazy-loaded properties

   The following properties decode the image stream on first access.
   Accessing them for the first time may be expensive for large images.

   .. autoproperty:: pypdf._page.ImageFile.data
   .. autoproperty:: pypdf._page.ImageFile.image

   .. rubric:: Stream header properties

   The following properties are read directly from the PDF stream header
   and are always cheap to access — they do **not** decode the image data.

   .. autoproperty:: pypdf._page.ImageFile.width
   .. autoproperty:: pypdf._page.ImageFile.height
   .. autoproperty:: pypdf._page.ImageFile.data_size

.. autofunction:: pypdf.mult