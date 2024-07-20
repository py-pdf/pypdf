# Robustness and strict=False

PDF is [specified in various versions](https://pdfa.org/resource/pdf-specification-archive/).
The specification of PDF 2.0 has 1003 pages. This length makes it hard to get
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

pypdf gives you the option to be strict or not.

pypdf has two core objects:

* [`PdfReader`](../modules/PdfReader.md)
* [`PdfWriter`](../modules/PdfWriter.md)

Only the PdfReader has a `strict` parameter, since presumably you do not want
to write a non-conforming PDF.

Choosing `strict=True` means that pypdf will raise an exception if a PDF does
not follow the specification.

Choosing `strict=False` means that pypdf will try to be forgiving and do
something reasonable, but it will log a warning message. It is a best-effort
approach.
