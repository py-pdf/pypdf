# Exceptions, Warnings, and Log messages

pypdf makes use of three mechanisms to show if something went wrong:

* **Exceptions** are error cases that pypdf users should explicitly handle.
  In the `strict=True` mode, most log messages with the warning level will
  become exceptions. This can be useful in applications where you can require
  a user to fix the broken PDF.
* **Warnings** are avoidable issues, such as using deprecated classes /
  functions / parameters. Another example is missing capabilities of pypdf.
  In those cases, pypdf users should adjust their code. Warnings
  are issued by the `warnings` module - those are different from the log-level
  "warning".
* **Log messages** are informative messages that can be used for post-mortem
  analysis. Most of the time, users can ignore them. They come in different
  *levels*, such as info / warning / error indicating the severity.
  Examples are non-standard compliant PDF files which pypdf can deal with or
  a missing implementation that leads to a part of the text not being extracted.


## Exceptions

Exceptions need to be caught if you want to handle them. For example, you could
want to read the text from a PDF as a part of a search function.

Most PDF files do not follow the specification. In this case pypdf needs to
guess which kinds of mistakes were potentially done when the PDF file was created.
See [the robustness page](robustness.md) for the related issues.

As a user, you likely do not care about it. If it is readable in any way, you
want the text. You might use pdfminer.six as a fallback and do this:

```python
from pypdf import PdfReader
from pdfminer.high_level import extract_text as fallback_text_extraction

text = ""
try:
    reader = PdfReader("example.pdf")
    for page in reader.pages:
        text += page.extract_text()
except Exception as exc:
    text = fallback_text_extraction("example.pdf")
```

You could also capture [`pypdf.errors.PyPdfError`](https://github.com/py-pdf/pypdf/blob/main/pypdf/errors.py)
if you prefer something more specific.

## Warnings

The [`warnings` module](https://docs.python.org/3/library/warnings.html) allows
you to ignore warnings:

```python
import warnings

warnings.filterwarnings("ignore")
```

In many cases, you actually want to start Python with the `-W` flag so that you
see all warnings. This is especially true for Continuous Integration (CI).

## Log messages

Log messages can be noisy in some cases. pypdf hopefully has a reasonable
level of log messages, but you can reduce which types of messages you want to
see:

```python
import logging

logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)
```

The [`logging` module](https://docs.python.org/3/library/logging.html#logging-levels)
defines six log levels:

* CRITICAL
* ERROR
* WARNING
* INFO
* DEBUG
* NOTSET
