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
2. **Write the File Header and Body** with `_write_pdf_structure`: In this step,
   the PDF header and objects are written to the output stream. This includes
   the PDF version (e.g., %PDF-1.7) and the objects that make up the content of
   the PDF, such as pages, annotations, and form fields. The locations (byte
   offsets) of these objects are stored for later use in generating the xref
   table.
3. **Write the Cross-Reference Table** with `_write_xref_table`: Using the stored
   object locations, this step generates and writes the cross-reference table
   (xref table) to the output stream. The cross-reference table contains the
   byte offsets for each object in the PDF file, allowing for quick random
   access to objects when reading the PDF.
4. **Write the File Trailer** with `_write_trailer`: The trailer is written to
   the output stream in this step. The trailer contains essential information,
   such as the number of objects in the PDF, the location of the root object
   (Catalog), and the Info object containing metadata. The trailer also
   specifies the location of the xref table.


## How others do it

Looking at alternative software designs and implementations can help to improve
our choices.

### fpdf2

[fpdf2](https://pypi.org/project/fpdf2/) has a [`PDFObject` class](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py)
with a serialize method which roughly maps to `pypdf.PdfObject.write_to_stream`.
Some other similarities include:

* [fpdf.output.OutputProducer.buffersize](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/output.py#L370-L485) vs {py:meth}`pypdf.PdfWriter.write_stream <pypdf.PdfWriter.write_stream>`
* [fpdpf.syntax.Name](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py#L124) vs {py:class}`pypdf.generic.NameObject <pypdf.generic.NameObject>`
* [fpdf.syntax.build_obj_dict](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/syntax.py#L222) vs {py:class}`pypdf.generic.DictionaryObject <pypdf.generic.DictionaryObject>`
* [fpdf.structure_tree.NumberTree](https://github.com/PyFPDF/fpdf2/blob/master/fpdf/structure_tree.py#L17) vs
 {py:class}`pypdf.generic.TreeObject <pypdf.generic.TreeObject>`


### pdfrw

[pdfrw](https://pypi.org/project/pdfrw/), in contrast, seems to work more with
the standard Python objects (bool, float, string) and not wrap them in custom
objects, if possible. It still has:

* [PdfArray](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/objects/pdfarray.py#L13)
* [PdfDict](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/objects/pdfdict.py#L49)
* [PdfName](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/objects/pdfname.py#L65)
* [PdfString](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/objects/pdfstring.py#L322)
* [PdfIndirect](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/objects/pdfindirect.py#L10)

The core classes of pdfrw are
[PdfReader](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/pdfreader.py#L26)
and
[PdfWriter](https://github.com/pmaupin/pdfrw/blob/master/pdfrw/pdfwriter.py#L224)
