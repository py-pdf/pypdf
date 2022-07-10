# Extract Text from a PDF

You can extract text from a PDF like this:

```python
from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")
page = reader.pages[0]
print(page.extract_text())
```

## Why Text Extraction is hard

Extracting text from a PDF can be pretty tricky. In several cases there is no
clear answer what the expected result should look like:

1. **Paragraphs**: Should the text of a paragraph have line breaks at the same places
   where the original PDF had them or should it rather be one block of text?
2. **Page numbers**: Should they be included in the extract?
3. **Headers and Footers**: Similar to page numbers - should they be extracted?
4. **Outlines**: Should outlines be extracted at all?
5. **Formatting**: If text is **bold** or *italic*, should it be included in the
   output?
6. **Tables**: Should the text extraction skip tables? Should it extract just the
   text? Should the borders be shown in some Markdown-like way or should the
   structure be present e.g. as an HTML table? How would you deal with merged
   cells?
7. **Captions**: Should image and table captions be included?
8. **Ligatures**: The Unicode symbol [U+FB00](https://www.compart.com/de/unicode/U+FB00)
   is a single symbol ﬀ for two lowercase letters 'f'. Should that be parsed as
   the Unicode symbol 'ﬀ' or as two ASCII symbols 'ff'?
9. **SVG images**: Should the text parts be extracted?
10. **Mathematical Formulas**: Should they be extracted? Formulas have indices,
    and nested fractions.
11. **Whitespace characters**: How many new lines should be extracted for 3cm of
    vertical whitespace? How many spaces should be extracted if there is 3cm of
    horizontal whitespace? When would you extract tabs and when spaces?
12. **Footnotes**: When the text of multiple pages is extracted, where should footnotes be shown?
13. **Hyperlinks and Metadata**: Should it be extracted at all? Where should it
    be placed in which format?
14. **Linearization**: Assume you have a floating figure in between a paragraph.
    Do you first finish the paragraph or do you put the figure text in between?

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

## OCR vs Text Extraction

Optical Character Recognition (OCR) is the process of extracting text from
images. Software which does this is called *OCR software*. The
[tesseract OCR engine](https://github.com/tesseract-ocr/tesseract) is the
most commonly known Open Source OCR software.

PyPDF2 is **not** OCR software.

### Digitally-born vs Scanned PDF files

PDF documents can contain images and text. PDF files don't store text in a
semantically meaningful way, but in a way that makes it easy to show the
text on screen or print it. For this reason text extraction from PDFs is hard.

If you scan a document, the resulting PDF typically shows the image of the scan.
Scanners then also run OCR software and put the recognized text in the background
of the image. This result of the scanners OCR software can be extracted by
PyPDF2. However, in such cases it's recommended to directly use OCR software as
errors can accumulate: The OCR software is not perfect in recognizing the text.
Then it stores the text in a format that is not meant for text extraction and
PyPDF2 might make mistakes parsing that.

Hence I would distinguish three types of PDF documents:

* **Digitally-born PDF files**: The file was created digitally on the computer.
  It can contain images, texts, links, bookmarks, JavaScript, ...
  If you Zoom in a lot, the text still looks sharp.
* **Scanned PDF files**: Any number of pages was scanned. The images were then
  stored in a PDF file. Hence the file is just a container for those images.
  You cannot copy the text, you don't have links, bookmarks, JavaScript.
* **OCRed PDF files**: The scanner ran OCR software and put the recognized text
  in the background of the image. Hence you can copy the text, but it still looks
  like a scan. If you zoom in enough, you can recognize pixels.


### Can we just always use OCR?

You might now wonder if it makes sense to just always use OCR software. If the
PDF file is digitally-born, you can just render it to an image.

I would recommend not to do that.

Text extraction software like PyPDF2 can use more information from the
PDF than just the image. It can know about fonts, encodings, typical character
distances and similar topics.

That means PyPDF2 has a clear advantage when it
comes to characters which are easy to confuse such as `oO0ö`.
**PyPDF2 will never confuse characters**. It just reads what is in the file.

PyPDF2 also has an edge when it comes to characters which are rare, e.g.
🤰. OCR software will not be able to recognize smileys correctly.
