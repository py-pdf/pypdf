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

import struct
import sys
import warnings
from hashlib import md5
from sys import version_info

from PyPDF2 import utils
from PyPDF2._page import PageObject
from PyPDF2._security import _alg33_1, _alg34, _alg35
from PyPDF2.constants import CatalogAttributes as CA
from PyPDF2.constants import Core as CO
from PyPDF2.constants import DocumentInformationAttributes as DI
from PyPDF2.constants import EncryptionDictAttributes as ED
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import PagesAttributes as PA
from PyPDF2.constants import StreamAttributes as SA
from PyPDF2.constants import TrailerKeys as TK
from PyPDF2.errors import PdfReadError, PdfReadWarning, PdfStreamError
from PyPDF2.generic import (
    ArrayObject,
    BooleanObject,
    ByteStringObject,
    Destination,
    DictionaryObject,
    Field,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    StreamObject,
    TextStringObject,
    createStringObject,
    readNonWhitespace,
    readObject,
)
from PyPDF2.utils import (
    ConvertFunctionsToVirtualList,
    b_,
    formatWarning,
    isString,
    readUntilWhitespace,
)

if version_info < (3, 0):
    from cStringIO import StringIO

    BytesIO = StringIO
else:
    from io import BytesIO, StringIO


def convertToInt(d, size):
    if size > 8:
        raise PdfReadError("invalid size in convertToInt")
    d = b_("\x00\x00\x00\x00\x00\x00\x00\x00") + b_(d)
    d = d[-8:]
    return struct.unpack(">q", d)[0]


class DocumentInformation(DictionaryObject):
    """
    A class representing the basic document metadata provided in a PDF File.
    This class is accessible through
    :meth:`.getDocumentInfo()`

    All text properties of the document metadata have
    *two* properties, eg. author and author_raw. The non-raw property will
    always return a ``TextStringObject``, making it ideal for a case where
    the metadata is being displayed. The raw property can sometimes return
    a ``ByteStringObject``, if PyPDF2 was unable to decode the string's
    text encoding; this requires additional safety in the caller and
    therefore is not as commonly accessed.
    """

    def __init__(self):
        DictionaryObject.__init__(self)

    def getText(self, key):
        retval = self.get(key, None)
        if isinstance(retval, TextStringObject):
            return retval
        return None

    @property
    def title(self):
        """Read-only property accessing the document's **title**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the title is not specified."""
        return (
            self.getText(DI.TITLE) or self.get(DI.TITLE).getObject()
            if self.get(DI.TITLE)
            else None
        )

    @property
    def title_raw(self):
        """The "raw" version of title; can return a ``ByteStringObject``."""
        return self.get(DI.TITLE)

    @property
    def author(self):
        """Read-only property accessing the document's **author**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the author is not specified."""
        return self.getText(DI.AUTHOR)

    @property
    def author_raw(self):
        """The "raw" version of author; can return a ``ByteStringObject``."""
        return self.get(DI.AUTHOR)

    @property
    def subject(self):
        """Read-only property accessing the document's **subject**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the subject is not specified."""
        return self.getText(DI.SUBJECT)

    @property
    def subject_raw(self):
        """The "raw" version of subject; can return a ``ByteStringObject``."""
        return self.get(DI.SUBJECT)

    @property
    def creator(self):
        """Read-only property accessing the document's **creator**. If the
        document was converted to PDF from another format, this is the name of the
        application (e.g. OpenOffice) that created the original document from
        which it was converted. Returns a unicode string (``TextStringObject``)
        or ``None`` if the creator is not specified."""
        return self.getText(DI.CREATOR)

    @property
    def creator_raw(self):
        """The "raw" version of creator; can return a ``ByteStringObject``."""
        return self.get(DI.CREATOR)

    @property
    def producer(self):
        """Read-only property accessing the document's **producer**.
        If the document was converted to PDF from another format, this is
        the name of the application (for example, OSX Quartz) that converted
        it to PDF. Returns a unicode string (``TextStringObject``)
        or ``None`` if the producer is not specified."""
        return self.getText(DI.PRODUCER)

    @property
    def producer_raw(self):
        """The "raw" version of producer; can return a ``ByteStringObject``."""
        return self.get(DI.PRODUCER)


class PdfFileReader(object):
    """
    Initialize a PdfFileReader object.

    This operation can take some time, as the PDF stream's cross-reference
    tables are read into memory.

    :param stream: A File object or an object that supports the standard read
        and seek methods similar to a File object. Could also be a
        string representing a path to a PDF file.
    :param bool strict: Determines whether user should be warned of all
        problems and also causes some correctable problems to be fatal.
        Defaults to ``True``.
    :param warndest: Destination for logging warnings (defaults to
        ``sys.stderr``).
    :param bool overwriteWarnings: Determines whether to override Python's
        ``warnings.py`` module with a custom implementation (defaults to
        ``True``).
    """

    def __init__(self, stream, strict=True, warndest=None, overwriteWarnings=True):
        if overwriteWarnings:
            # Have to dynamically override the default showwarning since there
            # are no public methods that specify the 'file' parameter
            def _showwarning(
                message, category, filename, lineno, file=warndest, line=None
            ):
                if file is None:
                    file = sys.stderr
                try:
                    # It is possible for sys.stderr to be defined as None, most commonly in the case that the script
                    # is being run vida pythonw.exe on Windows. In this case, just swallow the warning.
                    # See also https://docs.python.org/3/library/sys.html# sys.__stderr__
                    if file is not None:
                        file.write(
                            formatWarning(message, category, filename, lineno, line)
                        )
                except IOError:
                    pass

            warnings.showwarning = _showwarning
        self.strict = strict
        self.flattenedPages = None
        self.resolvedObjects = {}
        self.xrefIndex = 0
        self._pageId2Num = None  # map page IndirectRef number to Page Number
        if hasattr(stream, "mode") and "b" not in stream.mode:
            warnings.warn(
                "PdfFileReader stream/file object is not in binary mode. "
                "It may not be read correctly.",
                PdfReadWarning,
            )
        if isString(stream):
            with open(stream, "rb") as fileobj:
                stream = BytesIO(b_(fileobj.read()))
        self.read(stream)
        self.stream = stream

        self._override_encryption = False

    def getDocumentInfo(self):
        """
        Retrieve the PDF file's document information dictionary, if it exists.
        Note that some PDF files use metadata streams instead of docinfo
        dictionaries, and these metadata streams will not be accessed by this
        function.

        :return: the document information of this PDF file
        :rtype: :class:`DocumentInformation<pdf.DocumentInformation>` or
            ``None`` if none exists.
        """
        if TK.INFO not in self.trailer:
            return None
        obj = self.trailer[TK.INFO]
        retval = DocumentInformation()
        retval.update(obj)
        return retval

    @property
    def documentInfo(self):
        """
        Read-only property that accesses the
        :meth:`getDocumentInfo()<PdfFileReader.getDocumentInfo>` function.
        """
        return self.getDocumentInfo()

    def getXmpMetadata(self):
        """
        Retrieve XMP (Extensible Metadata Platform) data from the PDF document
        root.

        :return: a :class:`XmpInformation<xmp.XmpInformation>`
            instance that can be used to access XMP metadata from the document.
        :rtype: :class:`XmpInformation<xmp.XmpInformation>` or
            ``None`` if no metadata was found on the document root.
        """
        try:
            self._override_encryption = True
            return self.trailer[TK.ROOT].getXmpMetadata()
        finally:
            self._override_encryption = False

    @property
    def xmpMetadata(self):
        """
        Read-only property that accesses the
        :meth:`getXmpMetadata()<PdfFileReader.getXmpMetadata>` function.
        """
        return self.getXmpMetadata()

    def getNumPages(self):
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
                self._override_encryption = True
                self.decrypt("")
                return self.trailer[TK.ROOT]["/Pages"]["/Count"]
            except Exception:
                raise PdfReadError("File has not been decrypted")
            finally:
                self._override_encryption = False
        else:
            if self.flattenedPages is None:
                self._flatten()
            return len(self.flattenedPages)

    @property
    def numPages(self):
        """
        Read-only property that accesses the
        :meth:`getNumPages()<PdfFileReader.getNumPages>` function.
        """
        return self.getNumPages()

    def getPage(self, pageNumber):
        """
        Retrieves a page by number from this PDF file.

        :param int pageNumber: The page number to retrieve
            (pages begin at zero)
        :return: a :class:`PageObject<pdf.PageObject>` instance.
        :rtype: :class:`PageObject<pdf.PageObject>`
        """
        # ensure that we're not trying to access an encrypted PDF
        # assert not self.trailer.has_key(TK.ENCRYPT)
        if self.flattenedPages is None:
            self._flatten()
        return self.flattenedPages[pageNumber]

    @property
    def namedDestinations(self):
        """
        Read-only property that accesses the
        :meth:`getNamedDestinations()<PdfFileReader.getNamedDestinations>` function.
        """
        return self.getNamedDestinations()

    # A select group of relevant field attributes. For the complete list,
    # see section 8.6.2 of the PDF 1.7 reference.

    def getFields(self, tree=None, retval=None, fileobj=None):
        """
        Extracts field data if this PDF contains interactive form fields.
        The *tree* and *retval* parameters are for recursive use.

        :param fileobj: A file object (usually a text file) to write
            a report to on all interactive form fields found.
        :return: A dictionary where each key is a field name, and each
            value is a :class:`Field<PyPDF2.generic.Field>` object. By
            default, the mapping name is used for keys.
        :rtype: dict, or ``None`` if form data could not be located.
        """
        field_attributes = {
            "/FT": "Field Type",
            PA.PARENT: "Parent",
            "/T": "Field Name",
            "/TU": "Alternate Field Name",
            "/TM": "Mapping Name",
            "/Ff": "Field Flags",
            "/V": "Value",
            "/DV": "Default Value",
        }
        if retval is None:
            retval = {}
            catalog = self.trailer[TK.ROOT]
            # get the AcroForm tree
            if "/AcroForm" in catalog:
                tree = catalog["/AcroForm"]
            else:
                return None
        if tree is None:
            return retval

        self._checkKids(tree, retval, fileobj)
        for attr in field_attributes:
            if attr in tree:
                # Tree is a field
                self._buildField(tree, retval, fileobj, field_attributes)
                break

        if "/Fields" in tree:
            fields = tree["/Fields"]
            for f in fields:
                field = f.getObject()
                self._buildField(field, retval, fileobj, field_attributes)

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
        if PA.KIDS in tree:
            # recurse down the tree
            for kid in tree[PA.KIDS]:
                self.getFields(kid.getObject(), retval, fileobj)

    def _writeField(self, fileobj, field, fieldAttributes):
        order = ["/TM", "/T", "/FT", PA.PARENT, "/TU", "/Ff", "/V", "/DV"]
        for attr in order:
            attr_name = fieldAttributes[attr]
            try:
                if attr == "/FT":
                    # Make the field type value more clear
                    types = {
                        "/Btn": "Button",
                        "/Tx": "Text",
                        "/Ch": "Choice",
                        "/Sig": "Signature",
                    }
                    if field[attr] in types:
                        fileobj.write(attr_name + ": " + types[field[attr]] + "\n")
                elif attr == PA.PARENT:
                    # Let's just write the name of the parent
                    try:
                        name = field[PA.PARENT]["/TM"]
                    except KeyError:
                        name = field[PA.PARENT]["/T"]
                    fileobj.write(attr_name + ": " + name + "\n")
                else:
                    fileobj.write(attr_name + ": " + str(field[attr]) + "\n")
            except KeyError:
                # Field attribute is N/A or unknown, so don't write anything
                pass

    def getFormTextFields(self):
        """Retrieves form fields from the document with textual data (inputs, dropdowns)"""
        # Retrieve document form fields
        formfields = self.getFields()
        if formfields is None:
            return {}
        return {
            formfields[field]["/T"]: formfields[field].get("/V")
            for field in formfields
            if formfields[field].get("/FT") == "/Tx"
        }

    def getNamedDestinations(self, tree=None, retval=None):
        """
        Retrieves the named destinations present in the document.

        :return: a dictionary which maps names to
            :class:`Destinations<PyPDF2.generic.Destination>`.
        :rtype: dict
        """
        if retval is None:
            retval = {}
            catalog = self.trailer[TK.ROOT]

            # get the name tree
            if CA.DESTS in catalog:
                tree = catalog[CA.DESTS]
            elif CA.NAMES in catalog:
                names = catalog[CA.NAMES]
                if CA.DESTS in names:
                    tree = names[CA.DESTS]

        if tree is None:
            return retval

        if PA.KIDS in tree:
            # recurse down the tree
            for kid in tree[PA.KIDS]:
                self.getNamedDestinations(kid.getObject(), retval)

        if CA.NAMES in tree:
            names = tree[CA.NAMES]
            for i in range(0, len(names), 2):
                key = names[i].getObject()
                val = names[i + 1].getObject()
                if isinstance(val, DictionaryObject) and "/D" in val:
                    val = val["/D"]
                dest = self._buildDestination(key, val)
                if dest is not None:
                    retval[key] = dest

        return retval

    @property
    def outlines(self):
        """
        Read-only property that accesses the
            :meth:`getOutlines()<PdfFileReader.getOutlines>` function.
        """
        return self.getOutlines()

    def getOutlines(self, node=None, outlines=None):
        """
        Retrieve the document outline present in the document.

        :return: a nested list of :class:`Destinations<PyPDF2.generic.Destination>`.
        """
        if outlines is None:
            outlines = []
            catalog = self.trailer[TK.ROOT]

            # get the outline dictionary and named destinations
            if CO.OUTLINES in catalog:
                try:
                    lines = catalog[CO.OUTLINES]
                except PdfReadError:
                    # this occurs if the /Outlines object reference is incorrect
                    # for an example of such a file, see https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf
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
                sub_outlines = []
                self.getOutlines(node["/First"], sub_outlines)
                if sub_outlines:
                    outlines.append(sub_outlines)

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

        if isinstance(indirectRef, NullObject):
            return -1
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
            an instance of :class:`PageObject<PyPDF2.pdf.PageObject>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        indirect_ref = page.indirectRef
        ret = self._getPageNumberByIndirect(indirect_ref)
        return ret

    def getDestinationPageNumber(self, destination):
        """
        Retrieve page number of a given Destination object

        :param Destination destination: The destination to get page number.
             Should be an instance of
             :class:`Destination<PyPDF2.pdf.Destination>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        indirect_ref = destination.page
        ret = self._getPageNumberByIndirect(indirect_ref)
        return ret

    def _buildDestination(self, title, array):
        page, typ = array[0:2]
        array = array[2:]
        try:
            return Destination(title, page, typ, *array)
        except PdfReadError:
            warnings.warn("Unknown destination : " + title + " " + str(array))
            if self.strict:
                raise
            else:
                # create a link to first Page
                return Destination(
                    title, self.getPage(0).indirectRef, TextStringObject("/Fit")
                )

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

    @property
    def pages(self):
        """
        Read-only property that emulates a list based upon the
        :meth:`getNumPages()<PdfFileReader.getNumPages>` and
        :meth:`getPage()<PdfFileReader.getPage>` methods.
        """
        return ConvertFunctionsToVirtualList(self.getNumPages, self.getPage)

    def getPageLayout(self):
        """
        Get the page layout.

        See :meth:`setPageLayout()<PdfFileWriter.setPageLayout>`
        for a description of valid layouts.

        :return: Page layout currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self.trailer[TK.ROOT]["/PageLayout"]
        except KeyError:
            return None

    @property
    def pageLayout(self):
        """Read-only property accessing the
        :meth:`getPageLayout()<PdfFileReader.getPageLayout>` method."""
        return self.getPageLayout()

    def getPageMode(self):
        """
        Get the page mode.
        See :meth:`setPageMode()<PdfFileWriter.setPageMode>`
        for a description of valid modes.

        :return: Page mode currently being used.
        :rtype: ``str``, ``None`` if not specified
        """
        try:
            return self.trailer[TK.ROOT]["/PageMode"]
        except KeyError:
            return None

    @property
    def pageMode(self):
        """Read-only property accessing the
        :meth:`getPageMode()<PdfFileReader.getPageMode>` method."""
        return self.getPageMode()

    def _flatten(self, pages=None, inherit=None, indirectRef=None):
        inheritablePageAttributes = (
            NameObject(PG.RESOURCES),
            NameObject(PG.MEDIABOX),
            NameObject(PG.CROPBOX),
            NameObject(PG.ROTATE),
        )
        if inherit is None:
            inherit = {}
        if pages is None:
            # Fix issue 327: set flattenedPages attribute only for
            # decrypted file
            catalog = self.trailer[TK.ROOT].getObject()
            pages = catalog["/Pages"].getObject()
            self.flattenedPages = []

        t = "/Pages"
        if PA.TYPE in pages:
            t = pages[PA.TYPE]

        if t == "/Pages":
            for attr in inheritablePageAttributes:
                if attr in pages:
                    inherit[attr] = pages[attr]
            for page in pages[PA.KIDS]:
                addt = {}
                if isinstance(page, IndirectObject):
                    addt["indirectRef"] = page
                self._flatten(page.getObject(), inherit, **addt)
        elif t == "/Page":
            for attr, value in list(inherit.items()):
                # if the page has it's own value, it does not inherit the
                # parent's value:
                if attr not in pages:
                    pages[attr] = value
            page_obj = PageObject(self, indirectRef)
            page_obj.update(pages)
            self.flattenedPages.append(page_obj)

    def _getObjectFromStream(self, indirectReference):
        # indirect reference to object in object stream
        # read the entire object stream into memory
        stmnum, idx = self.xref_objStm[indirectReference.idnum]
        obj_stm = IndirectObject(stmnum, 0, self).getObject()
        # This is an xref to a stream, so its type better be a stream
        assert obj_stm["/Type"] == "/ObjStm"
        # /N is the number of indirect objects in the stream
        assert idx < obj_stm["/N"]
        stream_data = BytesIO(b_(obj_stm.getData()))
        for i in range(obj_stm["/N"]):
            readNonWhitespace(stream_data)
            stream_data.seek(-1, 1)
            objnum = NumberObject.readFromStream(stream_data)
            readNonWhitespace(stream_data)
            stream_data.seek(-1, 1)
            offset = NumberObject.readFromStream(stream_data)
            readNonWhitespace(stream_data)
            stream_data.seek(-1, 1)
            if objnum != indirectReference.idnum:
                # We're only interested in one object
                continue
            if self.strict and idx != i:
                raise PdfReadError("Object is in wrong index.")
            stream_data.seek(obj_stm["/First"] + offset, 0)
            try:
                obj = readObject(stream_data, self)
            except PdfStreamError as e:
                # Stream object cannot be read. Normally, a critical error, but
                # Adobe Reader doesn't complain, so continue (in strict mode?)
                e = sys.exc_info()[1]
                warnings.warn(
                    "Invalid stream (index %d) within object %d %d: %s"
                    % (i, indirectReference.idnum, indirectReference.generation, e),
                    PdfReadWarning,
                )

                if self.strict:
                    raise PdfReadError("Can't read object stream: %s" % e)
                # Replace with null. Hopefully it's nothing important.
                obj = NullObject()
            return obj

        if self.strict:
            raise PdfReadError("This is a fatal error in strict mode.")
        return NullObject()

    def getObject(self, indirectReference):
        retval = self.cacheGetIndirectObject(
            indirectReference.generation, indirectReference.idnum
        )
        if retval is not None:
            return retval
        if (
            indirectReference.generation == 0
            and indirectReference.idnum in self.xref_objStm
        ):
            retval = self._getObjectFromStream(indirectReference)
        elif (
            indirectReference.generation in self.xref
            and indirectReference.idnum in self.xref[indirectReference.generation]
        ):
            start = self.xref[indirectReference.generation][indirectReference.idnum]
            self.stream.seek(start, 0)
            idnum, generation = self.readObjectHeader(self.stream)
            if idnum != indirectReference.idnum and self.xrefIndex:
                # Xref table probably had bad indexes due to not being zero-indexed
                if self.strict:
                    raise PdfReadError(
                        "Expected object ID (%d %d) does not match actual (%d %d); xref table not zero-indexed."
                        % (
                            indirectReference.idnum,
                            indirectReference.generation,
                            idnum,
                            generation,
                        )
                    )
                else:
                    pass  # xref table is corrected in non-strict mode
            elif idnum != indirectReference.idnum and self.strict:
                # some other problem
                raise PdfReadError(
                    "Expected object ID (%d %d) does not match actual (%d %d)."
                    % (
                        indirectReference.idnum,
                        indirectReference.generation,
                        idnum,
                        generation,
                    )
                )
            if self.strict:
                assert generation == indirectReference.generation
            retval = readObject(self.stream, self)

            # override encryption is used for the /Encrypt dictionary
            if not self._override_encryption and self.isEncrypted:
                # if we don't have the encryption key:
                if not hasattr(self, "_decryption_key"):
                    raise PdfReadError("file has not been decrypted")
                # otherwise, decrypt here...
                pack1 = struct.pack("<i", indirectReference.idnum)[:3]
                pack2 = struct.pack("<i", indirectReference.generation)[:2]
                key = self._decryption_key + pack1 + pack2
                assert len(key) == (len(self._decryption_key) + 5)
                md5_hash = md5(key).digest()
                key = md5_hash[: min(16, len(self._decryption_key) + 5)]
                retval = self._decryptObject(retval, key)
        else:
            warnings.warn(
                "Object %d %d not defined."
                % (indirectReference.idnum, indirectReference.generation),
                PdfReadWarning,
            )
            if self.strict:
                raise PdfReadError("Could not find object.")
        self.cacheIndirectObject(
            indirectReference.generation, indirectReference.idnum, retval
        )
        return retval

    def _decryptObject(self, obj, key):
        if isinstance(obj, (ByteStringObject, TextStringObject)):
            obj = createStringObject(utils.RC4_encrypt(key, obj.original_bytes))
        elif isinstance(obj, StreamObject):
            obj._data = utils.RC4_encrypt(key, obj._data)
        elif isinstance(obj, DictionaryObject):
            for dictkey, value in list(obj.items()):
                obj[dictkey] = self._decryptObject(value, key)
        elif isinstance(obj, ArrayObject):
            for i in range(len(obj)):
                obj[i] = self._decryptObject(obj[i], key)
        return obj

    def readObjectHeader(self, stream):
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
        extra |= utils.skipOverWhitespace(stream)
        stream.seek(-1, 1)

        # although it's not used, it might still be necessary to read
        _obj = stream.read(3)  # noqa: F841

        readNonWhitespace(stream)
        stream.seek(-1, 1)
        if extra and self.strict:
            warnings.warn(
                "Superfluous whitespace found in object header %s %s"
                % (idnum, generation),
                PdfReadWarning,
            )
        return int(idnum), int(generation)

    def cacheGetIndirectObject(self, generation, idnum):
        out = self.resolvedObjects.get((generation, idnum))
        return out

    def cacheIndirectObject(self, generation, idnum, obj):
        if (generation, idnum) in self.resolvedObjects:
            msg = "Overwriting cache for %s %s" % (generation, idnum)
            if self.strict:
                raise PdfReadError(msg)
            else:
                warnings.warn(msg)
        self.resolvedObjects[(generation, idnum)] = obj
        return obj

    def read(self, stream):
        # start at the end:
        stream.seek(-1, 2)
        if not stream.tell():
            raise PdfReadError("Cannot read an empty file")
        if self.strict:
            stream.seek(0, 0)
            header_byte = stream.read(5)
            if header_byte != b"%PDF-":
                raise PdfReadError(
                    "PDF starts with '{}', but '%PDF-' expected".format(
                        header_byte.decode("utf8")
                    )
                )
            stream.seek(-1, 2)
        last1M = stream.tell() - 1024 * 1024 + 1  # offset of last MB of stream
        line = b_("")
        while line[:5] != b_("%%EOF"):
            if stream.tell() < last1M:
                raise PdfReadError("EOF marker not found")
            line = self.readNextEndLine(stream)

        startxref = self._find_startxref_pos(stream)

        # check and eventually correct the startxref only in not strict
        xref_issue_nr = self._get_xref_issues(stream, startxref)
        if xref_issue_nr != 0:
            if self.strict and xref_issue_nr:
                raise PdfReadError("Broken xref table")
            else:
                warnings.warn(
                    "incorrect startxref pointer({})".format(xref_issue_nr),
                    PdfReadWarning,
                )

        # read all cross reference tables and their trailers
        self.xref = {}
        self.xref_objStm = {}
        self.trailer = DictionaryObject()
        while True:
            # load the xref table
            stream.seek(startxref, 0)
            x = stream.read(1)
            if x == b_("x"):
                self._read_standard_xref_table(stream)
                readNonWhitespace(stream)
                stream.seek(-1, 1)
                new_trailer = readObject(stream, self)
                for key, value in list(new_trailer.items()):
                    if key not in self.trailer:
                        self.trailer[key] = value
                if "/Prev" in new_trailer:
                    startxref = new_trailer["/Prev"]
                else:
                    break
            elif xref_issue_nr:
                try:
                    self._rebuild_xref_table(stream)
                    break
                except Exception:
                    xref_issue_nr = 0
            elif x.isdigit():
                xrefstream = self._read_pdf15_xref_stream(stream)

                trailer_keys = TK.ROOT, TK.ENCRYPT, TK.INFO, TK.ID
                for key in trailer_keys:
                    if key in xrefstream and key not in self.trailer:
                        self.trailer[NameObject(key)] = xrefstream.raw_get(key)
                if "/Prev" in xrefstream:
                    startxref = xrefstream["/Prev"]
                else:
                    break
            else:
                # some PDFs have /Prev=0 in the trailer, instead of no /Prev
                if startxref == 0:
                    if self.strict:
                        raise PdfReadError(
                            "/Prev=0 in the trailer (try opening with strict=False)"
                        )
                    else:
                        warnings.warn(
                            "/Prev=0 in the trailer - assuming there"
                            " is no previous xref table"
                        )
                        break
                # bad xref character at startxref.  Let's see if we can find
                # the xref table nearby, as we've observed this error with an
                # off-by-one before.
                stream.seek(-11, 1)
                tmp = stream.read(20)
                xref_loc = tmp.find(b_("xref"))
                if xref_loc != -1:
                    startxref -= 10 - xref_loc
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
                # no xref table found at specified location
                raise PdfReadError("Could not find xref table at specified location")
        # if not zero-indexed, verify that the table is correct; change it if necessary
        if self.xrefIndex and not self.strict:
            loc = stream.tell()
            for gen in self.xref:
                if gen == 65535:
                    continue
                for id in self.xref[gen]:
                    stream.seek(self.xref[gen][id], 0)
                    try:
                        pid, pgen = self.readObjectHeader(stream)
                    except ValueError:
                        break
                    if pid == id - self.xrefIndex:
                        self._zeroXref(gen)
                        break
                    # if not, then either it's just plain wrong, or the
                    # non-zero-index is actually correct
            stream.seek(loc, 0)  # return to where it was

    def _find_startxref_pos(self, stream):
        """Find startxref entry - the location of the xref table"""
        line = self.readNextEndLine(stream)
        try:
            startxref = int(line)
        except ValueError:
            # 'startxref' may be on the same line as the location
            if not line.startswith(b_("startxref")):
                raise PdfReadError("startxref not found")
            startxref = int(line[9:].strip())
            warnings.warn("startxref on same line as offset")
        else:
            line = self.readNextEndLine(stream)
            if line[:9] != b_("startxref"):
                raise PdfReadError("startxref not found")
        return startxref

    def _read_standard_xref_table(self, stream):
        # standard cross-reference table
        ref = stream.read(4)
        if ref[:3] != b_("ref"):
            raise PdfReadError("xref table read error")
        readNonWhitespace(stream)
        stream.seek(-1, 1)
        firsttime = True  # check if the first time looking at the xref table
        while True:
            num = readObject(stream, self)
            if firsttime and num != 0:
                self.xrefIndex = num
                if self.strict:
                    warnings.warn(
                        "Xref table not zero-indexed. ID numbers for objects will be corrected.",
                        PdfReadWarning,
                    )
                    # if table not zero indexed, could be due to error from when PDF was created
                    # which will lead to mismatched indices later on, only warned and corrected if self.strict=True
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
                if generation not in self.xref:
                    self.xref[generation] = {}
                if num in self.xref[generation]:
                    # It really seems like we should allow the last
                    # xref table in the file to override previous
                    # ones. Since we read the file backwards, assume
                    # any existing key is already set correctly.
                    pass
                else:
                    self.xref[generation][num] = offset
                cnt += 1
                num += 1
            readNonWhitespace(stream)
            stream.seek(-1, 1)
            trailertag = stream.read(7)
            if trailertag != b_("trailer"):
                # more xrefs!
                stream.seek(-7, 1)
            else:
                break

    def _read_pdf15_xref_stream(self, stream):
        # PDF 1.5+ Cross-Reference Stream
        stream.seek(-1, 1)
        idnum, generation = self.readObjectHeader(stream)
        xrefstream = readObject(stream, self)
        assert xrefstream["/Type"] == "/XRef"
        self.cacheIndirectObject(generation, idnum, xrefstream)
        stream_data = BytesIO(b_(xrefstream.getData()))
        # Index pairs specify the subsections in the dictionary. If
        # none create one subsection that spans everything.
        idx_pairs = xrefstream.get("/Index", [0, xrefstream.get("/Size")])
        entry_sizes = xrefstream.get("/W")
        assert len(entry_sizes) >= 3
        if self.strict and len(entry_sizes) > 3:
            raise PdfReadError("Too many entry sizes: %s" % entry_sizes)

        def get_entry(i):
            # Reads the correct number of bytes for each entry. See the
            # discussion of the W parameter in PDF spec table 17.
            if entry_sizes[i] > 0:
                d = stream_data.read(entry_sizes[i])
                return convertToInt(d, entry_sizes[i])

            # PDF Spec Table 17: A value of zero for an element in the
            # W array indicates...the default value shall be used
            if i == 0:
                return 1  # First value defaults to 1
            else:
                return 0

        def used_before(num, generation):
            # We move backwards through the xrefs, don't replace any.
            return num in self.xref.get(generation, []) or num in self.xref_objStm

        # Iterate through each subsection
        self._read_xref_subsections(idx_pairs, get_entry, used_before)
        return xrefstream

    @staticmethod
    def _get_xref_issues(stream, startxref):
        """Return an int which indicates an issue. 0 means there is no issue."""
        stream.seek(startxref - 1, 0)  # -1 to check character before
        line = stream.read(1)
        if line not in b_("\r\n \t"):
            return 1
        line = stream.read(4)
        if line != b_("xref"):
            # not an xref so check if it is an XREF object
            line = b_("")
            while line in b_("0123456789 \t"):
                line = stream.read(1)
                if line == b_(""):
                    return 2
            line += stream.read(2)  # 1 char already read, +2 to check "obj"
            if line.lower() != b_("obj"):
                return 3
            # while stream.read(1) in b_(" \t\r\n"):
            #     pass
            # line = stream.read(256)  # check that it is xref obj
            # if b_("/xref") not in line.lower():
            #     return 4
        return 0

    def _rebuild_xref_table(self, stream):
        self.xref = {}
        stream.seek(0, 0)
        f_ = stream.read(-1)
        import re

        for m in re.finditer(b_(r"[\r\n \t][ \t]*(\d+)[ \t]+(\d+)[ \t]+obj"), f_):
            idnum = int(m.group(1))
            generation = int(m.group(2))
            if generation not in self.xref:
                self.xref[generation] = {}
            self.xref[generation][idnum] = m.start(1)
        trailer_pos = f_.rfind(b"trailer") - len(f_) + 7
        stream.seek(trailer_pos, 2)
        # code below duplicated
        readNonWhitespace(stream)
        stream.seek(-1, 1)

        # there might be something that is not a dict (see #856)
        new_trailer = readObject(stream, self)

        for key, value in list(new_trailer.items()):
            if key not in self.trailer:
                self.trailer[key] = value

    def _read_xref_subsections(self, idx_pairs, getEntry, used_before):
        last_end = 0
        for start, size in self._pairs(idx_pairs):
            # The subsections must increase
            assert start >= last_end
            last_end = start + size
            for num in range(start, start + size):
                # The first entry is the type
                xref_type = getEntry(0)
                # The rest of the elements depend on the xref_type
                if xref_type == 0:
                    # linked list of free objects
                    next_free_object = getEntry(1)  # noqa: F841
                    next_generation = getEntry(2)  # noqa: F841
                elif xref_type == 1:
                    # objects that are in use but are not compressed
                    byte_offset = getEntry(1)
                    generation = getEntry(2)
                    if generation not in self.xref:
                        self.xref[generation] = {}
                    if not used_before(num, generation):
                        self.xref[generation][num] = byte_offset
                elif xref_type == 2:
                    # compressed objects
                    objstr_num = getEntry(1)
                    obstr_idx = getEntry(2)
                    generation = 0  # PDF spec table 18, generation is 0
                    if not used_before(num, generation):
                        self.xref_objStm[num] = (objstr_num, obstr_idx)
                elif self.strict:
                    raise PdfReadError("Unknown xref type: %s" % xref_type)

    def _zeroXref(self, generation):
        self.xref[generation] = {
            k - self.xrefIndex: v for (k, v) in list(self.xref[generation].items())
        }

    def _pairs(self, array):
        i = 0
        while True:
            yield array[i], array[i + 1]
            i += 2
            if (i + 1) >= len(array):
                break

    def readNextEndLine(self, stream, limit_offset=0):
        line_parts = []
        while True:
            # Prevent infinite loops in malformed PDFs
            if stream.tell() == 0 or stream.tell() == limit_offset:
                raise PdfReadError("Could not read malformed PDF file")
            x = stream.read(1)
            if stream.tell() < 2:
                raise PdfReadError("EOL marker not found")
            stream.seek(-2, 1)
            if x == b_("\n") or x == b_("\r"):  ## \n = LF; \r = CR
                crlf = False
                while x == b_("\n") or x == b_("\r"):
                    x = stream.read(1)
                    if x == b_("\n") or x == b_("\r"):  # account for CR+LF
                        stream.seek(-1, 1)
                        crlf = True
                    if stream.tell() < 2:
                        raise PdfReadError("EOL marker not found")
                    stream.seek(-2, 1)
                stream.seek(
                    2 if crlf else 1, 1
                )  # if using CR+LF, go back 2 bytes, else 1
                break
            else:
                line_parts.append(x)
        line_parts.reverse()
        return b"".join(line_parts)

    def decrypt(self, password):
        """
        When using an encrypted / secured PDF file with the PDF Standard
        encryption handler, this function will allow the file to be decrypted.
        It checks the given password against the document's user password and
        owner password, and then stores the resulting decryption key if either
        password is correct.

        It does not matter which password was matched.  Both passwords provide
        the correct decryption key that will allow the document to be used with
        this library.

        :param str password: The password to match.
        :return: ``0`` if the password failed, ``1`` if the password matched the user
            password, and ``2`` if the password matched the owner password.
        :rtype: int
        :raises NotImplementedError: if document uses an unsupported encryption
            method.
        """

        self._override_encryption = True
        try:
            return self._decrypt(password)
        finally:
            self._override_encryption = False

    def decode_permissions(self, permissions_code):
        # Takes the permissions as an integer, returns the allowed access
        permissions = {}
        permissions["print"] = permissions_code & (1 << 3 - 1) != 0  # bit 3
        permissions["modify"] = permissions_code & (1 << 4 - 1) != 0  # bit 4
        permissions["copy"] = permissions_code & (1 << 5 - 1) != 0  # bit 5
        permissions["annotations"] = permissions_code & (1 << 6 - 1) != 0  # bit 6
        permissions["forms"] = permissions_code & (1 << 9 - 1) != 0  # bit 9
        permissions["accessability"] = permissions_code & (1 << 10 - 1) != 0  # bit 10
        permissions["assemble"] = permissions_code & (1 << 11 - 1) != 0  # bit 11
        permissions["print_high_quality"] = (
            permissions_code & (1 << 12 - 1) != 0
        )  # bit 12
        return permissions

    def _decrypt(self, password):
        # Decrypts data as per Section 3.5 (page 117) of PDF spec v1.7
        # "The security handler defines the use of encryption and decryption in
        # the document, using the rules specified by the CF, StmF, and StrF entries"
        encrypt = self.trailer[TK.ENCRYPT].getObject()
        # /Encrypt Keys:
        # Filter (name)   : "name of the preferred security handler "
        # V (number)      : Algorithm Code
        # Length (integer): Length of encryption key, in bits
        # CF (dictionary) : Crypt filter
        # StmF (name)     : Name of the crypt filter that is used by default when decrypting streams
        # StrF (name)     : The name of the crypt filter that is used when decrypting all strings in the document
        # R (number)      : Standard security handler revision number
        # U (string)      : A 32-byte string, based on the user password
        # P (integer)     : Permissions allowed with user access
        if encrypt["/Filter"] != "/Standard":
            raise NotImplementedError(
                "only Standard PDF encryption handler is available"
            )
        if not (encrypt["/V"] in (1, 2)):
            raise NotImplementedError(
                "only algorithm code 1 and 2 are supported. This PDF uses code %s"
                % encrypt["/V"]
            )
        user_password, key = self._authenticateUserPassword(password)
        if user_password:
            self._decryption_key = key
            return 1
        else:
            rev = encrypt["/R"].getObject()
            if rev == 2:
                keylen = 5
            else:
                keylen = encrypt[SA.LENGTH].getObject() // 8
            key = _alg33_1(password, rev, keylen)
            real_O = encrypt["/O"].getObject()
            if rev == 2:
                userpass = utils.RC4_encrypt(key, real_O)
            else:
                val = real_O
                for i in range(19, -1, -1):
                    new_key = b_("")
                    for l in range(len(key)):
                        new_key += b_(chr(utils.ord_(key[l]) ^ i))
                    val = utils.RC4_encrypt(new_key, val)
                userpass = val
            owner_password, key = self._authenticateUserPassword(userpass)
            if owner_password:
                self._decryption_key = key
                return 2
        return 0

    def _authenticateUserPassword(self, password):
        encrypt = self.trailer[TK.ENCRYPT].getObject()
        rev = encrypt[ED.R].getObject()
        owner_entry = encrypt[ED.O].getObject()
        p_entry = encrypt[ED.P].getObject()
        if TK.ID in self.trailer:
            id_entry = self.trailer[TK.ID].getObject()
        else:
            # Some documents may not have a /ID, use two empty
            # byte strings instead. Solves
            # https://github.com/mstamy2/PyPDF2/issues/608
            id_entry = ArrayObject([ByteStringObject(b""), ByteStringObject(b"")])
        id1_entry = id_entry[0].getObject()
        real_U = encrypt[ED.U].getObject().original_bytes
        if rev == 2:
            U, key = _alg34(password, owner_entry, p_entry, id1_entry)
        elif rev >= 3:
            U, key = _alg35(
                password,
                rev,
                encrypt[SA.LENGTH].getObject() // 8,
                owner_entry,
                p_entry,
                id1_entry,
                encrypt.get(ED.ENCRYPT_METADATA, BooleanObject(False)).getObject(),
            )
            U, real_U = U[:16], real_U[:16]
        return U == real_U, key

    def getIsEncrypted(self):
        return TK.ENCRYPT in self.trailer

    @property
    def isEncrypted(self):
        """
        Read-only boolean property showing whether this PDF file is encrypted.
        Note that this property, if true, will remain true even after the
        :meth:`decrypt()<PdfFileReader.decrypt>` method is called.
        """
        return self.getIsEncrypted()
