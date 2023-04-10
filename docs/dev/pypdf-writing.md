# How pypdf writes PDF files

pypdf uses {py:class}`PdfWriter <pypdf.PdfWriter>` to write PDF files. pypdf has
{py:class}`PdfObject <pypdf.generic.PdfObject>` and several subclasses with the
`write_to_stream` method. The {py:class}`PdfWriter.write <pypdf.PdfWriter.write>`
method uses the `write_to_stream` methods of the referenced objects.
