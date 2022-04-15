"""
See Portable Document Format Reference Manual, 1993. ISBN 0-201-62628-4.

See https://ia802202.us.archive.org/8/items/pdfy-0vt8s-egqFwDl7L2/PDF%20Reference%201.0.pdf
"""

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
    COLOR_SPACE = "/ColorSpace" # Chapter 6.8.5
    XOBJECT = "/XObject"  # Chapter 6.8.6


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

class StreamAttributes:
    """Table 4.2"""
    LENGTH = "/Length"  # integer, required
    FILTER = "/Filter"  # name or array of names, optional
    DECODE_PARAMS = "/DecodeParms"  # variable, optional

class FilterTypes:
    """Table 4.3"""
    ASCII_HEX_DECODE = "/ASCIIHexDecode"
    ASCII_85_DECODE = "/ASCII85Decode"
    LZW_DECODE = "/LZWDecode"
    RUN_LENGTH_DECODE = "/RunLengthDecode"
    CCITT_FAX_DECODE = "/CCITTFaxDecode"
    DCT_DECODE = "/DCTDecode"

PDF_KEYS = [PagesAttributes, PageAttributes, Ressources, ImageAttributes, StreamAttributes, FilterTypes]
