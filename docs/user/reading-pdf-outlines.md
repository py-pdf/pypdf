# Reading PDF Outlines

PDF outlines (also called *bookmarks*) help users navigate through a document.
pypdf allows you to read both simple and nested outlines from any PDF.


```{note}
* **`outline` parameter:** It represents a single bookmark in the PDF. Each bookmark has a title and points to a specific page.
* **`get_destination_page_number(outline)`:** It returns the destination page as a **0-indexed integer** (first page = 0).
* It supports both **simple (flat)** outlines and **nested (hierarchical)** outlines where Parent bookmarks contain child bookmarks.
```

## How nested outlines are represented internally

When a PDF contains hierarchical bookmarks (Chapter → Section → Topic),
pypdf stores them using **lists inside lists**.
Each list represents a deeper level of nesting.

### How to interpret the structure

- **A `Destination`** → represents a single bookmark
- **A list** → represents a group of child bookmarks
- Nesting can be **multiple levels deep** (there is no limit)

### Visual Interpretation (Tree Format)
This tree represents the exact same structure as the list above:

```text
Chapter 1
├── Section 1.1
│   ├── Topic 1.1.1
│   └── Topic 1.1.2
└── Section 1.2
Chapter 2
└── Section 2.1
```

### Example Python Structure (List Format)

This is how pypdf internally represents nested outlines:

```python

[
    Destination("Chapter 1"),
    [
        Destination("Section 1.1"),
        [
            Destination("Topic 1.1.1"),
            Destination("Topic 1.1.2")
        ],
        Destination("Section 1.2")
    ],
    Destination("Chapter 2"),
    [
        Destination("Section 2.1")
    ]
]
```

---


## Reading simple (non-nested) outlines

Use this method if your PDF has a flat list of outlines.

```{testsetup}
pypdf_test_setup("user/reading-pdf-outlines", {
    "example1.pdf": "../resources/example1.pdf",
    "output.pdf": "../resources/output.pdf"
})
```

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example1.pdf")

for outline in reader.outline:
    page_num = reader.get_destination_page_number(outline)
    print(f"{outline.title} -> page {page_num + 1}")
```

```{testoutput}
:hide:

Introduction -> page 1
```

### What this simple code does:
* Loops through each top-level outline item
* Gets the page number for that outline
* Prints a clean "Title → Page" format


## Reading nested outlines (hierarchical)

Use this method when your PDF contains parent → child outline items

```{testcode}
from pypdf import PdfReader

def print_outline(outlines, reader, level=0):
    """Recursively print all outline items with indentation."""
    for item in outlines:
        if isinstance(item, list):  # nested children
            print_outline(item, reader, level + 1)
        else:
            try:
                page_num = reader.get_destination_page_number(item)
            except Exception:
                page_num = None

            indent = "  " * level

            if page_num is None:
                print(f"{indent}- {item.title} (No page destination)")
            else:
                print(f"{indent}- {item.title} (Page {page_num + 1})")

reader = PdfReader("output.pdf")
print_outline(reader.outline, reader)
```

```{testoutput}
:hide:

- Introduction (Page 1)
  - Section 1 (Page 2)
  - Section 2 (Page 3)
```


### What this nested code does:
* Recursively handles hierarchical outline structures
* Indents output according to nesting depth
* Prints page numbers when available
* Safely handles undefined or invalid destinations
