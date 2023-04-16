# How pypdf writes PDF files

pypdf uses {py:class}`PdfWriter <pypdf.PdfWriter>` to write PDF files. pypdf has
{py:class}`PdfObject <pypdf.generic.PdfObject>` and several subclasses with the
`write_to_stream` method. The {py:class}`PdfWriter.write <pypdf.PdfWriter.write>`
method uses the `write_to_stream` methods of the referenced objects.

The `PdfWriter.write_stream` function has the following core steps:

1. `_sweep_indirect_references`
2. `_write_pdf_structure`: In this step, the PDF header and objects are written
   to the output stream. This includes the PDF version (e.g., %PDF-1.7) and the
   objects that make up the content of the PDF, such as pages, annotations, and
   form fields. The locations (byte offsets) of these objects are stored for
   later use in generating the xref table.
3. `_write_xref_table`: Using the stored object locations, this step generates
   and writes the cross-reference table (xref table) to the output stream. The
   xref table contains the byte offsets for each object in the PDF file,
   allowing for quick random access to objects when reading the PDF.
4. `_write_trailer`: The trailer is written to the output stream in this step.
   The trailer contains essential information, such as the number of objects in
   the PDF, the location of the root object (Catalog), and the Info object
   containing metadata. The trailer also specifies the location of the xref
   table.
