# How pypdf parses PDF files

pypdf uses {py:class}`PdfReader <pypdf.PdfReader>` to parse PDF files.
The method {py:meth}`PdfReader.reader <pypdf.PdfReader.reader>` shows the basic
structure of parsing:

1. **Finding and reading the cross-reference tables / trailer**: The
   cross-reference table (xref table) is a table of byte offsets that indicate
   the locations of objects within the file. The trailer provides additional
   information such as the root object (Catalog) and the Info object containing
   metadata.
2. **Parsing the objects**: After locating the xref table and the trailer, pypdf
   proceeds to parse the objects in the PDF. Objects in a PDF can be of various
   types such as dictionaries, arrays, streams, and simple data types (e.g.,
   integers, strings). pypdf parses these objects and stores them in
   {py:meth}`PdfReader.resolved_objects <pypdf.PdfReader.resolved_objects>`
   via {py:meth}`cache_indirect_object <pypdf.PdfReader.cache_indirect_object>`.
3. **Decoding content streams**: The content of a PDF is typically stored in
   content streams (see "7.8 Content Streams and Resources" in the PDF
   specification), which are sequences of PDF operators and operands. pypdf
   decodes these content streams by applying filters (e.g., FlateDecode,
   LZWDecode) specified in the stream's dictionary. This is only done when the
   object is requested via {py:meth}`PdfReader.get_object
   <pypdf.PdfReader.get_object>` in the
   {py:meth}`PdfReader._get_object_from_stream
   <pypdf.PdfReader._get_object_from_stream>` method.
