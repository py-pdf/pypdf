The PaperSize Class
-------------------

.. autoclass:: pypdf.PaperSize
    :members:
    :undoc-members:
    :show-inheritance:

Add blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. testsetup ::

    pypdf_test_setup("modules/PaperSize", {
        "example.pdf": "../resources/example.pdf",
    })

.. testcode ::

    from pypdf import PaperSize, PdfWriter

    writer = PdfWriter(clone_from="example.pdf")
    writer.add_blank_page(PaperSize.A8.width, PaperSize.A8.height)
    writer.write("out-1-add-page.pdf")

Insert blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. testcode ::

    from pypdf import PaperSize, PdfWriter

    writer = PdfWriter(clone_from="example.pdf")
    writer.insert_blank_page(PaperSize.A8.width, PaperSize.A8.height, 1)
    writer.write("out-2-insert-page.pdf")
