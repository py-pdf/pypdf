# Extract Text from a PDF

You can extract text from a PDF like this:

```python
from PyPDF2 import PdfFileReader

reader = PdfFileReader("example.pdf")
page = reader.pages[0]
print(page.extractText())
```

## Why Text Extraction is hard

Extracting text from a PDF can be pretty tricky. In several cases there is no
clear answer what the expected result should look like:

1. **Paragraphs**: Should the text of a paragraph have line breaks at the same places
   where the original PDF had them or should it rather be one block of text?
2. **Page numbers**: Should they be included in the extract?
3. **Outlines**: Should outlines be extracted at all?
4. **Formatting**: If text is **bold** or *italic*, should it be included in the
   output?
5. **Tables**: Should the text extraction skip tables? Should it extract just the
   text? Should the borders be shown in some Markdown-like way or should the
   structure be present e.g. as an HTML table? How would you deal with merged
   cells?
6. **Captions**: Should image and table captions be included?
7. **Ligatures**: The Unicode symbol [U+FB00](https://www.compart.com/de/unicode/U+FB00)
   is a single symbol ﬀ for two lowercase letters 'f'. Should that be parsed as
   the Unicode symbol 'ﬀ' or as two ASCII symbols 'ff'?

Then there are issues where most people would agree on the correct output, but
the way PDF stores information just makes it hard to achieve that:

1. **Tables**: Typically, tables are just absolutely positioned text. In the worst
   case, ever single letter could be absolutely positioned. That makes it hard
   to tell where columns / rows are.
2. **Images**: Sometimes PDFs do not contain the text as it's displayed, but
    instead an image. You notice that when you cannot copy the text. Then there
    are PDF files that contain an image and a text layer in the background.
    That typically happens when a document was scanned. Although the scanning
    software (OCR) is pretty good today, it still fails once in a while. PyPDF2
    is no OCR software; it will not be able to detect those failures. PyPDF2
    will also never be able to extract text from images.

And finally there are issues that PyPDF2 will deal with. If you find such a
text extraction bug, please share the PDF with us so we can work on it!
