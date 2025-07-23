# Metadata

PDF files can have two types of metadata: "Regular" and XMP ones. They can both exist at the same time.

## Reading metadata

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

meta = reader.metadata

# All the following could be None!
print(meta.title)
print(meta.author)
print(meta.subject)
print(meta.creator)
print(meta.producer)
print(meta.creation_date)
print(meta.modification_date)
```

## Writing metadata

```python
from datetime import datetime
from pypdf import PdfReader, PdfWriter

reader = PdfReader("example.pdf")
writer = PdfWriter()

# Add all pages to the writer
for page in reader.pages:
    writer.add_page(page)

# If you want to add the old metadata, include these two lines
if reader.metadata is not None:
    writer.add_metadata(reader.metadata)

# Format the current date and time for the metadata
utc_time = "-05'00'"  # UTC time optional
time = datetime.now().strftime(f"D\072%Y%m%d%H%M%S{utc_time}")

# Add the new metadata
writer.add_metadata(
    {
        "/Author": "Martin",
        "/Producer": "Libre Writer",
        "/Title": "Title",
        "/Subject": "Subject",
        "/Keywords": "Keywords",
        "/CreationDate": time,
        "/ModDate": time,
        "/Creator": "Creator",
        "/CustomField": "CustomField",
    }
)

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Updating metadata

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

# Change some values
writer.add_metadata(
    {
        "/Author": "Martin",
        "/Producer": "Libre Writer",
        "/Title": "Title",
    }
)

# Clear all data but keep the entry in PDF
writer.metadata = {}

# Replace all entries with new set of entries
writer.metadata = {
    "/Author": "Martin",
    "/Producer": "Libre Writer",
}

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Removing metadata entry

```python
from pypdf import PdfWriter

writer = PdfWriter("example.pdf")

# Remove Metadata (/Info entry)
writer.metadata = None

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Reading XMP metadata

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

meta = reader.xmp_metadata
if meta:
    print(meta.dc_title)
    print(meta.dc_description)
    print(meta.xmp_create_date)
```

## Modifying XMP metadata

Modifying XMP metadata is a bit more complicated.

As an example, we want to add the following PDF/UA identifier section to the XMP metadata:

```xml
<rdf:Description rdf:about="" xmlns:pdfuaid="http://www.aiim.org/pdfua/ns/id/">
    <pdfuaid:part>1</pdfuaid:part>
</rdf:Description>
```

This could be written like this:

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

metadata = writer.xmp_metadata
assert metadata  # Ensure that it is not `None`.
rdf_root = metadata.rdf_root
xmp_meta = rdf_root.parentNode
xmp_document = xmp_meta.parentNode

# Please note that without a text node, the corresponding elements might
# be omitted completely.
pdfuaid_description = xmp_document.createElement("rdf:Description")
pdfuaid_description.setAttribute("rdf:about", "")
pdfuaid_description.setAttribute("xmlns:pdfuaid", "http://www.aiim.org/pdfua/ns/id/")
pdfuaid_part = xmp_document.createElement("pdfuaid:part")
pdfuaid_part_text = xmp_document.createTextNode("1")
pdfuaid_part.appendChild(pdfuaid_part_text)
pdfuaid_description.appendChild(pdfuaid_part)
rdf_root.appendChild(pdfuaid_description)

metadata.stream.set_data(xmp_document.toxml().encode("utf-8"))

writer.write("output.pdf")
```

For further details on modifying the structure, please refer to {py:mod}`xml.dom.minidom`.
