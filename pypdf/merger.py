# vim: sw=4:expandtab:foldmethod=marker
#
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
from sys import version_info

from .generic import *
from .pagerange import PageRange
from .pdf import PdfFileReader, PdfFileWriter
from .utils import isString, pypdfStr

if version_info < (3, 0):
    from cStringIO import StringIO
    StreamIO = StringIO
else:
    from io import BytesIO
    from io import FileIO as file
    StreamIO = BytesIO


class _MergedPage(object):
    """
    _MergedPage is used internally by PdfFileMerger to collect necessary
    information on each page that is being merged.
    """
    def __init__(self, pagedata, src, id):
        self.src = src
        self.pagedata = pagedata
        self.out_pagedata = None
        self.id = id


class PdfFileMerger(object):
    """
    Initializes a PdfFileMerger object. PdfFileMerger merges multiple PDFs
    into a single PDF. It can concatenate, slice, insert, or any combination
    of the above.

    See the functions :meth:`merge()<merge>` (or :meth:`append()<append>`)
    and :meth:`write()<write>` for usage information.

    :param bool strict: Determines whether user should be warned of all
            problems and also causes some correctable problems to be fatal.
            Defaults to ``True``.
    """

    def __init__(self, strict=True):
        # TO-DO Add a stream parameter to __init__()
        self.strict = strict
        self._inputs = []
        self._pages = []
        self._writer = PdfFileWriter()
        self._bookmarks = []
        self._namedDests = []
        self._idCount = 0

    def merge(
            self, position, fileobj, bookmark=None, pages=None,
            importBookmarks=True
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
        :param pages: can be a :ref:`Page Range <page-range>` or a
            ``(start, stop[, step])`` tuple to merge only the specified range
            of pages from the source document into the output document.
        :param bool importBookmarks: You may prevent the source document's
            bookmarks from being imported by specifying this as ``False``.
        """
        # This parameter is passed to self._inputs.append and means
        # that the stream used was created in this method.
        myFile = False

        # If the fileobj parameter is a string, assume it is a path
        # and open a file object at that location. If it is a file,
        # copy the file's contents into a BytesIO (or StreamIO) stream object;
        # if it is a PdfFileReader, copy that reader's stream into a BytesIO
        # (or StreamIO) stream.
        # If fileobj is none of the above types, it is not modified
        decryptionKey = None

        if isString(fileobj):
            fileobj = file(fileobj, 'rb')
            myFile = True
        elif hasattr(fileobj, "seek") and hasattr(fileobj, "read"):
            fileobj.seek(0)
            filecontent = fileobj.read()
            fileobj = StreamIO(filecontent)
            myFile = True
        elif isinstance(fileobj, PdfFileReader):
            origTell = fileobj.stream.tell()
            fileobj.stream.seek(0)
            filecontent = StreamIO(fileobj.stream.read())
            # Reset the stream to its original location
            fileobj.stream.seek(origTell)
            fileobj = filecontent

            if hasattr(fileobj, '_decryption_key'):
                decryptionKey = fileobj._decryption_key

            myFile = True

        # Create a new PdfFileReader instance using the stream
        # (either file or BytesIO or StringIO) created above
        pdfr = PdfFileReader(fileobj, strict=self.strict)
        if decryptionKey is not None:
            pdfr._decryption_key = decryptionKey

        # Find the range of pages to merge.
        if pages is None:
            pages = (0, pdfr.getNumPages())
        elif isinstance(pages, PageRange):
            pages = pages.indices(pdfr.getNumPages())
        elif not isinstance(pages, tuple):
            raise TypeError('"pages" must be a tuple of (start, stop[, step])')

        srcpages = []
        if bookmark:
            bookmark = Bookmark(
                TextStringObject(bookmark), NumberObject(self._idCount),
                NameObject('/Fit')
            )

        outline = []

        if importBookmarks:
            outline = pdfr.getOutlines()
            outline = self._trimOutline(pdfr, outline, pages)
        if bookmark:
            self._bookmarks += [bookmark, outline]
        else:
            self._bookmarks += outline

        dests = pdfr.namedDestinations
        dests = self._trimDests(pdfr, dests, pages)
        self._namedDests += dests

        # Gather all the pages that are going to be merged
        for i in range(*pages):
            pg = pdfr.getPage(i)

            id = self._idCount
            self._idCount += 1

            mp = _MergedPage(pg, pdfr, id)

            srcpages.append(mp)

        self._associateDestsToPages(srcpages)
        self._associateBookmarksToPages(srcpages)

        # Slice to insert the pages at the specified position
        self._pages[position:position] = srcpages

        # Keep track of our input files so we can close them later
        self._inputs.append((fileobj, pdfr, myFile))

    def append(self, fileobj, bookmark=None, pages=None, importBookmarks=True):
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
        :param pages: can be a :ref:`Page Range <page-range>` or a
            ``(start, stop[, step])`` tuple to merge only the specified range
            of pages from the source document into the output document.
        :param bool importBookmarks: You may prevent the source document's
            bookmarks from being imported by specifying this as ``False``.
        """
        self.merge(len(self._pages), fileobj, bookmark, pages, importBookmarks)

    def write(self, fileobj):
        """
        Writes all data that has been merged to the given output file.

        :param fileobj: Output file. Can be a filename or any kind of file-like
            object.
        """
        myFile = False

        if isString(fileobj):
            fileobj = file(fileobj, 'wb')
            myFile = True

        # Add pages to the PdfFileWriter
        # The commented out line below was replaced with the two lines below it
        # to allow PdfFileMerger to work with PyPdf 1.13
        for page in self._pages:
            self._writer.addPage(page.pagedata)
            page.out_pagedata = self._writer.getReference(
                self._writer._pages.getObject()["/Kids"][-1].getObject()
            )

        # Once all pages are added, create bookmarks to point at those pages
        self._writeDests()
        self._writeBookmarks()

        # Write the output to the file
        # TO-DO Remove argument to write()
        self.output.write(fileobj)

        if myFile:
            fileobj.close()

    def close(self):
        """
        Shuts all file descriptors (input and output) and clears all memory
        usage.
        """
        self._pages = []

        for fo, pdfr, mine in self._inputs:
            if mine:
                fo.close()

        self._inputs = []
        del self._writer

    def addMetadata(self, infos):
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field and
            each value is your new metadata.
            Example: ``{u'/Title': u'My title'}``.
        """
        self._writer.addMetadata(infos)

    def setPageLayout(self, layout):
        """
        Set the page layout

        :param str layout: The page layout to be used

        Valid layouts are:
             /NoLayout        Layout explicitly not specified
             /SinglePage      Show one page at a time
             /OneColumn       Show one column at a time
             /TwoColumnLeft   Show pages in two columns, odd-numbered pages on
                 the left
             /TwoColumnRight  Show pages in two columns, odd-numbered pages on
                 the right
             /TwoPageLeft     Show two pages at a time, odd-numbered pages on
                 the left
             /TwoPageRight    Show two pages at a time, odd-numbered pages on
                 the right
        """
        self._writer.setPageLayout(layout)

    def setPageMode(self, mode):
        """
        Set the page mode.

        :param str mode: The page mode to use.

        Valid modes are:
            /UseNone         Do not show outlines or thumbnails panels
            /UseOutlines     Show outlines (aka bookmarks) panel
            /UseThumbs       Show page thumbnails panel
            /FullScreen      Full screen view
            /UseOC           Show Optional Content Group (OCG) panel
            /UseAttachments  Show attachments panel
        """
        self._writer.setPageMode(mode)

    def _trimDests(self, pdf, dests, pages):
        """
        Removes any named destinations that are not a part of the specified
        page set.
        """
        newDests = []
        prev_header_added = True

        for k, o in list(dests.items()):
            for j in range(*pages):
                if pdf.getPage(j).getObject() == o['/Page'].getObject():
                    o[NameObject('/Page')] = o['/Page'].getObject()
                    assert pypdfStr(k) == pypdfStr(o['/Title'])
                    newDests.append(o)
                    break

        return newDests

    def _trimOutline(self, pdf, outline, pages):
        """
        Removes any outline/bookmark entries that are not a part of the
        specified page set.
        """
        newOutline = []
        prevHeaderAdded = True

        for i, o in enumerate(outline):
            if isinstance(o, list):
                sub = self._trimOutline(pdf, o, pages)
                if sub:
                    if not prevHeaderAdded:
                        newOutline.append(outline[i-1])
                    newOutline.append(sub)
            else:
                prevHeaderAdded = False
                for j in range(*pages):
                    if pdf.getPage(j).getObject() == o['/Page'].getObject():
                        o[NameObject('/Page')] = o['/Page'].getObject()
                        newOutline.append(o)
                        prevHeaderAdded = True
                        break

        return newOutline

    def _writeDests(self):
        dests = self._namedDests

        for v in dests:
            pageno = None
            pdf = None

            if '/Page' in v:
                for i, p in enumerate(self._pages):
                    if p.id == v['/Page']:
                        v[NameObject('/Page')] = p.out_pagedata
                        pageno = i
                        pdf = p.src
                        break

            if pageno is not None:
                self._writer.addNamedDestinationObject(v)

    def _writeBookmarks(self, bookmarks=None, parent=None):
        if bookmarks is None:
            bookmarks = self._bookmarks

        last_added = None
        for b in bookmarks:
            if isinstance(b, list):
                self._writeBookmarks(b, last_added)
                continue

            pageno = None
            pdf = None

            if '/Page' in b:
                for i, p in enumerate(self._pages):
                    if p.id == b['/Page']:
                        args = [NumberObject(p.id), NameObject(b['/Type'])]
                        # Nothing more to add
                        if b['/Type'] == '/FitH' or b['/Type'] == '/FitBH':
                            if '/Top' in b and not\
                                    isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Top']
                        elif b['/Type'] == '/FitV' or b['/Type'] == '/FitBV':
                            if '/Left' in b and not\
                                    isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Left']
                        elif b['/Type'] == '/XYZ':
                            if '/Left' in b and not\
                                    isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            if '/Top' in b and not\
                                    isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            if '/Zoom' in b and not \
                                    isinstance(b['/Zoom'], NullObject):
                                args.append(FloatObject(b['/Zoom']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Top'], b['/Zoom'], b['/Left']
                        elif b['/Type'] == '/FitR':
                            if '/Left' in b and not\
                                    isinstance(b['/Left'], NullObject):
                                args.append(FloatObject(b['/Left']))
                            else:
                                args.append(FloatObject(0))
                            if '/Bottom' in b and not\
                                    isinstance(b['/Bottom'], NullObject):
                                args.append(FloatObject(b['/Bottom']))
                            else:
                                args.append(FloatObject(0))
                            if '/Right' in b and not\
                                    isinstance(b['/Right'], NullObject):
                                args.append(FloatObject(b['/Right']))
                            else:
                                args.append(FloatObject(0))
                            if '/Top' in b and not\
                                    isinstance(b['/Top'], NullObject):
                                args.append(FloatObject(b['/Top']))
                            else:
                                args.append(FloatObject(0))
                            del b['/Left'], b['/Right'], b['/Bottom'],\
                                b['/Top']

                        b[NameObject('/A')] = DictionaryObject({
                            NameObject('/S'): NameObject('/GoTo'),
                            NameObject('/D'): ArrayObject(args)
                        })

                        pageno = i
                        pdf = p.src
                        break
            if pageno is not None:
                del b['/Page'], b['/Type']
                last_added = self._writer.addBookmarkDict(b, parent)

    def _associateDestsToPages(self, pages):
        for nd in self._namedDests:
            pageno = None
            np = nd['/Page']

            if isinstance(np, NumberObject):
                continue

            for p in pages:
                if np.getObject() == p.pagedata.getObject():
                    pageno = p.id

            if pageno is not None:
                nd[NameObject('/Page')] = NumberObject(pageno)
            else:
                raise ValueError(
                    "Unresolved named destination '%s'" % nd['/Title']
                )

    def _associateBookmarksToPages(self, pages, bookmarks=None):
        if bookmarks is None:
            bookmarks = self._bookmarks

        for b in bookmarks:
            if isinstance(b, list):
                self._associateBookmarksToPages(pages, b)
                continue

            pageno = None
            bp = b['/Page']

            if isinstance(bp, NumberObject):
                continue

            for p in pages:
                if bp.getObject() == p.pagedata.getObject():
                    pageno = p.id

            if pageno is not None:
                b[NameObject('/Page')] = NumberObject(pageno)
            else:
                raise ValueError("Unresolved bookmark '%s'" % b['/Title'])

    def findBookmark(self, bookmark, root=None):
        if root is None:
            root = self._bookmarks

        for i, b in enumerate(root):
            if isinstance(b, list):
                res = self.findBookmark(bookmark, b)
                if res:
                    return [i] + res
            elif b == bookmark or b['/Title'] == bookmark:
                return [i]

        return None

    def addBookmark(self, title, pagenum, parent=None):
        """
        Add a bookmark to this PDF file.

        :param str title: Title to use for this bookmark.
        :param int pagenum: Page number this bookmark will point to.
        :param parent: A reference to a parent bookmark to create nested
            bookmarks.
        """
        if parent is None:
            iloc = [len(self._bookmarks) - 1]
        elif isinstance(parent, list):
            iloc = parent
        else:
            iloc = self.findBookmark(parent)

        dest = Bookmark(
            TextStringObject(title), NumberObject(pagenum),
            NameObject('/FitH'), NumberObject(826)
        )

        if parent is None:
            self._bookmarks.append(dest)
        else:
            bmparent = self._bookmarks

            for i in iloc[:-1]:
                bmparent = bmparent[i]
            npos = iloc[-1]+1

            if npos < len(bmparent) and isinstance(bmparent[npos], list):
                bmparent[npos].append(dest)
            else:
                bmparent.insert(npos, [dest])

        return dest

    def addNamedDestination(self, title, pagenum):
        """
        Add a destination to the output.

        :param str title: Title to use.
        :param int pagenum: Page number this destination points at.
        """

        dest = Destination(
            TextStringObject(title), NumberObject(pagenum),
            NameObject('/FitH'), NumberObject(826)
        )
        self._namedDests.append(dest)


class OutlinesObject(list):
    def __init__(self, pdf, tree, parent=None):
        list.__init__(self)
        self.tree = tree
        self.pdf = pdf
        self.parent = parent

    def remove(self, index):
        obj = self[index]
        del self[index]
        self.tree.removeChild(obj)

    def add(self, title, pagenum):
        pageRef = self.pdf.getObject(self.pdf._pages)['/Kids'][pagenum]
        action = DictionaryObject()
        action.update({
            NameObject('/D'): ArrayObject(
                [pageRef, NameObject('/FitH'), NumberObject(826)]
            ), NameObject('/S'): NameObject('/GoTo')
        })
        actionRef = self.pdf._addObject(action)
        bookmark = TreeObject()

        bookmark.update({
            NameObject('/A'): actionRef,
            NameObject('/Title'): createStringObject(title),
        })

        self.pdf._addObject(bookmark)

        self.tree.addChild(bookmark)

    def removeAll(self):
        for child in [x for x in self.tree.children()]:
            self.tree.removeChild(child)
            self.pop()
