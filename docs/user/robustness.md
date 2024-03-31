# Robustness and strict=False

PDF is [specified in various versions](https://www.pdfa.org/resource/pdf-specification-index/).
The specification of PDF 1.7 has 978 pages. This length makes it hard to get
everything right. As a consequence, a lot of PDF files are not strictly following the
specification.

If a PDF file does not follow the specification, it is not always possible to
be certain what the intended effect would be. Think of the following broken
Python code as an example:

```python
# Broken
function (foo, bar):

# Potentially intended:
def function(foo, bar):
    ...

# Also possible:
function = (foo, bar)
```

Writing a parser you can go two paths: Either you try to be forgiving and try
to figure out what the user intended, or you are strict and just tell the user
that they should fix their stuff.

PyPDF2 gives you the option to be strict or not.

PyPDF2 has three core objects and all of them have a `strict` parameter:

* [`PdfReader`](../modules/PdfReader.md)
* [`PdfWriter`](../modules/PdfWriter.md)
* [`PdfMerger`](../modules/PdfMerger.md)

Choosing `strict=True` means that PyPDF2 will raise an exception if a PDF does
not follow the specification.

Choosing `strict=False` means that PyPDF2 will try to be forgiving and do
something reasonable, but it will log a warning message. It is a best-effort
approach.
