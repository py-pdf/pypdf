# Encryption and Decryption of PDFs

> Please see the note in the [installation guide](installation.md)
> for installing the extra dependencies if interacting with PDFs that use AES.

## Encrypt

> ⚠️ WARNING ⚠️: pypdf uses by default [RC4 encryption](https://en.wikipedia.org/wiki/RC4)
> if you ommit the "algorithm" parameter.
> This encryption algorithm is insecure. The more modern and secure AES
> encryption requires [`pycryptodome`](https://pypi.org/project/pycryptodome/) to be installed.

Add a password to a PDF (encrypt it):

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

# Add all pages to the writer
for page in reader.pages:
    writer.add_page(page)

# Add a password to the new PDF
writer.encrypt("my-secret-password", algorithm="AES-256")

# Save the new PDF to a file
with open("encrypted-pdf.pdf", "wb") as f:
    writer.write(f)
```

We recommend using `AES-256-R5`:

* Using the [Advanced Encryption Standard](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) encryption
* with a key size of 256 bit


## Decrypt

Remove the password from a PDF (decrypt it):

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("encrypted-pdf.pdf")
writer = PdfWriter()

if reader.is_encrypted:
    reader.decrypt("my-secret-password")

# Add all pages to the writer
for page in reader.pages:
    writer.add_page(page)

# Save the new PDF to a file
with open("decrypted-pdf.pdf", "wb") as f:
    writer.write(f)
```
