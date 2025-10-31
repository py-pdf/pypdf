The PaperSize Class
-------------------

.. autoclass:: pypdf.PaperSize
    :members:
    :undoc-members:
    :show-inheritance:

Add blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python
    :linenos:

    from pypdf import PaperSize, PdfWriter

    writer = PdfWriter(clone_from="sample.pdf")
    writer.add_blank_page(PaperSize.A8.width, PaperSize.A8.height)
    writer.write("_build/doctest/paper-size-add-page.pdf")

Insert blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python
    :linenos:

    from pypdf import PaperSize, PdfWriter

    writer = PdfWriter(clone_from="sample.pdf")
    writer.insert_blank_page(PaperSize.A8.width, PaperSize.A8.height, 1)
    writer.write("_build/doctest/paper-size-insert-size.pdf")
