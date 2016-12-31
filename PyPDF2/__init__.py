from .pdf import PdfFileReader, PdfFileWriter
from .merger import PdfFileMerger
from .pagerange import PageRange, parse_filename_page_ranges
from ._version import __version__
__all__ = ["pdf", "PdfFileMerger"]

PERM_NONE = 0
PERM_PRINT = 2
PERM_MODIFY = 4
PERM_COPY_TEXT = 8
PERM_ANNOTATE = 16

PERM_ALL = PERM_PRINT | PERM_MODIFY | PERM_COPY_TEXT | PERM_ANNOTATE