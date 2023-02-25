# Extract Attachments

PDF documents can contain attachments. Attachments have a name, but it might not
be unique.

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for name, attachment_loader in reader.attachments:
    for i, content in enumerate(attachment_loader.reader()):
        with open(f"{name}-{i}", "wb") as fp:
            fp.write(content)
```
