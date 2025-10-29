# Metadata

PDF files can have two types of metadata: "Regular" and XMP ones. They can both exist at the same time.

## Reading metadata

```{testcode}
from pypdf import PdfReader

reader = PdfReader("resources/side-by-side-subfig.pdf")

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

```{testoutput}
:hide:

None
None
None
TeX
pdfTeX-1.40.23
2022-04-09 08:29:50+02:00
2022-04-09 08:29:50+02:00
```

## Writing metadata

```{testcode}
from datetime import datetime
from pypdf import PdfReader, PdfWriter

reader = PdfReader("resources/side-by-side-subfig.pdf")
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

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="resources/side-by-side-subfig.pdf")

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

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter("resources/side-by-side-subfig.pdf")

# Remove Metadata (/Info entry)
writer.metadata = None

# Save the new PDF to a file
with open("meta-pdf.pdf", "wb") as f:
    writer.write(f)
```

## Reading XMP metadata

```{testcode}
from pypdf import PdfReader

reader = PdfReader("resources/side-by-side-subfig.pdf")

meta = reader.xmp_metadata
if meta:
    print(meta.dc_title)
    print(meta.dc_description)
    print(meta.xmp_create_date)
```

## Creating XMP metadata

You can create XMP metadata easily using the `XmpInformation.create()` method:

```{testcode}
from pypdf import PdfWriter
from pypdf.xmp import XmpInformation

# Create a new XMP metadata object
xmp = XmpInformation.create()

# Set metadata fields
xmp.dc_title = {"x-default": "My Document Title"}
xmp.dc_creator = ["Author One", "Author Two"]
xmp.dc_description = {"x-default": "Document description"}
xmp.dc_subject = ["keyword1", "keyword2", "keyword3"]
xmp.pdf_producer = "pypdf"

# Create a writer and add the metadata
writer = PdfWriter()
writer.add_blank_page(612, 792)  # Add a page
writer.xmp_metadata = xmp
writer.write("output.pdf")
```

## Setting XMP metadata fields

The `XmpInformation` class provides property-based access for all supported metadata fields:

### Dublin Core fields

```{testcode}
from datetime import datetime
from pypdf.xmp import XmpInformation

xmp = XmpInformation.create()

# Single value fields
xmp.dc_coverage = "Global coverage"
xmp.dc_format = "application/pdf"
xmp.dc_identifier = "unique-id-123"
xmp.dc_source = "Original Source"

# Array fields (bags - unordered)
xmp.dc_contributor = ["Contributor One", "Contributor Two"]
xmp.dc_language = ["en", "fr", "de"]
xmp.dc_publisher = ["Publisher One"]
xmp.dc_relation = ["Related Doc 1", "Related Doc 2"]
xmp.dc_subject = ["keyword1", "keyword2"]
xmp.dc_type = ["Document", "Text"]

# Sequence fields (ordered arrays)
xmp.dc_creator = ["Primary Author", "Secondary Author"]
xmp.dc_date = [datetime.now()]

# Language alternative fields
xmp.dc_title = {"x-default": "Title", "en": "English Title", "fr": "Titre français"}
xmp.dc_description = {"x-default": "Description", "en": "English Description"}
xmp.dc_rights = {"x-default": "All rights reserved"}
```

### XMP fields

```{testcode}
from datetime import datetime

# Date fields accept both datetime objects and strings
xmp.xmp_create_date = datetime.now()
xmp.xmp_modify_date = datetime.fromisoformat("2023-12-25T10:30:45Z")
xmp.xmp_metadata_date = datetime.now()

# Text field
xmp.xmp_creator_tool = "pypdf"
```

### PDF fields

```{testcode}
xmp.pdf_keywords = "keyword1, keyword2, keyword3"
xmp.pdf_pdfversion = "1.4"
xmp.pdf_producer = "pypdf"
```

### XMP Media Management fields

```{testcode}
xmp.xmpmm_document_id = "uuid:12345678-1234-1234-1234-123456789abc"
xmp.xmpmm_instance_id = "uuid:87654321-4321-4321-4321-cba987654321"
```

### PDF/A fields

```{testcode}
xmp.pdfaid_part = "1"
xmp.pdfaid_conformance = "B"
```

### Clearing metadata fields

You can clear any field by assigning `None`:

```{testcode}
xmp.dc_title = None
xmp.dc_creator = None
xmp.pdf_producer = None
```

### Incrementally updating XMP metadata fields

When modifying existing XMP metadata, it is often necessary to add or update individual entries while preserving existing values. The XMP properties return standard Python data structures that can be manipulated directly:

```{testcode}
from pypdf.xmp import XmpInformation

xmp = XmpInformation.create()

# Language alternative fields return dictionaries
title = xmp.dc_title or {}
title["en"] = "English Title"
title["fr"] = "Titre français"
xmp.dc_title = title

# Bag fields (unordered collections) return lists
subjects = xmp.dc_subject or []
subjects.append("new_keyword")
xmp.dc_subject = subjects

# Sequence fields (ordered collections) return lists
creators = xmp.dc_creator or []
creators.append("New Author")
xmp.dc_creator = creators
```

This approach provides direct control over the data structures while maintaining the property-based interface.

## Modifying XMP metadata

Modifying XMP metadata is a bit more complicated.

As an example, we want to add the following PDF/UA identifier section to the XMP metadata:

```xml
<rdf:Description rdf:about="" xmlns:pdfuaid="http://www.aiim.org/pdfua/ns/id/">
    <pdfuaid:part>1</pdfuaid:part>
</rdf:Description>
```

This could be written like this:

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="resources/commented-xmp.pdf")

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
