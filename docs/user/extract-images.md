# Extract Images

```python
from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")

page = reader.pages[0]

for image_file_object in page.images:
    with open(image_file_object, "wb") as fp:
        fp.write(image_file_object.data)
```
