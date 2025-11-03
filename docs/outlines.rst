=========================
Working with Outlines
=========================

Outlines (also known as bookmarks) are used to create a clickable table of contents in a PDF.

Reading outlines
-----------------
.. code-block:: python

    from pypdf import PdfReader

    reader = PdfReader("example.pdf")
    outlines = reader.outline
    for item in outlines:
        print(item)

Adding outlines
----------------
.. code-block:: python

    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_outline_item("My First Page", 0)
    writer.write("output.pdf")
