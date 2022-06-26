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

from io import BytesIO, FileIO, IOBase
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, cast

from ._encryption import Encryption
from ._page import PageObject
from ._reader import PdfReader
from ._utils import StrByteType, deprecate_with_replacement, str_
from ._writer import PdfWriter
from .constants import PagesAttributes as PA
from .generic import (
    ArrayObject,
    Bookmark,
    Destination,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    TextStringObject,
    TreeObject,
)
from .pagerange import PageRange, PageRangeSpec
from .types import (
    BookmarkTypes,
    FitType,
    LayoutType,
    OutlinesType,
    PagemodeType,
    ZoomArgType,
)

ERR_CLOSED_WRITER = "close() was called and thus the writer cannot be used anymore"


class _MergedPage:
    """
    _MergedPage is used internally by PdfMerger to collect necessary
    information on each page that is being merged.
    """

    def __init__(self, pagedata: PageObject, src: PdfReader, id: int) -> None:
        self.src = src
        self.pagedata = pagedata
        self.out_pagedata = None
        self.id = id


class PdfMerger:
    """
    Initializes a ``PdfMerger`` object. ``PdfMerger`` merges multiple
    PDFs into a single PDF. It can concatenate, slice, insert, or any
    combination of the above.

    See the functions :meth:`merge()<merge>` (or :meth:`append()<append>`)
    and :meth:`write()<write>` for usage information.

    :param bool strict: Determines whether user should be warned of all
            problems and also causes some correctable problems to be fatal.
            Defaults to ``False``.
    """

    def __init__(self, strict: bool = False) -> None:
        self.inputs: List[Tuple[Any, PdfReader, bool]] = []
        self.pages: List[Any] = []
        self.output: Optional[PdfWriter] = PdfWriter()
        self.bookmarks: OutlinesType = []
        self.named_dests: List[Any] = []
        self.id_count = 0
        self.strict = strict

    def merge(
        self,
        position: int,
        fileobj: Union[StrByteType, PdfReader],
        bookmark: Optional[str] = None,
        pages: Optional[PageRangeSpec] = None,
        import_bookmarks: bool = True,
    ) -> None:
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

        stream, my_file, encryption_obj = self._create_stream(fileobj)

        # Create a new PdfReader instance using the stream
        # (either file or BytesIO or StringIO) created above
        reader = PdfReader(stream, strict=self.strict)  # type: ignore[arg-type]
        self.inputs.append((stream, reader, my_file))
        if encryption_obj is not None:
            reader._encryption = encryption_obj

        # Find the range of pages to merge.
        if pages is None:
            pages = (0, len(reader.pages))
        elif isinstance(pages, PageRange):
            pages = pages.indices(len(reader.pages))
        elif not isinstance(pages, tuple):
            raise TypeError('"pages" must be a tuple of (start, stop[, step])')

        srcpages = []

        outline = []
        if import_bookmarks:
            outline = reader.outlines
            outline = self._trim_outline(reader, outline, pages)

        if bookmark:
            bookmark_typ = Bookmark(
                TextStringObject(bookmark),
                NumberObject(self.id_count),
                NameObject("/Fit"),
            )
            self.bookmarks += [bookmark_typ, outline]  # type: ignore
        else:
            self.bookmarks += outline

        dests = reader.named_destinations
        trimmed_dests = self._trim_dests(reader, dests, pages)
        self.named_dests += trimmed_dests

        # Gather all the pages that are going to be merged
        for i in range(*pages):
            page = reader.pages[i]

            id = self.id_count
            self.id_count += 1

            mp = _MergedPage(page, reader, id)

            srcpages.append(mp)

        self._associate_dests_to_pages(srcpages)
        self._associate_bookmarks_to_pages(srcpages)

        # Slice to insert the pages at the specified position
        self.pages[position:position] = srcpages

    def _create_stream(
        self, fileobj: Union[StrByteType, PdfReader]
    ) -> Tuple[IOBase, bool, Optional[Encryption]]:
        # This parameter is passed to self.inputs.append and means
        # that the stream used was created in this method.
        my_file = False

        # If the fileobj parameter is a string, assume it is a path
        # and create a file object at that location. If it is a file,
        # copy the file's contents into a BytesIO stream object; if
        # it is a PdfReader, copy that reader's stream into a
        # BytesIO stream.
        # If fileobj is none of the above types, it is not modified
        encryption_obj = None
        stream: IOBase
        if isinstance(fileobj, str):
            stream = FileIO(fileobj, "rb")
            my_file = True
        elif isinstance(fileobj, PdfReader):
            if fileobj._encryption:
                encryption_obj = fileobj._encryption
            orig_tell = fileobj.stream.tell()
            fileobj.stream.seek(0)
            stream = BytesIO(fileobj.stream.read())

            # reset the stream to its original location
            fileobj.stream.seek(orig_tell)

            my_file = True
        elif hasattr(fileobj, "seek") and hasattr(fileobj, "read"):
            fileobj.seek(0)
            filecontent = fileobj.read()
            stream = BytesIO(filecontent)
            my_file = True
        else:
            stream = fileobj
        return stream, my_file, encryption_obj

    def append(
        self,
        fileobj: Union[StrByteType, PdfReader],
        bookmark: Optional[str] = None,
        pages: Union[None, PageRange, Tuple[int, int], Tuple[int, int, int]] = None,
        import_bookmarks: bool = True,
    ) -> None:
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

    def write(self, fileobj: StrByteType) -> None:
        """
        Writes all data that has been merged to the given output file.

        :param fileobj: Output file. Can be a filename or any kind of
            file-like object.
        """
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        my_file = False
        if isinstance(fileobj, str):
            fileobj = FileIO(fileobj, "wb")
            my_file = True

        # Add pages to the PdfWriter
        # The commented out line below was replaced with the two lines below it
        # to allow PdfMerger to work with PyPdf 1.13
        for page in self.pages:
            self.output.add_page(page.pagedata)
            pages_obj = cast(Dict[str, Any], self.output._pages.get_object())
            page.out_pagedata = self.output.get_reference(
                pages_obj[PA.KIDS][-1].get_object()
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

    def close(self) -> None:
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

    def add_metadata(self, infos: Dict[str, Any]) -> None:
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
            Example: ``{u'/Title': u'My title'}``
        """
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        self.output.add_metadata(infos)

    def addMetadata(self, infos: Dict[str, Any]) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_metadata` instead.
        """
        deprecate_with_replacement("addMetadata", "add_metadata")
        self.add_metadata(infos)

    def setPageLayout(self, layout: LayoutType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`set_page_layout` instead.
        """
        deprecate_with_replacement("setPageLayout", "set_page_layout")
        self.set_page_layout(layout)

    def set_page_layout(self, layout: LayoutType) -> None:
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
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        self.output._set_page_layout(layout)

    def setPageMode(self, mode: PagemodeType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`set_page_mode` instead.
        """
        deprecate_with_replacement("setPageMode", "set_page_mode")
        self.set_page_mode(mode)

    def set_page_mode(self, mode: PagemodeType) -> None:
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
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        self.output.set_page_mode(mode)

    def _trim_dests(
        self,
        pdf: PdfReader,
        dests: Dict[str, Dict[str, Any]],
        pages: Union[Tuple[int, int], Tuple[int, int, int]],
    ) -> List[Dict[str, Any]]:
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

    def _trim_outline(
        self,
        pdf: PdfReader,
        outline: OutlinesType,
        pages: Union[Tuple[int, int], Tuple[int, int, int]],
    ) -> OutlinesType:
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
                    if o["/Page"] is None:
                        continue
                    if pdf.pages[j].get_object() == o["/Page"].get_object():
                        o[NameObject("/Page")] = o["/Page"].get_object()
                        new_outline.append(o)
                        prev_header_added = True
                        break
        return new_outline

    def _write_dests(self) -> None:
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        for named_dest in self.named_dests:
            pageno = None
            if "/Page" in named_dest:
                for pageno, page in enumerate(self.pages):  # noqa: B007
                    if page.id == named_dest["/Page"]:
                        named_dest[NameObject("/Page")] = page.out_pagedata
                        break

            if pageno is not None:
                self.output.add_named_destination_object(named_dest)

    def _write_bookmarks(
        self,
        bookmarks: Optional[Iterable[Bookmark]] = None,
        parent: Optional[TreeObject] = None,
    ) -> None:
        if self.output is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        if bookmarks is None:
            bookmarks = self.bookmarks  # type: ignore
        assert bookmarks is not None, "hint for mypy"  # TODO: is that true?

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

    def _write_bookmark_on_page(
        self, bookmark: Union[Bookmark, Destination], page: _MergedPage
    ) -> None:
        # b[NameObject('/Page')] = p.out_pagedata
        bm_type = cast(BookmarkTypes, bookmark["/Type"])
        args = [NumberObject(page.id), NameObject(bm_type)]
        # nothing more to add
        # if b['/Type'] == '/Fit' or b['/Type'] == '/FitB'
        if bm_type == "/FitH" or bm_type == "/FitBH":
            if "/Top" in bookmark and not isinstance(bookmark["/Top"], NullObject):
                args.append(FloatObject(bookmark["/Top"]))
            else:
                args.append(FloatObject(0))
            del bookmark["/Top"]
        elif bm_type == "/FitV" or bm_type == "/FitBV":
            if "/Left" in bookmark and not isinstance(bookmark["/Left"], NullObject):
                args.append(FloatObject(bookmark["/Left"]))
            else:
                args.append(FloatObject(0))
            del bookmark["/Left"]
        elif bm_type == "/XYZ":
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
        elif bm_type == "/FitR":
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

    def _associate_dests_to_pages(self, pages: List[_MergedPage]) -> None:
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
                raise ValueError(f"Unresolved named destination '{nd['/Title']}'")

    def _associate_bookmarks_to_pages(
        self, pages: List[_MergedPage], bookmarks: Optional[Iterable[Bookmark]] = None
    ) -> None:
        if bookmarks is None:
            bookmarks = self.bookmarks  # type: ignore # TODO: self.bookmarks can be None!
        assert bookmarks is not None, "hint for mypy"
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
                raise ValueError(f"Unresolved bookmark '{b['/Title']}'")

    def find_bookmark(
        self,
        bookmark: Dict[str, Any],
        root: Optional[OutlinesType] = None,
    ) -> Optional[List[int]]:
        if root is None:
            root = self.bookmarks

        for i, b in enumerate(root):
            if isinstance(b, list):
                # b is still an inner node
                # (OutlinesType, if recursive types were supported by mypy)
                res = self.find_bookmark(bookmark, b)  # type: ignore
                if res:
                    return [i] + res
            elif b == bookmark or b["/Title"] == bookmark:
                # we found a leaf node
                return [i]

        return None

    def addBookmark(
        self,
        title: str,
        pagenum: int,
        parent: Union[None, TreeObject, IndirectObject] = None,
        color: Optional[Tuple[float, float, float]] = None,
        bold: bool = False,
        italic: bool = False,
        fit: FitType = "/Fit",
        *args: ZoomArgType,
    ) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0
            Use :meth:`add_bookmark` instead.
        """
        deprecate_with_replacement("addBookmark", "add_bookmark")
        return self.add_bookmark(
            title, pagenum, parent, color, bold, italic, fit, *args
        )

    def add_bookmark(
        self,
        title: str,
        pagenum: int,
        parent: Union[None, TreeObject, IndirectObject] = None,
        color: Optional[Tuple[float, float, float]] = None,
        bold: bool = False,
        italic: bool = False,
        fit: FitType = "/Fit",
        *args: ZoomArgType,
    ) -> IndirectObject:
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
            :meth:`addLink()<addLink>` for details.
        """
        writer = self.output
        if writer is None:
            raise RuntimeError(ERR_CLOSED_WRITER)
        return writer.add_bookmark(
            title, pagenum, parent, color, bold, italic, fit, *args
        )

    def addNamedDestination(self, title: str, pagenum: int) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0
            Use :meth:`add_named_destination` instead.
        """
        deprecate_with_replacement("addNamedDestination", "add_named_destination")
        return self.add_named_destination(title, pagenum)

    def add_named_destination(self, title: str, pagenum: int) -> None:
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


class PdfFileMerger(PdfMerger):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        deprecate_with_replacement("PdfFileMerger", "PdfMerge")

        if "strict" not in kwargs and len(args) < 1:
            kwargs["strict"] = True  # maintain the default
        super().__init__(*args, **kwargs)
