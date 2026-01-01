# Extract Images

```{note}
In order to use the following code you need to install optional
dependencies, see [installation guide](installation.md).
```

Every page of a PDF document can contain an arbitrary number of images.
The names of the files may not be unique.

```{testsetup}
pypdf_test_setup("user/extract-images", {
    "example.pdf": "../resources/example.pdf",
})
```

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

page = reader.pages[0]

for i, image_file_object in enumerate(page.images):
    file_name = "out-image-" + str(i) + "-" + image_file_object.name
    image_file_object.image.save(file_name)
```

## Other images

Some other objects can contain images, such as stamp annotations.

You can extract the image from the annotation with the following code:

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")
im = (
    reader.pages[0]["/Annots"][4]["/Parent"]
    .get_object()["/AP"]["/N"]["/Resources"]["/XObject"]["/Im4"]
    .decode_as_image()
)

im.save("out-annotation-image.png")
```

## Error handling

Iterating over `page.images` directly will raise an exception on the first issue.
If you expect some more or less broken PDF files, but still want to retrieve as many images as possible,
consider making this a multistep process:

```{testcode}
from pypdf import PdfReader

reader = PdfReader("example.pdf")

for page in reader.pages:
    for name in page.images.keys():
        try:
            # Try to retrieve actual image.
            image = page.images[name]
        except Exception as exception:
            # Handle exceptions.
            pass
```
