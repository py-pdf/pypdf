# Interactions with PDF Forms

## Reading form fields

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_form_text_fields()
fields == {"key": "value", "key2": "value2"}

# You can also get all fields:
fields = reader.get_fields()
```

## Filling out forms

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

page = reader.pages[0]
fields = reader.get_fields()

writer.append(reader)

writer.update_page_form_field_values(
    writer.pages[0],
    {"fieldname": "some filled in text"},
    auto_regenerate=False,
)

# write "output" to pypdf-output.pdf
with open("filled-out.pdf", "wb") as output_stream:
    writer.write(output_stream)
```

Generally speaking, you will always want to use `auto_regenerate=False`. The
parameter is `True` by default for legacy compatibility, but this flags the PDF
Viewer to recompute the field's rendering, and may trigger a "save changes"
dialog for users who open the generated PDF.

## A note about form fields and annotations
PDF forms have a dual-nature approach about the fields:
* within the root object, an `/AcroForm` structure exists.
  Inside it you could find (optional):
	- some global elements (Fonts, Ressources,...)
	- some global flags (like `/NeedAppearances` (set/cleared with `auto_regenerate` parameter in `update_form_field_values()`) that indicates if the reading program should re-render the visual fields upon document launch)
	- `/XFA` that houses a form in XDP format (very specific XML that describes the form rendered by some viewers) ; the `/XFA` form overrides the page content.
	- `/Fields` that houses array of indirect references that references TopMost(roots) _Field_ Objects
* within the page `/Annots`, you will spot `/Widget` annotations that defines the visual renderings.

To flesh out this overview:
* the core specific properties of a fields are :
	- `/FT` : Field Type (Button, Text, Choice, Signatures)
	- `/T` : Partial Field Name (see PDF Reference for more details)
	- `/V` : Field Value
	- `/DV` : Default Field Value (used when reseting a form for exemple)
* in order to streamline readability, _Field_ Objects and _Widget_ Objects can be fused housing all properties.
* Field can be organised hierarchically, meaning one field can be placed under another. in such instances, the `/Parent` will stock an IndirectObject providing Bottom-Up links and `/Childs` is an array carrying IndirectObjects for Top-Down navigation ; _Widget_ Objects are still required for visual rendering ; to call upon them, use *full qualified field name* (with all the individual names of the parent objects are seperated by `.`)
  For instance 2 (visual) fields both called _city_ but attached below _sender_ and _receiver_ ; the data full names will be _sender.city_ and _receiver.city_
* When a field is repeated on multiple pages, the Field Object will have many _Widget_ Objects in  `/Childs`. These objects are pure _widgets_, containing no _field_ specific data
* if Fields stores only hidden values, No _Widget_ are required.

In _pypdf_ fields are extracted from the `/Fields` array
```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()
```

```python
from pypdf import PdfReader
from pypdf.constants import AnnotationDictionaryAttributes

reader = PdfReader("form.pdf")
fields = []
for page in reader.pagesP:
    for annot in page.annotations:
        annot = annot.get_object()
        if annot[AnnotationDictionaryAttributes.Subtype] == "/Widget":
            fields.append(annot)
```

However, while similar, there are some very important differences between the two above blocks of code. Most importantly, the first block will return a list of Field objects, where as the second will return more generic dictionary-like objects. The objects lists will *mostly* reference the same object in the underlying PDF, meaning you'll find that `obj_taken_fom_first_list.indirect_reference == obj_taken_from _second_list.indirect_reference`. Field objects are generally more ergonomic, as the exposed data can be access via clearly named properties. However, the more generic dictionary-like objects will contain data that the Field object does not expose, such as the Rect (the widget's position on the page). So, which to use will depend on your use case.

However, it's also important to note that the two lists do not *always* refer to the same underlying PDF objects. For example, if the form contains radio buttons, you will find that `reader.get_fields()` will get the parent object (the group of radio buttons) whereas `page.annotations` will return all the child objects (the individual radio buttons).


__Caution:
Remember that fields are not stored in pages: If you use  `add_page()` the field structure is not copied.
It is recommended to use `.append() with the proper parameters`__

In case of missing _field_ objects in `/Fields`, `writer.reattach_fields()` will parse page(s) annotations and will reattach them. This fix can not guess intermediate fields and will not report fields using the same _name_
