# Adding Viewer Preferences

It is possible to set viewer preferences of a PDF file.
These properties are described in Section 12.2 of the [PDF 1.7 specification](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf).

Note that the `/ViewerPreferences` dictionary does not exist by default.
If it is not already present, it must be created by calling the `create_viewer_preferences` method
of the `PdfWriter` object.

If viewer preferences exist in a PDF file being read with `PdfReader`,
you can access them as properties of `viewer_preferences`.
Otherwise, the `viewer_preferences` property will be set to `None`.

## Example

```python
from pypdf import PdfWriter
from pypdf.generic import ArrayObject, NumberObject

writer = PdfWriter()

writer.create_viewer_preferences()

# /HideToolbar
writer.viewer_preferences.hide_toolbar = True
# /HideMenubar
writer.viewer_preferences.hide_menubar = True
# /HideWindowUI
writer.viewer_preferences.hide_windowui = True
# /FitWindow
writer.viewer_preferences.fit_window = True
# /CenterWindow
writer.viewer_preferences.center_window = True
# /DisplayDocTitle
writer.viewer_preferences.display_doctitle = True

# /NonFullScreenPageMode
writer.viewer_preferences.non_fullscreen_pagemode = "/UseNone"  # default
writer.viewer_preferences.non_fullscreen_pagemode = "/UseOutlines"
writer.viewer_preferences.non_fullscreen_pagemode = "/UseThumbs"
writer.viewer_preferences.non_fullscreen_pagemode = "/UseOC"

# /Direction
writer.viewer_preferences.direction = "/L2R"  # default
writer.viewer_preferences.direction = "/R2L"

# /ViewArea
writer.viewer_preferences.view_area = "/CropBox"
# /ViewClip
writer.viewer_preferences.view_clip = "/CropBox"
# /PrintArea
writer.viewer_preferences.print_area = "/CropBox"
# /PrintClip
writer.viewer_preferences.print_clip = "/CropBox"

# /PrintScaling
writer.viewer_preferences.print_scaling = "/None"
writer.viewer_preferences.print_scaling = "/AppDefault"  # default according to PDF spec

# /Duplex
writer.viewer_preferences.duplex = "/Simplex"
writer.viewer_preferences.duplex = "/DuplexFlipShortEdge"
writer.viewer_preferences.duplex = "/DuplexFlipLongEdge"

# /PickTrayByPDFSize
writer.viewer_preferences.pick_tray_by_pdfsize = True
# /PrintPageRange
writer.viewer_preferences.print_pagerange = ArrayObject(
    [NumberObject("1"), NumberObject("10"), NumberObject("20"), NumberObject("30")]
)
# /NumCopies
writer.viewer_preferences.num_copies = 2

for i in range(40):
    writer.add_blank_page(10, 10)

with open("output.pdf", "wb") as output_stream:
    writer.write(output_stream)
```

The names beginning with a slash character are part of the PDF file format. They are
included here to ease searching the pypdf documentation
for these names from the PDF specification.
