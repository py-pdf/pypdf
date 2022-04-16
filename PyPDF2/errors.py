class PyPdfError(Exception):
    pass


class PdfReadError(PyPdfError):
    pass


class PageSizeNotDefinedError(PyPdfError):
    pass


class PdfReadWarning(UserWarning):
    pass


class PdfStreamError(PdfReadError):
    pass


class ParseError(Exception):
    pass


STREAM_TRUNCATED_PREMATURELY = "Stream has ended unexpectedly"
