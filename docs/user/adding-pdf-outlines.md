# Adding PDF Outlines

```{note}
PDF outlines — also known as bookmarks — provide a structured navigation panel in PDF readers.
With pypdf, you can create simple or deeply nested outlines programmatically.
```

## `PdfWriter.add_outline_item()`

**Source:** `pypdf/_writer.py`  
Adds an outline (bookmark) entry to the PDF document.


## **Syntax**

```python
add_outline_item(
    title: str,
    page_number: int | None = None,
    parent: Any | None = None,
    color: tuple | None = None,
    bold: bool = False,
    italic: bool = False,
    is_open: bool = True,
    fit: str | None = None,
    zoom: float | None = None
) -> Any
```


## Parameters

The following parameters are available for `add_outline_item()`:

| Name         | Type                     | Default | Description |
|--------------|---------------------------|---------|-------------|
| `title`      | `str`                     | —       | The visible text label shown in the PDF outline panel. |
| `page_number`| `int`, optional           | `None`  | Zero-based target page index. If `None`, the item becomes a non-clickable parent/group header. |
| `parent`     | `Any`, optional           | `None`  | The parent outline item under which this one will be nested. If omitted, this becomes a top-level outline. |
| `color`      | `tuple`, optional         | `None`  | RGB color tuple with values between `0–1`. Example: `(1, 0, 0)` for red. |
| `bold`       | `bool`                    | `False` | If `True`, the outline title is displayed in bold. |
| `italic`     | `bool`                    | `False` | If `True`, the outline title is displayed in italic. |
| `is_open`       | `bool`                    | `True`  | Whether the outline node is expanded when the PDF opens. |
| `fit`        | `str`, optional           | `None`  | Controls how the destination page is displayed (Fit, FitH, FitV, FitR, XYZ). |
| `zoom`       | `float`, optional         | `None`  | Used only when `fit="XYZ"`. Example: `1.0` = 100% zoom. |

### Fit Mode Options

| Value  | Meaning |
|--------|---------|
| `"Fit"`  | Display the entire page. |
| `"FitH"` | Fit to width, aligned at the top. |
| `"FitV"` | Fit to height. |
| `"FitR"` | Fit a specific rectangle region. |
| `"XYZ"`  | Use a custom zoom level (`zoom=` required). |



## **Return Type:** `Any`

The method returns a reference to the created outline item.  
This reference is typically used when creating nested (child) outline items.

### Example
```python
parent = writer.add_outline_item("Chapter 1", page_number=0)
writer.add_outline_item("Section 1.1", page_number=1, parent=parent)
```


## Exceptions

The `add_outline_item()` method may raise the following exceptions:

| Exception       | When it occurs |
|-----------------|----------------|
| `ValueError`    | Raised when `page_number` is out of range, `fit` is invalid, or `color` is not a valid `(r, g, b)` tuple (each value must be a float between 0–1). |
| Internal errors | Occur if an invalid `parent` reference is passed, or if the outline tree becomes corrupted internally. |



## Example: Full PDF Outline with All Parameters

```python
from pypdf import PdfReader, PdfWriter
from pypdf.generic._fit import Fit  # Use Fit only

reader = PdfReader("input.pdf")  # Replace with your input PDF
writer = PdfWriter()

# Copy all pages into the writer
for page in reader.pages:
    writer.add_page(page)

# Top-level chapter (blue, bold, expanded)
chapter1 = writer.add_outline_item(
    title="Chapter 1: Introduction",
    page_number=0,
    color=(0, 0, 1),
    bold=True,
    italic=False,
    is_open=True,
    fit=Fit.fit()
)

# Section under Chapter 1 (dark green, italic, collapsed)
section1_1 = writer.add_outline_item(
    title="Section 1.1: Overview",
    page_number=1,
    parent=chapter1,
    color=(0, 0.5, 0),
    bold=False,
    italic=True,
    is_open=False,
    fit=Fit.fit_horizontally(top=800)
)

# Section with custom zoom
section1_2 = writer.add_outline_item(
    title="Section 1.2: Details",
    page_number=2,
    parent=chapter1,
    color=(1, 0, 0),
    bold=True,
    italic=True,
    is_open=True,
    fit=Fit.xyz(left=0, top=800, zoom=1.25)
)

# Non-clickable parent (no page number)
appendix = writer.add_outline_item(
    title="Appendices",
    page_number=None,
    color=(0.5, 0, 0.5),
    bold=True,
    italic=False,
    is_open=False
)

# Child under non-clickable parent
writer.add_outline_item(
    title="Appendix A: Extra Data",
    page_number=3,
    parent=appendix,
    color=(0, 0, 0),
    bold=False,
    italic=False,
    is_open=True,
    fit=Fit.fit_vertically(left=50)
)

# Save the PDF
output_path = "output.pdf"
with open(output_path, "wb") as f:
    writer.write(f)

print(f"PDF with outlines created successfully: {output_path}")
```

### What this code demonstrates

* Adding top-level and nested bookmarks.
* Using all parameters: `title`, `page_number`, `parent`, `color`, `bold`, `italic`, `is_open`, `fit.`
* Creating non-clickable parent nodes (`page_number=None`).
* Using different page view modes: `Fit, FitH, FitV, XYZ.`
* Produces a navigable outline tree in the PDF reader.


## Adding a Simple Outline

Use this when you want a single top-level bookmark pointing to a page.
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Copy all pages into the writer
for page in reader.pages:
    writer.add_page(page)

# Add a top-level bookmark
writer.add_outline_item(
    title="Introduction",
    page_number=0  # zero-based index
)

with open("output.pdf", "wb") as f:
    writer.write(f)
```

### What the simple outline code does

* Loads the original PDF
* Copies each page
* Adds an outlines named "Introduction"
* Save the updated PDF

![PDF outline output](simple-outline.png)


## Adding Nested (Hierarchical) Outlines

Nested outlines create structures like:

```text
Chapter 1
├── Section 1.1
└── Section 1.2
```

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Copy pages
for page in reader.pages:
    writer.add_page(page)

# Add parent (chapter)
chapter = writer.add_outline_item(
    title="Chapter 1",
    page_number=0
)

# Add children (sections)
writer.add_outline_item(
    title="Section 1.1",
    page_number=1,
    parent=chapter
)

writer.add_outline_item(
    title="Section 1.2",
    page_number=2,
    parent=chapter
)

with open("output.pdf", "wb") as f:
    writer.write(f)
```

### What the nested outline code does

* Copies all pages into the new PDF
* Creates a top-level outline called Chapter 1
* Adds Section 1.1 under that chapter
* Adds Section 1.2 under the same chapter
* Produces an outline tree like:

![PDF outline output](nested-outline.png)

### Key points

- `parent=` creates nested outlines — without it, all outlines become top level.
- `page_number` is zero-based (`0` = first page).
- You must **add pages before** adding outlines — otherwise bookmarks won’t work.
- You can build multiple hierarchical levels (chapter → section → subsection → etc.).
- A bookmark must point to a valid page, or the PDF reader may hide or ignore it.
- Nested outlines improve navigation for large PDFs.




