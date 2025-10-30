# Handle Attachments

PDF documents can contain attachments, from time to time named embedded file as well.

## Retrieve Attachments

Attachments have a name, but it might not be unique. For this reason, the value of `reader.attachments["attachment_name"]`
is a list.

You can extract all attachments like this:

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for name, content_list in reader.attachments.items():
    for i, content in enumerate(content_list):
        with open(f"{name}-{i}", "wb") as fp:
            fp.write(content)
```

Alternatively, you can retrieve them in an object-oriented fashion if you need
further details for these files:

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for attachment in reader.attachment_list:
    print(attachment.name, attachment.alternative_name, attachment.content)
```

## Add Attachments

To add a new attachment, use the following code:

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")
writer.add_attachment(filename="test.txt", data=b"Hello World!")
```

As you can see, the basic attachment properties are its name and content. If you
want to modify further properties of it, the returned object provides corresponding
setters:

```{testcode}
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

writer.write("out-attachment-file.pdf")
```

The same functionality is available if you iterate over the attachments of a writer
using `writer.attachment_list`.

## Delete Attachments

To delete an existing attachment, use the following code:

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")
attachment = writer.add_attachment(filename="test.txt", data=b"Hello World!")
attachment.delete()
assert list(writer.attachment_list) == []
```

Please note that this will not delete the associated file relationship
if it exists. Deleting them as well would require us to know where this has
been defined, which requires more complexity. For now, please consider looking
for the corresponding definition yourself and delete it from the array.

### PDF/A compliance

The following example shows how to add an attachment to a PDF/A-3B compliant document
without breaking compliance:

```{testcode}
from pypdf import PdfWriter
from pypdf.constants import AFRelationship
from pypdf.generic import create_string_object, ArrayObject, NameObject

writer = PdfWriter(clone_from="example.pdf")
attachment = writer.add_attachment(filename="test.txt", data="Hello World!")
attachment.subtype = NameObject("/text/plain")
attachment.associated_file_relationship = NameObject(AFRelationship.SUPPLEMENT)
attachment.alternative_name = create_string_object(attachment.name)

if "/AF" in writer.root_object:
    af = writer.root_object["/AF"].get_object()
else:
    af = ArrayObject()
    writer.root_object[NameObject("/AF")] = af
af.append(attachment.pdf_object.indirect_reference)

writer.write("out-attachment-a3b.pdf")
```

This example marks a relationship of the attachment to the whole document.
Alternatively, it can be added to most of the other PDF objects as well.
For details, see the corresponding PDF specification, like section 14.13
of the PDF 2.0 specification.
