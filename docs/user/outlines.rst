==============================
Working with PDF outlines (bookmarks)
==============================

PDF outlines (also called *bookmarks*) provide a navigation structure in PDF viewers.
They appear in the left sidebar and allow users to jump to different sections of the document.

pypdf allows you to:

- Add outline items (bookmarks)
- Nest outline items (parent → child hierarchy)
- Read existing outlines from PDFs

------------------------------------
Adding outline items (bookmarks)
------------------------------------

.. note::

   Page numbers in pypdf are **zero-based**.  
   The first page is ``page_number=0``.

.. warning::

   If you reference a page that does not exist
   (e.g., ``page_number=5`` in a 3-page PDF),
   pypdf will raise ``IndexError``.

.. code-block:: python

    from pypdf import PdfReader, PdfWriter

    reader = PdfReader("input.pdf")
    writer = PdfWriter()

    # Copy pages to the writer
    for page in reader.pages:
        writer.add_page(page)

    # Add bookmarks (outline items)
    writer.add_outline_item("Chapter 1 - Introduction", page_number=0)
    writer.add_outline_item("Chapter 2 - Methods", page_number=2)
    writer.add_outline_item("Appendix", page_number=5)

    with open("output_with_outlines.pdf", "wb") as f:
        writer.write(f)

After saving, the bookmarks will appear in the sidebar of PDF viewers such as
Chrome, Adobe Reader, and other PDF apps.

------------------------------------
Nested outline items
------------------------------------

You can create outline items under a parent outline item (bookmark hierarchy).

.. code-block:: python

    from pypdf import PdfReader, PdfWriter

    reader = PdfReader("input.pdf")
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Parent outline item
    parent = writer.add_outline_item("Main Topic", page_number=0)

    # Nested outline items under the parent
    writer.add_outline_item("Section A", page_number=1, parent=parent)
    writer.add_outline_item("Section B", page_number=3, parent=parent)

    with open("nested_outline.pdf", "wb") as f:
        writer.write(f)

------------------------------------
Reading existing outlines (simple)
------------------------------------

Use this approach if your PDF has non-nested bookmarks.

.. code-block:: python

    from pypdf import PdfReader

    reader = PdfReader("output_with_outlines.pdf")

    for outline in reader.outline:
        page_num = reader.get_destination_page_number(outline)
        print(f"{outline.title} -> page {page_num + 1}")

------------------------------------
Reading nested outlines (advanced)
------------------------------------

Use this version if your PDF contains nested bookmarks.  
This prints indentation depending on nesting depth.

.. code-block:: python

    from pypdf import PdfReader

    def print_outline(outlines, level=0):
        """Recursively print outline items."""
        for item in outlines:
            if isinstance(item, list):  # nested items
                print_outline(item, level + 1)
            else:
                page_num = reader.get_destination_page_number(item)
                indent = "  " * level
                print(f"{indent}- {item.title} -> page {page_num + 1}")

    reader = PdfReader("output_with_outlines.pdf")
    print_outline(reader.outline)

------------------------------------
API Reference Links
------------------------------------

- :class:`~pypdf.PdfWriter`
- :meth:`~pypdf.PdfWriter.add_outline_item`
- :class:`~pypdf.PdfReader`
- :attr:`~pypdf.PdfReader.outline`
