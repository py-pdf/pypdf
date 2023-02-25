# Extract Attachments

PDF documents can contain attachments. Attachments have a name, but it might not
be unique.

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for name, content_list in reader.attachments:
    for i, content in enumerate(content_list):
        with open(f"{name}-{i}", "wb") as fp:
            fp.write(content)
```
