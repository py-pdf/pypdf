# Adding JavaScript to a PDF


# https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

# Add JavaScript to launch the print window on opening this PDF.
# The password dialog may prevent the print dialog from being shown,
# comment the encryption lines, if that's the case, to try this out.
writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

# Write to pypdf-output.pdf.
with open("pypdf-output.pdf", "wb") as fp:
    writer.write(fp)
```

## Open at a given page

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

  # Write to pypdf-output.pdf.
       # https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/JS_API_AcroJS.html#beep
       # On Mac OS and UNIX systems the beep type is ignored.

# Add JavaScript to launch the print window on opening this PDF.
writer.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")

# Write to pypdf-output.pdf.
with open("pypdf-output.pdf", "wb") as fp:
    writer.write(fp)
```



## Write to console

![](plain-merge.png)

is the result of

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="example.pdf")

# Add JavaScript to print to the console on opening this PDF.
javascript = "console.clear(); console.show(); console.println(\"This text was written by JavaScript embedded in\");"
writer.add_js(javascript)

# Write to pypdf-output.pdf.
with open("pypdf-output.pdf", "wb") as fp:
    writer.write(fp)
```
