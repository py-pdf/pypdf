# Suppress Warnings and Log messages

PyPDF2 makes use of 3 mechanisms to show that something went wrong:

* **Exceptions**: Error-cases the client should explicitly handle.
* **Warnings**: Avoidable issues, such as using deprecated classes / functions / parameters
* **Log messages**: Nothing the client can do, but they should know it happened.


## Exceptions

Exeptions need to be catched if you want to handle them. For example, you could
want to read the text from a PDF as a part of a search function.

Most PDF files don't follow the specifications. In this case PyPDF2 needs to
guess which kinds of mistakes were potentially done when the PDF file was created.
See [the robustness page](robustness.md) for the related issues.

As a users, you likely don't care about it. If it's readable in any way, you
want the text. You might use pdfminer.six as a fallback and do this:

```python
from PyPDF2 import PdfReader
from pdfminer.high_level import extract_text as fallback_text_extraction

text = ""
try:
    reader = PdfReader("example.pdf")
    for page in reader.pages:
        text += page.extract_text()
except Exception as exc:
    text = fallback_text_extraction("example.pdf")
```

You could also capture [`PyPDF2.errors.PyPdfError`](https://github.com/py-pdf/PyPDF2/blob/main/PyPDF2/errors.py)
if you prefer something more specific.

## Warnings

```python
import warnings

warnings.filterwarnings("ignore")
```

## Log messages

```python
import logging

logger = logging.getLogger("PyPDF2")
logger.setLevel(logging.ERROR)
```
