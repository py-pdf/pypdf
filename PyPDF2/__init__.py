from PyPDF2 import pdf
from PyPDF2._reader import PdfFileReader
from PyPDF2._version import __version__
from PyPDF2._writer import PdfFileWriter
from PyPDF2.merger import PdfFileMerger
from PyPDF2.pagerange import PageRange, parse_filename_page_ranges
from PyPDF2.papersizes import PaperSize

__all__ = [
    "__version__",
    "PageRange",
    "PaperSize",
    "parse_filename_page_ranges",
    "pdf",
    "PdfFileMerger",
    "PdfFileReader",
    "PdfFileWriter",
]
