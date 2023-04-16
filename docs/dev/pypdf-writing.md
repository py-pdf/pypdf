# How pypdf writes PDF files

pypdf uses {py:class}`PdfWriter <pypdf.PdfWriter>` to write PDF files. pypdf has
{py:class}`PdfObject <pypdf.generic.PdfObject>` and several subclasses with the
{py:meth}`write_to_stream <pypdf.generic.PdfObject.write_to_stream>` method.
The {py:meth}`PdfWriter.write <pypdf.PdfWriter.write>` method uses the
`write_to_stream` methods of the referenced objects.

The {py:meth}`PdfWriter.write_stream <pypdf.PdfWriter.write_stream>` method
has the following core steps:

1. `_sweep_indirect_references`: This step ensures that any circular references
   to objects are correctly handled. It adds the object reference numbers of any
   circularly referenced objects to an external reference map, so that
   self-page-referencing trees can reference the correct new object location,
   rather than copying in a new copy of the page object.
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


## How others do it

[fpdf](https://pypi.org/project/fpdf2/) has a [`PDFObject` class](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py)
with a serialize method which roughly maps to `pypdf.PdfObject.write_to_stream`.
Some other similarities include:

* [fpdf.output.OutputProducer.buffersize](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/output.py#L370-L485) vs {py:meth}`pypdf.PdfWriter.write_stream <pypdf.PdfWriter.write_stream>`
* [fpdpf.syntax.Name](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py#L124) vs {py:class}`pypdf.generic.NameObject <pypdf.generic.NameObject>`
* [fpdf.syntax.build_obj_dict](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py#L222) vs {py:class}`pypdf.generic.DictionaryObject <pypdf.generic.DictionaryObject>`
* [fpdf.structure_tree.NumberTree](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/structure_tree.py#L17) vs
 {py:class}`pypdf.generic.TreeObject <pypdf.generic.TreeObject>`
