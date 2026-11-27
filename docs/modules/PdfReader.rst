The PdfReader Class
-------------------

.. warning::
   Treat :class:`pypdf.PdfReader` instances as read-only. Some mutating
   operations are available for historical reasons, but they are not
   guaranteed to keep reader state (such as page-number caches) consistent.
   Use :class:`pypdf.PdfWriter` when modifying pages or form fields.

.. autoclass:: pypdf.PdfReader
    :members:
    :inherited-members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pypdf.PasswordType
    :members:
    :undoc-members:
    :show-inheritance:
