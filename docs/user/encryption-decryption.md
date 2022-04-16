# Encryption and Decryption of PDFs

## Encrypt

Add a password to a PDF (encrypt it):

```python
from PyPDF2 import PdfFileReader, PdfFileWriter

reader = PdfFileReader("example.pdf")
writer = PdfFileWriter()

# Add all pages to the writer
for i in range(reader.numPages):
    page = reader.pages[i]
    writer.addPage(page)

# Add a password to the new PDF
writer.encrypt("my-secret-password")

# Save the new PDF to a file
with open("encrypted-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Decrypt

Remove the password from a PDF (decrypt it):

```python
from PyPDF2 import PdfFileReader, PdfFileWriter

reader = PdfFileReader("encrypted-pdf.pdf")
writer = PdfFileWriter()

if reader.isEncrypted:
    reader.decrypt("my-secret-password")

# Add all pages to the writer
for i in range(reader.numPages):
    page = reader.pages[i]
    writer.addPage(page)

# Save the new PDF to a file
with open("decrypted-pdf.pdf", "wb") as f:
    writer.write(f)
```
