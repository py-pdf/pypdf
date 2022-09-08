# Copyright (c) 2006, Mathieu Fenniak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import warnings
from sys import version_info

from PyPDF2._reader import PdfReader
from PyPDF2._utils import DEPR_MSG, _isString, str_
from PyPDF2._writer import PdfWriter
from PyPDF2.constants import PagesAttributes as PA
from PyPDF2.generic import *
from PyPDF2.pagerange import PageRange

if version_info < (3, 0):
    from cStringIO import StringIO

    StreamIO = StringIO
else:
    from io import BytesIO
    from io import FileIO as file

    StreamIO = BytesIO


class _MergedPage(object):
    """
    _MergedPage is used internally by PdfMerger to collect necessary
    information on each page that is being merged.
    """

    def __init__(self, pagedata, src, id):
        self.src = src
        self.pagedata = pagedata
        self.out_pagedata = None
        self.id = id


class PdfMerger(object):
    """
    Initializes a ``PdfMerger`` object. ``PdfMerger`` merges multiple
    PDFs into a single PDF. It can concatenate, slice, insert, or any
    combination of the above.

    See the functions :meth:`merge()<merge>` (or :meth:`append()<append>`)
    and :meth:`write()<write>` for usage information.

    :param bool strict: Determines whether user should be warned of all
            problems and also causes some correctable problems to be fatal.
            Defaults to ``True``.
    :param bool overwriteWarnings: Determines whether to override Python's
        ``warnings.py`` module with a custom implementation (defaults to
        ``True``). This attribute is deprecated and will be removed.
    """

    def __init__(self, strict=False, overwriteWarnings="deprecated"):
        if overwriteWarnings != "deprecated":
            warnings.warn(
                "The `overwriteWarnings` argument to PdfReader will be removed with PyPDF2 2.0.0.",
                PendingDeprecationWarning,
                stacklevel=2,
            )
        self.inputs = []
        self.pages = []
        self.output = PdfWriter()
        self.bookmarks = []
        self.named_dests = []
        self.id_count = 0
        self.strict = strict
        self.overwriteWarnings = overwriteWarnings

    def merge(
        self, position, fileobj, bookmark=None, pages=None, import_bookmarks=True
    ):
        """
        Merges the pages from the given file into the output file at the
        specified page number.

        :param int position: The *page number* to insert this file. File will
            be inserted after the given number.

        :param fileobj: A File Object or an object that supports the standard
            read and seek methods similar to a File Object. Could also be a
            string representing a path to a PDF file.

        :param str bookmark: Optionally, you may specify a bookmark to be
            applied at the beginning of the included file by supplying the text
            of the bookmark.

        :param pages: can be a :class:`PageRange<PyPDF2.pagerange.PageRange>`
            or a ``(start, stop[, step])`` tuple
            to merge only the specified range of pages from the source
            document into the output document.

        :param bool import_bookmarks: You may prevent the source document's
            bookmarks from being imported by specifying this as ``False``.
        """

        # This parameter is passed to self.inputs.append and means
        # that the stream used was created in this method.
        my_file = False

        # If the fileobj parameter is a string, assume it is a path
        # and create a file object at that location. If it is a file,
        # copy the file's contents into a BytesIO (or StreamIO) stream object; if
        # it is a PdfReader, copy that reader's stream into a
        # BytesIO (or StreamIO) stream.
        # If fileobj is none of the above types, it is not modified
        decryption_key = None
        if _isString(fileobj):
            fileobj = file(fileobj, "rb")
            my_file = True
        elif hasattr(fileobj, "seek") and hasattr(fileobj, "read"):
            fileobj.seek(0)
            filecontent = fileobj.read()
            fileobj = StreamIO(filecontent)
            my_file = True
        elif isinstance(fileobj, PdfReader):
            if hasattr(fileobj, "_decryption_key"):
                decryption_key = fileobj._decryption_key
            orig_tell = fileobj.stream.tell()
            fileobj.stream.seek(0)
            filecontent = StreamIO(fileobj.stream.read())

            # reset the stream to its original location
            fileobj.stream.seek(orig_tell)

            fileobj = filecontent
            my_file = True

        # Create a new PdfReader instance using the stream
        # (either file or BytesIO or StringIO) created above
        reader = PdfReader(
            fileobj, strict=self.strict, overwriteWarnings=self.overwriteWarnings
        )
        if decryption_key is not None:
            reader._decryption_key = decryption_key

        # Find the range of pages to merge.
        if pages is None:
            pages = (0, len(reader.pages))
        elif isinstance(pages, PageRange):
            pages = pages.indices(len(reader.pages))
        elif not isinstance(pages, tuple):
            raise TypeError('"pages" must be a tuple of (start, stop[, step])')

        srcpages = []
        if bookmark:
            bookmark = Bookmark(
                TextStringObject(bookmark),
                NumberObject(self.id_count),
                NameObject("/Fit"),
            )

        outline = []
        if import_bookmarks:
            outline = reader.outlines
            outline = self._trim_outline(reader, outline, pages)

        if bookmark:
            self.bookmarks += [bookmark, outline]
        else:
            self.bookmarks += outline

        dests = reader.named_destinations
        trimmed_dests = self._trim_dests(reader, dests, pages)
        self.named_dests += trimmed_dests

        # Gather all the pages that are going to be merged
        for i in range(*pages):
            pg = reader.pages[i]

            id = self.id_count
            self.id_count += 1

            mp = _MergedPage(pg, reader, id)

            srcpages.append(mp)

        self._associate_dests_to_pages(srcpages)
        self._associate_bookmarks_to_pages(srcpages)

        # Slice to insert the pages at the specified position
        self.pages[position:position] = srcpages

        # Keep track of our input files so we can close them later
        self.inputs.append((fileobj, reader, my_file))

    def append(self, fileobj, bookmark=None, pages=None, import_bookmarks=True):
        """
        Identical to the :meth:`merge()<merge>` method, but assumes you want to
        concatenate all pages onto the end of the file instead of specifying a
        position.

        :param fileobj: A File Object or an object that supports the standard
            read and seek methods similar to a File Object. Could also be a
            string representing a path to a PDF file.

        :param str bookmark: Optionally, you may specify a bookmark to be
            applied at the beginning of the included file by supplying the text
            of the bookmark.

        :param pages: can be a :class:`PageRange<PyPDF2.pagerange.PageRange>`
            or a ``(start, stop[, step])`` tuple
            to merge only the specified range of pages from the source
            document into the output document.

        :param bool import_bookmarks: You may prevent the source document's
            bookmarks from being imported by specifying this as ``False``.
        """
        self.merge(len(self.pages), fileobj, bookmark, pages, import_bookmarks)

    def write(self, fileobj):
        """
        Writes all data that has been merged to the given output file.

        :param fileobj: Output file. Can be a filename or any kind of
            file-like object.
        """
        my_file = False
        if _isString(fileobj):
            fileobj = file(fileobj, "wb")
            my_file = True

        # Add pages to the PdfWriter
        # The commented out line below was replaced with the two lines below it
        # to allow PdfMerger to work with PyPdf 1.13
        for page in self.pages:
            self.output.add_page(page.pagedata)
            page.out_pagedata = self.output.get_reference(
                self.output._pages.get_object()[PA.KIDS][-1].get_object()
            )
            # idnum = self.output._objects.index(self.output._pages.get_object()[PA.KIDS][-1].get_object()) + 1
            # page.out_pagedata = IndirectObject(idnum, 0, self.output)

        # Once all pages are added, create bookmarks to point at those pages
        self._write_dests()
        self._write_bookmarks()

        # Write the output to the file
        self.output.write(fileobj)

        if my_file:
            fileobj.close()

    def close(self):
        """
        Shuts all file descriptors (input and output) and clears all memory
        usage.
        """
        self.pages = []
        for fo, _reader, mine in self.inputs:
            if mine:
                fo.close()

        self.inputs = []
        self.output = None

    def add_metadata(self, infos):
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
            Example: ``{u'/Title': u'My title'}``
        """
        self.output.add_metadata(infos)

    def addMetadata(self, infos):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_metadata` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addMetadata", "add_metadata"), PendingDeprecationWarning
        )
        self.add_metadata(infos)

    def setPageLayout(self, layout):
        """
        .. deprecated:: 1.28.0

            Use :meth:`set_page_layout` instead.
        """
        warnings.warn(
            DEPR_MSG.format("setPageLayout", "set_page_layout"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.set_page_layout(layout)

    def set_page_layout(self, layout):
        """
        Set the page layout

        :param str layout: The page layout to be used

        .. list-table:: Valid ``layout`` arguments
           :widths: 50 200

           * - /NoLayout
             - Layout explicitly not specified
           * - /SinglePage
             - Show one page at a time
           * - /OneColumn
             - Show one column at a time
           * - /TwoColumnLeft
             - Show pages in two columns, odd-numbered pages on the left
           * - /TwoColumnRight
             - Show pages in two columns, odd-numbered pages on the right
           * - /TwoPageLeft
             - Show two pages at a time, odd-numbered pages on the left
           * - /TwoPageRight
             - Show two pages at a time, odd-numbered pages on the right
        """
        self.output._set_page_layout(layout)

    def setPageMode(self, mode):
        """
        .. deprecated:: 1.28.0

            Use :meth:`set_page_mode` instead.
        """
        warnings.warn(
            DEPR_MSG.format("setPageMode", "set_page_mode"), PendingDeprecationWarning
        )
        self.set_page_mode(mode)

    def set_page_mode(self, mode):
        """
        Set the page mode.

        :param str mode: The page mode to use.

        .. list-table:: Valid ``mode`` arguments
           :widths: 50 200

           * - /UseNone
             - Do not show outlines or thumbnails panels
           * - /UseOutlines
             - Show outlines (aka bookmarks) panel
           * - /UseThumbs
             - Show page thumbnails panel
           * - /FullScreen
             - Fullscreen view
           * - /UseOC
             - Show Optional Content Group (OCG) panel
           * - /UseAttachments
             - Show attachments panel
        """
        self.output.set_page_mode(mode)

    def _trim_dests(self, pdf, dests, pages):
        """
        Removes any named destinations that are not a part of the specified
        page set.
        """
        new_dests = []
        for key, obj in dests.items():
            for j in range(*pages):
                if pdf.pages[j].get_object() == obj["/Page"].get_object():
                    obj[NameObject("/Page")] = obj["/Page"].get_object()
                    assert str_(key) == str_(obj["/Title"])
                    new_dests.append(obj)
                    break
        return new_dests

    def _trim_outline(self, pdf, outline, pages):
        """
        Removes any outline/bookmark entries that are not a part of the
        specified page set.
        """
        new_outline = []
        prev_header_added = True
        for i, o in enumerate(outline):
            if isinstance(o, list):
                sub = self._trim_outline(pdf, o, pages)  # type: ignore
                if sub:
                    if not prev_header_added:
                        new_outline.append(outline[i - 1])
                    new_outline.append(sub)  # type: ignore
            else:
                prev_header_added = False
                for j in range(*pages):
                    if pdf.pages[j].get_object() == o["/Page"].get_object():
                        o[NameObject("/Page")] = o["/Page"].get_object()
                        new_outline.append(o)
                        prev_header_added = True
                        break
        return new_outline

    def _write_dests(self):
        for named_dest in self.named_dests:
            pageno = None
            if "/Page" in named_dest:
                for pageno, page in enumerate(self.pages):  # noqa: B007
                    if page.id == named_dest["/Page"]:
                        named_dest[NameObject("/Page")] = page.out_pagedata
                        break

            if pageno is not None:
                self.output.add_named_destination_object(named_dest)

    def _write_bookmarks(self, bookmarks=None, parent=None):
        if bookmarks is None:
            bookmarks = self.bookmarks

        last_added = None
        for bookmark in bookmarks:
            if isinstance(bookmark, list):
                self._write_bookmarks(bookmark, last_added)
                continue

            page_no = None
            if "/Page" in bookmark:
                for page_no, page in enumerate(self.pages):  # noqa: B007
                    if page.id == bookmark["/Page"]:
                        self._write_bookmark_on_page(bookmark, page)
                        break
            if page_no is not None:
                del bookmark["/Page"], bookmark["/Type"]
                last_added = self.output.add_bookmark_dict(bookmark, parent)

    def _write_bookmark_on_page(self, bookmark, page):
        # b[NameObject('/Page')] = p.out_pagedata
        args = [NumberObject(page.id), NameObject(bookmark["/Type"])]
        # nothing more to add
        # if b['/Type'] == '/Fit' or b['/Type'] == '/FitB'
        if bookmark["/Type"] == "/FitH" or bookmark["/Type"] == "/FitBH":
            if "/Top" in bookmark and not isinstance(bookmark["/Top"], NullObject):
                args.append(FloatObject(bookmark["/Top"]))
            else:
                args.append(FloatObject(0))
            del bookmark["/Top"]
        elif bookmark["/Type"] == "/FitV" or bookmark["/Type"] == "/FitBV":
            if "/Left" in bookmark and not isinstance(bookmark["/Left"], NullObject):
                args.append(FloatObject(bookmark["/Left"]))
            else:
                args.append(FloatObject(0))
            del bookmark["/Left"]
        elif bookmark["/Type"] == "/XYZ":
            if "/Left" in bookmark and not isinstance(bookmark["/Left"], NullObject):
                args.append(FloatObject(bookmark["/Left"]))
            else:
                args.append(FloatObject(0))
            if "/Top" in bookmark and not isinstance(bookmark["/Top"], NullObject):
                args.append(FloatObject(bookmark["/Top"]))
            else:
                args.append(FloatObject(0))
            if "/Zoom" in bookmark and not isinstance(bookmark["/Zoom"], NullObject):
                args.append(FloatObject(bookmark["/Zoom"]))
            else:
                args.append(FloatObject(0))
            del bookmark["/Top"], bookmark["/Zoom"], bookmark["/Left"]
        elif bookmark["/Type"] == "/FitR":
            if "/Left" in bookmark and not isinstance(bookmark["/Left"], NullObject):
                args.append(FloatObject(bookmark["/Left"]))
            else:
                args.append(FloatObject(0))
            if "/Bottom" in bookmark and not isinstance(
                bookmark["/Bottom"], NullObject
            ):
                args.append(FloatObject(bookmark["/Bottom"]))
            else:
                args.append(FloatObject(0))
            if "/Right" in bookmark and not isinstance(bookmark["/Right"], NullObject):
                args.append(FloatObject(bookmark["/Right"]))
            else:
                args.append(FloatObject(0))
            if "/Top" in bookmark and not isinstance(bookmark["/Top"], NullObject):
                args.append(FloatObject(bookmark["/Top"]))
            else:
                args.append(FloatObject(0))
            del (
                bookmark["/Left"],
                bookmark["/Right"],
                bookmark["/Bottom"],
                bookmark["/Top"],
            )

        bookmark[NameObject("/A")] = DictionaryObject(
            {NameObject("/S"): NameObject("/GoTo"), NameObject("/D"): ArrayObject(args)}
        )

    def _associate_dests_to_pages(self, pages):
        for nd in self.named_dests:
            pageno = None
            np = nd["/Page"]

            if isinstance(np, NumberObject):
                continue

            for p in pages:
                if np.get_object() == p.pagedata.get_object():
                    pageno = p.id

            if pageno is not None:
                nd[NameObject("/Page")] = NumberObject(pageno)
            else:
                raise ValueError("Unresolved named destination '%s'" % (nd["/Title"],))

    def _associate_bookmarks_to_pages(self, pages, bookmarks=None):
        if bookmarks is None:
            bookmarks = self.bookmarks

        for b in bookmarks:
            if isinstance(b, list):
                self._associate_bookmarks_to_pages(pages, b)
                continue

            pageno = None
            bp = b["/Page"]

            if isinstance(bp, NumberObject):
                continue

            for p in pages:
                if bp.get_object() == p.pagedata.get_object():
                    pageno = p.id

            if pageno is not None:
                b[NameObject("/Page")] = NumberObject(pageno)
            else:
                raise ValueError("Unresolved bookmark '%s'" % (b["/Title"],))

    def findBookmark(self, bookmark, root=None):
        """
        .. deprecated:: 1.28.0
            Use :meth:`find_bookmark` instead.
        """
        warnings.warn(
            "findBookmark is deprecated. Use find_bookmark instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.find_bookmark(bookmark, root=root)

    def find_bookmark(self, bookmark, root=None):
        if root is None:
            root = self.bookmarks

        for i, b in enumerate(root):
            if isinstance(b, list):
                # b is still an inner node
                res = self.find_bookmark(bookmark, b)  # type: ignore
                if res:
                    return [i] + res
            elif b == bookmark or b["/Title"] == bookmark:
                # we found a leaf node
                return [i]

        return None

    def addBookmark(
        self,
        title,
        pagenum,
        parent=None,
        color=None,
        bold=False,
        italic=False,
        fit="/Fit",
        *args
    ):
        """
        .. deprecated:: 1.28.0
            Use :meth:`add_bookmark` instead.
        """
        warnings.warn(
            "addBookmark is deprecated. Use add_bookmark instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_bookmark(
            title, pagenum, parent, color, bold, italic, fit, *args
        )

    def add_bookmark(
        self,
        title,
        pagenum,
        parent=None,
        color=None,
        bold=False,
        italic=False,
        fit="/Fit",
        *args
    ):
        """
        Add a bookmark to this PDF file.

        :param str title: Title to use for this bookmark.
        :param int pagenum: Page number this bookmark will point to.
        :param parent: A reference to a parent bookmark to create nested
            bookmarks.
        :param tuple color: Color of the bookmark as a red, green, blue tuple
            from 0.0 to 1.0
        :param bool bold: Bookmark is bold
        :param bool italic: Bookmark is italic
        :param str fit: The fit of the destination page. See
            :meth:`addLink()<addLin>` for details.
        """
        if len(self.output.get_object(self.output._pages)["/Kids"]) > 0:
            page_ref = self.output.get_object(self.output._pages)["/Kids"][pagenum]
        else:
            page_ref = self.output.get_object(self.output._pages)

        action = DictionaryObject()
        zoom_args = []
        for a in args:
            if a is not None:
                zoom_args.append(NumberObject(a))
            else:
                zoom_args.append(NullObject())
        dest = Destination(
            NameObject("/" + title + " bookmark"), page_ref, NameObject(fit), *zoom_args
        )
        dest_array = dest.dest_array
        action.update(
            {NameObject("/D"): dest_array, NameObject("/S"): NameObject("/GoTo")}
        )
        action_ref = self.output._add_object(action)

        outline_ref = self.output.get_outline_root()

        if parent is None:
            parent = outline_ref

        bookmark = TreeObject()

        bookmark.update(
            {
                NameObject("/A"): action_ref,
                NameObject("/Title"): createStringObject(title),
            }
        )

        if color is not None:
            bookmark.update(
                {NameObject("/C"): ArrayObject([FloatObject(c) for c in color])}
            )

        format = 0
        if italic:
            format += 1
        if bold:
            format += 2
        if format:
            bookmark.update({NameObject("/F"): NumberObject(format)})

        bookmark_ref = self.output._add_object(bookmark)
        parent = parent.get_object()
        parent.add_child(bookmark_ref, self.output)

        return bookmark_ref

    def addNamedDestination(self, title, pagenum):
        """
        .. deprecated:: 1.28.0
            Use :meth:`add_named_destionation` instead.
        """
        warnings.warn(
            "addNamedDestination is deprecated. Use add_named_destionation instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.add_named_destionation(title, pagenum)

    def add_named_destionation(self, title, pagenum):
        """
        Add a destination to the output.

        :param str title: Title to use
        :param int pagenum: Page number this destination points at.
        """

        dest = Destination(
            TextStringObject(title),
            NumberObject(pagenum),
            NameObject("/FitH"),
            NumberObject(826),
        )
        self.named_dests.append(dest)


class OutlinesObject(list):
    def __init__(self, pdf, tree, parent=None):
        warnings.warn(
            "The OutlinesObject class will be removed with PyPDF2 2.0.0",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        list.__init__(self)
        self.tree = tree
        self.pdf = pdf
        self.parent = parent

    def remove(self, index):
        obj = self[index]
        del self[index]
        self.tree.removeChild(obj)

    def add(self, title, pagenum):
        page_ref = self.pdf.get_object(self.pdf._pages)[PA.KIDS][pagenum]
        action = DictionaryObject()
        action.update(
            {
                NameObject("/D"): ArrayObject(
                    [page_ref, NameObject("/FitH"), NumberObject(826)]
                ),
                NameObject("/S"): NameObject("/GoTo"),
            }
        )
        action_ref = self.pdf._addObject(action)
        bookmark = TreeObject()

        bookmark.update(
            {
                NameObject("/A"): action_ref,
                NameObject("/Title"): createStringObject(title),
            }
        )

        self.pdf._addObject(bookmark)

        self.tree.add_child(bookmark)

    def removeAll(self):
        for child in self.tree.children():
            self.tree.removeChild(child)
            self.pop()


class PdfFileMerger(PdfMerger):
    def __init__(self, *args, **kwargs):
        import warnings

        warnings.warn(
            "PdfFileMerger was renamed to PdfMerger. PdfFileMerger will be removed",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        if "strict" not in kwargs and len(args) < 1:
            kwargs["strict"] = True  # maintain the default
        super(PdfFileMerger, self).__init__(*args, **kwargs)
