from ._merger import PdfMerger
from ._page import Transformation
from ._reader import DocumentInformation, PdfFileReader, PdfReader
from ._version import __version__
from ._writer import PdfFileWriter, PdfWriter
from .pagerange import PageRange, parse_filename_page_ranges
from .papersizes import PaperSize

__all__ = [
    "__version__",
    "PageRange",
    "PaperSize",
    "DocumentInformation",
    "parse_filename_page_ranges",
    "PdfFileMerger",  # will be removed soon; use PdfMerger instead
    "PdfFileReader",  # will be removed soon; use PdfReader instead
    "PdfFileWriter",  # will be removed soon; use PdfWriter instead
    "PdfMerger",
    "Transformation",
    "PdfReader",
    "PdfWriter",
]
