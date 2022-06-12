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
import decimal
import logging
import random
import struct
import time
import uuid
import warnings
from hashlib import md5
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, cast

from ._page import PageObject, _VirtualList
from ._reader import PdfReader
from ._security import _alg33, _alg34, _alg35
from ._utils import StreamType, b_, deprecate_with_replacement
from .constants import CatalogAttributes as CA
from .constants import Core as CO
from .constants import EncryptionDictAttributes as ED
from .constants import PageAttributes as PG
from .constants import PagesAttributes as PA
from .constants import StreamAttributes as SA
from .constants import TrailerKeys as TK
from .generic import (
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
    PdfObject,
    RectangleObject,
    StreamObject,
    TextStringObject,
    TreeObject,
    createStringObject,
)
from .types import (
    BookmarkTypes,
    BorderArrayType,
    FitType,
    LayoutType,
    PagemodeType,
    ZoomArgsType,
    ZoomArgType,
)

logger = logging.getLogger(__name__)


class PdfWriter:
    """
    This class supports writing PDF files out, given pages produced by another
    class (typically :class:`PdfReader<PyPDF2.PdfReader>`).
    """

    def __init__(self) -> None:
        self._header = b_("%PDF-1.3")
        self._objects: List[Optional[PdfObject]] = []  # array of indirect objects

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
                    codecs.BOM_UTF16_BE + "PyPDF2".encode("utf-16be")
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
        self._root: Optional[IndirectObject] = None
        self._root_object = root

    def _add_object(self, obj: Optional[PdfObject]) -> IndirectObject:
        self._objects.append(obj)
        return IndirectObject(len(self._objects), 0, self)

    def get_object(self, ido: IndirectObject) -> PdfObject:
        if ido.pdf != self:
            raise ValueError("pdf must be self")
        return self._objects[ido.idnum - 1]  # type: ignore

    def getObject(self, ido: IndirectObject) -> PdfObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_object` instead.
        """
        deprecate_with_replacement("getObject", "get_object")
        return self.get_object(ido)

    def _add_page(
        self, page: PageObject, action: Callable[[Any, IndirectObject], None]
    ) -> None:
        assert page[PA.TYPE] == CO.PAGE
        page[NameObject(PA.PARENT)] = self._pages
        page_ind = self._add_object(page)
        pages = cast(DictionaryObject, self.get_object(self._pages))
        action(pages[PA.KIDS], page_ind)
        page_count = cast(int, pages[PA.COUNT])
        pages[NameObject(PA.COUNT)] = NumberObject(page_count + 1)

    def set_need_appearances_writer(self) -> None:
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

    def add_page(self, page: PageObject) -> None:
        """
        Add a page to this PDF file.  The page is usually acquired from a
        :class:`PdfReader<PyPDF2.PdfReader>` instance.

        :param PageObject page: The page to add to the document. Should be
            an instance of :class:`PageObject<PyPDF2._page.PageObject>`
        """
        self._add_page(page, list.append)

    def addPage(self, page: PageObject) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_page` instead.
        """
        deprecate_with_replacement("addPage", "add_page")
        self.add_page(page)

    def insert_page(self, page: PageObject, index: int = 0) -> None:
        """
        Insert a page in this PDF file. The page is usually acquired from a
        :class:`PdfReader<PyPDF2.PdfReader>` instance.

        :param PageObject page: The page to add to the document.  This
            argument should be an instance of :class:`PageObject<PyPDF2._page.PageObject>`.
        :param int index: Position at which the page will be inserted.
        """
        self._add_page(page, lambda l, p: l.insert(index, p))

    def insertPage(self, page: PageObject, index: int = 0) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`insert_page` instead.
        """
        deprecate_with_replacement("insertPage", "insert_page")
        self.insert_page(page, index)

    def get_page(self, pageNumber: int) -> PageObject:  # TODO: PEP8
        """
        Retrieve a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: the page at the index given by *pageNumber*
        :rtype: :class:`PageObject<PyPDF2._page.PageObject>`
        """
        pages = cast(Dict[str, Any], self.get_object(self._pages))
        # XXX: crude hack
        return pages[PA.KIDS][pageNumber].get_object()

    def getPage(self, pageNumber: int) -> PageObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :code:`writer.pages[page_number]` instead.
        """
        deprecate_with_replacement("getPage", "writer.pages[page_number]")
        return self.get_page(pageNumber)

    def _get_num_pages(self) -> int:
        """
        :return: the number of pages.
        :rtype: int
        """
        pages = cast(Dict[str, Any], self.get_object(self._pages))
        return int(pages[NameObject("/Count")])

    def getNumPages(self) -> int:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :code:`len(writer.pages)` instead.
        """
        deprecate_with_replacement("getNumPages", "len(writer.pages)")
        return self._get_num_pages()

    @property
    def pages(self) -> List[PageObject]:
        """
        Property that emulates a list of :class:`PageObject<PyPDF2._page.PageObject>`
        """
        return _VirtualList(self._get_num_pages, self.get_page)  # type: ignore

    def add_blank_page(
        self, width: Optional[float] = None, height: Optional[float] = None
    ) -> PageObject:
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

    def addBlankPage(
        self, width: Optional[float] = None, height: Optional[float] = None
    ) -> PageObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_blank_page` instead.
        """
        deprecate_with_replacement("addBlankPage", "add_blank_page")
        return self.add_blank_page(width, height)

    def insert_blank_page(
        self,
        width: Optional[decimal.Decimal] = None,
        height: Optional[decimal.Decimal] = None,
        index: int = 0,
    ) -> PageObject:
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
            oldpage = self.pages[index]
            width = oldpage.mediabox.width
            height = oldpage.mediabox.height
        page = PageObject.create_blank_page(self, width, height)
        self.insert_page(page, index)
        return page

    def insertBlankPage(
        self,
        width: Optional[decimal.Decimal] = None,
        height: Optional[decimal.Decimal] = None,
        index: int = 0,
    ) -> PageObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`insertBlankPage` instead.
        """
        deprecate_with_replacement("insertBlankPage", "insert_blank_page")
        return self.insert_blank_page(width, height, index)

    def add_js(self, javascript: str) -> None:
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

    def addJS(self, javascript: str) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_js` instead.
        """
        deprecate_with_replacement("addJS", "add_js")
        return self.add_js(javascript)

    def add_attachment(self, filename: str, data: Union[str, bytes]) -> None:
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
        file_entry.set_data(data)
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
        embedded_files_names_dictionary = DictionaryObject()
        embedded_files_names_dictionary.update(
            {
                NameObject(CA.NAMES): ArrayObject(
                    [createStringObject(filename), filespec]
                )
            }
        )

        embedded_files_dictionary = DictionaryObject()
        embedded_files_dictionary.update(
            {NameObject("/EmbeddedFiles"): embedded_files_names_dictionary}
        )
        # Update the root
        self._root_object.update({NameObject(CA.NAMES): embedded_files_dictionary})

    def addAttachment(
        self, fname: str, fdata: Union[str, bytes]
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_attachment` instead.
        """
        deprecate_with_replacement("addAttachment", "add_attachment")
        return self.add_attachment(fname, fdata)

    def append_pages_from_reader(
        self,
        reader: PdfReader,
        after_page_append: Optional[Callable[[PageObject], None]] = None,
    ) -> None:
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
        for rpagenum in range(reader_num_pages):
            reader_page = reader.pages[rpagenum]
            self.add_page(reader_page)
            writer_page = self.pages[writer_num_pages + rpagenum]
            # Trigger callback, pass writer page as parameter
            if callable(after_page_append):
                after_page_append(writer_page)

    def appendPagesFromReader(
        self,
        reader: PdfReader,
        after_page_append: Optional[Callable[[PageObject], None]] = None,
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`append_pages_from_reader` instead.
        """
        deprecate_with_replacement("appendPagesFromReader", "append_pages_from_reader")
        self.append_pages_from_reader(reader, after_page_append)

    def update_page_form_field_values(
        self, page: PageObject, fields: Dict[str, Any], flags: int = 0
    ) -> None:
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
        self.set_need_appearances_writer()
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

    def updatePageFormFieldValues(
        self, page: PageObject, fields: Dict[str, Any], flags: int = 0
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`update_page_form_field_values` instead.
        """
        deprecate_with_replacement(
            "updatePageFormFieldValues", "update_page_form_field_values"
        )
        return self.update_page_form_field_values(page, fields, flags)

    def clone_reader_document_root(self, reader: PdfReader) -> None:
        """
        Copy the reader document root to the writer.

        :param reader:  PdfReader from the document root should be copied.
        :callback after_page_append:
        """
        self._root_object = cast(DictionaryObject, reader.trailer[TK.ROOT])

    def cloneReaderDocumentRoot(self, reader: PdfReader) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`clone_reader_document_root` instead.
        """
        deprecate_with_replacement(
            "cloneReaderDocumentRoot", "clone_reader_document_root"
        )
        self.clone_reader_document_root(reader)

    def clone_document_from_reader(
        self,
        reader: PdfReader,
        after_page_append: Optional[Callable[[PageObject], None]] = None,
    ) -> None:
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

    def cloneDocumentFromReader(
        self,
        reader: PdfReader,
        after_page_append: Optional[Callable[[PageObject], None]] = None,
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`clone_document_from_reader` instead.
        """
        deprecate_with_replacement(
            "cloneDocumentFromReader", "clone_document_from_reader"
        )
        self.clone_document_from_reader(reader, after_page_append)

    def encrypt(
        self,
        user_pwd: str,
        owner_pwd: Optional[str] = None,
        use_128bit: bool = True,
        permissions_flag: int = -1,
    ) -> None:
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

    def write(self, stream: StreamType) -> None:
        """
        Write the collection of pages added to this object out as a PDF file.

        :param stream: An object to write the file to.  The object must support
            the write method and the tell method, similar to a file object.
        """
        if hasattr(stream, "mode") and "b" not in stream.mode:
            warnings.warn(
                (
                    "File <{}> to write to is not in binary mode. "  # type: ignore
                    "It may not be written to correctly."
                ).format(stream.name)
            )

        if not self._root:
            self._root = self._add_object(self._root_object)

        external_reference_map: Dict[Any, Any] = {}

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
            if isinstance(obj, PageObject) and obj.indirect_ref is not None:
                data = obj.indirect_ref
                if data.pdf not in external_reference_map:
                    external_reference_map[data.pdf] = {}
                if data.generation not in external_reference_map[data.pdf]:
                    external_reference_map[data.pdf][data.generation] = {}
                external_reference_map[data.pdf][data.generation][
                    data.idnum
                ] = IndirectObject(obj_index + 1, 0, self)

        self.stack: List[int] = []
        self._sweep_indirect_references(external_reference_map, self._root)
        del self.stack

        object_positions = self._write_header(stream)
        xref_location = self._write_xref_table(stream, object_positions)
        self._write_trailer(stream)
        stream.write(b_("\nstartxref\n%s\n%%%%EOF\n" % (xref_location)))  # eof

    def _write_header(self, stream: StreamType) -> List[int]:
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

    def _write_xref_table(self, stream: StreamType, object_positions: List[int]) -> int:
        xref_location = stream.tell()
        stream.write(b_("xref\n"))
        stream.write(b_("0 %s\n" % (len(self._objects) + 1)))
        stream.write(b_("%010d %05d f \n" % (0, 65535)))
        for offset in object_positions:
            stream.write(b_("%010d %05d n \n" % (offset, 0)))
        return xref_location

    def _write_trailer(self, stream: StreamType) -> None:
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

    def add_metadata(self, infos: Dict[str, Any]) -> None:
        """
        Add custom metadata to the output.

        :param dict infos: a Python dictionary where each key is a field
            and each value is your new metadata.
        """
        args = {}
        for key, value in list(infos.items()):
            args[NameObject(key)] = createStringObject(value)
        self.get_object(self._info).update(args)  # type: ignore

    def addMetadata(self, infos: Dict[str, Any]) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_metadata` instead.
        """
        deprecate_with_replacement("addMetadata", "add_metadata")
        self.add_metadata(infos)

    def _sweep_indirect_references(
        self,
        extern_map: Dict[Any, Any],
        data: Union[
            ArrayObject,
            BooleanObject,
            DictionaryObject,
            FloatObject,
            IndirectObject,
            NameObject,
            PdfObject,
            NumberObject,
            TextStringObject,
            NullObject,
        ],
    ) -> Union[Any, StreamObject]:
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
                        f"I/O operation on closed file: {data.pdf.stream.name}"
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

    def get_reference(self, obj: PdfObject) -> IndirectObject:
        idnum = self._objects.index(obj) + 1
        ref = IndirectObject(idnum, 0, self)
        assert ref.get_object() == obj
        return ref

    def getReference(self, obj: PdfObject) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_reference` instead.
        """
        deprecate_with_replacement("getReference", "get_reference")
        return self.get_reference(obj)

    def get_outline_root(self) -> TreeObject:
        if CO.OUTLINES in self._root_object:
            # TABLE 3.25 Entries in the catalog dictionary
            outline = cast(TreeObject, self._root_object[CO.OUTLINES])
            idnum = self._objects.index(outline) + 1
            outline_ref = IndirectObject(idnum, 0, self)
            assert outline_ref.get_object() == outline
        else:
            outline = TreeObject()
            outline.update({})
            outline_ref = self._add_object(outline)
            self._root_object[NameObject(CO.OUTLINES)] = outline_ref

        return outline

    def getOutlineRoot(self) -> TreeObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_outline_root` instead.
        """
        deprecate_with_replacement("getOutlineRoot", "get_outline_root")
        return self.get_outline_root()

    def get_named_dest_root(self) -> ArrayObject:
        if CA.NAMES in self._root_object and isinstance(
            self._root_object[CA.NAMES], DictionaryObject
        ):
            names = cast(DictionaryObject, self._root_object[CA.NAMES])
            idnum = self._objects.index(names) + 1
            names_ref = IndirectObject(idnum, 0, self)
            assert names_ref.get_object() == names
            if CA.DESTS in names and isinstance(names[CA.DESTS], DictionaryObject):
                # 3.6.3 Name Dictionary (PDF spec 1.7)
                dests = cast(DictionaryObject, names[CA.DESTS])
                idnum = self._objects.index(dests) + 1
                dests_ref = IndirectObject(idnum, 0, self)
                assert dests_ref.get_object() == dests
                if CA.NAMES in dests:
                    # TABLE 3.33 Entries in a name tree node dictionary
                    nd = cast(ArrayObject, dests[CA.NAMES])
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

    def getNamedDestRoot(self) -> ArrayObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_named_dest_root` instead.
        """
        deprecate_with_replacement("getNamedDestRoot", "get_named_dest_root")
        return self.get_named_dest_root()

    def add_bookmark_destination(
        self, dest: PageObject, parent: Optional[TreeObject] = None
    ) -> IndirectObject:
        dest_ref = self._add_object(dest)

        outline_ref = self.get_outline_root()

        if parent is None:
            parent = outline_ref

        parent = cast(TreeObject, parent.get_object())
        parent.add_child(dest_ref, self)

        return dest_ref

    def addBookmarkDestination(
        self, dest: PageObject, parent: Optional[TreeObject] = None
    ) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_bookmark_destination` instead.
        """
        deprecate_with_replacement("addBookmarkDestination", "add_bookmark_destination")
        return self.add_bookmark_destination(dest, parent)

    def add_bookmark_dict(
        self, bookmark: BookmarkTypes, parent: Optional[TreeObject] = None
    ) -> IndirectObject:
        bookmark_obj = TreeObject()
        for k, v in list(bookmark.items()):
            bookmark_obj[NameObject(str(k))] = v
        bookmark_obj.update(bookmark)

        if "/A" in bookmark:
            action = DictionaryObject()
            a_dict = cast(DictionaryObject, bookmark["/A"])
            for k, v in list(a_dict.items()):
                action[NameObject(str(k))] = v
            action_ref = self._add_object(action)
            bookmark_obj[NameObject("/A")] = action_ref

        bookmark_ref = self._add_object(bookmark_obj)

        outline_ref = self.get_outline_root()

        if parent is None:
            parent = outline_ref

        parent = parent.get_object()  # type: ignore
        assert parent is not None, "hint for mypy"
        parent.add_child(bookmark_ref, self)

        return bookmark_ref

    def addBookmarkDict(  # pragma: no cover
        self, bookmark: BookmarkTypes, parent: Optional[TreeObject] = None
    ) -> IndirectObject:
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_bookmark_dict` instead.
        """
        deprecate_with_replacement("addBookmarkDict", "add_bookmark_dict")
        return self.add_bookmark_dict(bookmark, parent)

    def add_bookmark(
        self,
        title: str,
        pagenum: int,
        parent: Union[None, TreeObject, IndirectObject] = None,
        color: Optional[Tuple[float, float, float]] = None,
        bold: bool = False,
        italic: bool = False,
        fit: FitType = "/Fit",
        *args: ZoomArgsType,
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
        pages_obj = cast(Dict[str, Any], self.get_object(self._pages))
        page_ref = pages_obj[PA.KIDS][pagenum]
        action = DictionaryObject()
        zoom_args: ZoomArgsType = []
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

        format_flag = 0
        if italic:
            format_flag += 1
        if bold:
            format_flag += 2
        if format_flag:
            bookmark.update({NameObject("/F"): NumberObject(format_flag)})

        bookmark_ref = self._add_object(bookmark)

        assert parent is not None, "hint for mypy"
        parent_obj = cast(TreeObject, parent.get_object())
        parent_obj.add_child(bookmark_ref, self)

        return bookmark_ref

    def addBookmark(
        self,
        title: str,
        pagenum: int,
        parent: Union[None, TreeObject, IndirectObject] = None,
        color: Optional[Tuple[float, float, float]] = None,
        bold: bool = False,
        italic: bool = False,
        fit: FitType = "/Fit",
        *args: ZoomArgsType,
    ) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_bookmark` instead.
        """
        deprecate_with_replacement("addBookmark", "add_bookmark")
        return self.add_bookmark(
            title, pagenum, parent, color, bold, italic, fit, *args
        )

    def add_named_destination_object(self, dest: PdfObject) -> IndirectObject:
        dest_ref = self._add_object(dest)

        nd = self.get_named_dest_root()
        nd.extend([dest["/Title"], dest_ref])  # type: ignore
        return dest_ref

    def addNamedDestinationObject(
        self, dest: PdfObject
    ) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_named_destination_object` instead.
        """
        deprecate_with_replacement(
            "addNamedDestinationObject", "add_named_destination_object"
        )
        return self.add_named_destination_object(dest)

    def add_named_destination(self, title: str, pagenum: int) -> IndirectObject:
        page_ref = self.get_object(self._pages)[PA.KIDS][pagenum]  # type: ignore
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

    def addNamedDestination(
        self, title: str, pagenum: int
    ) -> IndirectObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_named_destination` instead.
        """
        deprecate_with_replacement("addNamedDestination", "add_named_destination")
        return self.add_named_destination(title, pagenum)

    def remove_links(self) -> None:
        """Remove links and annotations from this output."""
        pg_dict = cast(DictionaryObject, self.get_object(self._pages))
        pages = cast(ArrayObject, pg_dict[PA.KIDS])
        for page in pages:
            page_ref = cast(DictionaryObject, self.get_object(page))
            if PG.ANNOTS in page_ref:
                del page_ref[PG.ANNOTS]

    def removeLinks(self) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_links` instead.
        """
        deprecate_with_replacement("removeLinks", "remove_links")
        return self.remove_links()

    def remove_images(self, ignore_byte_string_object: bool = False) -> None:
        """
        Remove images from this output.

        :param bool ignore_byte_string_object: optional parameter
            to ignore ByteString Objects.
        """
        pg_dict = cast(DictionaryObject, self.get_object(self._pages))
        pages = cast(ArrayObject, pg_dict[PA.KIDS])
        jump_operators = (
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
        )
        for j in range(len(pages)):
            page = pages[j]
            page_ref = cast(DictionaryObject, self.get_object(page))
            content = page_ref["/Contents"].get_object()
            if not isinstance(content, ContentStream):
                content = ContentStream(content, page_ref)

            _operations = []
            seq_graphics = False
            for operands, operator in content.operations:
                if operator in [b_("Tj"), b_("'")]:
                    text = operands[0]
                    if ignore_byte_string_object and not isinstance(
                        text, TextStringObject
                    ):
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

    def removeImages(
        self, ignoreByteStringObject: bool = False
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_images` instead.
        """
        deprecate_with_replacement("removeImages", "remove_images")
        return self.remove_images(ignoreByteStringObject)

    def remove_text(self, ignore_byte_string_object: bool = False) -> None:
        """
        Remove text from this output.

        :param bool ignore_byte_string_object: optional parameter
            to ignore ByteString Objects.
        """
        pg_dict = cast(DictionaryObject, self.get_object(self._pages))
        pages = cast(List[IndirectObject], pg_dict[PA.KIDS])
        for j in range(len(pages)):
            page = pages[j]
            page_ref = cast(Dict[str, Any], self.get_object(page))
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

    def removeText(
        self, ignoreByteStringObject: bool = False
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`remove_text` instead.
        """
        deprecate_with_replacement("removeText", "remove_text")
        return self.remove_text(ignoreByteStringObject)

    def add_uri(
        self,
        pagenum: int,
        uri: int,
        rect: RectangleObject,
        border: Optional[ArrayObject] = None,
    ) -> None:
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

        page_link = self.get_object(self._pages)[PA.KIDS][pagenum]  # type: ignore
        page_ref = cast(Dict[str, Any], self.get_object(page_link))

        border_arr: BorderArrayType
        if border is not None:
            border_arr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dash_pattern = ArrayObject([NameObject(n) for n in border[3]])
                border_arr.append(dash_pattern)
        else:
            border_arr = [NumberObject(2)] * 3

        if isinstance(rect, str):
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

    def addURI(
        self,
        pagenum: int,
        uri: int,
        rect: RectangleObject,
        border: Optional[ArrayObject] = None,
    ) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_uri` instead.
        """
        deprecate_with_replacement("addURI", "add_uri")
        return self.add_uri(pagenum, uri, rect, border)

    def add_link(
        self,
        pagenum: int,
        pagedest: int,
        rect: RectangleObject,
        border: Optional[ArrayObject] = None,
        fit: FitType = "/Fit",
        *args: ZoomArgType,
    ) -> None:
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
        pages_obj = cast(Dict[str, Any], self.get_object(self._pages))
        page_link = pages_obj[PA.KIDS][pagenum]
        page_dest = pages_obj[PA.KIDS][pagedest]  # TODO: switch for external link
        page_ref = cast(Dict[str, Any], self.get_object(page_link))

        border_arr: BorderArrayType
        if border is not None:
            border_arr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dash_pattern = ArrayObject([NameObject(n) for n in border[3]])
                border_arr.append(dash_pattern)
        else:
            border_arr = [NumberObject(0)] * 3

        if isinstance(rect, str):
            rect = NameObject(rect)
        elif isinstance(rect, RectangleObject):
            pass
        else:
            rect = RectangleObject(rect)

        zoom_args: ZoomArgsType = []
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

    def addLink(  # pragma: no cover
        self,
        pagenum: int,
        pagedest: int,
        rect: RectangleObject,
        border: Optional[ArrayObject] = None,
        fit: FitType = "/Fit",
        *args: ZoomArgType,
    ) -> None:
        """
        .. deprecated:: 1.28.0

            Use :meth:`add_link` instead.
        """
        deprecate_with_replacement("addLink", "add_link")
        return self.add_link(pagenum, pagedest, rect, border, fit, *args)

    _valid_layouts = (
        "/NoLayout",
        "/SinglePage",
        "/OneColumn",
        "/TwoColumnLeft",
        "/TwoColumnRight",
        "/TwoPageLeft",
        "/TwoPageRight",
    )

    def _get_page_layout(self) -> Optional[LayoutType]:
        try:
            return cast(LayoutType, self._root_object["/PageLayout"])
        except KeyError:
            return None

    def getPageLayout(self) -> Optional[LayoutType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement("getPageLayout", "page_layout")
        return self._get_page_layout()

    def _set_page_layout(self, layout: Union[NameObject, LayoutType]) -> None:
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

    def setPageLayout(self, layout: LayoutType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement(
            "writer.setPageLayout(val)", "writer.page_layout = val"
        )
        return self._set_page_layout(layout)

    @property
    def page_layout(self) -> Optional[LayoutType]:
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
    def page_layout(self, layout: LayoutType) -> None:
        self._set_page_layout(layout)

    @property
    def pageLayout(self) -> Optional[LayoutType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement("pageLayout", "page_layout")
        return self.page_layout

    @pageLayout.setter
    def pageLayout(self, layout: LayoutType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement("pageLayout", "page_layout")
        self.page_layout = layout

    _valid_modes = (
        "/UseNone",
        "/UseOutlines",
        "/UseThumbs",
        "/FullScreen",
        "/UseOC",
        "/UseAttachments",
    )

    def _get_page_mode(self) -> Optional[PagemodeType]:
        try:
            return cast(PagemodeType, self._root_object["/PageMode"])
        except KeyError:
            return None

    def getPageMode(self) -> Optional[PagemodeType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("getPageMode", "page_mode")
        return self._get_page_mode()

    def set_page_mode(self, mode: PagemodeType) -> None:
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        if isinstance(mode, NameObject):
            mode_name: NameObject = mode
        else:
            if mode not in self._valid_modes:
                warnings.warn(
                    "Mode should be one of: {}".format(", ".join(self._valid_modes))
                )
            mode_name = NameObject(mode)
        self._root_object.update({NameObject("/PageMode"): mode_name})

    def setPageMode(self, mode: PagemodeType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("writer.setPageMode(val)", "writer.page_mode = val")
        self.set_page_mode(mode)

    @property
    def page_mode(self) -> Optional[PagemodeType]:
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
    def page_mode(self, mode: PagemodeType) -> None:
        self.set_page_mode(mode)

    @property
    def pageMode(self) -> Optional[PagemodeType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("pageMode", "page_mode")
        return self.page_mode

    @pageMode.setter
    def pageMode(self, mode: PagemodeType) -> None:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("pageMode", "page_mode")
        self.page_mode = mode


class PdfFileWriter(PdfWriter):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        deprecate_with_replacement("PdfFileWriter", "PdfWriter")
        super().__init__(*args, **kwargs)
