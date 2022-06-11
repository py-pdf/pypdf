from ._merger import PdfFileMerger, PdfMerger
from ._page import Transformation, PageObject
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
    "PdfFileMerger",  # will be removed in PyPDF2 3.0.0; use PdfMerger instead
    "PdfFileReader",  # will be removed in PyPDF2 3.0.0; use PdfReader instead
    "PdfFileWriter",  # will be removed in PyPDF2 3.0.0; use PdfWriter instead
    "PdfMerger",
    "PdfReader",
    "PdfWriter",
    "Transformation",
    "PageObject",
]
