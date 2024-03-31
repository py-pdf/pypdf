# Exceptions, Warnings, and Log messages

PyPDF2 makes use of 3 mechanisms to show that something went wrong:

* **Log messages** are informative messages that can be used for post-mortem
  analysis. Most of the time, users can ignore them. They come in different
  *levels*, such as info / warning / error indicating the severity.
  Examples are non-standard compliant PDF files which PyPDF2 can deal with.
* **Warnings** are avoidable issues, such as using deprecated classes /
  functions / parameters. Another example is missing capabilities of PyPDF2.
  In those cases, PyPDF2 users should adjust their code. Warnings
  are issued by the `warnings` module - those are different from the log-level
  "warning".
* **Exceptions** are error-cases that PyPDF2 users should explicitly handle.
  In the `strict=True` mode, most log messages with the warning level will
  become exceptions. This can be useful in applications where you can force to
  user to fix the broken PDF.


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

The [`warnings` module](https://docs.python.org/3/library/warnings.html) allows
you to ignore warnings:

```python
import warnings

warnings.filterwarnings("ignore")
```

In many cases, you actually want to start Python with the `-W` flag so that you
see all warnings. This is especially true for Continuous Integration (CI).

## Log messages

Log messages can be noisy in some cases. PyPDF2 hopefully is having a reasonable
level of log messages, but you can reduce which types of messages you want to
see:

```python
import logging

logger = logging.getLogger("PyPDF2")
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
