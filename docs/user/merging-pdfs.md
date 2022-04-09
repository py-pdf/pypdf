# Merging PDF files

```python
from PyPDF2 import PdfFileMerger

merger = PdfFileMerger()

for pdf in ["file1.pdf", "file2.pdf", "file3.pdf", "file4.pdf"]:
    merger.append(pdf)

merger.write("merged-pdf.pdf")
merger.close()
```

For more details, see an excellent answer on [StackOverflow](https://stackoverflow.com/questions/3444645/merge-pdf-files) by Paul Rooney.
