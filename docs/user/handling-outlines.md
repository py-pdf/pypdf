# Handling Outlines

PDF outlines - also known as bookmarks - provide a structured navigation panel in PDF readers. `pypdf` allows you to read, create, and modify both simple and deeply nested outlines.

## Writing PDF Outlines

To add outlines, use the {meth}`~pypdf.PdfWriter.add_outline_item` method. This method returns a reference to the created outline, which you can use as a parent to create nested (hierarchical) bookmarks.

### Adding a Simple Outline

The following example shows how to add a single top-level bookmark. We add an outline item pointing to the first page (index `0`) and save the result.


```{testsetup}
pypdf_test_setup("user/handling-outlines", {
    "crazyones.pdf":"../resources/crazyones.pdf",
})
```

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="crazyones.pdf")

# Add a top-level bookmark
writer.add_outline_item(
    title="Introduction",
    page_number=0
)

writer.write("simple-example.pdf")
```


### Adding Nested Outlines

You can build hierarchies (like Chapter → Section) by passing the parent outline item to the `parent` parameter of a new item.

In the example below, we create a root item "Introduction" and nest two sections under it.

```{testcode}
from pypdf import PdfWriter

writer = PdfWriter(clone_from="crazyones.pdf")

# Add parent (Chapter)
introduction = writer.add_outline_item(
    title="Chapter 1",
    page_number=0
)

# Add children (sections) nested under the introduction
writer.add_outline_item(
    title="Section 1.1",
    page_number=0,
    parent=introduction
)

writer.add_outline_item(
    title="Section 1.2",
    page_number=0,
    parent=introduction
)

writer.write("nested-example.pdf")
```


### Advanced Styling and View Modes (Fit Options)

You can customize the appearance and behavior of bookmarks using optional parameters, such as changing the text color or applying bold and italic styles.

For detailed information on all available parameters and their formats, please refer to the {meth}`~pypdf.PdfWriter.add_outline_item` API documentation.

The ``fit`` parameter determines how the page is displayed when the user clicks the bookmark. You can use the {class}`~pypdf.generic.Fit` helper to specify modes like {meth}`~pypdf.generic.Fit.fit`, {meth}`~pypdf.generic.Fit.fit_horizontally`, or {meth}`~pypdf.generic.Fit.xyz`.


```{testcode}
from pypdf import PdfWriter
from pypdf.generic import Fit

writer = PdfWriter(clone_from="crazyones.pdf")

# Top-level chapter (Points to Page 3, Index 2)
chapter2 = writer.add_outline_item(
    title="Chapter 2",
    page_number=0,
    color=(0, 0, 1),
    bold=True,
    italic=False,
    is_open=True,
    fit=Fit.fit()
)

# Section under Chapter 2 (Points to Page 3, Index 2)
section2_1 = writer.add_outline_item(
    title="Section 2.1",
    page_number=0,
    parent=chapter2,
    color=(0, 0.5, 0),
    bold=False,
    italic=True,
    is_open=False,
    fit=Fit.fit_horizontally(top=800)
)

# Section with custom zoom (Points to Page 3, Index 2)
section2_2 = writer.add_outline_item(
    title="Section 2.2",
    page_number=0,
    parent=chapter2,
    color=(1, 0, 0),
    bold=True,
    italic=True,
    is_open=True,
    fit=Fit.xyz(left=0, top=800, zoom=1.25)
)

writer.write("advanced-example.pdf")
```

```{figure} complete-outlines.png
:alt: An annotated screenshot illustrating simple, nested, and advanced PDF bookmarks.

An annotated screenshot illustrating simple, nested, and advanced PDF bookmarks in a Table of Contents.
```

## Reading PDF Outlines

`pypdf` represents outlines as a list of {class}`~pypdf.generic.Destination` objects. If an outline has children, they appear as a nested list directly following their parent.

To retrieve the page number a bookmark points to, use the {meth}`~pypdf.PdfReader.get_destination_page_number` method, which returns a zero-based page index.

### Reading Simple Outlines

To extract only the top-level bookmarks (ignoring nested sections), you can iterate over the {attr}`~pypdf.PdfReader.outline` property. Since nested children appear as lists within the outline structure, you must explicitly check for and skip them (`isinstance(outline, list)`) to avoid errors. The example below reads the file created in the previous section.

```{testcode}
from pypdf import PdfReader

reader = PdfReader("simple-example.pdf")

print("Simple Outline (Top-Level Only):")
print("-" * 32)

for outline in reader.outline:
    # Check if the item is a list (which represents nested children)
    if isinstance(outline, list):
        continue  # Skip the nested parts completely

    page_number = reader.get_destination_page_number(outline)

    if page_number is None:
        print(f"{outline.title} -> No page destination")
    else:
        print(f"{outline.title} -> page {page_number + 1}")
```

```{testoutput}
Simple Outline (Top-Level Only):
--------------------------------
Introduction -> page 1
```

### Reading Nested Outlines

When dealing with hierarchical bookmarks, the {attr}`~pypdf.PdfReader.outline` property may contain lists inside lists. You should use a recursive function to traverse the tree.

The following example defines a `print_outline` function that handles indentation and nested lists to display the structure of the document we created earlier.

```{testcode}
from typing import List, Union

from pypdf import PdfReader
from pypdf.generic import Destination


def print_outline(
    outlines: List[Union[Destination, List[Destination]]],
    reader: PdfReader,
    level: int = 0
) -> None:
    """Recursively print all outline items with indentation."""
    for item in outlines:
        if isinstance(item, list):
            # Recursively handle the nested list of children
            print_outline(item, reader, level + 1)
        else:
            page_number = reader.get_destination_page_number(item)

            indent = "  " * level

            if page_number is None:
                print(f"{indent}- {item.title} (No page destination)")
            else:
                print(f"{indent}- {item.title} (Page {page_number + 1})")


reader = PdfReader("nested-example.pdf")

print("Nested Outline Hierarchy:")
print("-" * 25)

print_outline(reader.outline, reader)
```

```{testoutput}
Nested Outline Hierarchy:
-------------------------
- Chapter 1 (Page 1)
  - Section 1.1 (Page 1)
  - Section 1.2 (Page 1)
```
