The PaperSize Class
-------------------

.. autoclass:: pypdf.PaperSize
    :members:
    :undoc-members:
    :show-inheritance:

add blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python
    :linenos:

    from PyPDF2 import PaperSize, PdfReader, PdfWriter  
    pdf_reader = PdfReader("sample.pdf")
    pdf_writer = PdfWriter()
    pdf_writer.append_pages_from_reader(pdf_reader)
    pdf_writer.add_blank_page(PaperSize.A8.width, PaperSize.A8.height)
    with open("output.pdf", "wb") as output_stream:
        pdf_writer.write(output_stream)

insert blank page with PaperSize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python
    :linenos:
    
    from PyPDF2 import PaperSize, PdfReader, PdfWriter  
    pdf_reader = PdfReader("sample.pdf")
    pdf_writer = PdfWriter()
    pdf_writer.append_pages_from_reader(pdf_reader)
    pdf_writer.insert_blank_page(PaperSize.A8.width, PaperSize.A8.height, 1)
    with open("output.pdf", "wb") as output_stream:
        pdf_writer.write(output_stream)
    