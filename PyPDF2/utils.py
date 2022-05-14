from PyPDF2._security import RC4_encrypt  # noqa: F401
from PyPDF2._utils import *

warnings.warn(
    "`PyPDF2.utils` will be removed with PyPDF2 2.0.0",
    PendingDeprecationWarning,
)
