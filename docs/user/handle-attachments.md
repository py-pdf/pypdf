# Handle Attachments

PDF documents can contain attachments, from time to time named embedded file as well.

## Retrieve Attachments

Attachments have a name, but it might not be unique. For this reason, the value of `reader.attachments["attachment_name"]`
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

## Add Attachments

To add a new attachment, use the following code:

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")
writer.add_attachment(filename="test.txt", data=b"Hello World!")
```

As you can see, the basic attachment properties are its name and content. If you
want to modify further properties of it, the returned object provides corresponding
setters:

```python
import datetime
import hashlib

from pypdf import PdfWriter
from pypdf.generic import create_string_object, ByteStringObject, NameObject, NumberObject


writer = PdfWriter(clone_from="example.pdf")
embedded_file = writer.add_attachment(filename="test.txt", data=b"Hello World!")

embedded_file.size = NumberObject(len(b"Hello World!"))
embedded_file.alternative_name = create_string_object("test1.txt")
embedded_file.description = create_string_object("My test file")
embedded_file.subtype = NameObject("/text/plain")
embedded_file.checksum = ByteStringObject(hashlib.md5(b"Hello World!").digest())
embedded_file.modification_date = datetime.datetime.now(tz=datetime.timezone.utc)
# embedded_file.content = "My new content."

embedded_file.write("output.pdf")
```

The same functionality is available if you iterate over the attachments of a writer
using `writer.attachment_list`.
