# The PDF Format

It's recommended to look in the PDF specification for details and clarifications.
This is only intended to give a very rough overview of the format.

## Overall Structure

A PDF consists of:

1. Header: Contains the version of the PDF, e.g. `%PDF-1.7`
2. Body: Contains a sequence of indirect objects
3. Cross-reference table (xref): Contains a list of the indirect objects in the body
4. Trailer

## The xref table

A cross-reference table (xref) is a table of the indirect objects in the body.
It allows quick access to those objects by pointing to their location in the file.

It looks like this:

```text
xref 42 5
0000001000 65535 f
0000001234 00000 n
0000001987 00000 n
0000011987 00000 n
0000031987 00000 n
```

Let's go through it step-by-step:

* `xref` is justa keyword that specifies the start of the xref table.
* `42` is TODO; `6` is the number of entries in the xref table.
* Now every object has 3 entries `nnnnnnnnnn ggggg n`: The 10-digit byte offset,
  a 5-digit generation number, and a literal keyword which is either `n` or `f`.
    * `nnnnnnnnnn` is the byte offset of the object. It tells the reader where
      the object is in the file.
    * `ggggg` is the generation number. It tells the reader how old the object is.
    * `n` means that the object is a normal in-use object, `f` means that the object
      is a free object.
        * The first free object always has a generation number of 65535. It forms
          the head of a linked-list of all free objects.
        * The generation number of a normal object is always 0. The generation
          number allows the PDF format to contain multiple versions of the same
          object. This is a version history mechanism.

## The body

The body is a sequence of indirect objects:

`counter generationnumber << the_object >> endobj`

* `counter` (integer) is a unique identifier for the object.
* `generationnumber` (integer) is the generation number of the object.
* `the_object` is the object itself. It can be empty. Starts with `/Keyword` to
  specify which kind of object it is.
* `endobj` marks the end of the object.

A concrete example can be found in `test_reader.py::test_get_images_raw`:

```text
1 0 obj << /Count 1 /Kids [4 0 R] /Type /Pages >> endobj
2 0 obj << >> endobj
3 0 obj << >> endobj
4 0 obj << /Contents 3 0 R /CropBox [0.0 0.0 2550.0 3508.0]
 /MediaBox [0.0 0.0 2550.0 3508.0] /Parent 1 0 R
 /Resources << /Font << >> >>
 /Rotate 0 /Type /Page >> endobj
5 0 obj << /Pages 1 0 R /Type /Catalog >> endobj
```

## The trailer

The trailer looks like this:

```text
trailer << /Root 5 0 R
           /Size 6
        >>
startxref 1234
%%EOF
```

Let's go through it:

* `trailer <<` indicates that the *trailer dictionary* starts. It ends with `>>`.
* `startxref` is a keyword followed by the byte-location of the `xref` keyword.
  As the trailer is always at the bottom of the file, this allows readers to
  quickly find the xref table.
* `%%EOF` is the end-of-file marker.

The trailer dictionary is a key-value list. The keys are specified in
Table 3.13 of the PDF Reference 1.7, e.g. `/Root` and `/Size` (both are required).

* `/Root` (dictionary) contains the document catalog.
    * The `5` is the object number of the catalog dictionary
    * `0` is the generation number of the catalog dictionary
    * `R` is the keyword that indicates that the object is a reference to the
      catalog dictionary.
* `/Size` (integer) contains the total number of entries in the files xref table.


## Reading PDF files

Most PDF files are compressed. If you want to read them, first uncompress them:

```bash
pdftk crazyones.pdf output crazyones-uncomp.pdf uncompress
```

Then rename `crazyones-uncomp.pdf` to `crazyones-uncomp.txt` and open it in
our favorite IDE / text editor.
