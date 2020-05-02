# -*- coding: utf-8 -*-
#
# vim: sw=4:expandtab:foldmethod=marker
#
# Copyright (c) 2006, Mathieu Fenniak
# Copyright (c) 2007, Ashish Kulkarni <kulkarni.ashish@gmail.com>
#
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
"""
A pure-Python PDF library with an increasing number of capabilities.
See README.md for links to FAQ, documentation, homepage, etc.
"""

import io
import random
import struct
import time
import uuid
from hashlib import md5
from sys import version_info

from pypdf import utils
from pypdf.generic import *
from pypdf.utils import *
from pypdf.utils import pypdfBytes as b_

if version_info < (3, 0):
    from cStringIO import StringIO
    BytesIO = StringIO
else:
    from io import StringIO, BytesIO


__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"
__maintainer__ = "Phaseit, Inc."
__maintainer_email = "PyPDF4@phaseit.net"


class PdfFileWriter(object):
    def __init__(self, stream, debug=False):
        """
        This class supports writing PDF files out, given pages produced by
        another class (typically :class:`PdfFileReader<PdfFileReader>`).

        :param stream: File-like object or path to a PDF file in ``str``
            format. If of the former type, the object must support the
            ``write()`` and the ``tell()`` methods.
        :param bool debug: Whether this class should emit debug informations
            (recommended for development). Defaults to False.
        """
        self._header = b_("%PDF-1.3")
        self._objects = []  # array of indirect objects
        self.debug = debug

        if isString(stream):
            self._stream = open(stream, "wb")
        else:
            # We rely on duck typing
            self._stream = stream

        if hasattr(self._stream, "mode") and "b" not in self._stream.mode:
            warnings.warn(
                "File <%s> to write to is not in binary mode. It may not be "
                "written to correctly." % self._stream.name
            )

        # The root of our page tree node.
        pages = DictionaryObject()
        pages.update({
            NameObject("/Type"): NameObject("/Pages"),
            NameObject("/Count"): NumberObject(0),
            NameObject("/Kids"): ArrayObject(),
        })
        self._pages = self._addObject(pages)

        info = DictionaryObject()
        info.update({
            NameObject("/Producer"): createStringObject(
                codecs.BOM_UTF16_BE + pypdfUnicode("pypdf").encode('utf-16be')
            )
        })
        self._info = self._addObject(info)

        root = DictionaryObject()
        root.update({
            NameObject("/Type"): NameObject("/Catalog"),
            NameObject("/Pages"): self._pages,
        })
        self._root = None
        self._rootObject = root

    def __enter__(self):
        return self

    def __exit__(self, excType, excVal, excTb):
        # TO-DO Implement AND TEST along with PdfFileWriter.close()
        if not self.isClosed:
            self.close()

        return False

    def __repr__(self):
        return "<%s.%s _stream=%s, _header=%s, isClosed=%s, debug=%s>" % (
            self.__class__.__module__, self.__class__.__name__, self._stream,
            self._header.decode(), self.isClosed, self.debug
        )

    def __del__(self):
        self.close()

        for a in (
                "_objects", "_stream", "_pages", "_info", "_root",
                "_rootObject"
        ):
            if hasattr(self, a):
                delattr(self, a)

    def close(self):
        """
        Deallocates file-system resources associated with this
        ``PdfFileWriter`` instance.
        """
        if not self._stream.closed:
            self._stream.flush()
            self._stream.close()

    @property
    def isClosed(self):
        """
        :return: ``True`` if the IO streams associated with this file have
            been closed, ``False`` otherwise.
        """
        return not bool(self._stream) or self._stream.closed

    def _addObject(self, obj):
        self._objects.append(obj)

        return IndirectObject(len(self._objects), 0, self)

    def getObject(self, ido):
        if ido.pdf is not self:
            raise ValueError("ido.pdf must be self")

        return self._objects[ido.idnum - 1]

    def _addPage(self, page, action):
        if page["/Type"] != "/Page":
            raise ValueError("Page type is not /Page")

        page[NameObject("/Parent")] = self._pages
        pages = self.getObject(self._pages)
        action(pages["/Kids"], self._addObject(page))

        pages[NameObject("/Count")] = NumberObject(pages["/Count"] + 1)

    def addPage(self, page):
        """
        Adds a page to this PDF file.  The page is usually acquired from a
        :class:`PdfFileReader<PdfFileReader>` instance.

        :param PageObject page: The page to add to the document. Should be
            an instance of :class:`PageObject<pypdf.pdf.PageObject>`
        """
        self._addPage(page, list.append)

    def insertPage(self, page, index=0):
        """
        Insert a page in this PDF file. The page is usually acquired from a
        :class:`PdfFileReader<PdfFileReader>` instance.

        :param PageObject page: The page to add to the document.  This argument
            should be an instance of :class:`PageObject<pdf.PageObject>`.
        :param int index: Position at which the page will be inserted.
        """
        self._addPage(page, lambda l, p: l.insert(index, p))

    def getPage(self, pageNumber):
        """
        Retrieves a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero).
        :return: the page at the index given by *pageNumber*
        :rtype: :class:`PageObject<pdf.PageObject>`
        """
        pages = self.getObject(self._pages)
        # XXX: crude hack
        return pages["/Kids"][pageNumber].getObject()

    @property
    def numPages(self):
        """
        :return: the number of pages.
        :rtype: int
        """
        return int(
            self.getObject(self._pages)[NameObject("/Count")]
        )

    def addBlankPage(self, width=None, height=None):
        """
        Appends a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :return: the newly appended page
        :rtype: :class:`PageObject<pypdf.pdf.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        page = PageObject.createBlankPage(self, width, height)
        self.addPage(page)

        return page

    def insertBlankPage(self, width=None, height=None, index=0):
        """
        Inserts a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :param int index: Position to add the page.
        :return: the newly appended page
        :rtype: :class:`PageObject<pypdf.pdf.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        if width is None or height is None and\
                (self.numPages - 1) >= index:
            oldpage = self.getPage(index)
            width = oldpage.mediaBox.getWidth()
            height = oldpage.mediaBox.getHeight()

        page = PageObject.createBlankPage(self, width, height)
        self.insertPage(page, index)

        return page

    def addJS(self, javascript):
        """
        Add a Javascript code snippet to be launched upon this PDF opening.\n
        As an example, this will launch the print window when the PDF is
        opened:\n
        writer.addJS(\
            "this.print({bUI:true,bSilent:false,bShrinkToFit:true});"\\
        )\

        :param str javascript: Javascript code.
        """
        js = DictionaryObject()
        js.update({
            NameObject("/Type"): NameObject("/Action"),
            NameObject("/S"): NameObject("/JavaScript"),
            NameObject("/JS"): NameObject("(%s)" % javascript)
        })
        js_indirect_object = self._addObject(js)

        # We need a name for parameterized javascript in the pdf file, but it
        # can be anything.
        js_string_name = str(uuid.uuid4())

        js_name_tree = DictionaryObject()
        js_name_tree.update({
            NameObject("/JavaScript"): DictionaryObject({
                NameObject("/Names"):
                    ArrayObject(
                        [createStringObject(js_string_name),
                         js_indirect_object]
                    )
            })
        })
        self._addObject(js_name_tree)

        self._rootObject.update({
            NameObject("/JavaScript"): js_indirect_object,
            NameObject("/Names"): js_name_tree
        })

    def addAttachment(self, fname, fdata):
        """
        Embed a file inside the PDF.

        :param str fname: The filename to display.
        :param str fdata: The data in the file.
      
        Reference:
        https://www.adobe.com/content/dam/Adobe/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
        Section 7.11.3
        """
        # We need three entries:
        # * The file's data
        # * The /Filespec entry
        # * The file's name, which goes in the Catalog

        # The entry for the file
        """ Sample:
        8 0 obj
        <<
            /Length 12
            /Type /EmbeddedFile
        >>
        stream
        Hello world!
        endstream
        endobj        
        """
        file_entry = DecodedStreamObject()
        file_entry.setData(fdata)
        file_entry.update({
            NameObject("/Type"): NameObject("/EmbeddedFile")
        })

        # The Filespec entry
        """Sample:
        7 0 obj
        <<
         /Type /Filespec
         /F (hello.txt)
         /EF << /F 8 0 R >>
        >>
        """
        efEntry = DictionaryObject()
        efEntry.update({NameObject("/F"): file_entry})

        filespec = DictionaryObject()
        filespec.update({
            NameObject("/Type"): NameObject("/Filespec"),
            # Perhaps also try TextStringObject
            NameObject("/F"): createStringObject(fname),
            NameObject("/EF"): efEntry
        })

        # Then create the entry for the root, as it needs a reference to the
        # Filespec
        """Sample:
        1 0 obj
        <<
            /Type /Catalog
            /Outlines 2 0 R
            /Pages 3 0 R
            /Names << /EmbeddedFiles << /Names [(hello.txt) 7 0 R] >> >>
        >>
        endobj
        
        """
        embeddedFilesNamesDictionary = DictionaryObject()
        embeddedFilesNamesDictionary.update({
            NameObject("/Names"): ArrayObject(
                [createStringObject(fname), filespec]
            )
        })

        embeddedFilesDictionary = DictionaryObject()
        embeddedFilesDictionary.update({
            NameObject("/EmbeddedFiles"): embeddedFilesNamesDictionary
        })
        # Update the root
        self._rootObject.update({
            NameObject("/Names"): embeddedFilesDictionary
        })

    def appendPagesFromReader(self, reader, afterPageAppend=None):
        """
         Copy pages from reader to writer. Includes an optional callback
         parameter which is invoked after pages are appended to the writer.

         :param reader: a PdfFileReader object from which to copy page
             annotations to this writer object.  The writer's annots will then
             be updated.
         :param afterPageAppend: Callback function that is invoked after each
             page is appended to the writer. Takes a ``writerPageref`` argument
             that references to the page appended to the writer.
         """
        # Get page count from writer and reader
        readerNumPages = reader.numPages
        writerNumPages = self.numPages

        # Copy pages from reader to writer
        for rpagenum in range(readerNumPages):
            self.addPage(reader.getPage(rpagenum))
            writerPage = self.getPage(writerNumPages + rpagenum)

            # Trigger callback, pass writer page as parameter
            if callable(afterPageAppend):
                afterPageAppend(writerPage)

    def updatePageFormFieldValues(self, page, fields):
        """
        Update the form field values for a given page from a fields dictionary.
        Copy field texts and values from fields to page.

        :param page: Page reference from PDF writer where the annotations and
            field data will be updated.
        :param fields: a Python dictionary of field names (/T) and text values
            (/V).
        """
        # Iterate through the pages and update field values
        for j in range(len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()

            for field in fields:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/V"): TextStringObject(fields[field])
                    })

    def cloneReaderDocumentRoot(self, reader):
        """
        Copy the reader document root to the writer.

        :param reader: ``PdfFileReader`` from the document root that should be
            copied.
        """
        self._rootObject = reader._trailer['/Root']

    def cloneDocumentFromReader(self, reader, afterPageAppend=None):
        """
        Create a clone of a document from a PDF file reader.

        :param reader: PDF file reader instance from which the clone
            should be created.
        :param afterPageAppend: Callback function that is invoked after each
            page is appended to the writer. Takes as a single argument a
            reference to the page appended.
        """
        self.cloneReaderDocumentRoot(reader)
        self.appendPagesFromReader(reader, afterPageAppend)

    def encrypt(self, userPwd, ownerPwd=None, use128Bits=True):
        """
        Encrypt this PDF file with the PDF Standard encryption handler.

        :param str userPwd: The "user password", which allows for opening and
            reading the PDF file with the restrictions provided.
        :param str ownerPwd: The "owner password", which allows for opening the
            PDF files without any restrictions.  By default, the owner password
            is the same as the user password.
        :param bool use128Bits: flag as to whether to use 128bit encryption.
            When false, 40bit encryption will be used.  By default, this flag
            is on.
        """
        # TO-DO Clean this method's code, as it fires up many code linting
        # warnings
        if ownerPwd is None:
            ownerPwd = userPwd
        if use128Bits:
            V = 2
            rev = 3
            keylen = int(128 / 8)
        else:
            V = 1
            rev = 2
            keylen = int(40 / 8)
        # Permit everything:
        P = -1
        O = ByteStringObject(_alg33(ownerPwd, userPwd, rev, keylen))
        ID_1 = ByteStringObject(md5(b_(repr(time.time()))).digest())
        ID_2 = ByteStringObject(md5(b_(repr(random.random()))).digest())
        self._ID = ArrayObject((ID_1, ID_2))

        if rev == 2:
            U, key = _alg34(userPwd, O, P, ID_1)
        else:
            assert rev == 3
            U, key = _alg35(userPwd, rev, keylen, O, P, ID_1, False)

        encrypt = DictionaryObject()
        encrypt[NameObject("/Filter")] = NameObject("/Standard")
        encrypt[NameObject("/V")] = NumberObject(V)

        if V == 2:
            encrypt[NameObject("/Length")] = NumberObject(keylen * 8)

        encrypt[NameObject("/R")] = NumberObject(rev)
        encrypt[NameObject("/O")] = ByteStringObject(O)
        encrypt[NameObject("/U")] = ByteStringObject(U)
        encrypt[NameObject("/P")] = NumberObject(P)
        self._encrypt = self._addObject(encrypt)
        self._encrypt_key = key

    def write(self):
        """
        Writes the collection of pages added to this object out as a PDF file.
        """
        if not self._root:
            self._root = self._addObject(self._rootObject)

        externalReferenceMap = {}

        # PDF objects sometimes have circular references to their /Page objects
        # inside their object tree (for example, annotations).  Those will be
        # indirect references to objects that we've recreated in this PDF.  To
        # address this problem, PageObject's store their original object
        # reference number, and we add it to the external reference map before
        # we sweep for indirect references.  This forces self-page-referencing
        # trees to reference the correct new object location, rather than
        # copying in a new copy of the page object.
        for objIndex in range(len(self._objects)):
            obj = self._objects[objIndex]

            if isinstance(obj, PageObject) and obj.indirectRef is not None:
                data = obj.indirectRef

                if data.pdf not in externalReferenceMap:
                    externalReferenceMap[data.pdf] = {}
                if data.generation not in externalReferenceMap[data.pdf]:
                    externalReferenceMap[data.pdf][data.generation] = {}
                externalReferenceMap[data.pdf][data.generation][data.idnum]\
                    = IndirectObject(objIndex + 1, 0, self)

        # TO-DO Instance attribute defined outside __init__(). Carefully move
        # it out of here
        self.stack = []

        self._sweepIndirectReferences(externalReferenceMap, self._root)
        del self.stack

        # Begin writing:
        object_positions = []
        self._stream.write(self._header + b_("\n"))
        self._stream.write(b_("%\xE2\xE3\xCF\xD3\n"))

        for i in range(len(self._objects)):
            idnum = (i + 1)
            obj = self._objects[i]
            object_positions.append(self._stream.tell())
            self._stream.write(b_(str(idnum) + " 0 obj\n"))
            key = None

            if hasattr(self, "_encrypt") and idnum != self._encrypt.idnum:
                pack1 = struct.pack("<i", i + 1)[:3]
                pack2 = struct.pack("<i", 0)[:2]
                key = self._encrypt_key + pack1 + pack2
                assert len(key) == (len(self._encrypt_key) + 5)
                md5_hash = md5(key).digest()
                key = md5_hash[:min(16, len(self._encrypt_key) + 5)]
            obj.writeToStream(self._stream, key)
            self._stream.write(b_("\nendobj\n"))

        # xref table
        xref_location = self._stream.tell()
        self._stream.write(b_("xref\n"))
        self._stream.write(b_("0 %s\n" % (len(self._objects) + 1)))
        self._stream.write(b_("%010d %05d f \n" % (0, 65535)))

        for offset in object_positions:
            self._stream.write(b_("%010d %05d n \n" % (offset, 0)))

        self._stream.write(b_("trailer\n"))
        trailer = DictionaryObject()
        trailer.update({
            NameObject("/Size"): NumberObject(len(self._objects) + 1),
            NameObject("/Root"): self._root,
            NameObject("/Info"): self._info,
        })

        if hasattr(self, "_ID"):
            trailer[NameObject("/ID")] = self._ID
        if hasattr(self, "_encrypt"):
            trailer[NameObject("/Encrypt")] = self._encrypt

        trailer.writeToStream(self._stream, None)

        # EOF
        self._stream.write(b_("\nstartxref\n%s\n%%%%EOF\n" % xref_location))

    def addMetadata(self, infos):
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
        """
        args = {}

        for key, value in list(infos.items()):
            args[NameObject(key)] = createStringObject(value)

        self.getObject(self._info).update(args)

    def _sweepIndirectReferences(self, externMap, data):
        if self.debug:
            print(data, "TYPE", data.__class__.__name__)

        if isinstance(data, DictionaryObject):
            for key, value in data.items():
                value = self._sweepIndirectReferences(externMap, value)

                if isinstance(value, StreamObject):
                    # a dictionary value is a stream.  streams must be indirect
                    # objects, so we need to change this value.
                    value = self._addObject(value)
                data[key] = value

            return data
        elif isinstance(data, ArrayObject):
            for i in range(len(data)):
                value = self._sweepIndirectReferences(externMap, data[i])
                if isinstance(value, StreamObject):
                    # An array value is a stream.  streams must be indirect
                    # objects, so we need to change this value
                    value = self._addObject(value)
                data[i] = value
            return data
        elif isinstance(data, IndirectObject):
            # Internal indirect references are fine
            if data.pdf == self:
                if data.idnum in self.stack:
                    return data
                else:
                    self.stack.append(data.idnum)
                    realdata = self.getObject(data)
                    self._sweepIndirectReferences(externMap, realdata)
                    return data
            else:
                if data.pdf.isClosed:
                    raise ValueError(
                        "I/O operation on closed file: "
                        + data.pdf._stream.name
                    )
                newobj = externMap.get(data.pdf, {}).\
                    get(data.generation, {}).\
                    get(data.idnum, None)

                if newobj is None:
                    try:
                        newobj = data.pdf.getObject(data)
                        self._objects.append(None)  # placeholder
                        idnum = len(self._objects)
                        newobj_ido = IndirectObject(idnum, 0, self)

                        if data.pdf not in externMap:
                            externMap[data.pdf] = {}
                        if data.generation not in externMap[data.pdf]:
                            externMap[data.pdf][data.generation] = {}

                        externMap[data.pdf][data.generation][data.idnum]\
                            = newobj_ido
                        newobj\
                            = self._sweepIndirectReferences(externMap, newobj)
                        self._objects[idnum-1] = newobj

                        return newobj_ido
                    except ValueError:
                        # Unable to resolve the Object, returning NullObject
                        # instead.
                        warnings.warn(
                            "Unable to resolve [{}: {}], returning NullObject "
                            "instead".format(data.__class__.__name__, data)
                        )
                        return NullObject()
                return newobj
        else:
            return data

    def getReference(self, obj):
        idnum = self._objects.index(obj) + 1
        ref = IndirectObject(idnum, 0, self)

        assert ref.getObject() == obj

        return ref

    def getOutlineRoot(self):
        if '/Outlines' in self._rootObject:
            outline = self._rootObject['/Outlines']
            idnum = self._objects.index(outline) + 1
            outlineRef = IndirectObject(idnum, 0, self)

            assert outlineRef.getObject() == outline
        else:
            outline = TreeObject()
            outline.update({})
            outlineRef = self._addObject(outline)
            self._rootObject[NameObject('/Outlines')] = outlineRef

        return outline

    def getNamedDestRoot(self):
        if '/Names' in self._rootObject and \
                isinstance(self._rootObject['/Names'], DictionaryObject):
            names = self._rootObject['/Names']
            idnum = self._objects.index(names) + 1
            namesRef = IndirectObject(idnum, 0, self)

            assert namesRef.getObject() == names

            if '/Dests' in names and \
                    isinstance(names['/Dests'], DictionaryObject):
                dests = names['/Dests']
                idnum = self._objects.index(dests) + 1
                destsRef = IndirectObject(idnum, 0, self)

                assert destsRef.getObject() == dests

                if '/Names' in dests:
                    nd = dests['/Names']
                else:
                    nd = ArrayObject()
                    dests[NameObject('/Names')] = nd
            else:
                dests = DictionaryObject()
                destsRef = self._addObject(dests)
                names[NameObject('/Dests')] = destsRef
                nd = ArrayObject()
                dests[NameObject('/Names')] = nd

        else:
            names = DictionaryObject()
            namesRef = self._addObject(names)
            self._rootObject[NameObject('/Names')] = namesRef
            dests = DictionaryObject()
            destsRef = self._addObject(dests)
            names[NameObject('/Dests')] = destsRef
            nd = ArrayObject()
            dests[NameObject('/Names')] = nd

        return nd

    def addBookmarkDestination(self, dest, parent=None):
        destRef = self._addObject(dest)

        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        parent = parent.getObject()
        parent.addChild(destRef, self)

        return destRef

    def addBookmarkDict(self, bookmark, parent=None):
        bookmarkObj = TreeObject()

        for k, v in list(bookmark.items()):
            bookmarkObj[NameObject(str(k))] = v
        bookmarkObj.update(bookmark)

        if '/A' in bookmark:
            action = DictionaryObject()
            for k, v in list(bookmark['/A'].items()):
                action[NameObject(str(k))] = v
            actionRef = self._addObject(action)
            bookmarkObj[NameObject('/A')] = actionRef

        bookmarkRef = self._addObject(bookmarkObj)
        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        parent = parent.getObject()
        parent.addChild(bookmarkRef, self)

        return bookmarkRef

    def addBookmark(
            self, title, pagenum, parent=None, color=None, bold=False,
            italic=False, fit='/Fit', *args
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
            :meth:`addLink()<addLink>` for details.
        """
        pageRef = self.getObject(self._pages)['/Kids'][pagenum]
        action = DictionaryObject()
        zoomArgs = []

        for a in args:
            if a is not None:
                zoomArgs.append(NumberObject(a))
            else:
                zoomArgs.append(NullObject())

        dest = Destination(NameObject("/"+title + " bookmark"), pageRef,
                           NameObject(fit), *zoomArgs)
        destArray = dest.getDestArray()
        action.update({
            NameObject('/D'): destArray, NameObject('/S'): NameObject('/GoTo')
        })
        actionRef = self._addObject(action)
        outlineRef = self.getOutlineRoot()

        if parent is None:
            parent = outlineRef

        bookmark = TreeObject()
        bookmark.update({
            NameObject('/A'): actionRef,
            NameObject('/Title'): createStringObject(title),
        })

        if color is not None:
            bookmark.update({
                NameObject('/C'): ArrayObject([FloatObject(c) for c in color])
            })

        format = 0

        if italic:
            format += 1
        if bold:
            format += 2
        if format:
            bookmark.update({NameObject('/F'): NumberObject(format)})

        bookmarkRef = self._addObject(bookmark)

        parent = parent.getObject()
        parent.addChild(bookmarkRef, self)

        return bookmarkRef

    def addNamedDestinationObject(self, dest):
        destRef = self._addObject(dest)

        nd = self.getNamedDestRoot()
        nd.extend([dest['/Title'], destRef])

        return destRef

    def addNamedDestination(self, title, pagenum):
        pageRef = self.getObject(self._pages)['/Kids'][pagenum]
        dest = DictionaryObject()
        dest.update({
            NameObject('/D'):
                ArrayObject([pageRef, NameObject('/FitH'), NumberObject(826)]),
            NameObject('/S'): NameObject('/GoTo')
        })

        destRef = self._addObject(dest)
        nd = self.getNamedDestRoot()
        nd.extend([title, destRef])

        return destRef

    def removeLinks(self):
        """
        Removes links and annotations from this output.
        """
        pages = self.getObject(self._pages)['/Kids']

        for page in pages:
            pageRef = self.getObject(page)

            if "/Annots" in pageRef:
                del pageRef['/Annots']

    def removeImages(self, ignoreByteStringObject=False):
        """
        Removes images from this output.

        :param bool ignoreByteStringObject: optional parameter to ignore
            ByteString Objects.
        """
        pages = self.getObject(self._pages)['/Kids']

        for j in range(len(pages)):
            page = pages[j]
            pageRef = self.getObject(page)
            content = pageRef['/Contents'].getObject()

            if not isinstance(content, ContentStream):
                content = ContentStream(content, pageRef)

            _operations = []
            seq_graphics = False

            for operands, operator in content.operations:
                if operator == b_('Tj'):
                    text = operands[0]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_("'"):
                    text = operands[0]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if ignoreByteStringObject:
                        if not isinstance(text, TextStringObject):
                            operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if ignoreByteStringObject and not \
                                isinstance(operands[0][i], TextStringObject):
                                operands[0][i] = TextStringObject()

                if operator == b_('q'):
                    seq_graphics = True
                if operator == b_('Q'):
                    seq_graphics = False
                if seq_graphics:
                    if operator in [
                        b_('cm'), b_('w'), b_('J'), b_('j'), b_('M'), b_('d'),
                        b_('ri'), b_('i'), b_('gs'), b_('W'), b_('b'), b_('s'),
                        b_('S'), b_('f'), b_('F'), b_('n'), b_('m'), b_('l'),
                        b_('c'), b_('v'), b_('y'), b_('h'), b_('B'), b_('Do'),
                        b_('sh')
                    ]:
                        continue
                if operator == b_('re'):
                    continue
                _operations.append((operands, operator))

            content.operations = _operations
            pageRef.__setitem__(NameObject('/Contents'), content)

    def removeText(self, ignoreByteStringObject=False):
        """
        Removes images from this output.

        :param bool ignoreByteStringObject: optional parameter to ignore
            ByteString Objects.
        """
        pages = self.getObject(self._pages)['/Kids']

        for j in range(len(pages)):
            page = pages[j]
            pageRef = self.getObject(page)
            content = pageRef['/Contents'].getObject()

            if not isinstance(content, ContentStream):
                content = ContentStream(content, pageRef)
            for operands,operator in content.operations:
                if operator == b_('Tj'):
                    text = operands[0]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_("'"):
                    text = operands[0]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if not ignoreByteStringObject:
                        if isinstance(text, TextStringObject):
                            operands[2] = TextStringObject()
                    else:
                        if isinstance(text, TextStringObject) or \
                                isinstance(text, ByteStringObject):
                            operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if not ignoreByteStringObject:
                            if isinstance(operands[0][i], TextStringObject):
                                operands[0][i] = TextStringObject()
                        else:
                            if isinstance(operands[0][i], TextStringObject)\
                                    or isinstance(operands[0][i],
                                                  ByteStringObject):
                                operands[0][i] = TextStringObject()

            pageRef.__setitem__(NameObject('/Contents'), content)

    def addURI(self, pagenum, uri, rect, border=None):
        """
        Add an URI from a rectangular area to the specified page. This uses the
        basic structure of AddLink.

        :param int pagenum: index of the page on which to place the URI action.
        :param int uri: string -- uri of resource to link to.
        :param rect: :class:`RectangleObject<pypdf.generic.RectangleObject>`
            or array of four integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form
            ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be drawn
            if this argument is omitted.
        """
        pageLink = self.getObject(self._pages)['/Kids'][pagenum]
        pageRef = self.getObject(pageLink)

        if border is not None:
            borderArr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dashPattern = ArrayObject([NameObject(n) for n in border[3]])
                borderArr.append(dashPattern)
        else:
            borderArr = [NumberObject(2)] * 3

        if isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        lnk2 = DictionaryObject()
        lnk2.update({
            NameObject('/S'): NameObject('/URI'),
            NameObject('/URI'): TextStringObject(uri)
        })

        lnk = DictionaryObject()
        lnk.update({
            NameObject('/Type'): NameObject('/Annot'),
            NameObject('/Subtype'): NameObject('/Link'),
            NameObject('/P'): pageLink,
            NameObject('/Rect'): rect,
            NameObject('/H'): NameObject('/I'),
            NameObject('/Border'): ArrayObject(borderArr),
            NameObject('/A'): lnk2
        })
        lnkRef = self._addObject(lnk)

        if "/Annots" in pageRef:
            pageRef['/Annots'].append(lnkRef)
        else:
            pageRef[NameObject('/Annots')] = ArrayObject([lnkRef])

    def addLink(self, pagenum, pagedest, rect, border=None, fit='/Fit', *args):
        """
        Add an internal link from a rectangular area to the specified page.

        :param int pagenum: index of the page on which to place the link.
        :param int pagedest: index of the page to which the link should go.
        :param rect: :class:`RectangleObject<pypdf.generic.RectangleObject>`
            or array of four integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form
            ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be drawn
            if this argument is omitted.
        :param str fit: Page fit or 'zoom' option (see below). Additional
            arguments may need to be supplied. Passing ``None`` will be read as
            a null value for that coordinate.

        Valid zoom arguments (see Table 8.2 of the PDF 1.7 reference for
        details):
             /Fit       No additional arguments
             /XYZ       [left] [top] [zoomFactor]
             /FitH      [top]
             /FitV      [left]
             /FitR      [left] [bottom] [right] [top]
             /FitB      No additional arguments
             /FitBH     [top]
             /FitBV     [left]
        """
        pageLink = self.getObject(self._pages)['/Kids'][pagenum]
        # TO-DO: switch for external link
        pageDest = self.getObject(self._pages)['/Kids'][pagedest]
        pageRef = self.getObject(pageLink)

        if border is not None:
            borderArr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dashPattern = ArrayObject([NameObject(n) for n in border[3]])
                borderArr.append(dashPattern)
        else:
            borderArr = [NumberObject(0)] * 3

        if isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        zoomArgs = []
        for a in args:
            if a is not None:
                zoomArgs.append(NumberObject(a))
            else:
                zoomArgs.append(NullObject())
        # TO-DO: create a better name for the link
        dest = Destination(NameObject("/LinkName"), pageDest, NameObject(fit),
                           *zoomArgs)
        destArray = dest.getDestArray()

        lnk = DictionaryObject()
        lnk.update({
            NameObject('/Type'): NameObject('/Annot'),
            NameObject('/Subtype'): NameObject('/Link'),
            NameObject('/P'): pageLink,
            NameObject('/Rect'): rect,
            NameObject('/Border'): ArrayObject(borderArr),
            NameObject('/Dest'): destArray
        })
        lnkRef = self._addObject(lnk)

        if "/Annots" in pageRef:
            pageRef['/Annots'].append(lnkRef)
        else:
            pageRef[NameObject('/Annots')] = ArrayObject([lnkRef])

    _VALID_LAYOUTS = [
        '/NoLayout', '/SinglePage', '/OneColumn', '/TwoColumnLeft',
        '/TwoColumnRight', '/TwoPageLeft', '/TwoPageRight'
    ]

    def getPageLayout(self):
        """
        Get the page layout.
        See :meth:`setPageLayout()<PdfFileWriter.setPageLayout>` for a
        description of valid layouts.

        :return: Page layout currently being used.
        :rtype: str, None if not specified.
        """
        try:
            return self._rootObject['/PageLayout']
        except KeyError:
            return None

    def setPageLayout(self, layout):
        """
        Set the page layout.

        :param str layout: The page layout to be used.

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
        if not isinstance(layout, NameObject):
            if layout not in self._VALID_LAYOUTS:
                warnings.warn("Layout should be one of: {}".format(
                    ', '.join(self._VALID_LAYOUTS))
                )
            layout = NameObject(layout)
        self._rootObject.update({NameObject('/PageLayout'): layout})

    pageLayout = property(getPageLayout, setPageLayout)
    """
    Read and write property accessing the
    :meth:`getPageLayout()<PdfFileWriter.getPageLayout>` and
    :meth:`setPageLayout()<PdfFileWriter.setPageLayout>` methods.
    """

    _VALID_MODES = (
        '/UseNone', '/UseOutlines', '/UseThumbs', '/FullScreen', '/UseOC',
        '/UseAttachments'
    )

    def getPageMode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfFileWriter.setPageMode>` for a description
        of valid modes.

        :return: Page mode currently being used.
        :rtype: str, None if not specified.
        """
        try:
            return self._rootObject['/PageMode']
        except KeyError:
            return None

    def setPageMode(self, mode):
        """
        Set the page mode.

        :param str mode: The page mode to use.

        Valid modes are:
            /UseNone         Do not show outlines or thumbnails panels
            /UseOutlines     Show outlines (aka bookmarks) panel
            /UseThumbs       Show page thumbnails panel
            /FullScreen      Fullscreen view
            /UseOC           Show Optional Content Group (OCG) panel
            /UseAttachments  Show attachments panel
        """
        if not isinstance(mode, NameObject):
            if mode not in self._VALID_MODES:
                warnings.warn("Mode should be one of: {}".format(
                    ', '.join(self._VALID_MODES)
                ))
            mode = NameObject(mode)
        self._rootObject.update({NameObject('/PageMode'): mode})

    pageMode = property(getPageMode, setPageMode)
    """
    Read and write property accessing the
    :meth:`getPageMode()<PdfFileWriter.getPageMode>` and
    :meth:`setPageMode()<PdfFileWriter.setPageMode>` methods.
    """


class PdfFileReader(object):
    R_XTABLE, R_XSTREAM, R_BOTH = (1, 2, 3)

    def __init__(
            self, stream, strict=True, warndest=None, overwriteWarnings=True,
            debug=False
    ):
        """
        Initializes a ``PdfFileReader`` instance.  This operation can take some
        time, as the PDF stream's cross-reference tables are read into memory.

        :param stream: A file-like object with ``read()`` and ``seek()``
            methods. Could also be a string representing a path to a PDF file.
        :param bool strict: Determines whether user should be warned of all
            problems and also causes some correctable problems to be fatal.
            Defaults to ``True``.
        :param warndest: Destination for logging warnings (defaults to
            ``sys.stderr``).
        :param bool overwriteWarnings: Determines whether to override Python's
            ``warnings.py`` module with a custom implementation (defaults to
            ``True``).
        :param bool debug: Whether this class should emit debug informations
            (recommended for development). Defaults to ``False``.
        """
        if overwriteWarnings:
            # Have to dynamically override the default showwarning since there
            # are no public methods that specify the 'file' parameter
            def _showwarning(
                    message, category, filename, lineno, file=warndest,
                    line=None
            ):
                if file is None:
                    file = sys.stderr

                try:
                    file.write(
                        formatWarning(message, category, filename, lineno,
                                      line)
                    )
                except IOError:
                    pass

            warnings.showwarning = _showwarning

        self._xrefTable = {}
        """
        Stores the Cross-Reference Table indices. The keys are gen. numbers,
        the values a dict of the form ``{obj. id: (byte offset within file, is
        in free object list)}``.
        """
        self._xrefIndex = 0
        self._xrefStm = {}
        """
        Stores the Cross-Reference Stream data. The keys are id numbers of
        objects. The values are exactly as in Table 18 of section 7.5.8.3 of
        the ISO 32000 Reference (2008), represented as a tuple of length three.
        """
        self._cachedObjects = {}
        self._trailer = DictionaryObject()
        self._pageId2Num = None  # Maps page IndirectRef number to Page Number
        self._flattenedPages = None

        self.strict = strict
        self.debug = debug
        self._overrideEncryption = False

        if isinstance(stream, io.FileIO):
            self._filepath = stream.name
        elif isString(stream):
            self._filepath = stream
        else:
            self._filepath = None

        if isString(stream):
            with open(stream, 'rb') as fileobj:
                self._stream = BytesIO(fileobj.read())
        else:
            # We rely on duck typing
            self._stream = stream

        if hasattr(self._stream, 'mode') and 'b' not in self._stream.mode:
            warnings.warn(
                "PdfFileReader stream/file object is not in binary mode. It "
                "may not be read correctly.", PdfReadWarning
            )

        self._parsePdfFile(self._stream)

    def __repr__(self):
        return "<%s.%s isClosed=%s, _filepath=%s, _stream=%s, strict=%s, " \
               "debug=%s>" % (
            self.__class__.__module__, self.__class__.__name__, self.isClosed,
            self._filepath, self._stream, self.strict, self.debug
        )

    def __del__(self):
        self.close()

        for a in (
                "_xrefTable", "_xrefStm", "_cachedObjects", "_trailer",
                "_pageId2Num", "_flattenedPages", "_stream"
        ):
            if hasattr(self, a):
                delattr(self, a)

    def __enter__(self):
        return self

    def __exit__(self, excType, excVal, excTb):
        if not self.isClosed:
            self.close()

        return False

    @property
    def filepath(self):
        """
        :return: The PDF file path this ``PdfFileReader`` is associated to, or
            ``None`` if there isn't such a path (like when initializing a
            ``PdfFileReader`` from a non-file stream).
        """
        if self._filepath:
            return self._filepath

        return None

    @property
    def isClosed(self):
        """
        :return: ``True`` if the IO streams associated with this file have
            been closed, ``False`` otherwise.
        """
        return not bool(self._stream) or self._stream.closed

    def close(self):
        """
        Deallocates file-system resources associated with this
        ``PdfFileReader`` instance.
        """
        if getattr(self, "_stream", None) and hasattr(self._stream, "close") \
                and callable(self._stream.close):
            self._stream.close()

    @property
    def documentInfo(self):
        """
        Retrieves the PDF file's document information dictionary, if it exists.
        Note that some PDF files use metadata streams instead of docinfo
        dictionaries, and these metadata streams will not be accessed by this
        function.

        :return: the document information of this PDF file.
        :rtype: :class:`DocumentInformation<pdf.DocumentInformation>` or
            ``None`` if none exists.
        """
        if "/Info" not in self._trailer:
            return None

        retval = DocumentInformation()
        retval.update(self._trailer["/Info"])

        return retval

    @property
    def xmpMetadata(self):
        """
        Retrieves XMP (Extensible Metadata Platform) data from the PDF document
        root.

        :return: a :class:`XmpInformation<xmp.XmpInformation>`
            instance that can be used to access XMP metadata from the document.
        :rtype: :class:`XmpInformation<xmp.XmpInformation>` or
            ``None`` if no metadata was found on the document root.
        """
        try:
            self._overrideEncryption = True
            return self._trailer["/Root"].getXmpMetadata()
        finally:
            self._overrideEncryption = False

    @property
    def numPages(self):
        """
        Calculates the number of pages in this PDF file.

        :return: number of pages
        :rtype: int
        :raises PdfReadError: if file is encrypted and restrictions prevent
            this action.
        """
        # Flattened pages will not work on an Encrypted PDF;
        # the PDF file's page count is used in this case. Otherwise,
        # the original method (flattened page count) is used.
        if self.isEncrypted:
            try:
                self._overrideEncryption = True
                self.decrypt('')

                return self._trailer["/Root"]["/Pages"]["/Count"]
            except Exception:
                raise PdfReadError("File has not been decrypted")
            finally:
                self._overrideEncryption = False
        else:
            if self._flattenedPages is None:
                self._flatten()

            return len(self._flattenedPages)

    def getPage(self, pageNumber):
        """
        Retrieves a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: a :class:`PageObject<pdf.PageObject>` instance.
        :rtype: :class:`PageObject<pdf.PageObject>`
        """
        # Ensure that we're not trying to access an encrypted PDF
        if self._flattenedPages is None:
            self._flatten()

        return self._flattenedPages[pageNumber]

    def getFields(self, tree=None, retval=None, fileobj=None):
        """
        Extracts field data if this PDF contains interactive form fields.
        The ``tree`` and ``retval`` parameters are for recursive use.

        :param retval:
        :param tree:
        :param fileobj: A file object (usually a text file) to write
            a report to on all interactive form fields found.
        :return: A dictionary where each key is a field name, and each
            value is a :class:`Field<pypdf.generic.Field>` object. By
            default, the mapping name is used for keys.
        :rtype: ``dict``, or ``None`` if form data could not be located.
        """
        fieldAttributes = {
            "/FT": "Field Type", "/Parent": "Parent", "/T": "Field Name",
            "/TU": "Alternate Field Name", "/TM": "Mapping Name",
            "/Ff": "Field Flags", "/V": "Value", "/DV": "Default Value"
        }

        if retval is None:
            retval = {}
            catalog = self._trailer["/Root"]

            # Get the AcroForm tree
            if "/AcroForm" in catalog:
                tree = catalog["/AcroForm"]
            else:
                return None
        if tree is None:
            return retval

        self._checkKids(tree, retval, fileobj)
        for attr in fieldAttributes:
            if attr in tree:
                # Tree is a field
                self._buildField(tree, retval, fileobj, fieldAttributes)
                break

        if "/Fields" in tree:
            fields = tree["/Fields"]
            for f in fields:
                field = f.getObject()
                self._buildField(field, retval, fileobj, fieldAttributes)

        return retval

    def _buildField(self, field, retval, fileobj, fieldAttributes):
        self._checkKids(field, retval, fileobj)
        try:
            key = field["/TM"]
        except KeyError:
            try:
                key = field["/T"]
            except KeyError:
                # Ignore no-name field for now
                return
        if fileobj:
            self._writeField(fileobj, field, fieldAttributes)
            fileobj.write("\n")
        retval[key] = Field(field)

    def _checkKids(self, tree, retval, fileobj):
        if "/Kids" in tree:
            # Recurse down the tree
            for kid in tree["/Kids"]:
                self.getFields(kid.getObject(), retval, fileobj)

    def _writeField(self, fileobj, field, fieldAttributes):
        order = ["/TM", "/T", "/FT", "/Parent", "/TU", "/Ff", "/V", "/DV"]

        for attr in order:
            attrName = fieldAttributes[attr]

            try:
                if attr == "/FT":
                    # Make the field type value more clear
                    types = {
                        "/Btn": "Button", "/Tx": "Text", "/Ch": "Choice",
                        "/Sig": "Signature"
                    }
                    if field[attr] in types:
                        fileobj.write(
                            attrName + ": " + types[field[attr]] + "\n"
                        )
                elif attr == "/Parent":
                    # Let's just write the name of the parent
                    try:
                        name = field["/Parent"]["/TM"]
                    except KeyError:
                        name = field["/Parent"]["/T"]
                    fileobj.write(attrName + ": " + name + "\n")
                else:
                    fileobj.write(attrName + ": " + str(field[attr]) + "\n")
            except KeyError:
                # Field attribute is N/A or unknown, so don't write anything
                pass

    @property
    def formTextFields(self):
        """
        Retrieves form fields from the document with textual data (inputs,
        dropdowns).
        """
        formfields = self.getFields()

        return dict(
            (formfields[field]['/T'], formfields[field].get('/V'))
            for field in formfields if formfields[field].get('/FT') == '/Tx'
        )

    def getNamedDestinations(self, tree=None, retval=None):
        """
        Retrieves the named destinations present in the document.

        :return: a dictionary which maps names to
            :class:`Destinations<pypdf.generic.Destination>`.
        :rtype: dict
        """
        if retval is None:
            retval = {}
            catalog = self._trailer["/Root"]

            # get the name tree
            if "/Dests" in catalog:
                tree = catalog["/Dests"]
            elif "/Names" in catalog:
                names = catalog['/Names']
                if "/Dests" in names:
                    tree = names['/Dests']

        if tree is None:
            return retval

        if "/Kids" in tree:
            # recurse down the tree
            for kid in tree["/Kids"]:
                self.getNamedDestinations(kid.getObject(), retval)

        if "/Names" in tree:
            names = tree["/Names"]
            for i in range(0, len(names), 2):
                key = names[i].getObject()
                val = names[i+1].getObject()

                if isinstance(val, DictionaryObject) and '/D' in val:
                    val = val['/D']

                dest = self._buildDestination(key, val)
                if dest is not None:
                    retval[key] = dest

        return retval

    def getOutlines(self, node=None, outlines=None):
        """
        Retrieves the document outline present in the document.

        :return: a nested list of
            :class:`Destinations<pypdf.generic.Destination>`.
        """
        if outlines is None:
            outlines = []
            catalog = self._trailer["/Root"]

            # get the outline dictionary and named destinations
            if "/Outlines" in catalog:
                try:
                    lines = catalog["/Outlines"]
                except PdfReadError:
                    # This occurs if the /Outlines object reference is
                    # incorrect for an example of such a file, see
                    # https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf
                    # so continue to load the file without the Bookmarks
                    return outlines

                if "/First" in lines:
                    node = lines["/First"]

            self._namedDests = self.getNamedDestinations()

        if node is None:
            return outlines

        # see if there are any more outlines
        while True:
            outline = self._buildOutline(node)
            if outline:
                outlines.append(outline)

            # check for sub-outlines
            if "/First" in node:
                subOutlines = []
                self.getOutlines(node["/First"], subOutlines)
                if subOutlines:
                    outlines.append(subOutlines)

            if "/Next" not in node:
                break
            node = node["/Next"]

        return outlines

    def _getPageNumberByIndirect(self, indirectRef):
        """Generate _pageId2Num"""
        if self._pageId2Num is None:
            id2num = {}

            for i, x in enumerate(self.pages):
                id2num[x.indirectRef.idnum] = i

            self._pageId2Num = id2num

        if isinstance(indirectRef, int):
            idnum = indirectRef
        else:
            idnum = indirectRef.idnum

        ret = self._pageId2Num.get(idnum, -1)

        return ret

    def getPageNumber(self, page):
        """
        Retrieve page number of a given PageObject

        :param PageObject page: The page to get page number. Should be
            an instance of :class:`PageObject<pypdf.pdf.PageObject>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        indirectRef = page.indirectRef
        ret = self._getPageNumberByIndirect(indirectRef)
        return ret

    def getDestinationPageNumber(self, destination):
        """
        Retrieves the page number of a given ``Destination`` object

        :param Destination destination: The destination to get page number.
             Should be an instance of
             :class:`Destination<pypdf.pdf.Destination>`
        :return: the page number or ``-1`` if the page was not found.
        :rtype: int
        """
        indirectRef = destination.page
        ret = self._getPageNumberByIndirect(indirectRef)
        return ret

    def _buildDestination(self, title, array):
        return Destination(title, array[0], array[1], *array[2:])

    def _buildOutline(self, node):
        dest, title, outline = None, None, None

        if "/A" in node and "/Title" in node:
            # Action, section 8.5 (only type GoTo supported)
            title = node["/Title"]
            action = node["/A"]
            if action["/S"] == "/GoTo":
                dest = action["/D"]
        elif "/Dest" in node and "/Title" in node:
            # Destination, section 8.2.1
            title = node["/Title"]
            dest = node["/Dest"]

        # if destination found, then create outline
        if dest:
            if isinstance(dest, ArrayObject):
                outline = self._buildDestination(title, dest)
            elif isString(dest) and dest in self._namedDests:
                outline = self._namedDests[dest]
                outline[NameObject("/Title")] = title
            else:
                raise PdfReadError("Unexpected destination %r" % dest)
        return outline

    pages = property(
        lambda self: ConvertFunctionsToVirtualList(
            lambda: self.numPages, self.getPage
        )
    )
    """
    Read-only property that emulates a list based upon the
    :meth:`numPages<PdfFileReader.numPages>` and
    :meth:`getPage()<PdfFileReader.getPage>` methods.
    """

    @property
    def pageLayout(self):
        """
        Get the page layout.
        See :meth:`setPageLayout()<PdfFileWriter.setPageLayout>`
        for a description of valid layouts.

        :return: Page layout currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self._trailer['/Root']['/PageLayout']
        except KeyError:
            return None

    @property
    def pageMode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfFileWriter.setPageMode>`
        for a description of valid modes.

        :return: Page mode currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self._trailer['/Root']['/PageMode']
        except KeyError:
            return None

    def _flatten(self, pages=None, inherit=None, indirectRef=None):
        inheritablePageAttributes = (
            NameObject("/Resources"), NameObject("/MediaBox"),
            NameObject("/CropBox"), NameObject("/Rotate")
        )
        if inherit is None:
            inherit = dict()
        if pages is None:
            self._flattenedPages = []
            catalog = self._trailer["/Root"].getObject()
            pages = catalog["/Pages"].getObject()

        t = "/Pages"
        if "/Type" in pages:
            t = pages["/Type"]

        if t == "/Pages":
            for attr in inheritablePageAttributes:
                if attr in pages:
                    inherit[attr] = pages[attr]
            for page in pages["/Kids"]:
                addt = {}
                if isinstance(page, IndirectObject):
                    addt["indirectRef"] = page
                self._flatten(page.getObject(), inherit, **addt)
        elif t == "/Page":
            for attr, value in list(inherit.items()):
                # If the page has its own value, it does not inherit the
                # parent's value:
                if attr not in pages:
                    pages[attr] = value

            pageObj = PageObject(self, indirectRef)
            pageObj.update(pages)
            self._flattenedPages.append(pageObj)

    def _getObjectByRef(self, ref, source):
        """
        Fetches an indirect object identified by ``ref`` from either the XRef
        Table or the XRef Stream.

        :param ref: an ``IndirectObject`` instance.
        :param source: the source whence the object should be fetched,
            between the XRef Table and the XRef Stream. Accepted values are:\n
            * ``PdfFileReader.R_XTABLE``   XRef Table
            * ``PdfFileReader.R_XSTREAM``    Cross-Reference Stream
        :rtype: PdfObject
        """
        isXTable, isXStream = source & self.R_XTABLE, source & self.R_XSTREAM

        if isXTable:
            if self._xrefTable[ref.generation][ref.idnum][1] is True:
                raise PdfReadError(
                    "Cannot fetch a free object (id, next gen.) = (%d, %d)" %
                    (ref.idnum, ref.generation)
                )

            offset = self._xrefTable[ref.generation][ref.idnum][0]
        elif isXStream:
            # See ISO 32000 (2008), Table 18 "Entries in a cross-reference
            # stream"
            type = self._xrefStm[ref.idnum][0]

            if type == 0:
                raise PdfReadError(
                    "Cannot fetch a free object (id, next gen.) = (%d, %d)" %
                    (ref.idnum, ref.generation)
                )
            elif type == 1:
                offset, generation = self._xrefStm[ref.idnum][1:3]

                if generation != ref.generation:
                    raise ValueError(
                        "Generation number given as input (%d) doesn't equal "
                        "the one stored (%d) in the XRef Stream"
                        % (ref.generation, generation)
                    )
            elif type == 2:
                return self._getCompressedObjectFromXRefStream(ref)
            else:
                # «Any other value shall be interpreted as a reference to the
                # null object, thus permitting new entry types to be defined in
                # the future.» Section 7.5.8.3 of ISO 32000 (2008)
                return NullObject()
        else:
            raise ValueError("Unaccepted value of source = %d" % source)

        self._stream.seek(offset, 0)
        actualId, actualGen = self._readObjectHeader(self._stream)

        if isXTable and self._xrefIndex and actualId != ref.idnum:
            # Xref table probably had bad indexes due to not being
            # zero-indexed
            if self.strict:
                raise PdfReadError(
                    "Expected object ID (%d %d) does not match actual "
                    "(%d %d); xref table not zero-indexed."
                    % (ref.idnum, ref.generation, actualId, actualGen)
                )
            else:
                # XRef Table is corrected in non-strict mode
                pass
        elif self.strict and (
                actualId != ref.idnum or actualGen != ref.generation
        ):
            # Some other problem
            raise PdfReadError(
                "Expected object ID (%d, %d) does not match actual (%d, %d)."
                % (ref.idnum, ref.generation, actualId, actualGen)
            )

        retval = readObject(self._stream, self)

        # Override encryption is used for the /Encrypt dictionary
        if not self._overrideEncryption and self.isEncrypted:
            # If we don't have the encryption key:
            if not hasattr(self, '_decryption_key'):
                raise PdfReadError("file has not been decrypted")

            # otherwise, decrypt here...
            pack1 = struct.pack("<i", ref.idnum)[:3]
            pack2 = struct.pack("<i", ref.generation)[:2]
            key = self._decryption_key + pack1 + pack2
            assert len(key) == (len(self._decryption_key) + 5)
            md5Hash = md5(key).digest()
            key = md5Hash[:min(16, len(self._decryption_key) + 5)]

            retval = self._decryptObject(retval, key)

        return retval

    def _getCompressedObjectFromXRefStream(self, ref):
        """
        Fetches a type 2 compressed object from a Cross-Reference stream.

        :param ref: an ``IndirectObject`` instance.
        :return: a ``PdfObject`` stored into a compressed object stream.
        """
        entryType, objStmId, localId = self._xrefStm[ref.idnum]

        if entryType != 2:
            raise PdfReadError(
                "Expected a type 2 (compressed) object but type is %d" %
                entryType
            )

        # Object streams always have a generation number of 0
        objStm = IndirectObject(objStmId, 0, self).getObject()

        if objStm["/Type"] != "/ObjStm":
            raise PdfReadError(
                "/Type of object stream expected to be /ObjStm, was %s instead"
                % objStm["/Type"]
            )
        if localId >= objStm["/N"]:
            raise PdfStreamError(
                "Local object id is %d, but a maximum of only %d is allowed" %
                (localId, objStm["/N"] - 1)
            )

        streamData = BytesIO(b_(objStm.getData()))

        for index in range(objStm['/N']):
            readNonWhitespace(streamData)
            streamData.seek(-1, 1)
            objnum = NumberObject.readFromStream(streamData)

            readNonWhitespace(streamData)
            streamData.seek(-1, 1)
            offset = NumberObject.readFromStream(streamData)

            readNonWhitespace(streamData)
            streamData.seek(-1, 1)

            if objnum != ref.idnum:
                # We're only interested in one object
                continue
            if self.strict and localId != index:
                raise PdfReadError("Object is in wrong index.")

            streamData.seek(objStm['/First'] + offset, 0)

            try:
                obj = readObject(streamData, self)
            except PdfStreamError as e:
                # Stream object cannot be read. Normally, a critical error,
                # but Adobe Reader doesn't complain, so continue (in strict
                # mode?)
                e = sys.exc_info()[1]
                warnings.warn(
                    "Invalid stream (index %d) within object %d %d: %s" %
                    (index, ref.idnum, ref.generation, e),
                    utils.PdfReadWarning
                )

                if self.strict:
                    raise PdfReadError("Can't read object stream: %s" % e)

                # Replace with null. Hopefully it's nothing important.
                obj = NullObject()

            return obj

        if self.strict:
            raise PdfReadError("This is a fatal error in strict mode.")
        else:
            return NullObject()

    def objects(self, select=R_BOTH, freeObjects=False):
        """
        Returns an iterable of :class:`IndirectObject<generic.IndirectObject>`
        instances (either by the Cross-Reference Tables or Cross-Reference
        Streams) stored in this PDF file.

        :param select: whether to include items from the XRef Table only, the
            Cross-Reference Stream only or both. Accepted values are:\n
            * PdfFileReader.R_XTABLE   Only items from the XRef Table
            * PdfFileReader.R_XSTREAM    Only items from the
                Cross-Reference Stream
            * PdfFileReader.R_BOTH  The default, selects both of the above
        :param freeObjects: whether to include objects from the free entries
            list. Defaults to ``False`` (only objects that can be fetched from
            the File Body are included).
        :return: an unsorted iterable of
            :class:`IndirectObject<generic.IndirectObject>` values.
        """
        if select & self.R_XTABLE:
            # Reverse-sorted list of generation numbers from the XRef Table
            gens = sorted(self._xrefTable.keys(), reverse=True)

            # We give the X-Ref Table a higher precedence than the
            # Cross-Reference Stream
            for gen in gens:
                for id in self._xrefTable[gen]:
                    # "If freeObjects or this object is not a free one..."
                    if freeObjects or self._xrefTable[gen][id][1] is False:
                        yield IndirectObject(id, gen, self)
        if select & self.R_XSTREAM:
            # Iterate through the Cross-Reference Stream
            for id, v in self._xrefStm.items():
                if freeObjects and v[0] == 0:
                   yield IndirectObject(id, v[2], self)
                elif v[0] == 1:
                    yield IndirectObject(id, v[2], self)
                elif v[0] == 2:
                    yield IndirectObject(id, 0, self)

    def getObject(self, ref):
        """
        Retrieves an indirect reference object, caching it appropriately, from
        the File Body of the associated PDF file.

        :param IndirectObject ref: an
            :class:`IndirectObject<generic.IndirectObject>` instance
            identifying the indirect object properties (id. and gen. number).
        :return: the :class:`PdfObject<generic.PdfObject` queried for, if
            found.
        :raises PdfReadError: if ``ref`` did not relate to any object.
        """
        if (ref.generation, ref.idnum) in self._cachedObjects:
            return self._cachedObjects[(ref.generation, ref.idnum)]
        elif ref.idnum in self._xrefStm:
            retval = self._getObjectByRef(ref, self.R_XSTREAM)
        elif ref.generation in self._xrefTable and \
                ref.idnum in self._xrefTable[ref.generation]:
            retval = self._getObjectByRef(ref, self.R_XTABLE)
        else:
            warnings.warn(
                "Object %d %d not defined." %
                (ref.idnum, ref.generation), PdfReadWarning
            )
            raise PdfReadError(
                "Could not find object (%d, %d)" % (ref.idnum, ref.generation)
            )

        self._cacheIndirectObject(ref.generation, ref.idnum, retval)

        return retval

    def isObjectFree(self, ref):
        """
        :param ref: a :class:`IndirectObject<pypdf.generic.IndirectObject>`
            instance.
        :return: ``True`` if ``ref`` is in the free entries list, ``False``
            otherwise.
        """
        if ref.generation in self._xrefTable\
            and ref.idnum in self._xrefTable[ref.generation]:
            return self._xrefTable[ref.generation][ref.idnum][1]
        elif ref.idnum in self._xrefStm:
            return self._xrefStm[ref.idnum][0] == 0

        # Object does not exist
        raise ValueError(
            "%r does not exist in %s" % (str(ref), self._filepath)
        )

    def _parsePdfFile(self, stream):
        def getEntry(i, streamData):
            """
            Reads the correct number of bytes for each entry. See the
            discussion of the ``/W`` parameter in ISO 32000, section 7.5.8.2,
            table 17.
            """
            if entrySizes[i] > 0:
                d = streamData.read(entrySizes[i])
                return _convertToInt(d, entrySizes[i])

            # PDF Spec Table 17: A value of zero for an element in the
            # W array indicates... the default value shall be used
            if i == 0:
                # First value defaults to 1
                return 1
            else:
                return 0

        def usedBefore(num, generation):
            # We move backwards through the xrefs, don't replace any.
            return num in self._xrefTable.get(generation, []) or \
                   num in self._xrefStm

        stream.seek(-1, 2)  # Start at the end:

        if not stream.tell():
            raise PdfReadError("Cannot read an empty file")

        # Offset of last 1024 bytes of stream
        last1K = stream.tell() - 1024 + 1
        line = b_('')

        while line[:5] != b_("%%EOF"):
            if stream.tell() < last1K:
                raise PdfReadError("EOF marker not found")

            line = self._readNextEndLine(stream)

        # Find startxref entry - the location of the xref table
        line = self._readNextEndLine(stream)
        try:
            startxref = int(line)
        except ValueError:
            # startxref may be on the same line as the location
            if not line.startswith(b_("startxref")):
                raise PdfReadError("startxref not found")

            startxref = int(line[9:].strip())
            warnings.warn("startxref on same line as offset")
        else:
            line = self._readNextEndLine(stream)

            if line[:9] != b_("startxref"):
                raise PdfReadError("startxref not found")

        # Read all cross reference tables and their trailers
        while True:
            # Load the xref table
            stream.seek(startxref, 0)
            x = stream.read(1)

            if x == b_("x"):
                # Standard cross-reference table
                ref = stream.read(4)

                if ref[:3] != b_("ref"):
                    raise PdfReadError("xref table read error")

                readNonWhitespace(stream)
                stream.seek(-1, 1)
                # Check if the first time looking at the xref table
                firsttime = True

                while True:
                    # The current id of this subsection items
                    currid = readObject(stream, self)

                    if firsttime and currid != 0:
                        self._xrefIndex = currid

                        if self.strict:
                            warnings.warn(
                                "Xref table not zero-indexed. ID numbers for "
                                "objects will be corrected.",
                                PdfReadWarning
                            )
                            # If table not zero indexed, could be due to error
                            # from when PDF was created #which will lead to
                            # mismatched indices later on, only warned and
                            # corrected if self.strict=True

                    firsttime = False
                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    size = readObject(stream, self)
                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    cnt = 0

                    while cnt < size:
                        line = stream.read(20)
                        # It's very clear in section 3.4.3 of the PDF spec
                        # that all cross-reference table lines are a fixed
                        # 20 bytes (as of PDF 1.7). However, some files have
                        # 21-byte entries (or more) due to the use of \r\n
                        # (CRLF) EOL's. Detect that case, and adjust the line
                        # until it does not begin with a \r (CR) or \n (LF).
                        while line[0] in b_("\x0D\x0A"):
                            stream.seek(-20 + 1, 1)
                            line = stream.read(20)

                        # On the other hand, some malformed PDF files
                        # use a single character EOL without a preceeding
                        # space.  Detect that case, and seek the stream
                        # back one character.  (0-9 means we've bled into
                        # the next xref entry, t means we've bled into the
                        # text "trailer"):
                        if line[-1] in b_("0123456789t"):
                            stream.seek(-1, 1)

                        offset, generation = line[:16].split(b_(" "))
                        offset, generation = int(offset), int(generation)
                        # state should be in {"f", "n"}
                        state = line[17]

                        # Probably stream is a byte string and we need to
                        # convert a single line[k] to str
                        if isinstance(state, int):
                            state = chr(state)

                        if state not in "fn":
                            raise PdfReadError(
                                "Error in Cross-Reference table with object "
                                "(%d, %d): third item (18th byte) should be "
                                "either \"n\" or \"f\", found \"%c\"" % (
                                    currid, offset, state
                                )
                            )

                        if generation not in self._xrefTable:
                            self._xrefTable[generation] = {}
                        if currid in self._xrefTable[generation]:
                            # It really seems like we should allow the last
                            # xref table in the file to override previous
                            # ones. Since we read the file backwards, assume
                            # any existing key is already set correctly.
                            pass
                        else:
                            self._xrefTable[generation][currid] \
                                = (offset, state == "f")

                        cnt += 1
                        currid += 1

                    readNonWhitespace(stream)
                    stream.seek(-1, 1)
                    trailertag = stream.read(7)

                    if trailertag != b_("trailer"):
                        # More xrefs!
                        stream.seek(-7, 1)
                    else:
                        break

                readNonWhitespace(stream)
                stream.seek(-1, 1)
                newTrailer = readObject(stream, self)

                for key, value in newTrailer.items():
                    if key not in self._trailer:
                        self._trailer[key] = value

                if "/XRefStm" in newTrailer:
                    startxref = newTrailer["/XRefStm"]
                elif "/Prev" in newTrailer:
                    startxref = newTrailer["/Prev"]
                else:
                    break
            elif x.isdigit():   # PDF 1.5+ Cross-Reference Stream
                stream.seek(-1, 1)
                xrefstreamOffset = stream.tell()
                xrefstmId, xrefstmGen = self._readObjectHeader(stream)
                xrefstream = readObject(stream, self)

                if xrefstream["/Type"] != "/XRef":
                    raise PdfReadError(
                        "The type of this object should be /XRef, found %s "
                        "instead" % xrefstream["/Type"]
                    )

                self._cacheIndirectObject(xrefstmGen, xrefstmId, xrefstream)

                streamData = BytesIO(b_(xrefstream.getData()))
                # Index pairs specify the subsections in the dictionary. If
                # none create one subsection that spans everything.
                idrange = xrefstream.get(
                    "/Index", [0, xrefstream.get("/Size")]
                )

                entrySizes = xrefstream.get("/W")

                if len(entrySizes) < 3:
                    raise PdfReadError(
                        "Insufficient number of /W entries: %s" % entrySizes
                    )
                if self.strict and len(entrySizes) > 3:
                    raise PdfReadError(
                        "Excess number of /W entries: %s" % entrySizes
                    )

                # Iterate through each subsection
                lastEnd = 0

                for start, size in pairs(idrange):
                    # The subsections must increase
                    assert start >= lastEnd
                    lastEnd = start + size

                    for idnum in range(start, start + size):
                        # The first entry is the type
                        xrefType = getEntry(0, streamData)

                        # The rest of the elements depend on the xrefType
                        if xrefType == 0:
                            # Linked list of free objects
                            nextFreeObject = getEntry(1, streamData)
                            nextGeneration = getEntry(2, streamData)

                            self._xrefStm[idnum] = (
                                0, nextFreeObject, nextGeneration
                            )
                        elif xrefType == 1:
                            # Objects that are in use but are not compressed
                            byteOffset = getEntry(1, streamData)
                            generation = getEntry(2, streamData)

                            if not usedBefore(idnum, generation):
                                self._xrefStm[idnum] = (
                                    1, byteOffset, generation
                                )
                        elif xrefType == 2:
                            # Compressed objects
                            objStmId = getEntry(1, streamData)
                            localId = getEntry(2, streamData)
                            # According to PDF spec table 18, generation is 0

                            if not usedBefore(idnum, 0):
                                self._xrefStm[idnum] = (2, objStmId, localId)
                        elif self.strict:
                            raise PdfReadError(
                                "Unknown xref type: %s" % xrefType
                            )

                # As we've seen this happen, if the XRef Stream wasn't indexed
                # in neither the XRef Table or within itself, we artificially
                # add it with a /W type value of 1 (used but uncompressed
                # objects).
                if not usedBefore(xrefstmId, xrefstmGen):
                    self._xrefStm[xrefstmId] = (
                        1, xrefstreamOffset, xrefstmGen
                    )

                trailerKeys = ("/Root", "/Encrypt", "/Info", "/ID")

                for key in trailerKeys:
                    if key in xrefstream and key not in self._trailer:
                        self._trailer[NameObject(key)] = xrefstream.rawGet(key)

                if "/Prev" in xrefstream:
                    startxref = xrefstream["/Prev"]
                else:
                    break
            else:
                # Bad xref character at startxref.  Let's see if we can find
                # the xref table nearby, as we've observed this error with an
                # off-by-one before.
                stream.seek(-11, 1)
                tmp = stream.read(20)
                xrefLoc = tmp.find(b_("xref"))

                if xrefLoc != -1:
                    startxref -= (10 - xrefLoc)
                    continue
                # No explicit xref table, try finding a cross-reference stream.
                stream.seek(startxref, 0)
                found = False

                for look in range(5):
                    if stream.read(1).isdigit():
                        # This is not a standard PDF, consider adding a warning
                        startxref += look
                        found = True
                        break
                if found:
                    continue
                # No xref table found at specified location
                raise PdfReadError(
                    "Could not find xref table at specified location"
                )

        # If not zero-indexed, verify that the table is correct; change it if
        # necessary
        if self._xrefIndex and not self.strict:
            loc = stream.tell()

            for gen in self._xrefTable:
                if gen == 65535:
                    continue

                for id in self._xrefTable[gen]:
                    stream.seek(self._xrefTable[gen][id][0], 0)

                    try:
                        pid, pgen = self._readObjectHeader(stream)
                    except ValueError:
                        break

                    if pid == id - self._xrefIndex:
                        self._zeroXref(gen)
                        break
                    # If not, then either it's just plain wrong, or the
                    # non-zero-index is actually correct

            # Return to where it was
            stream.seek(loc, 0)

    def _decryptObject(self, obj, key):
        if isinstance(obj, ByteStringObject)\
                or isinstance(obj, TextStringObject):
            obj = createStringObject(RC4Encrypt(key, obj.original_bytes))
        elif isinstance(obj, StreamObject):
            obj._data = RC4Encrypt(key, obj._data)
        elif isinstance(obj, DictionaryObject):
            for dictkey, value in list(obj.items()):
                obj[dictkey] = self._decryptObject(value, key)
        elif isinstance(obj, ArrayObject):
            for i in range(len(obj)):
                obj[i] = self._decryptObject(obj[i], key)

        return obj

    def _readObjectHeader(self, stream):
        # Should never be necessary to read out whitespace, since the
        # cross-reference table should put us in the right spot to read the
        # object header.  In reality... some files have stupid cross reference
        # tables that are off by whitespace bytes.
        extra = False
        utils.skipOverComment(stream)
        extra |= utils.skipOverWhitespace(stream)
        stream.seek(-1, 1)

        idnum = readUntilWhitespace(stream)
        extra |= utils.skipOverWhitespace(stream)
        stream.seek(-1, 1)

        generation = readUntilWhitespace(stream)
        obj = stream.read(3)
        readNonWhitespace(stream)
        stream.seek(-1, 1)

        if extra and self.strict:
            # Not a fatal error
            warnings.warn(
                "Superfluous whitespace found in object header %s %s" %
                (idnum, generation), PdfReadWarning
            )

        return int(idnum), int(generation)

    def _cacheIndirectObject(self, generation, idnum, obj):
        # Sometimes we want to turn off cache for debugging.
        if (generation, idnum) in self._cachedObjects:
            msg = "Overwriting cache for %s %s" % (generation, idnum)

            if self.strict:
                raise PdfReadError(msg)
            else:
                warnings.warn(msg)

        self._cachedObjects[(generation, idnum)] = obj

        return obj

    def _zeroXref(self, generation):
        self._xrefTable[generation] = dict(
            (id - self._xrefIndex, v) for (id, v)
            in list(self._xrefTable[generation].items())
        )

    def _readNextEndLine(self, stream):
        line = b_("")

        while True:
            # Prevent infinite loops in malformed PDFs
            if stream.tell() == 0:
                raise PdfReadError("Could not read malformed PDF file")
            x = stream.read(1)

            if stream.tell() < 2:
                raise PdfReadError("EOL marker not found")

            stream.seek(-2, 1)

            if x == b_('\n') or x == b_('\r'):  # \n = LF; \r = CR
                crlf = False

                while x == b_('\n') or x == b_('\r'):
                    x = stream.read(1)
                    if x == b_('\n') or x == b_('\r'): # account for CR+LF
                        stream.seek(-1, 1)
                        crlf = True
                    if stream.tell() < 2:
                        raise PdfReadError("EOL marker not found")
                    stream.seek(-2, 1)

                # If using CR+LF, go back 2 bytes, else 1
                stream.seek(2 if crlf else 1, 1)
                break
            else:
                line = x + line

        return line

    def decrypt(self, password):
        """
        When using an encrypted/secured PDF file with the PDF Standard
        encryption handler, this function will allow the file to be decrypted.
        It checks the given password against the document's user password and
        owner password, and then stores the resulting decryption key if either
        password is correct.

        It does not matter which password was matched.  Both passwords provide
        the correct decryption key that will allow the document to be used with
        this library.

        :param str password: The password to match.
        :return: ``0`` if the password failed, ``1`` if the password matched
            the user password, and ``2`` if the password matched the owner
            password.
        :rtype: int
        :raises NotImplementedError: if document uses an unsupported encryption
            method.
        """
        self._overrideEncryption = True

        try:
            return self._decrypt(password)
        finally:
            self._overrideEncryption = False

    def _decrypt(self, password):
        encrypt = self._trailer['/Encrypt'].getObject()

        if encrypt['/Filter'] != '/Standard':
            raise NotImplementedError(
                "only Standard PDF encryption handler is available"
            )
        if not (encrypt['/V'] in (1, 2)):
            raise NotImplementedError(
                "only algorithm codes 1 and 2 are supported. This PDF uses "
                "code %s" % encrypt['/V']
            )
        user_password, key = self._authenticateUserPassword(password)

        if user_password:
            self._decryption_key = key
            return 1
        else:
            rev = encrypt['/R'].getObject()

            if rev == 2:
                keylen = 5
            else:
                keylen = encrypt['/Length'].getObject() // 8

            key = _alg33_1(password, rev, keylen)
            real_O = encrypt["/O"].getObject()

            if rev == 2:
                userpass = RC4Encrypt(key, real_O)
            else:
                val = real_O

                for i in range(19, -1, -1):
                    new_key = b_('')

                    for l in range(len(key)):
                        new_key += b_(chr(pypdfOrd(key[l]) ^ i))

                    val = RC4Encrypt(new_key, val)
                userpass = val
            owner_password, key = self._authenticateUserPassword(userpass)

            if owner_password:
                self._decryption_key = key
                return 2

        return 0

    def _authenticateUserPassword(self, password):
        encrypt = self._trailer['/Encrypt'].getObject()
        rev = encrypt['/R'].getObject()
        owner_entry = encrypt['/O'].getObject()
        p_entry = encrypt['/P'].getObject()
        id_entry = self._trailer['/ID'].getObject()
        id1_entry = id_entry[0].getObject()
        real_U = encrypt['/U'].getObject().original_bytes

        if rev == 2:
            U, key = _alg34(password, owner_entry, p_entry, id1_entry)
        elif rev >= 3:
            U, key = _alg35(
                password, rev, encrypt["/Length"].getObject() // 8,
                owner_entry, p_entry, id1_entry,
                encrypt.get("/EncryptMetadata", BooleanObject(False))
                    .getObject()
            )
            U, real_U = U[:16], real_U[:16]

        return U == real_U, key

    @property
    def isEncrypted(self):
        return "/Encrypt" in self._trailer


def _convertToInt(d, size):
    if size > 8:
        raise PdfReadError("Invalid size in _convertToInt")

    d = b_("\x00\x00\x00\x00\x00\x00\x00\x00") + b_(d)
    d = d[-8:]

    return struct.unpack(">q", d)[0]


# TO-DO Refactor the code pertaining to these _algX() functions, as they do not
# seem to conform with OOP and local project conventions.
# ref: pdf1.8 spec section 3.5.2 algorithm 3.2
_ENCRYPTION_PADDING =\
    b_('\x28\xbf\x4e\x5e\x4e\x75\x8a\x41\x64\x00\x4e\x56') + \
    b_('\xff\xfa\x01\x08\x2e\x2e\x00\xb6\xd0\x68\x3e\x80\x2f\x0c') + \
    b_('\xa9\xfe\x64\x53\x69\x7a')


def _alg32(
        password, rev, keylen, owner_entry, p_entry, id1_entry,
        metadata_encrypt=True
):
    """
    Implementation of algorithm 3.2 of the PDF standard security handler,
    section 3.5.2 of the PDF 1.6 reference.
    """
    # 1. Pad or truncate the password string to exactly 32 bytes.  If the
    # password string is more than 32 bytes long, use only its first 32 bytes;
    # if it is less than 32 bytes long, pad it by appending the required number
    # of additional bytes from the beginning of the padding string
    # (_ENCRYPTION_PADDING).
    password = b_((pypdfStr(password) + pypdfStr(_ENCRYPTION_PADDING))[:32])
    # 2. Initialize the MD5 hash function and pass the result of step 1 as
    # input to this function.
    m = md5(password)
    # 3. Pass the value of the encryption dictionary's /O entry to the MD5 hash
    # function.
    m.update(owner_entry.original_bytes)
    # 4. Treat the value of the /P entry as an unsigned 4-byte integer and pass
    # these bytes to the MD5 hash function, low-order byte first.
    p_entry = struct.pack('<i', p_entry)
    m.update(p_entry)
    # 5. Pass the first element of the file's file identifier array to the MD5
    # hash function.
    m.update(id1_entry.original_bytes)
    # 6. (Revision 3 or greater) If document metadata is not being encrypted,
    # pass 4 bytes with the value 0xFFFFFFFF to the MD5 hash function.
    if rev >= 3 and not metadata_encrypt:
        m.update(b_("\xff\xff\xff\xff"))
    # 7. Finish the hash.
    md5_hash = m.digest()
    # 8. (Revision 3 or greater) Do the following 50 times: Take the output
    # from the previous MD5 hash and pass the first n bytes of the output as
    # input into a new MD5 hash, where n is the number of bytes of the
    # encryption key as defined by the value of the encryption dictionary's
    # /Length entry.
    if rev >= 3:
        for i in range(50):
            md5_hash = md5(md5_hash[:keylen]).digest()
    # 9. Set the encryption key to the first n bytes of the output from the
    # final MD5 hash, where n is always 5 for revision 2 but, for revision 3 or
    # greater, depends on the value of the encryption dictionary's /Length
    # entry.
    return md5_hash[:keylen]


def _alg33(owner_pwd, user_pwd, rev, keylen):
    """
    Implementation of algorithm 3.3 of the PDF standard security handler,
    section 3.5.2 of the PDF 1.6 reference.
    """
    # steps 1 - 4
    key = _alg33_1(owner_pwd, rev, keylen)
    # 5. Pad or truncate the user password string as described in step 1 of
    # algorithm 3.2.
    user_pwd = b_((user_pwd + pypdfStr(_ENCRYPTION_PADDING))[:32])
    # 6. Encrypt the result of step 5, using an RC4 encryption function with
    # the encryption key obtained in step 4.
    val = RC4Encrypt(key, user_pwd)
    # 7. (Revision 3 or greater) Do the following 19 times: Take the output
    # from the previous invocation of the RC4 function and pass it as input to
    # a new invocation of the function; use an encryption key generated by
    # taking each byte of the encryption key obtained in step 4 and performing
    # an XOR operation between that byte and the single-byte value of the
    # iteration counter (from 1 to 19).
    if rev >= 3:
        for i in range(1, 20):
            new_key = ''
            for l in range(len(key)):
                new_key += chr(pypdfOrd(key[l]) ^ i)
            val = RC4Encrypt(new_key, val)
    # 8. Store the output from the final invocation of the RC4 as the value of
    # the /O entry in the encryption dictionary.
    return val


def _alg33_1(password, rev, keylen):
    """
    Steps 1-4 of algorithm 3.3.
    """
    # 1. Pad or truncate the owner password string as described in step 1 of
    # algorithm 3.2.  If there is no owner password, use the user password
    # instead.
    password = b_((password + pypdfStr(_ENCRYPTION_PADDING))[:32])
    # 2. Initialize the MD5 hash function and pass the result of step 1 as
    # input to this function.
    m = md5(password)
    # 3. (Revision 3 or greater) Do the following 50 times: Take the output
    # from the previous MD5 hash and pass it as input into a new MD5 hash.
    md5_hash = m.digest()
    if rev >= 3:
        for i in range(50):
            md5_hash = md5(md5_hash).digest()
    # 4. Create an RC4 encryption key using the first n bytes of the output
    # from the final MD5 hash, where n is always 5 for revision 2 but, for
    # revision 3 or greater, depends on the value of the encryption
    # dictionary's /Length entry.
    key = md5_hash[:keylen]
    return key


def _alg34(password, owner_entry, p_entry, id1_entry):
    """
    Implementation of algorithm 3.4 of the PDF standard security handler,
    section 3.5.2 of the PDF 1.6 reference.
    """
    # 1. Create an encryption key based on the user password string, as
    # described in algorithm 3.2.
    key = _alg32(password, 2, 5, owner_entry, p_entry, id1_entry)
    # 2. Encrypt the 32-byte padding string shown in step 1 of algorithm 3.2,
    # using an RC4 encryption function with the encryption key from the
    # preceding step.
    U = RC4Encrypt(key, _ENCRYPTION_PADDING)
    # 3. Store the result of step 2 as the value of the /U entry in the
    # encryption dictionary.
    return U, key


def _alg35(
        password, rev, keylen, owner_entry, p_entry, id1_entry,
        metadata_encrypt
):
    """
    Implementation of algorithm 3.4 of the PDF standard security handler,
    section 3.5.2 of the PDF 1.6 reference.
    """
    # 1. Create an encryption key based on the user password string, as
    # described in Algorithm 3.2.
    key = _alg32(password, rev, keylen, owner_entry, p_entry, id1_entry)
    # 2. Initialize the MD5 hash function and pass the 32-byte padding string
    # shown in step 1 of Algorithm 3.2 as input to this function.
    m = md5()
    m.update(_ENCRYPTION_PADDING)
    # 3. Pass the first element of the file's file identifier array (the value
    # of the ID entry in the document's trailer dictionary; see Table 3.13 on
    # page 73) to the hash function and finish the hash.  (See implementation
    # note 25 in Appendix H.)
    m.update(id1_entry.original_bytes)
    md5_hash = m.digest()
    # 4. Encrypt the 16-byte result of the hash, using an RC4 encryption
    # function with the encryption key from step 1.
    val = RC4Encrypt(key, md5_hash)
    # 5. Do the following 19 times: Take the output from the previous
    # invocation of the RC4 function and pass it as input to a new invocation
    # of the function; use an encryption key generated by taking each byte of
    # the original encryption key (obtained in step 2) and performing an XOR
    # operation between that byte and the single-byte value of the iteration
    # counter (from 1 to 19).
    for i in range(1, 20):
        new_key = b_('')
        for l in range(len(key)):
            new_key += b_(chr(pypdfOrd(key[l]) ^ i))
        val = RC4Encrypt(new_key, val)
    # 6. Append 16 bytes of arbitrary padding to the output from the final
    # invocation of the RC4 function and store the 32-byte result as the value
    # of the U entry in the encryption dictionary.
    # (implementator note: I don't know what "arbitrary padding" is supposed to
    # mean, so I have used null bytes.  This seems to match a few other
    # people's implementations)
    return val + (b_('\x00') * 16), key
