# Extract Images

> Please note: In order to use the following code you need to install optional
> dependencies, see [installation guide](installation.html).

Every page of a PDF document can contain an arbitrary amount of images.
The names of the files may not be unique.

```python
from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")

page = reader.pages[0]
count = 0

for image_file_object in page.images:
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
        count += 1
```
