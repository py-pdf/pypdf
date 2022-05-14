from PyPDF2._security import RC4_encrypt  # noqa: F401
from PyPDF2._utils import *

warnings.warn(
    "The PyPDF2.utils module is deprecated. "
    "Import either from PyPDF2 directly, PyPDF2.errors, or PyPDF2.generic",
    PendingDeprecationWarning,
    stacklevel=2,
)
