"""
See Portable Document Format Reference Manual, 1993. ISBN 0-201-62628-4.

See https://ia802202.us.archive.org/8/items/pdfy-0vt8s-egqFwDl7L2/PDF%20Reference%201.0.pdf

PDF Reference, third edition, Version 1.4, 2001. ISBN 0-201-75839-3.

PDF Reference, sixth edition, Version 1.7, 2006.
"""


class Core:
    """Keywords that don't quite belong anywhere else"""

    OUTLINES = "/Outlines"
    PAGE = "/Page"
    PAGES = "/Pages"
    CATALOG = "/Catalog"


class TrailerKeys:
    ROOT = "/Root"
    ENCRYPT = "/Encrypt"
    ID = "/ID"
    INFO = "/Info"
    SIZE = "/Size"


class CatalogAttributes:
    NAMES = "/Names"
    DESTS = "/Dests"


class PagesAttributes:
    """Page Attributes, Table 6.2, Page 52"""

    TYPE = "/Type"  # name, required; must be /Pages
    KIDS = "/Kids"  # array, required; List of indirect references
    COUNT = "/Count"  # integer, required; the number of all nodes und this node
    PARENT = "/Parent"  # dictionary, required; indirect reference to pages object


class PageAttributes:
    """Page attributes, Table 6.3, Page 53"""

    TYPE = "/Type"  # name, required; must be /Page
    MEDIABOX = "/MediaBox"  # array, required; rectangle specifying page size
    PARENT = "/Parent"  # dictionary, required; a pages object
    RESOURCES = "/Resources"  # dictionary, required if there are any
    CONTENTS = "/Contents"  # stream or array, optional
    CROPBOX = "/CropBox"  # array, optional; rectangle
    ROTATE = "/Rotate"  # integer, optional; page rotation in degrees
    THUMB = "/Thumb"  # stream, optional; indirect reference to image of the page
    ANNOTS = "/Annots"  # array, optional; an array of annotations


class Ressources:
    PROCSET = "/ProcSet"  # Chapter 6.8.1
    FONT = "/Font"  # Chapter 6.8.2
    # encoding
    # font descriptors : 6.8.4
    COLOR_SPACE = "/ColorSpace"  # Chapter 6.8.5
    XOBJECT = "/XObject"  # Chapter 6.8.6


class StreamAttributes:
    """Table 4.2"""

    LENGTH = "/Length"  # integer, required
    FILTER = "/Filter"  # name or array of names, optional
    DECODE_PARMS = "/DecodeParms"  # variable, optional -- 'decodeParams is wrong


class FilterTypes:
    """
    Table 4.3 of the 1.4 Manual

    Page 354 of the 1.7 Manual
    """

    ASCII_HEX_DECODE = "/ASCIIHexDecode"  # abbreviation: AHx
    ASCII_85_DECODE = "/ASCII85Decode"  # abbreviation: A85
    LZW_DECODE = "/LZWDecode"  # abbreviation: LZW
    FLATE_DECODE = "/FlateDecode"  # abbreviation: Fl, PDF 1.2
    RUN_LENGTH_DECODE = "/RunLengthDecode"  # abbreviation: RL
    CCITT_FAX_DECODE = "/CCITTFaxDecode"  # abbreviation: CCF
    DCT_DECODE = "/DCTDecode"  # abbreviation: DCT


class FilterTypeAbbreviations:
    """
    Table 4.44 of the 1.7 Manual (page 353ff)
    """

    AHx = "/AHx"
    A85 = "/A85"
    LZW = "/LZW"
    FL = "/Fl"  # FlateDecode
    RL = "/RL"
    CCF = "/CCF"
    DCT = "/DCT"


class LzwFilterParameters:
    """Table 4.4"""

    PREDICTOR = "/Predictor"  # integer
    COLUMNS = "/Columns"  # integer
    COLORS = "/Colors"  # integer
    BITS_PER_COMPONENT = "/BitsPerComponent"  # integer
    EARLY_CHANGE = "/EarlyChange"  # integer


class CcittFaxDecodeParameters:
    """Table 4.5"""

    K = "/K"  # integer
    END_OF_LINE = "/EndOfLine"  # boolean
    ENCODED_BYTE_ALIGN = "/EncodedByteAlign"  # boolean
    COLUMNS = "/Columns"  # integer
    ROWS = "/Rows"  # integer
    END_OF_BLOCK = "/EndOfBlock"  # boolean
    BLACK_IS_1 = "/BlackIs1"  # boolean
    DAMAGED_ROWS_BEFORE_ERROR = "/DamagedRowsBeforeError"  # integer


class ImageAttributes:
    """Table 6.20."""

    TYPE = "/Type"  # name, required; must be /XObject
    SUBTYPE = "/Subtype"  # name, required; must be /Image
    NAME = "/Name"  # name, required
    WIDTH = "/Width"  # integer, required
    HEIGHT = "/Height"  # integer, required
    BITS_PER_COMPONENT = "/BitsPerComponent"  # integer, required
    COLOR_SPACE = "/ColorSpace"  # name, required
    DECODE = "/Decode"  # array, optional
    INTERPOLATE = "/Interpolate"  # boolean, optional
    IMAGE_MASK = "/ImageMask"  # boolean, optional


class ColorSpaces:
    DEVICE_RGB = "/DeviceRGB"
    DEVICE_CMYK = "/DeviceCMYK"
    DEVICE_GRAY = "/DeviceGray"


class TypArguments:
    """Table 8.2 of the PDF 1.7 reference"""

    LEFT = "/Left"
    RIGHT = "/Right"
    BOTTOM = "/Bottom"
    TOP = "/Top"


class TypFitArguments:
    """Table 8.2 of the PDF 1.7 reference"""

    FIT = "/Fit"
    FIT_V = "/FitV"
    FIT_BV = "/FitBV"
    FIT_B = "/FitB"
    FIT_H = "/FitH"
    FIT_BH = "/FitBH"
    FIT_R = "/FitR"


class PageLayouts:
    """Page 84, PDF 1.4 reference"""

    SINGLE_PAGE = "/SinglePage"
    ONE_COLUMN = "/OneColumn"
    TWO_COLUMN_LEFT = "/TwoColumnLeft"
    TWO_COLUMN_RIGHT = "/TwoColumnRight"


class GraphicsStateParameters:
    """Table 4.8 of the 1.7 reference"""

    TYPE = "/Type"  # name, optional
    LW = "/LW"  # number, optional
    # TODO: Many more!
    FONT = "/Font"  # array, optional
    S_MASK = "/SMask"  # dictionary or name, optional


class CatalogDictionary:
    """Table 3.25 in the 1.7 reference"""

    TYPE = "/Type"  # name, required; must be /Catalog
    # TODO: Many more!


PDF_KEYS = [
    PagesAttributes,
    PageAttributes,
    Ressources,
    ImageAttributes,
    StreamAttributes,
    FilterTypes,
    LzwFilterParameters,
    TypArguments,
    TypFitArguments,
    PageLayouts,
    GraphicsStateParameters,
    CatalogDictionary,
    Core,
    TrailerKeys,
    CatalogAttributes,
]
