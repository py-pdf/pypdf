from PyPDF2._reader import DocumentInformation, PdfFileReader, PdfReader
from PyPDF2._version import __version__
from PyPDF2._writer import PdfFileWriter, PdfWriter
from PyPDF2.merger import PdfFileMerger, PdfMerger
from PyPDF2.pagerange import PageRange, parse_filename_page_ranges
from PyPDF2.papersizes import PaperSize

from ._page import Transformation

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
