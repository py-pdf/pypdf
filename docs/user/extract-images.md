# Extract Images

```{note}
In order to use the following code you need to install optional
dependencies, see [installation guide](installation.md).
```

Every page of a PDF document can contain an arbitrary amount of images.
The names of the files may not be unique.

```python
from pypdf import PdfReader

reader = PdfReader("example.pdf")

page = reader.pages[0]

for count, image_file_object in enumerate(page.images):
    with open(str(count) + image_file_object.name, "wb") as fp:
        fp.write(image_file_object.data)
```

# Other images

Some other objects can contain images, such as stamp annotations.

For example, this document contains such stamps:
[test_stamp.pdf](https://github.com/user-attachments/files/15751424/test_stamp.pdf)

You can extract the image from the annotation with the following code:

```python
from pypdf import PdfReader

reader = PdfReader("test_stamp.pdf")
im = (
    reader.pages[0]["/Annots"][0]
    .get_object()["/AP"]["/N"]["/Resources"]["/XObject"]["/Im4"]
    .decode_as_image()
)

im.show()
```
