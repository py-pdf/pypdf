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
    
