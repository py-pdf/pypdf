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

Alternatively, you can retrieve them in an object-oriented fashion if you need
further details for these files:

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for attachment in reader.attachment_list:
    print(attachment.name, attachment.alternative_name, attachment.content)
```
