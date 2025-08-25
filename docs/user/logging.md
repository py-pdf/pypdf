# Logging

All log messages from `pypdf` go through Python’s standard `logging` library under the logger name `pypdf`. This gives you full control over verbosity, whether you want detailed debug information or only critical errors.

## Filtering logs

You can adjust the minimum log level of pypdf as follow:

```py
import logging
from pypdf import PdfReader


logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)  # <--- set the minimum level expected

reader = PdfReader('file.pdf')
```

## Temporarily Reducing Log Noise

If you only want to suppress logs during a specific operation, you can wrap that code in a context manager:

```py
import logging
from contextlib import contextmanager


@contextmanager
def reduce_log_level(level=logging.ERROR):
    logger = logging.getLogger("pypdf")
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)
```

#### Usage:

```py
from pypdf import PdfReader, PdfWriter
from my_module import reduce_log_level  # adjust path to your module

# Standard logging level applies
reader = PdfReader("file.pdf")
writer = PdfWriter()

page = reader.pages[0]
writer.add_page(page)

with reduce_log_level(level=logging.ERROR):
    # Example: ignore warnings when adding annotations
    for page, annotation in annotations:  # annotations must be defined
        writer.add_annotation(page_number=page, annotation=annotation)

with open("new_file.pdf", "wb") as fp:
    writer.write(fp)
```

## Customizing Log Records

If you prefer to remap log levels (e.g., turn errors into warnings), you can subclass `logging.Logger` as follow:

```py
import logging
from pypdf import PdfReader

class PypdfCustomLogger(logging.Logger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
        if name == 'pypdf':
            level_mapping = {
                logging.NOTSET: logging.NOTSET,
                logging.DEBUG: logging.DEBUG,
                logging.INFO: logging.DEBUG,
                logging.WARNING: logging.INFO,
                logging.ERROR: logging.WARNING,
                logging.CRITICAL: logging.ERROR
            }
            level = level_mapping.get(level, logging.DEBUG)
        return super().makeRecord(name, new_level, fn, lno, msg, args, exc_info, func, extra, sinfo)
```

#### Usage:

```py
import logging
from my_module import PypdfCustomLogger  # adjust path to your module

logging.setLoggerClass(PypdfCustomLogger)
logging.basicConfig()

pdf_logger = logging.getLogger('pypdf')
myapp_logger = logging.getLogger('myapp')

# pypdf logger level is adjusted
pdf_logger.info("This will be captured as a DEBUG message.")
pdf_logger.warning("This will be captured as a INFO message.")
pdf_logger.error("This will be captured as a WARNING message.")

# other loggers are not impacted.
myapp_logger.error("This will be captured as a ERROR message.")
```
