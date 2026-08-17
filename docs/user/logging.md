# Logging

All log messages from `pypdf` go through Python’s standard `logging` library under the logger name `pypdf`. This gives you full control over verbosity, whether you want detailed debug information or only critical errors.

## Filtering logs

You can adjust the minimum log level of pypdf as follow:

```py
import logging
from pypdf import PdfReader

# Get the logger for the pypdf library
# This allows you to configure its logging level independently
logger = logging.getLogger("pypdf")
logger.setLevel(logging.ERROR)

reader = PdfReader("file.pdf")
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
from my_module import reduce_log_level  # Adjust path to your module

# Standard logging level applies
reader = PdfReader("file.pdf")
writer = PdfWriter()

page = reader.pages[0]
writer.add_page(page)

with reduce_log_level(level=logging.ERROR):
    # Adjusted level applies
    # Logs lower than ERROR will be filtered-out
    do_something()

# Original logging level applies
with open("new_file.pdf", "wb") as fp:
    writer.write(fp)
```

## Customizing Log Records

If you prefer to remap log levels (e.g., turn errors into warnings), you can subclass `logging.Logger` as follow:

```py
import logging
from pypdf import PdfReader

class PypdfCustomLogger(logging.Logger):
    def makeRecord(self, name: str, level: int, *args, **kwargs):
        if name == "pypdf":
            level_mapping = {
                logging.NOTSET: logging.NOTSET,
                logging.DEBUG: logging.DEBUG,
                logging.INFO: logging.DEBUG,
                logging.WARNING: logging.INFO,
                logging.ERROR: logging.WARNING,
                logging.CRITICAL: logging.ERROR,
            }
            new_level = level_mapping.get(level, logging.DEBUG)
        else:
            new_level = level

        # Generate a record using the new level defined
        return super().makeRecord(name, new_level, *args, **kwargs)
```

#### Usage:

```py
import logging
from my_module import PypdfCustomLogger  # Adjust path to your module

logging.setLoggerClass(PypdfCustomLogger)
logging.basicConfig()

pdf_logger = logging.getLogger("pypdf")
other_logger = logging.getLogger("other_logger")

# pypdf logger level is adjusted
pdf_logger.info("This will be captured as a DEBUG message.")
pdf_logger.warning("This will be captured as a INFO message.")
pdf_logger.error("This will be captured as a WARNING message.")

# Other loggers are not impacted
other_logger.error("This will be captured as a ERROR message.")
```
