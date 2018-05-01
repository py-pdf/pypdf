from .pdf import PdfFileReader, PdfFileWriter
from .merger import PdfFileMerger
from .pagerange import PageRange, parse_filename_page_ranges
from ._version import __version__
__all__ = ["pdf", "PdfFileMerger"]

from .perms import PERM_NONE, PERM_ALL, PERM_ASSEMBLE, PERM_COPY, PERM_FILL_FIELDS, PERM_MODIFY, PERM_MODIFY_TEXT, PERM_PRINT