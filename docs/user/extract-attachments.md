# Extract Attachments

PDF documents can contain attachments. Attachments have a name, but it might not
be unique. For this reason, the value of `reader.attachments["attachment_name"]`
is a list.

You can extract all attachments like this:

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for name, content_list in reader.attachments.items():
    for i, content in enumerate(content_list):
        with open(f"{name}-{i}", "wb") as fp:
            fp.write(content)
```
