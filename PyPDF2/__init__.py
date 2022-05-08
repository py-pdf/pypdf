from PyPDF2 import pdf
from PyPDF2._reader import PdfFileReader, PdfReader
from PyPDF2._version import __version__
from PyPDF2._writer import PdfFileWriter, PdfWriter
from PyPDF2.merger import PdfFileMerger, PdfMerger
from PyPDF2.pagerange import PageRange, parse_filename_page_ranges
from PyPDF2.papersizes import PaperSize

__all__ = [
    "__version__",
    "PageRange",
    "PaperSize",
    "parse_filename_page_ranges",
    "pdf",
    "PdfFileMerger",  # will be deprecated soon; use PdfMerger instead
    "PdfFileReader",  # will be deprecated soon; use PdfReader instead
    "PdfFileWriter",  # will be deprecated soon; use PdfWriter instead
    "PdfMerger",
    "PdfReader",
    "PdfWriter",
]
