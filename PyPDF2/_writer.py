# -*- coding: utf-8 -*-
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

import codecs
import logging
import struct
import uuid
import warnings
from hashlib import md5

from PyPDF2._page import PageObject
from PyPDF2._security import _alg33, _alg34, _alg35
from PyPDF2._utils import DEPR_MSG, _isString, _VirtualList, b_, u_
from PyPDF2.constants import CatalogAttributes as CA
from PyPDF2.constants import Core as CO
from PyPDF2.constants import EncryptionDictAttributes as ED
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import PagesAttributes as PA
from PyPDF2.constants import StreamAttributes as SA
from PyPDF2.constants import TrailerKeys as TK
from PyPDF2.generic import (
    ArrayObject,
    BooleanObject,
    ByteStringObject,
    ContentStream,
    DecodedStreamObject,
    Destination,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    RectangleObject,
    StreamObject,
    TextStringObject,
    TreeObject,
    createStringObject,
)

logger = logging.getLogger(__name__)


class PdfWriter(object):
    """
    This class supports writing PDF files out, given pages produced by another
    class (typically :class:`PdfReader<PdfReader>`).
    """

    def __init__(self):
        self._header = b_("%PDF-1.3")
        self._objects = []  # array of indirect objects

        # The root of our page tree node.
        pages = DictionaryObject()
        pages.update(
            {
                NameObject(PA.TYPE): NameObject("/Pages"),
                NameObject(PA.COUNT): NumberObject(0),
                NameObject(PA.KIDS): ArrayObject(),
            }
        )
        self._pages = self._add_object(pages)

        # info object
        info = DictionaryObject()
        info.update(
            {
                NameObject("/Producer"): createStringObject(
                    codecs.BOM_UTF16_BE + u_("PyPDF2").encode("utf-16be")
                )
            }
        )
        self._info = self._add_object(info)

        # root object
        root = DictionaryObject()
        root.update(
            {
                NameObject(PA.TYPE): NameObject(CO.CATALOG),
                NameObject(CO.PAGES): self._pages,
            }
        )
        self._root = None
        self._root_object = root
        self.set_need_appearances_writer()

    def _add_object(self, obj):
        self._objects.append(obj)
        return IndirectObject(len(self._objects), 0, self)

    def get_object(self, ido):
        if ido.pdf != self:
            raise ValueError("pdf must be self")
        return self._objects[ido.idnum - 1]  # type: ignore

    def getObject(self, ido):
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_object` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getObject()", "get_object()"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_object(ido)

    def _add_page(self, page, action):
        assert page[PA.TYPE] == CO.PAGE
        page[NameObject(PA.PARENT)] = self._pages
        page = self._add_object(page)
        pages = self.get_object(self._pages)
        action(pages[PA.KIDS], page)
        pages[NameObject(PA.COUNT)] = NumberObject(pages[PA.COUNT] + 1)

    def set_need_appearances_writer(self):
        # See 12.7.2 and 7.7.2 for more information:
        # http://www.adobe.com/content/dam/acom/en/devnet/acrobat/pdfs/PDF32000_2008.pdf
        try:
            catalog = self._root_object
            # get the AcroForm tree
            if "/AcroForm" not in catalog:
                self._root_object.update(
                    {
                        NameObject("/AcroForm"): IndirectObject(
                            len(self._objects), 0, self
                        )
                    }
                )

            need_appearances = NameObject("/NeedAppearances")
            self._root_object["/AcroForm"][need_appearances] = BooleanObject(True)  # type: ignore

        except Exception as exc:
            logger.error("set_need_appearances_writer() catch : ", repr(exc))

    def add_page(self, page):
        """
        Add a page to this PDF file.  The page is usually acquired from a
        :class:`PdfReader<PdfReader>` instance.

        :param PageObject page: The page to add to the document. Should be
            an instance of :class:`PageObject<PyPDF2._page.PageObject>`
        """
        self._add_page(page, list.append)

    def addPage(self, page):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_page` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addPage()", "add_page()"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.add_page(page)

    def insert_page(self, page, index=0):
        """
        Insert a page in this PDF file. The page is usually acquired from a
        :class:`PdfReader<PdfReader>` instance.

        :param PageObject page: The page to add to the document.  This
            argument should be an instance of :class:`PageObject<PyPDF2._page.PageObject>`.
        :param int index: Position at which the page will be inserted.
        """
        self._add_page(page, lambda l, p: l.insert(index, p))

    def insertPage(self, page, index=0):
        """
        .. deprecated:: 1.28.0

            Use :meth:`insert_page` instead.
        """
        warnings.warn(
            DEPR_MSG.format("insertPage()", "insert_page()"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.insert_page(page, index)

    def get_page(self, page_number):
        """
        Retrieve a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: the page at the index given by *pageNumber*
        :rtype: :class:`PageObject<PyPDF2._page.PageObject>`
        """
        pages = self.get_object(self._pages)
        # XXX: crude hack
        return pages[PA.KIDS][page_number].get_object()

    def getPage(self, pageNumber):
        """
        .. deprecated:: 1.28.0

            Use :code:`writer.pages[page_number]` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getPage()", "writer.pages[page_number]"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_page(pageNumber)

    def _get_num_pages(
        self,
    ):  # consistency with reader: should be possible to use the same
        """
        :return: the number of pages.
        :rtype: int
        """
        pages = self.get_object(self._pages)
        return int(pages[NameObject("/Count")])

    def getNumPages(self):
        """
        .. deprecated:: 1.28.0

            Use :code:`len(writer.pages)` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getNumPages()", "len(writer.pages)"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._get_num_pages()

    @property
    def pages(self):
        """
        Property that emulates a list of :class:`PageObject<PyPDF2._page.PageObject>`
        """
        return _VirtualList(self._get_num_pages, self.get_page)

    def add_blank_page(self, width=None, height=None):
        """
        Append a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :return: the newly appended page
        :rtype: :class:`PageObject<PyPDF2._page.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        page = PageObject.create_blank_page(self, width, height)
        self.add_page(page)
        return page

    def addBlankPage(self, width=None, height=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_blank_page` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addBlankPage", "add_blank_page"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.add_blank_page(width, height)

    def insert_blank_page(self, width=None, height=None, index=0):
        """
        Insert a blank page to this PDF file and returns it. If no page size
        is specified, use the size of the last page.

        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default
            user space units.
        :param int index: Position to add the page.
        :return: the newly appended page
        :rtype: :class:`PageObject<PyPDF2._page.PageObject>`
        :raises PageSizeNotDefinedError: if width and height are not defined
            and previous page does not exist.
        """
        if width is None or height is None and (self._get_num_pages() - 1) >= index:
            oldpage = self.get_page(index)
            width = oldpage.mediabox.width
            height = oldpage.mediabox.height
        page = PageObject.create_blank_page(self, width, height)
        self.insert_page(page, index)
        return page

    def insertBlankPage(self, width=None, height=None, index=0):
        """
        .. deprecated:: 1.28.0

            Use :meth:`insertBlankPage` instead.
        """
        warnings.warn(
            DEPR_MSG.format("insertBlankPage", "insert_blank_page"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.insert_blank_page(width, height, index)

    def add_js(self, javascript):
        """
        Add Javascript which will launch upon opening this PDF.

        :param str javascript: Your Javascript.

        >>> output.add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        # Example: This will launch the print window when the PDF is opened.
        """
        js = DictionaryObject()
        js.update(
            {
                NameObject(PA.TYPE): NameObject("/Action"),
                NameObject("/S"): NameObject("/JavaScript"),
                NameObject("/JS"): NameObject("(%s)" % javascript),
            }
        )
        js_indirect_object = self._add_object(js)

        # We need a name for parameterized javascript in the pdf file, but it can be anything.
        js_string_name = str(uuid.uuid4())

        js_name_tree = DictionaryObject()
        js_name_tree.update(
            {
                NameObject("/JavaScript"): DictionaryObject(
                    {
                        NameObject(CA.NAMES): ArrayObject(
                            [createStringObject(js_string_name), js_indirect_object]
                        )
                    }
                )
            }
        )
        self._add_object(js_name_tree)

        self._root_object.update(
            {
                NameObject("/OpenAction"): js_indirect_object,
                NameObject(CA.NAMES): js_name_tree,
            }
        )

    def addJS(self, javascript):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_js` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addJS", "add_js"), PendingDeprecationWarning, stacklevel=2
        )
        return self.add_js(javascript)

    def add_attachment(self, filename, data):
        """
        Embed a file inside the PDF.

        :param str filename: The filename to display.
        :param str data: The data in the file.

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
        file_entry.setData(data)
        file_entry.update({NameObject(PA.TYPE): NameObject("/EmbeddedFile")})

        # The Filespec entry
        """ Sample:
        7 0 obj
        <<
         /Type /Filespec
         /F (hello.txt)
         /EF << /F 8 0 R >>
        >>
        """
        ef_entry = DictionaryObject()
        ef_entry.update({NameObject("/F"): file_entry})

        filespec = DictionaryObject()
        filespec.update(
            {
                NameObject(PA.TYPE): NameObject("/Filespec"),
                NameObject("/F"): createStringObject(
                    filename
                ),  # Perhaps also try TextStringObject
                NameObject("/EF"): ef_entry,
            }
        )

        # Then create the entry for the root, as it needs a reference to the Filespec
        """ Sample:
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
        embeddedFilesNamesDictionary.update(
            {
                NameObject(CA.NAMES): ArrayObject(
                    [createStringObject(filename), filespec]
                )
            }
        )

        embeddedFilesDictionary = DictionaryObject()
        embeddedFilesDictionary.update(
            {NameObject("/EmbeddedFiles"): embeddedFilesNamesDictionary}
        )
        # Update the root
        self._root_object.update({NameObject(CA.NAMES): embeddedFilesDictionary})

    def addAttachment(self, fname, fdata):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_attachment` instead.
        """
        warnings.warn(
            DEPR_MSG.format(
                "addAttachment(fname, fdata)", "add_attachment(filename, data)"
            ),
        )
        return self.add_attachment(fname, fdata)

    def append_pages_from_reader(self, reader, after_page_append=None):
        """
        Copy pages from reader to writer. Includes an optional callback parameter
        which is invoked after pages are appended to the writer.

        :param reader: a PdfReader object from which to copy page
            annotations to this writer object.  The writer's annots
            will then be updated
        :callback after_page_append (function): Callback function that is invoked after
            each page is appended to the writer. Callback signature:
        :param writer_pageref (PDF page reference): Reference to the page
            appended to the writer.
        """
        # Get page count from writer and reader
        reader_num_pages = len(reader.pages)
        writer_num_pages = len(self.pages)

        # Copy pages from reader to writer
        for rpagenum in range(0, reader_num_pages):
            reader_page = reader.pages[rpagenum]
            self.add_page(reader_page)
            writer_page = self.get_page(writer_num_pages + rpagenum)
            # Trigger callback, pass writer page as parameter
            if callable(after_page_append):
                after_page_append(writer_page)

    def appendPagesFromReader(self, reader, after_page_append=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`append_pages_from_reader` instead.
        """
        warnings.warn(
            DEPR_MSG.format("appendPagesFromReader", "append_pages_from_reader"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.append_pages_from_reader(reader, after_page_append)

    def update_page_form_field_values(self, page, fields, flags=0):
        """
        Update the form field values for a given page from a fields dictionary.
        Copy field texts and values from fields to page.
        If the field links to a parent object, add the information to the parent.

        :param page: Page reference from PDF writer where the annotations
            and field data will be updated.
        :param fields: a Python dictionary of field names (/T) and text
            values (/V)
        :param flags: An integer (0 to 7). The first bit sets ReadOnly, the
            second bit sets Required, the third bit sets NoExport. See
            PDF Reference Table 8.70 for details.
        """
        # Iterate through pages, update field values
        for j in range(len(page[PG.ANNOTS])):  # type: ignore
            writer_annot = page[PG.ANNOTS][j].get_object()  # type: ignore
            # retrieve parent field values, if present
            writer_parent_annot = {}  # fallback if it's not there
            if PG.PARENT in writer_annot:
                writer_parent_annot = writer_annot[PG.PARENT]
            for field in fields:
                if writer_annot.get("/T") == field:
                    writer_annot.update(
                        {NameObject("/V"): TextStringObject(fields[field])}
                    )
                    if flags:
                        writer_annot.update({NameObject("/Ff"): NumberObject(flags)})
                elif writer_parent_annot.get("/T") == field:
                    writer_parent_annot.update(
                        {NameObject("/V"): TextStringObject(fields[field])}
                    )

    def updatePageFormFieldValues(self, page, fields, flags=0):
        """
        .. deprecated:: 1.28.0

            Use :meth:`update_page_form_field_values` instead.
        """
        warnings.warn(
            DEPR_MSG.format(
                "updatePageFormFieldValues", "update_page_form_field_values"
            ),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.update_page_form_field_values(page, fields, flags)

    def clone_reader_document_root(self, reader):
        """
        Copy the reader document root to the writer.

        :param reader:  PdfReader from the document root should be copied.
        :callback after_page_append:
        """
        self._root_object = reader.trailer[TK.ROOT]

    def cloneReaderDocumentRoot(self, reader):
        """
        .. deprecated:: 1.28.0

            Use :meth:`clone_reader_document_root` instead.
        """
        warnings.warn(
            DEPR_MSG.format("cloneReaderDocumentRoot", "clone_reader_document_root"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.clone_reader_document_root(reader)

    def clone_document_from_reader(self, reader, after_page_append=None):
        """
        Create a copy (clone) of a document from a PDF file reader

        :param reader: PDF file reader instance from which the clone
            should be created.
        :callback after_page_append (function): Callback function that is invoked after
            each page is appended to the writer. Signature includes a reference to the
            appended page (delegates to appendPagesFromReader). Callback signature:

            :param writer_pageref (PDF page reference): Reference to the page just
                appended to the document.
        """
        self.clone_reader_document_root(reader)
        self.append_pages_from_reader(reader, after_page_append)

    def cloneDocumentFromReader(self, reader, after_page_append=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`clone_document_from_reader` instead.
        """
        warnings.warn(
            DEPR_MSG.format("cloneDocumentFromReader", "clone_document_from_reader"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.clone_document_from_reader(reader, after_page_append)

    def encrypt(self, user_pwd, owner_pwd=None, use_128bit=True, permissions_flag=-1):
        """
        Encrypt this PDF file with the PDF Standard encryption handler.

        :param str user_pwd: The "user password", which allows for opening
            and reading the PDF file with the restrictions provided.
        :param str owner_pwd: The "owner password", which allows for
            opening the PDF files without any restrictions.  By default,
            the owner password is the same as the user password.
        :param bool use_128bit: flag as to whether to use 128bit
            encryption.  When false, 40bit encryption will be used.  By default,
            this flag is on.
        :param unsigned int permissions_flag: permissions as described in
            TABLE 3.20 of the PDF 1.7 specification. A bit value of 1 means the
            permission is grantend. Hence an integer value of -1 will set all
            flags.
            Bit position 3 is for printing, 4 is for modifying content, 5 and 6
            control annotations, 9 for form fields, 10 for extraction of
            text and graphics.
        """
        import random
        import time

        if owner_pwd is None:
            owner_pwd = user_pwd
        if use_128bit:
            V = 2
            rev = 3
            keylen = int(128 / 8)
        else:
            V = 1
            rev = 2
            keylen = int(40 / 8)
        P = permissions_flag
        O = ByteStringObject(_alg33(owner_pwd, user_pwd, rev, keylen))
        ID_1 = ByteStringObject(md5(b_(repr(time.time()))).digest())
        ID_2 = ByteStringObject(md5(b_(repr(random.random()))).digest())
        self._ID = ArrayObject((ID_1, ID_2))
        if rev == 2:
            U, key = _alg34(user_pwd, O, P, ID_1)
        else:
            assert rev == 3
            U, key = _alg35(user_pwd, rev, keylen, O, P, ID_1, False)
        encrypt = DictionaryObject()
        encrypt[NameObject(SA.FILTER)] = NameObject("/Standard")
        encrypt[NameObject("/V")] = NumberObject(V)
        if V == 2:
            encrypt[NameObject(SA.LENGTH)] = NumberObject(keylen * 8)
        encrypt[NameObject(ED.R)] = NumberObject(rev)
        encrypt[NameObject(ED.O)] = ByteStringObject(O)
        encrypt[NameObject(ED.U)] = ByteStringObject(U)
        encrypt[NameObject(ED.P)] = NumberObject(P)
        self._encrypt = self._add_object(encrypt)
        self._encrypt_key = key

    def write(self, stream):
        """
        Write the collection of pages added to this object out as a PDF file.

        :param stream: An object to write the file to.  The object must support
            the write method and the tell method, similar to a file object.
        """
        if hasattr(stream, "mode") and "b" not in stream.mode:
            warnings.warn(
                "File <%s> to write to is not in binary mode. It may not be written to correctly."
                % stream.name
            )

        if not self._root:
            self._root = self._add_object(self._root_object)

        external_reference_map = {}

        # PDF objects sometimes have circular references to their /Page objects
        # inside their object tree (for example, annotations).  Those will be
        # indirect references to objects that we've recreated in this PDF.  To
        # address this problem, PageObject's store their original object
        # reference number, and we add it to the external reference map before
        # we sweep for indirect references.  This forces self-page-referencing
        # trees to reference the correct new object location, rather than
        # copying in a new copy of the page object.
        for obj_index in range(len(self._objects)):
            obj = self._objects[obj_index]
            if isinstance(obj, PageObject) and obj.indirectRef is not None:
                data = obj.indirectRef
                if data.pdf not in external_reference_map:
                    external_reference_map[data.pdf] = {}
                if data.generation not in external_reference_map[data.pdf]:
                    external_reference_map[data.pdf][data.generation] = {}
                external_reference_map[data.pdf][data.generation][
                    data.idnum
                ] = IndirectObject(obj_index + 1, 0, self)

        self.stack = []
        self._sweep_indirect_references(external_reference_map, self._root)
        del self.stack

        object_positions = self._write_header(stream)
        xref_location = self._write_xref_table(stream, object_positions)
        self._write_trailer(stream)
        stream.write(b_("\nstartxref\n%s\n%%%%EOF\n" % (xref_location)))  # eof

    def _write_header(self, stream):
        object_positions = []
        stream.write(self._header + b_("\n"))
        stream.write(b_("%\xE2\xE3\xCF\xD3\n"))
        for i in range(len(self._objects)):
            obj = self._objects[i]
            # If the obj is None we can't write anything
            if obj is not None:
                idnum = i + 1
                object_positions.append(stream.tell())
                stream.write(b_(str(idnum) + " 0 obj\n"))
                key = None
                if hasattr(self, "_encrypt") and idnum != self._encrypt.idnum:
                    pack1 = struct.pack("<i", i + 1)[:3]
                    pack2 = struct.pack("<i", 0)[:2]
                    key = self._encrypt_key + pack1 + pack2
                    assert len(key) == (len(self._encrypt_key) + 5)
                    md5_hash = md5(key).digest()
                    key = md5_hash[: min(16, len(self._encrypt_key) + 5)]
                obj.write_to_stream(stream, key)
                stream.write(b_("\nendobj\n"))
        return object_positions

    def _write_xref_table(self, stream, object_positions):
        xref_location = stream.tell()
        stream.write(b_("xref\n"))
        stream.write(b_("0 %s\n" % (len(self._objects) + 1)))
        stream.write(b_("%010d %05d f \n" % (0, 65535)))
        for offset in object_positions:
            stream.write(b_("%010d %05d n \n" % (offset, 0)))
        return xref_location

    def _write_trailer(self, stream):
        stream.write(b_("trailer\n"))
        trailer = DictionaryObject()
        trailer.update(
            {
                NameObject(TK.SIZE): NumberObject(len(self._objects) + 1),
                NameObject(TK.ROOT): self._root,
                NameObject(TK.INFO): self._info,
            }
        )
        if hasattr(self, "_ID"):
            trailer[NameObject(TK.ID)] = self._ID
        if hasattr(self, "_encrypt"):
            trailer[NameObject(TK.ENCRYPT)] = self._encrypt
        trailer.write_to_stream(stream, None)

    def add_metadata(self, infos):
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
        """
        args = {}
        for key, value in list(infos.items()):
            args[NameObject(key)] = createStringObject(value)
        self.get_object(self._info).update(args)

    def addMetadata(self, infos):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_metadata` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addMetadata", "add_metadata"),
        )
        self.add_metadata(infos)

    def _sweep_indirect_references(self, extern_map, data):
        if isinstance(data, DictionaryObject):
            for key, value in list(data.items()):
                value = self._sweep_indirect_references(extern_map, value)
                if isinstance(value, StreamObject):
                    # a dictionary value is a stream.  streams must be indirect
                    # objects, so we need to change this value.
                    value = self._add_object(value)
                data[key] = value
            return data
        elif isinstance(data, ArrayObject):
            for i in range(len(data)):
                value = self._sweep_indirect_references(extern_map, data[i])
                if isinstance(value, StreamObject):
                    # an array value is a stream.  streams must be indirect
                    # objects, so we need to change this value
                    value = self._add_object(value)
                data[i] = value
            return data
        elif isinstance(data, IndirectObject):
            # internal indirect references are fine
            if data.pdf == self:
                if data.idnum in self.stack:
                    return data
                else:
                    self.stack.append(data.idnum)
                    realdata = self.get_object(data)
                    self._sweep_indirect_references(extern_map, realdata)
                    return data
            else:
                if hasattr(data.pdf, "stream") and data.pdf.stream.closed:
                    raise ValueError(
                        "I/O operation on closed file: {}".format(data.pdf.stream.name)
                    )
                newobj = (
                    extern_map.get(data.pdf, {})
                    .get(data.generation, {})
                    .get(data.idnum, None)
                )
                if newobj is None:
                    try:
                        newobj = data.pdf.get_object(data)
                        self._objects.append(None)  # placeholder
                        idnum = len(self._objects)
                        newobj_ido = IndirectObject(idnum, 0, self)
                        if data.pdf not in extern_map:
                            extern_map[data.pdf] = {}
                        if data.generation not in extern_map[data.pdf]:
                            extern_map[data.pdf][data.generation] = {}
                        extern_map[data.pdf][data.generation][data.idnum] = newobj_ido
                        newobj = self._sweep_indirect_references(extern_map, newobj)
                        self._objects[idnum - 1] = newobj
                        return newobj_ido
                    except (ValueError, RecursionError):
                        # Unable to resolve the Object, returning NullObject instead.
                        warnings.warn(
                            "Unable to resolve [{}: {}], returning NullObject instead".format(
                                data.__class__.__name__, data
                            )
                        )
                        return NullObject()
                return newobj
        else:
            return data

    def get_reference(self, obj):
        idnum = self._objects.index(obj) + 1
        ref = IndirectObject(idnum, 0, self)
        assert ref.get_object() == obj
        return ref

    def getReference(self, obj):
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_reference` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getReference", "get_reference"), PendingDeprecationWarning
        )
        return self.get_reference(obj)

    def get_outline_root(self):
        if CO.OUTLINES in self._root_object:
            # TABLE 3.25 Entries in the catalog dictionary
            outline = self._root_object[CO.OUTLINES]
            idnum = self._objects.index(outline) + 1
            outline_ref = IndirectObject(idnum, 0, self)
            assert outline_ref.get_object() == outline
        else:
            outline = TreeObject()
            outline.update({})
            outline_ref = self._add_object(outline)
            self._root_object[NameObject(CO.OUTLINES)] = outline_ref

        return outline

    def getOutlineRoot(self):
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_outline_root` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getOutlineRoot", "get_outline_root"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_outline_root()

    def get_named_dest_root(self):
        if CA.NAMES in self._root_object and isinstance(
            self._root_object[CA.NAMES], DictionaryObject
        ):
            names = self._root_object[CA.NAMES]
            idnum = self._objects.index(names) + 1
            names_ref = IndirectObject(idnum, 0, self)
            assert names_ref.get_object() == names
            if CA.DESTS in names and isinstance(names[CA.DESTS], DictionaryObject):
                # 3.6.3 Name Dictionary (PDF spec 1.7)
                dests = names[CA.DESTS]
                idnum = self._objects.index(dests) + 1
                dests_ref = IndirectObject(idnum, 0, self)
                assert dests_ref.get_object() == dests
                if CA.NAMES in dests:
                    # TABLE 3.33 Entries in a name tree node dictionary
                    nd = dests[CA.NAMES]
                else:
                    nd = ArrayObject()
                    dests[NameObject(CA.NAMES)] = nd
            else:
                dests = DictionaryObject()
                dests_ref = self._add_object(dests)
                names[NameObject(CA.DESTS)] = dests_ref
                nd = ArrayObject()
                dests[NameObject(CA.NAMES)] = nd

        else:
            names = DictionaryObject()
            names_ref = self._add_object(names)
            self._root_object[NameObject(CA.NAMES)] = names_ref
            dests = DictionaryObject()
            dests_ref = self._add_object(dests)
            names[NameObject(CA.DESTS)] = dests_ref
            nd = ArrayObject()
            dests[NameObject(CA.NAMES)] = nd

        return nd

    def getNamedDestRoot(self):
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_named_dest_root` instead.
        """
        warnings.warn(
            DEPR_MSG.format("getNamedDestRoot", "get_named_dest_root"),
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.get_named_dest_root()

    def add_bookmark_destination(self, dest, parent=None):
        dest_ref = self._add_object(dest)

        outline_ref = self.get_outline_root()

        if parent is None:
            parent = outline_ref

        parent = parent.get_object()
        parent.add_child(dest_ref, self)

        return dest_ref

    def addBookmarkDestination(self, dest, parent=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_bookmark_destination` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addBookmarkDestination", "add_bookmark_destination"),
        )
        return self.add_bookmark_destination(dest, parent)

    def add_bookmark_dict(self, bookmark, parent=None):
        bookmark_obj = TreeObject()
        for k, v in list(bookmark.items()):
            bookmark_obj[NameObject(str(k))] = v
        bookmark_obj.update(bookmark)

        if "/A" in bookmark:
            action = DictionaryObject()
            for k, v in list(bookmark["/A"].items()):
                action[NameObject(str(k))] = v
            action_ref = self._add_object(action)
            bookmark_obj[NameObject("/A")] = action_ref

        bookmark_ref = self._add_object(bookmark_obj)

        outline_ref = self.get_outline_root()

        if parent is None:
            parent = outline_ref

        parent = parent.get_object()
        parent.add_child(bookmark_ref, self)

        return bookmark_ref

    def addBookmarkDict(self, bookmark, parent=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_bookmark_dict` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addBookmarkDict", "add_bookmark_dict"),
        )
        return self.add_bookmark_dict(bookmark, parent)

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
            :meth:`addLink()<addLink>` for details.
        """
        page_ref = self.get_object(self._pages)[PA.KIDS][pagenum]
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
        action_ref = self._add_object(action)

        outline_ref = self.get_outline_root()

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

        bookmark_ref = self._add_object(bookmark)

        parent = parent.get_object()
        parent.add_child(bookmark_ref, self)

        return bookmark_ref

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
            DEPR_MSG.format("addBookmark", "add_bookmark"), PendingDeprecationWarning
        )
        return self.add_bookmark(
            title, pagenum, parent, color, bold, italic, fit, *args
        )

    def add_named_destination_object(self, dest):
        dest_ref = self._add_object(dest)

        nd = self.get_named_dest_root()
        nd.extend([dest["/Title"], dest_ref])
        return dest_ref

    def addNamedDestinationObject(self, dest):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_named_destination_object` instead.
        """
        warnings.warn(
            DEPR_MSG.format(
                "addNamedDestinationObject", "add_named_destination_object"
            ),
        )
        return self.add_named_destination_object(dest)

    def add_named_destination(self, title, pagenum):
        page_ref = self.get_object(self._pages)[PA.KIDS][pagenum]
        dest = DictionaryObject()
        dest.update(
            {
                NameObject("/D"): ArrayObject(
                    [page_ref, NameObject("/FitH"), NumberObject(826)]
                ),
                NameObject("/S"): NameObject("/GoTo"),
            }
        )

        dest_ref = self._add_object(dest)
        nd = self.get_named_dest_root()
        nd.extend([title, dest_ref])
        return dest_ref

    def addNamedDestination(self, title, pagenum):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_named_destination` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addNamedDestination", "add_named_destination"),
        )
        return self.add_named_destination(title, pagenum)

    def remove_links(self):
        """Remove links and annotations from this output."""
        pages = self.get_object(self._pages)[PA.KIDS]
        for page in pages:
            page_ref = self.get_object(page)
            if PG.ANNOTS in page_ref:
                del page_ref[PG.ANNOTS]

    def removeLinks(self):
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_links` instead.
        """
        warnings.warn(
            DEPR_MSG.format("removeLinks", "remove_links"),
        )
        return self.remove_links()

    def remove_images(self, ignore_byte_string_object=False):
        """
        Remove images from this output.

        :param bool ignoreByteStringObject: optional parameter
            to ignore ByteString Objects.
        """
        pages = self.get_object(self._pages)[PA.KIDS]
        jump_operators = [
            b_("cm"),
            b_("w"),
            b_("J"),
            b_("j"),
            b_("M"),
            b_("d"),
            b_("ri"),
            b_("i"),
            b_("gs"),
            b_("W"),
            b_("b"),
            b_("s"),
            b_("S"),
            b_("f"),
            b_("F"),
            b_("n"),
            b_("m"),
            b_("l"),
            b_("c"),
            b_("v"),
            b_("y"),
            b_("h"),
            b_("B"),
            b_("Do"),
            b_("sh"),
        ]
        for j in range(len(pages)):
            page = pages[j]
            page_ref = self.get_object(page)
            content = page_ref["/Contents"].get_object()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, page_ref)

            _operations = []
            seq_graphics = False
            for operands, operator in content.operations:
                if operator in [b_("Tj"), b_("'")]:
                    text = operands[0]
                    if ignore_byte_string_object:
                        if not isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if ignore_byte_string_object and not isinstance(
                        text, TextStringObject
                    ):
                        operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if ignore_byte_string_object and not isinstance(
                            operands[0][i], TextStringObject
                        ):
                            operands[0][i] = TextStringObject()

                if operator == b_("q"):
                    seq_graphics = True
                if operator == b_("Q"):
                    seq_graphics = False
                if seq_graphics and operator in jump_operators:
                    continue
                if operator == b_("re"):
                    continue
                _operations.append((operands, operator))

            content.operations = _operations
            page_ref.__setitem__(NameObject("/Contents"), content)

    def removeImages(self, ignoreByteStringObject=False):
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_images` instead.
        """
        warnings.warn(
            DEPR_MSG.format(
                "removeImages(ignoreByteStringObject=False)",
                "remove_images(ignore_byte_string_object=False)",
            ),
        )
        return self.remove_images(ignoreByteStringObject)

    def remove_text(self, ignore_byte_string_object=False):
        """
        Remove text from this output.

        :param bool ignoreByteStringObject: optional parameter
            to ignore ByteString Objects.
        """
        pages = self.get_object(self._pages)[PA.KIDS]
        for j in range(len(pages)):
            page = pages[j]
            page_ref = self.get_object(page)
            content = page_ref["/Contents"].get_object()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, page_ref)
            for operands, operator in content.operations:
                if operator in [b_("Tj"), b_("'")]:
                    text = operands[0]
                    if not ignore_byte_string_object:
                        if isinstance(text, TextStringObject):
                            operands[0] = TextStringObject()
                    else:
                        if isinstance(text, (TextStringObject, ByteStringObject)):
                            operands[0] = TextStringObject()
                elif operator == b_('"'):
                    text = operands[2]
                    if not ignore_byte_string_object:
                        if isinstance(text, TextStringObject):
                            operands[2] = TextStringObject()
                    else:
                        if isinstance(text, (TextStringObject, ByteStringObject)):
                            operands[2] = TextStringObject()
                elif operator == b_("TJ"):
                    for i in range(len(operands[0])):
                        if not ignore_byte_string_object:
                            if isinstance(operands[0][i], TextStringObject):
                                operands[0][i] = TextStringObject()
                        else:
                            if isinstance(
                                operands[0][i], (TextStringObject, ByteStringObject)
                            ):
                                operands[0][i] = TextStringObject()

            page_ref.__setitem__(NameObject("/Contents"), content)

    def removeText(self, ignoreByteStringObject=False):
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_text` instead.
        """
        warnings.warn(
            DEPR_MSG.format(
                "removeText(ignoreByteStringObject=False)",
                "remove_text(ignore_byte_string_object=False)",
            ),
        )
        return self.remove_text(ignoreByteStringObject)

    def add_uri(self, pagenum, uri, rect, border=None):
        """
        Add an URI from a rectangular area to the specified page.
        This uses the basic structure of AddLink

        :param int pagenum: index of the page on which to place the URI action.
        :param int uri: string -- uri of resource to link to.
        :param rect: :class:`RectangleObject<PyPDF2.generic.RectangleObject>` or array of four
            integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be
            drawn if this argument is omitted.

        REMOVED FIT/ZOOM ARG
        -John Mulligan
        """

        page_link = self.get_object(self._pages)[PA.KIDS][pagenum]
        page_ref = self.get_object(page_link)

        if border is not None:
            border_arr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dash_pattern = ArrayObject([NameObject(n) for n in border[3]])
                border_arr.append(dash_pattern)
        else:
            border_arr = [NumberObject(2)] * 3

        if _isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        lnk2 = DictionaryObject()
        lnk2.update(
            {
                NameObject("/S"): NameObject("/URI"),
                NameObject("/URI"): TextStringObject(uri),
            }
        )
        lnk = DictionaryObject()
        lnk.update(
            {
                NameObject("/Type"): NameObject(PG.ANNOTS),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/P"): page_link,
                NameObject("/Rect"): rect,
                NameObject("/H"): NameObject("/I"),
                NameObject("/Border"): ArrayObject(border_arr),
                NameObject("/A"): lnk2,
            }
        )
        lnk_ref = self._add_object(lnk)

        if PG.ANNOTS in page_ref:
            page_ref[PG.ANNOTS].append(lnk_ref)
        else:
            page_ref[NameObject(PG.ANNOTS)] = ArrayObject([lnk_ref])

    def addURI(self, pagenum, uri, rect, border=None):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_uri` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addURI", "add_uri"),
        )
        return self.add_uri(pagenum, uri, rect, border)

    def add_link(self, pagenum, pagedest, rect, border=None, fit="/Fit", *args):
        """
        Add an internal link from a rectangular area to the specified page.

        :param int pagenum: index of the page on which to place the link.
        :param int pagedest: index of the page to which the link should go.
        :param rect: :class:`RectangleObject<PyPDF2.generic.RectangleObject>` or array of four
            integers specifying the clickable rectangular area
            ``[xLL, yLL, xUR, yUR]``, or string in the form ``"[ xLL yLL xUR yUR ]"``.
        :param border: if provided, an array describing border-drawing
            properties. See the PDF spec for details. No border will be
            drawn if this argument is omitted.
        :param str fit: Page fit or 'zoom' option (see below). Additional arguments may need
            to be supplied. Passing ``None`` will be read as a null value for that coordinate.

        .. list-table:: Valid ``zoom`` arguments (see Table 8.2 of the PDF 1.7 reference for details)
           :widths: 50 200

           * - /Fit
             - No additional arguments
           * - /XYZ
             - [left] [top] [zoomFactor]
           * - /FitH
             - [top]
           * - /FitV
             - [left]
           * - /FitR
             - [left] [bottom] [right] [top]
           * - /FitB
             - No additional arguments
           * - /FitBH
             - [top]
           * - /FitBV
             - [left]
        """

        page_link = self.get_object(self._pages)[PA.KIDS][pagenum]
        page_dest = self.get_object(self._pages)[PA.KIDS][
            pagedest
        ]  # TODO: switch for external link
        page_ref = self.get_object(page_link)

        if border is not None:
            border_arr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dash_pattern = ArrayObject([NameObject(n) for n in border[3]])
                border_arr.append(dash_pattern)
        else:
            border_arr = [NumberObject(0)] * 3

        if _isString(rect):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        zoom_args = []
        for a in args:
            if a is not None:
                zoom_args.append(NumberObject(a))
            else:
                zoom_args.append(NullObject())
        dest = Destination(
            NameObject("/LinkName"), page_dest, NameObject(fit), *zoom_args
        )  # TODO: create a better name for the link
        dest_array = dest.dest_array

        lnk = DictionaryObject()
        lnk.update(
            {
                NameObject("/Type"): NameObject(PG.ANNOTS),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/P"): page_link,
                NameObject("/Rect"): rect,
                NameObject("/Border"): ArrayObject(border_arr),
                NameObject("/Dest"): dest_array,
            }
        )
        lnk_ref = self._add_object(lnk)

        if PG.ANNOTS in page_ref:
            page_ref[PG.ANNOTS].append(lnk_ref)
        else:
            page_ref[NameObject(PG.ANNOTS)] = ArrayObject([lnk_ref])

    def addLink(self, pagenum, pagedest, rect, border=None, fit="/Fit", *args):
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_link` instead.
        """
        warnings.warn(
            DEPR_MSG.format("addLink", "add_link"),
        )
        return self.add_link(pagenum, pagedest, rect, border, fit, *args)

    _valid_layouts = [
        "/NoLayout",
        "/SinglePage",
        "/OneColumn",
        "/TwoColumnLeft",
        "/TwoColumnRight",
        "/TwoPageLeft",
        "/TwoPageRight",
    ]

    def _get_page_layout(self):
        """
        Get the page layout.

        See :meth:`setPageLayout()<PdfWriter.setPageLayout>` for a description of valid layouts.

        :return: Page layout currently being used.
        :rtype: str, None if not specified
        """
        try:
            return self._root_object["/PageLayout"]
        except KeyError:
            return None

    def getPageLayout(self):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        warnings.warn(
            "getPageLayout() will be removed in PyPDF2 2.0.0. "
            "Use the page_layout attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._get_page_layout()

    def _set_page_layout(self, layout):
        """
        Set the page layout.

        :param str layout: The page layout to be used.

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
        if not isinstance(layout, NameObject):
            if layout not in self._valid_layouts:
                warnings.warn(
                    "Layout should be one of: {}".format(", ".join(self._valid_layouts))
                )
            layout = NameObject(layout)
        self._root_object.update({NameObject("/PageLayout"): layout})

    def setPageLayout(self, layout):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        warnings.warn(
            "setPageLayout() will be removed in PyPDF2 2.0.0. "
            "Use the page_layout attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._set_page_layout(layout)

    @property
    def page_layout(self):
        """
        Page layout property.

        .. list-table:: Valid ``layout`` values
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
        return self._get_page_layout()

    @page_layout.setter
    def page_layout(self, layout):
        self._set_page_layout(layout)

    @property
    def pageLayout(self):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        warnings.warn(
            "pageLayout will be removed in PyPDF2 2.0.0. "
            "Use the page_layout attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.page_layout

    @pageLayout.setter
    def pageLayout(self, layout):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        warnings.warn(
            "pageLayout will be removed in PyPDF2 2.0.0. "
            "Use the page_layout attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.page_layout = layout

    _valid_modes = [
        "/UseNone",
        "/UseOutlines",
        "/UseThumbs",
        "/FullScreen",
        "/UseOC",
        "/UseAttachments",
    ]

    def _get_page_mode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfWriter.setPageMode>` for a description
        of valid modes.

        :return: Page mode currently being used.
        :rtype: str, None if not specified.
        """
        try:
            return self._root_object["/PageMode"]
        except KeyError:
            return None

    def getPageMode(self):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        warnings.warn(
            "getPageMode() will be removed in PyPDF2 2.0.0. "
            "Use the page_mode attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self._get_page_mode()

    def set_page_mode(self, mode):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        if not isinstance(mode, NameObject):
            if mode not in self._valid_modes:
                warnings.warn(
                    "Mode should be one of: {}".format(", ".join(self._valid_modes))
                )
            mode = NameObject(mode)
        self._root_object.update({NameObject("/PageMode"): mode})

    def setPageMode(self, mode):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        warnings.warn(
            "setPageMode() will be removed in PyPDF2 2.0.0. "
            "Use the page_mode attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.set_page_mode(mode)

    @property
    def page_mode(self):
        """
        Page mode property.

        .. list-table:: Valid ``mode`` values
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
        return self._get_page_mode()

    @page_mode.setter
    def page_mode(self, mode):
        self.set_page_mode(mode)

    @property
    def pageMode(self):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        warnings.warn(
            "pageMode will be removed in PyPDF2 2.0.0. "
            "Use the page_mode attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self.page_mode

    @pageMode.setter
    def pageMode(self, mode):
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        warnings.warn(
            "pageMode will be removed in PyPDF2 2.0.0. "
            "Use the page_mode attribute instead.",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        self.page_mode = mode


class PdfFileWriter(PdfWriter):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "PdfFileWriter was renamed to PdfWriter. PdfFileWriter will be removed",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        super(PdfFileWriter, self).__init__(*args, **kwargs)
