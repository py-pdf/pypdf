# Adding JavaScript to a PDF

PDF readers vary in the extent they support JavaScript, with some not supporting it at all.

Adobe has documentation on its support here:
https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/index.html

## Launch print window on opening

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
