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

import os
import re
import struct
import warnings
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from ._encryption import Encryption, PasswordType
from ._page import PageObject, _VirtualList
from ._utils import (
    StrByteType,
    StreamType,
    b_,
    deprecate_no_replacement,
    deprecate_with_replacement,
    read_non_whitespace,
    read_previous_line,
    read_until_whitespace,
    skip_over_comment,
    skip_over_whitespace,
)
from .constants import CatalogAttributes as CA
from .constants import CatalogDictionary as CD
from .constants import Core as CO
from .constants import DocumentInformationAttributes as DI
from .constants import PageAttributes as PG
from .constants import PagesAttributes as PA
from .constants import TrailerKeys as TK
from .errors import (
    PdfReadError,
    PdfReadWarning,
    PdfStreamError,
)
from .generic import (
    ArrayObject,
    ContentStream,
    DecodedStreamObject,
    Destination,
    DictionaryObject,
    EncodedStreamObject,
    Field,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    PdfObject,
    TextStringObject,
    TreeObject,
    read_object,
)
from .types import OutlinesType, PagemodeType
from .xmp import XmpInformation


def convert_to_int(d: bytes, size: int) -> Union[int, Tuple[Any, ...]]:
    if size > 8:
        raise PdfReadError("invalid size in convert_to_int")
    d = b"\x00\x00\x00\x00\x00\x00\x00\x00" + d
    d = d[-8:]
    return struct.unpack(">q", d)[0]


def convertToInt(
    d: bytes, size: int
) -> Union[int, Tuple[Any, ...]]:  # pragma: no cover
    deprecate_with_replacement("convertToInt", "convert_to_int")
    return convert_to_int(d, size)


class DocumentInformation(DictionaryObject):
    """
    A class representing the basic document metadata provided in a PDF File.
    This class is accessible through :py:class:`PdfReader.metadata<PyPDF2.PdfReader.metadata>`.

    All text properties of the document metadata have
    *two* properties, eg. author and author_raw. The non-raw property will
    always return a ``TextStringObject``, making it ideal for a case where
    the metadata is being displayed. The raw property can sometimes return
    a ``ByteStringObject``, if PyPDF2 was unable to decode the string's
    text encoding; this requires additional safety in the caller and
    therefore is not as commonly accessed.
    """

    def __init__(self) -> None:
        DictionaryObject.__init__(self)

    def _get_text(self, key: str) -> Optional[str]:
        retval = self.get(key, None)
        if isinstance(retval, TextStringObject):
            return retval
        return None

    def getText(self, key: str) -> Optional[str]:  # pragma: no cover
        """
        The text value of the specified key or None.

        .. deprecated:: 1.28.0

            Use the attributes (e.g. :py:attr:`title` / :py:attr:`author`).
        """
        deprecate_no_replacement("getText")
        return self._get_text(key)

    @property
    def title(self) -> Optional[str]:
        """Read-only property accessing the document's **title**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the title is not specified."""
        return (
            self._get_text(DI.TITLE) or self.get(DI.TITLE).get_object()  # type: ignore
            if self.get(DI.TITLE)
            else None
        )

    @property
    def title_raw(self) -> Optional[str]:
        """The "raw" version of title; can return a ``ByteStringObject``."""
        return self.get(DI.TITLE)

    @property
    def author(self) -> Optional[str]:
        """Read-only property accessing the document's **author**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the author is not specified."""
        return self._get_text(DI.AUTHOR)

    @property
    def author_raw(self) -> Optional[str]:
        """The "raw" version of author; can return a ``ByteStringObject``."""
        return self.get(DI.AUTHOR)

    @property
    def subject(self) -> Optional[str]:
        """Read-only property accessing the document's **subject**.
        Returns a unicode string (``TextStringObject``) or ``None``
        if the subject is not specified."""
        return self._get_text(DI.SUBJECT)

    @property
    def subject_raw(self) -> Optional[str]:
        """The "raw" version of subject; can return a ``ByteStringObject``."""
        return self.get(DI.SUBJECT)

    @property
    def creator(self) -> Optional[str]:
        """Read-only property accessing the document's **creator**. If the
        document was converted to PDF from another format, this is the name of the
        application (e.g. OpenOffice) that created the original document from
        which it was converted. Returns a unicode string (``TextStringObject``)
        or ``None`` if the creator is not specified."""
        return self._get_text(DI.CREATOR)

    @property
    def creator_raw(self) -> Optional[str]:
        """The "raw" version of creator; can return a ``ByteStringObject``."""
        return self.get(DI.CREATOR)

    @property
    def producer(self) -> Optional[str]:
        """Read-only property accessing the document's **producer**.
        If the document was converted to PDF from another format, this is
        the name of the application (for example, OSX Quartz) that converted
        it to PDF. Returns a unicode string (``TextStringObject``)
        or ``None`` if the producer is not specified."""
        return self._get_text(DI.PRODUCER)

    @property
    def producer_raw(self) -> Optional[str]:
        """The "raw" version of producer; can return a ``ByteStringObject``."""
        return self.get(DI.PRODUCER)


class PdfReader:
    """
    Initialize a PdfReader object.

    This operation can take some time, as the PDF stream's cross-reference
    tables are read into memory.

    :param stream: A File object or an object that supports the standard read
        and seek methods similar to a File object. Could also be a
        string representing a path to a PDF file.
    :param bool strict: Determines whether user should be warned of all
        problems and also causes some correctable problems to be fatal.
        Defaults to ``False``.
    :param None/str/bytes password: Decrypt PDF file at initialization. If the
        password is None, the file will not be decrypted.
        Defaults to ``None``
    """

    def __init__(
        self,
        stream: Union[StrByteType, Path],
        strict: bool = False,
        password: Union[None, str, bytes] = None,
    ) -> None:
        self.strict = strict
        self.flattened_pages: Optional[List[PageObject]] = None
        self.resolved_objects: Dict[Tuple[Any, Any], Optional[PdfObject]] = {}
        self.xref_index = 0
        self._page_id2num: Optional[
            Dict[Any, Any]
        ] = None  # map page indirect_ref number to Page Number
        if hasattr(stream, "mode") and "b" not in stream.mode:  # type: ignore
            warnings.warn(
                "PdfReader stream/file object is not in binary mode. "
                "It may not be read correctly.",
                PdfReadWarning,
            )
        if isinstance(stream, (str, Path)):
            with open(stream, "rb") as fh:
                stream = BytesIO(fh.read())
        self.read(stream)
        self.stream = stream

        self._override_encryption = False
        self._encryption: Optional[Encryption] = None
        if self.is_encrypted:
            self._override_encryption = True
            # Some documents may not have a /ID, use two empty
            # byte strings instead. Solves
            # https://github.com/mstamy2/PyPDF2/issues/608
            id_entry = self.trailer.get(TK.ID)
            id1_entry = id_entry[0].get_object().original_bytes if id_entry else b""
            encrypt_entry = cast(DictionaryObject, self.trailer[TK.ENCRYPT].get_object())
            self._encryption = Encryption.read(encrypt_entry, id1_entry)

            # try empty password if no password provided
            pwd = password if password is not None else b""
            if self._encryption.verify(pwd) == PasswordType.NOT_DECRYPTED and password is not None:
                # raise if password provided
                raise PdfReadError("Wrong password")
            self._override_encryption = False
        else:
            if password is not None:
                raise PdfReadError("Not encrypted file")

    @property
    def pdf_header(self) -> str:
        loc = self.stream.tell()
        self.stream.seek(0, 0)
        pdf_file_version = self.stream.read(8).decode("utf-8")
        self.stream.seek(loc, 0)  # return to where it was
        return pdf_file_version

    @property
    def metadata(self) -> Optional[DocumentInformation]:
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
        retval.update(obj)  # type: ignore
        return retval

    def getDocumentInfo(self) -> Optional[DocumentInformation]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use the attribute :py:attr:`metadata` instead.
        """
        deprecate_with_replacement("getDocumentInfo", "metadata")
        return self.metadata

    @property
    def documentInfo(self) -> Optional[DocumentInformation]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use the attribute :py:attr:`metadata` instead.
        """
        deprecate_with_replacement("documentInfo", "metadata")
        return self.metadata

    @property
    def xmp_metadata(self) -> Optional[XmpInformation]:
        """
        XMP (Extensible Metadata Platform) data

        :return: a :class:`XmpInformation<xmp.XmpInformation>`
            instance that can be used to access XMP metadata from the document.
        :rtype: :class:`XmpInformation<xmp.XmpInformation>` or
            ``None`` if no metadata was found on the document root.
        """
        try:
            self._override_encryption = True
            return self.trailer[TK.ROOT].xmp_metadata  # type: ignore
        finally:
            self._override_encryption = False

    def getXmpMetadata(self) -> Optional[XmpInformation]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use the attribute :py:attr:`xmp_metadata` instead.
        """
        deprecate_with_replacement("getXmpMetadata", "xmp_metadata")
        return self.xmp_metadata

    @property
    def xmpMetadata(self) -> Optional[XmpInformation]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use the attribute :py:attr:`xmp_metadata` instead.
        """
        deprecate_with_replacement("xmpMetadata", "xmp_metadata")
        return self.xmp_metadata

    def _get_num_pages(self) -> int:
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
        if self.is_encrypted:
            return self.trailer[TK.ROOT]["/Pages"]["/Count"]  # type: ignore
        else:
            if self.flattened_pages is None:
                self._flatten()
            return len(self.flattened_pages)  # type: ignore

    def getNumPages(self) -> int:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :code:`len(reader.pages)` instead.
        """
        deprecate_with_replacement("reader.getNumPages", "len(reader.pages)")
        return self._get_num_pages()

    @property
    def numPages(self) -> int:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :code:`len(reader.pages)` instead.
        """
        deprecate_with_replacement("reader.numPages", "len(reader.pages)")
        return self._get_num_pages()

    def getPage(self, pageNumber: int) -> PageObject:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :code:`reader.pages[pageNumber]` instead.
        """
        deprecate_with_replacement(
            "reader.getPage(pageNumber)", "reader.pages[pageNumber]"
        )
        return self._get_page(pageNumber)

    def _get_page(self, page_number: int) -> PageObject:
        """
        Retrieves a page by number from this PDF file.

        :param int page_number: The page number to retrieve
            (pages begin at zero)
        :return: a :class:`PageObject<PyPDF2._page.PageObject>` instance.
        :rtype: :class:`PageObject<PyPDF2._page.PageObject>`
        """
        # ensure that we're not trying to access an encrypted PDF
        # assert not self.trailer.has_key(TK.ENCRYPT)
        if self.flattened_pages is None:
            self._flatten()
        assert self.flattened_pages is not None, "hint for mypy"
        return self.flattened_pages[page_number]

    @property
    def namedDestinations(self) -> Dict[str, Any]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`named_destinations` instead.
        """
        deprecate_with_replacement("namedDestinations", "named_destinations")
        return self.named_destinations

    @property
    def named_destinations(self) -> Dict[str, Any]:
        """
        A read-only dictionary which maps names to
        :class:`Destinations<PyPDF2.generic.Destination>`
        """
        return self._get_named_destinations()

    # A select group of relevant field attributes. For the complete list,
    # see section 8.6.2 of the PDF 1.7 reference.

    def get_fields(
        self,
        tree: Optional[TreeObject] = None,
        retval: Optional[Dict[Any, Any]] = None,
        fileobj: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
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
            catalog = cast(DictionaryObject, self.trailer[TK.ROOT])
            # get the AcroForm tree
            if "/AcroForm" in catalog:
                tree = cast(Optional[TreeObject], catalog["/AcroForm"])
            else:
                return None
        if tree is None:
            return retval

        self._check_kids(tree, retval, fileobj)
        for attr in field_attributes:
            if attr in tree:
                # Tree is a field
                self._build_field(tree, retval, fileobj, field_attributes)
                break

        if "/Fields" in tree:
            fields = cast(ArrayObject, tree["/Fields"])
            for f in fields:
                field = f.get_object()
                self._build_field(field, retval, fileobj, field_attributes)

        return retval

    def getFields(
        self,
        tree: Optional[TreeObject] = None,
        retval: Optional[Dict[Any, Any]] = None,
        fileobj: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_fields` instead.
        """
        deprecate_with_replacement("getFields", "get_fields")
        return self.get_fields(tree, retval, fileobj)

    def _build_field(
        self,
        field: Union[TreeObject, DictionaryObject],
        retval: Dict[Any, Any],
        fileobj: Any,
        field_attributes: Any,
    ) -> None:
        self._check_kids(field, retval, fileobj)
        try:
            key = field["/TM"]
        except KeyError:
            try:
                key = field["/T"]
            except KeyError:
                # Ignore no-name field for now
                return
        if fileobj:
            self._write_field(fileobj, field, field_attributes)
            fileobj.write("\n")
        retval[key] = Field(field)

    def _check_kids(
        self, tree: Union[TreeObject, DictionaryObject], retval: Any, fileobj: Any
    ) -> None:
        if PA.KIDS in tree:
            # recurse down the tree
            for kid in tree[PA.KIDS]:  # type: ignore
                self.get_fields(kid.get_object(), retval, fileobj)

    def _write_field(self, fileobj: Any, field: Any, field_attributes: Any) -> None:
        order = ("/TM", "/T", "/FT", PA.PARENT, "/TU", "/Ff", "/V", "/DV")
        for attr in order:
            attr_name = field_attributes[attr]
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

    def get_form_text_fields(self) -> Dict[str, Any]:
        """
        Retrieves form fields from the document with textual data.

        The key is the name of the form field, the value is the content of the
        field.

        If the document contains multiple form fields with the same name, the
        second and following will get the suffix _2, _3, ...
        """
        # Retrieve document form fields
        formfields = self.get_fields()
        if formfields is None:
            return {}
        return {
            formfields[field]["/T"]: formfields[field].get("/V")
            for field in formfields
            if formfields[field].get("/FT") == "/Tx"
        }

    def getFormTextFields(self) -> Dict[str, Any]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_form_text_fields` instead.
        """
        deprecate_with_replacement("getFormTextFields", "get_form_text_fields")
        return self.get_form_text_fields()

    def _get_named_destinations(
        self,
        tree: Union[TreeObject, None] = None,
        retval: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves the named destinations present in the document.

        :return: a dictionary which maps names to
            :class:`Destinations<PyPDF2.generic.Destination>`.
        :rtype: dict
        """
        if retval is None:
            retval = {}
            catalog = cast(DictionaryObject, self.trailer[TK.ROOT])

            # get the name tree
            if CA.DESTS in catalog:
                tree = cast(TreeObject, catalog[CA.DESTS])
            elif CA.NAMES in catalog:
                names = cast(DictionaryObject, catalog[CA.NAMES])
                if CA.DESTS in names:
                    tree = cast(TreeObject, names[CA.DESTS])

        if tree is None:
            return retval

        if PA.KIDS in tree:
            # recurse down the tree
            for kid in cast(ArrayObject, tree[PA.KIDS]):
                self._get_named_destinations(kid.get_object(), retval)

        # TABLE 3.33 Entries in a name tree node dictionary (PDF 1.7 specs)
        if CA.NAMES in tree:
            names = cast(DictionaryObject, tree[CA.NAMES])
            for i in range(0, len(names), 2):
                key = cast(str, names[i].get_object())
                value = names[i + 1].get_object()
                if isinstance(value, DictionaryObject) and "/D" in value:
                    value = value["/D"]
                dest = self._build_destination(key, value)  # type: ignore
                if dest is not None:
                    retval[key] = dest

        return retval

    def getNamedDestinations(
        self,
        tree: Union[TreeObject, None] = None,
        retval: Optional[Any] = None,
    ) -> Dict[str, Any]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`named_destinations` instead.
        """
        deprecate_with_replacement("getNamedDestinations", "named_destinations")
        return self._get_named_destinations(tree, retval)

    @property
    def outlines(self) -> OutlinesType:
        """
        Read-only property for outlines present in the document.

        :return: a nested list of :class:`Destinations<PyPDF2.generic.Destination>`.
        """
        return self._get_outlines()

    def _get_outlines(
        self, node: Optional[DictionaryObject] = None, outlines: Optional[Any] = None
    ) -> OutlinesType:
        if outlines is None:
            outlines = []
            catalog = cast(DictionaryObject, self.trailer[TK.ROOT])

            # get the outline dictionary and named destinations
            if CO.OUTLINES in catalog:
                try:
                    lines = cast(DictionaryObject, catalog[CO.OUTLINES])
                except PdfReadError:
                    # this occurs if the /Outlines object reference is incorrect
                    # for an example of such a file, see https://unglueit-files.s3.amazonaws.com/ebf/7552c42e9280b4476e59e77acc0bc812.pdf
                    # so continue to load the file without the Bookmarks
                    return outlines

                # TABLE 8.3 Entries in the outline dictionary
                if "/First" in lines:
                    node = cast(DictionaryObject, lines["/First"])
            self._namedDests = self._get_named_destinations()

        if node is None:
            return outlines

        # see if there are any more outlines
        while True:
            outline = self._build_outline(node)
            if outline:
                outlines.append(outline)

            # check for sub-outlines
            if "/First" in node:
                sub_outlines: List[Any] = []
                self._get_outlines(cast(DictionaryObject, node["/First"]), sub_outlines)
                if sub_outlines:
                    outlines.append(sub_outlines)

            if "/Next" not in node:
                break
            node = cast(DictionaryObject, node["/Next"])

        return outlines

    def getOutlines(
        self, node: Optional[DictionaryObject] = None, outlines: Optional[Any] = None
    ) -> OutlinesType:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`outlines` instead.
        """
        deprecate_with_replacement("getOutlines", "outlines")
        return self._get_outlines(node, outlines)

    def _get_page_number_by_indirect(
        self, indirect_ref: Union[None, int, NullObject, IndirectObject]
    ) -> int:
        """Generate _page_id2num"""
        if self._page_id2num is None:
            self._page_id2num = {
                x.indirect_ref.idnum: i for i, x in enumerate(self.pages)  # type: ignore
            }

        if indirect_ref is None or isinstance(indirect_ref, NullObject):
            return -1
        if isinstance(indirect_ref, int):
            idnum = indirect_ref
        else:
            idnum = indirect_ref.idnum
        assert self._page_id2num is not None, "hint for mypy"
        ret = self._page_id2num.get(idnum, -1)
        return ret

    def get_page_number(self, page: PageObject) -> int:
        """
        Retrieve page number of a given PageObject

        :param PageObject page: The page to get page number. Should be
            an instance of :class:`PageObject<PyPDF2._page.PageObject>`
        :return: the page number or -1 if page not found
        :rtype: int
        """
        return self._get_page_number_by_indirect(page.indirect_ref)

    def getPageNumber(self, page: PageObject) -> int:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_page_number` instead.
        """
        deprecate_with_replacement("getPageNumber", "get_page_number")
        return self.get_page_number(page)

    def get_destination_page_number(self, destination: Destination) -> int:
        """
        Retrieve page number of a given Destination object.

        :param Destination destination: The destination to get page number.
        :return: the page number or -1 if page not found
        :rtype: int
        """
        return self._get_page_number_by_indirect(destination.page)

    def getDestinationPageNumber(
        self, destination: Destination
    ) -> int:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_destination_page_number` instead.
        """
        deprecate_with_replacement(
            "getDestinationPageNumber", "get_destination_page_number"
        )
        return self.get_destination_page_number(destination)

    def _build_destination(
        self,
        title: str,
        array: List[Union[NumberObject, IndirectObject, NullObject, DictionaryObject]],
    ) -> Destination:
        page, typ = array[0:2]
        array = array[2:]
        try:
            return Destination(title, page, typ, *array)  # type: ignore
        except PdfReadError:
            warnings.warn(f"Unknown destination: {title} {array}", PdfReadWarning)
            if self.strict:
                raise
            else:
                # create a link to first Page
                tmp = self.pages[0].indirect_ref
                indirect_ref = NullObject() if tmp is None else tmp
                return Destination(
                    title, indirect_ref, TextStringObject("/Fit")  # type: ignore
                )

    def _build_outline(self, node: DictionaryObject) -> Optional[Destination]:
        dest, title, outline = None, None, None

        if "/A" in node and "/Title" in node:
            # Action, section 8.5 (only type GoTo supported)
            title = node["/Title"]
            action = cast(DictionaryObject, node["/A"])
            action_type = cast(NameObject, action["/S"])
            if action_type == "/GoTo":
                dest = action["/D"]
        elif "/Dest" in node and "/Title" in node:
            # Destination, section 8.2.1
            title = node["/Title"]
            dest = node["/Dest"]

        # if destination found, then create outline
        if dest:
            if isinstance(dest, ArrayObject):
                outline = self._build_destination(title, dest)  # type: ignore
            elif isinstance(dest, str) and dest in self._namedDests:
                outline = self._namedDests[dest]
                outline[NameObject("/Title")] = title  # type: ignore
            else:
                raise PdfReadError(f"Unexpected destination {dest!r}")
        return outline

    @property
    def pages(self) -> _VirtualList:
        """Read-only property that emulates a list of :py:class:`Page<PyPDF2._page.Page>` objects."""
        return _VirtualList(self._get_num_pages, self._get_page)

    @property
    def page_layout(self) -> Optional[str]:
        """
        Get the page layout.

        :return: Page layout currently being used.
        :rtype: ``str``, ``None`` if not specified

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
        trailer = cast(DictionaryObject, self.trailer[TK.ROOT])
        if CD.PAGE_LAYOUT in trailer:
            return cast(NameObject, trailer[CD.PAGE_LAYOUT])
        return None

    def getPageLayout(self) -> Optional[str]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement("getPageLayout", "page_layout")
        return self.page_layout

    @property
    def pageLayout(self) -> Optional[str]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_layout` instead.
        """
        deprecate_with_replacement("pageLayout", "page_layout")
        return self.page_layout

    @property
    def page_mode(self) -> Optional[PagemodeType]:
        """
        Get the page mode.

        :return: Page mode currently being used.
        :rtype: ``str``, ``None`` if not specified

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
        try:
            return self.trailer[TK.ROOT]["/PageMode"]  # type: ignore
        except KeyError:
            return None

    def getPageMode(self) -> Optional[PagemodeType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("getPageMode", "page_mode")
        return self.page_mode

    @property
    def pageMode(self) -> Optional[PagemodeType]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`page_mode` instead.
        """
        deprecate_with_replacement("pageMode", "page_mode")
        return self.page_mode

    def _flatten(
        self,
        pages: Union[None, DictionaryObject, PageObject] = None,
        inherit: Optional[Dict[str, Any]] = None,
        indirect_ref: Optional[IndirectObject] = None,
    ) -> None:
        inheritable_page_attributes = (
            NameObject(PG.RESOURCES),
            NameObject(PG.MEDIABOX),
            NameObject(PG.CROPBOX),
            NameObject(PG.ROTATE),
        )
        if inherit is None:
            inherit = {}
        if pages is None:
            # Fix issue 327: set flattened_pages attribute only for
            # decrypted file
            catalog = self.trailer[TK.ROOT].get_object()
            pages = catalog["/Pages"].get_object()  # type: ignore
            self.flattened_pages = []

        t = "/Pages"
        if PA.TYPE in pages:
            t = pages[PA.TYPE]  # type: ignore

        if t == "/Pages":
            for attr in inheritable_page_attributes:
                if attr in pages:
                    inherit[attr] = pages[attr]
            for page in pages[PA.KIDS]:  # type: ignore
                addt = {}
                if isinstance(page, IndirectObject):
                    addt["indirect_ref"] = page
                self._flatten(page.get_object(), inherit, **addt)
        elif t == "/Page":
            for attr_in, value in list(inherit.items()):
                # if the page has it's own value, it does not inherit the
                # parent's value:
                if attr_in not in pages:
                    pages[attr_in] = value
            page_obj = PageObject(self, indirect_ref)
            page_obj.update(pages)

            # TODO: Could flattened_pages be None at this point?
            self.flattened_pages.append(page_obj)  # type: ignore

    def _get_object_from_stream(
        self, indirect_reference: IndirectObject
    ) -> Union[int, PdfObject, str]:
        # indirect reference to object in object stream
        # read the entire object stream into memory
        stmnum, idx = self.xref_objStm[indirect_reference.idnum]
        obj_stm: EncodedStreamObject = IndirectObject(stmnum, 0, self).get_object()  # type: ignore
        # This is an xref to a stream, so its type better be a stream
        assert obj_stm["/Type"] == "/ObjStm"
        # /N is the number of indirect objects in the stream
        assert idx < obj_stm["/N"]
        stream_data = BytesIO(b_(obj_stm.get_data()))  # type: ignore
        for i in range(obj_stm["/N"]):  # type: ignore
            read_non_whitespace(stream_data)
            stream_data.seek(-1, 1)
            objnum = NumberObject.read_from_stream(stream_data)
            read_non_whitespace(stream_data)
            stream_data.seek(-1, 1)
            offset = NumberObject.read_from_stream(stream_data)
            read_non_whitespace(stream_data)
            stream_data.seek(-1, 1)
            if objnum != indirect_reference.idnum:
                # We're only interested in one object
                continue
            if self.strict and idx != i:
                raise PdfReadError("Object is in wrong index.")
            stream_data.seek(int(obj_stm["/First"] + offset), 0)  # type: ignore

            # to cope with some case where the 'pointer' is on a white space
            read_non_whitespace(stream_data)
            stream_data.seek(-1, 1)

            try:
                obj = read_object(stream_data, self)
            except PdfStreamError as exc:
                # Stream object cannot be read. Normally, a critical error, but
                # Adobe Reader doesn't complain, so continue (in strict mode?)
                warnings.warn(
                    f"Invalid stream (index {i}) within object "
                    f"{indirect_reference.idnum} {indirect_reference.generation}: "
                    f"{exc}",
                    PdfReadWarning,
                )

                if self.strict:
                    raise PdfReadError(f"Can't read object stream: {exc}")
                # Replace with null. Hopefully it's nothing important.
                obj = NullObject()
            return obj

        if self.strict:
            raise PdfReadError("This is a fatal error in strict mode.")
        return NullObject()

    def get_object(self, indirect_reference: IndirectObject) -> Optional[PdfObject]:
        retval = self.cache_get_indirect_object(
            indirect_reference.generation, indirect_reference.idnum
        )
        if retval is not None:
            return retval
        if (
            indirect_reference.generation == 0
            and indirect_reference.idnum in self.xref_objStm
        ):
            retval = self._get_object_from_stream(indirect_reference)  # type: ignore
        elif (
            indirect_reference.generation in self.xref
            and indirect_reference.idnum in self.xref[indirect_reference.generation]
        ):
            start = self.xref[indirect_reference.generation][indirect_reference.idnum]
            self.stream.seek(start, 0)
            idnum, generation = self.read_object_header(self.stream)
            if idnum != indirect_reference.idnum and self.xref_index:
                # Xref table probably had bad indexes due to not being zero-indexed
                if self.strict:
                    raise PdfReadError(
                        f"Expected object ID ({indirect_reference.idnum} {indirect_reference.generation}) "
                        f"does not match actual ({idnum} {generation}); "
                        "xref table not zero-indexed."
                    )
                else:
                    pass  # xref table is corrected in non-strict mode
            elif idnum != indirect_reference.idnum and self.strict:
                # some other problem
                raise PdfReadError(
                    f"Expected object ID ({indirect_reference.idnum} "
                    f"{indirect_reference.generation}) does not match actual "
                    f"({idnum} {generation})."
                )
            if self.strict:
                assert generation == indirect_reference.generation
            retval = read_object(self.stream, self)  # type: ignore

            # override encryption is used for the /Encrypt dictionary
            if not self._override_encryption and self._encryption is not None:
                # if we don't have the encryption key:
                if not self._encryption.is_decrypted():
                    raise PdfReadError("File has not been decrypted")
                # otherwise, decrypt here...
                retval = cast(PdfObject, retval)
                retval = self._encryption.decrypt_object(
                    retval, indirect_reference.idnum, indirect_reference.generation
                )
        else:
            warnings.warn(
                f"Object {indirect_reference.idnum} {indirect_reference.generation} "
                "not defined.",
                PdfReadWarning,
            )
            if self.strict:
                raise PdfReadError("Could not find object.")
        self.cache_indirect_object(
            indirect_reference.generation, indirect_reference.idnum, retval
        )
        return retval

    def getObject(
        self, indirectReference: IndirectObject
    ) -> Optional[PdfObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`get_object` instead.
        """
        deprecate_with_replacement("getObject", "get_object")
        return self.get_object(indirectReference)

    def read_object_header(self, stream: StreamType) -> Tuple[int, int]:
        # Should never be necessary to read out whitespace, since the
        # cross-reference table should put us in the right spot to read the
        # object header.  In reality... some files have stupid cross reference
        # tables that are off by whitespace bytes.
        extra = False
        skip_over_comment(stream)
        extra |= skip_over_whitespace(stream)
        stream.seek(-1, 1)
        idnum = read_until_whitespace(stream)
        extra |= skip_over_whitespace(stream)
        stream.seek(-1, 1)
        generation = read_until_whitespace(stream)
        extra |= skip_over_whitespace(stream)
        stream.seek(-1, 1)

        # although it's not used, it might still be necessary to read
        _obj = stream.read(3)  # noqa: F841

        read_non_whitespace(stream)
        stream.seek(-1, 1)
        if extra and self.strict:
            warnings.warn(
                f"Superfluous whitespace found in object header {idnum} {generation}",  # type: ignore
                PdfReadWarning,
            )
        return int(idnum), int(generation)

    def readObjectHeader(
        self, stream: StreamType
    ) -> Tuple[int, int]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`read_object_header` instead.
        """
        deprecate_with_replacement("readObjectHeader", "read_object_header")
        return self.read_object_header(stream)

    def cache_get_indirect_object(
        self, generation: int, idnum: int
    ) -> Optional[PdfObject]:
        return self.resolved_objects.get((generation, idnum))

    def cacheGetIndirectObject(
        self, generation: int, idnum: int
    ) -> Optional[PdfObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`cache_get_indirect_object` instead.
        """
        deprecate_with_replacement(
            "cacheGetIndirectObject", "cache_get_indirect_object"
        )
        return self.cache_get_indirect_object(generation, idnum)

    def cache_indirect_object(
        self, generation: int, idnum: int, obj: Optional[PdfObject]
    ) -> Optional[PdfObject]:
        if (generation, idnum) in self.resolved_objects:
            msg = f"Overwriting cache for {generation} {idnum}"
            if self.strict:
                raise PdfReadError(msg)
            else:
                warnings.warn(msg)
        self.resolved_objects[(generation, idnum)] = obj
        return obj

    def cacheIndirectObject(
        self, generation: int, idnum: int, obj: Optional[PdfObject]
    ) -> Optional[PdfObject]:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :meth:`cache_indirect_object` instead.
        """
        deprecate_with_replacement("cacheIndirectObject", "cache_indirect_object")
        return self.cache_indirect_object(generation, idnum, obj)

    def read(self, stream: StreamType) -> None:
        # start at the end:
        stream.seek(0, os.SEEK_END)
        if not stream.tell():
            raise PdfReadError("Cannot read an empty file")
        if self.strict:
            stream.seek(0, os.SEEK_SET)
            header_byte = stream.read(5)
            if header_byte != b"%PDF-":
                raise PdfReadError(
                    f"PDF starts with '{header_byte.decode('utf8')}', "
                    "but '%PDF-' expected"
                )
            stream.seek(0, os.SEEK_END)
        last_mb = stream.tell() - 1024 * 1024 + 1  # offset of last MB of stream
        line = b""
        while line[:5] != b"%%EOF":
            if stream.tell() < last_mb:
                raise PdfReadError("EOF marker not found")
            line = read_previous_line(stream)

        startxref = self._find_startxref_pos(stream)

        # check and eventually correct the startxref only in not strict
        xref_issue_nr = self._get_xref_issues(stream, startxref)
        if xref_issue_nr != 0:
            if self.strict and xref_issue_nr:
                raise PdfReadError("Broken xref table")
            else:
                warnings.warn(
                    f"incorrect startxref pointer({xref_issue_nr})", PdfReadWarning
                )

        # read all cross reference tables and their trailers
        self.xref: Dict[int, Dict[Any, Any]] = {}
        self.xref_objStm: Dict[int, Tuple[Any, Any]] = {}
        self.trailer = DictionaryObject()
        while True:
            # load the xref table
            stream.seek(startxref, 0)
            x = stream.read(1)
            if x == b"x":
                self._read_standard_xref_table(stream)
                read_non_whitespace(stream)
                stream.seek(-1, 1)
                new_trailer = cast(Dict[str, Any], read_object(stream, self))
                for key, value in new_trailer.items():
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
                    startxref = cast(int, xrefstream["/Prev"])
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
                xref_loc = tmp.find(b"xref")
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
        if self.xref_index and not self.strict:
            loc = stream.tell()
            for gen, xref_entry in self.xref.items():
                if gen == 65535:
                    continue
                for id in xref_entry:
                    stream.seek(xref_entry[id], 0)
                    try:
                        pid, _pgen = self.read_object_header(stream)
                    except ValueError:
                        break
                    if pid == id - self.xref_index:
                        self._zero_xref(gen)
                        break
                    # if not, then either it's just plain wrong, or the
                    # non-zero-index is actually correct
            stream.seek(loc, 0)  # return to where it was

    def _find_startxref_pos(self, stream: StreamType) -> int:
        """Find startxref entry - the location of the xref table"""
        line = read_previous_line(stream)
        try:
            startxref = int(line)
        except ValueError:
            # 'startxref' may be on the same line as the location
            if not line.startswith(b"startxref"):
                raise PdfReadError("startxref not found")
            startxref = int(line[9:].strip())
            warnings.warn("startxref on same line as offset", PdfReadWarning)
        else:
            line = read_previous_line(stream)
            if line[:9] != b"startxref":
                raise PdfReadError("startxref not found")
        return startxref

    def _read_standard_xref_table(self, stream: StreamType) -> None:
        # standard cross-reference table
        ref = stream.read(4)
        if ref[:3] != b"ref":
            raise PdfReadError("xref table read error")
        read_non_whitespace(stream)
        stream.seek(-1, 1)
        firsttime = True  # check if the first time looking at the xref table
        while True:
            num = cast(int, read_object(stream, self))
            if firsttime and num != 0:
                self.xref_index = num
                if self.strict:
                    warnings.warn(
                        "Xref table not zero-indexed. ID numbers for objects will be corrected.",
                        PdfReadWarning,
                    )
                    # if table not zero indexed, could be due to error from when PDF was created
                    # which will lead to mismatched indices later on, only warned and corrected if self.strict==True
            firsttime = False
            read_non_whitespace(stream)
            stream.seek(-1, 1)
            size = cast(int, read_object(stream, self))
            read_non_whitespace(stream)
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
                while line[0] in b"\x0D\x0A":
                    stream.seek(-20 + 1, 1)
                    line = stream.read(20)

                # On the other hand, some malformed PDF files
                # use a single character EOL without a preceding
                # space.  Detect that case, and seek the stream
                # back one character.  (0-9 means we've bled into
                # the next xref entry, t means we've bled into the
                # text "trailer"):
                if line[-1] in b"0123456789t":
                    stream.seek(-1, 1)

                offset_b, generation_b = line[:16].split(b" ")
                offset, generation = int(offset_b), int(generation_b)
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
            read_non_whitespace(stream)
            stream.seek(-1, 1)
            trailertag = stream.read(7)
            if trailertag != b"trailer":
                # more xrefs!
                stream.seek(-7, 1)
            else:
                break

    def _read_pdf15_xref_stream(
        self, stream: StreamType
    ) -> Union[ContentStream, EncodedStreamObject, DecodedStreamObject]:
        # PDF 1.5+ Cross-Reference Stream
        stream.seek(-1, 1)
        idnum, generation = self.read_object_header(stream)
        xrefstream = cast(ContentStream, read_object(stream, self))
        assert xrefstream["/Type"] == "/XRef"
        self.cache_indirect_object(generation, idnum, xrefstream)
        stream_data = BytesIO(b_(xrefstream.get_data()))
        # Index pairs specify the subsections in the dictionary. If
        # none create one subsection that spans everything.
        idx_pairs = xrefstream.get("/Index", [0, xrefstream.get("/Size")])
        entry_sizes = cast(Dict[Any, Any], xrefstream.get("/W"))
        assert len(entry_sizes) >= 3
        if self.strict and len(entry_sizes) > 3:
            raise PdfReadError(f"Too many entry sizes: {entry_sizes}")

        def get_entry(i: int) -> Union[int, Tuple[int, ...]]:
            # Reads the correct number of bytes for each entry. See the
            # discussion of the W parameter in PDF spec table 17.
            if entry_sizes[i] > 0:
                d = stream_data.read(entry_sizes[i])
                return convert_to_int(d, entry_sizes[i])

            # PDF Spec Table 17: A value of zero for an element in the
            # W array indicates...the default value shall be used
            if i == 0:
                return 1  # First value defaults to 1
            else:
                return 0

        def used_before(num: int, generation: Union[int, Tuple[int, ...]]) -> bool:
            # We move backwards through the xrefs, don't replace any.
            return num in self.xref.get(generation, []) or num in self.xref_objStm  # type: ignore

        # Iterate through each subsection
        self._read_xref_subsections(idx_pairs, get_entry, used_before)
        return xrefstream

    @staticmethod
    def _get_xref_issues(stream: StreamType, startxref: int) -> int:
        """Return an int which indicates an issue. 0 means there is no issue."""
        stream.seek(startxref - 1, 0)  # -1 to check character before
        line = stream.read(1)
        if line not in b"\r\n \t":
            return 1
        line = stream.read(4)
        if line != b"xref":
            # not an xref so check if it is an XREF object
            line = b""
            while line in b"0123456789 \t":
                line = stream.read(1)
                if line == b"":
                    return 2
            line += stream.read(2)  # 1 char already read, +2 to check "obj"
            if line.lower() != b"obj":
                return 3
            # while stream.read(1) in b" \t\r\n":
            #     pass
            # line = stream.read(256)  # check that it is xref obj
            # if b"/xref" not in line.lower():
            #     return 4
        return 0

    def _rebuild_xref_table(self, stream: StreamType) -> None:
        self.xref = {}
        stream.seek(0, 0)
        f_ = stream.read(-1)

        for m in re.finditer(rb"[\r\n \t][ \t]*(\d+)[ \t]+(\d+)[ \t]+obj", f_):
            idnum = int(m.group(1))
            generation = int(m.group(2))
            if generation not in self.xref:
                self.xref[generation] = {}
            self.xref[generation][idnum] = m.start(1)
        stream.seek(0, 0)
        for m in re.finditer(rb"[\r\n \t][ \t]*trailer[\r\n \t]*(<<)", f_):
            stream.seek(m.start(1), 0)
            new_trailer = cast(Dict[Any, Any], read_object(stream, self))
            # Here, we are parsing the file from start to end, the new data have to erase the existing.
            for key, value in list(new_trailer.items()):
                self.trailer[key] = value

    def _read_xref_subsections(
        self,
        idx_pairs: List[int],
        get_entry: Callable[[int], Union[int, Tuple[int, ...]]],
        used_before: Callable[[int, Union[int, Tuple[int, ...]]], bool],
    ) -> None:
        last_end = 0
        for start, size in self._pairs(idx_pairs):
            # The subsections must increase
            assert start >= last_end
            last_end = start + size
            for num in range(start, start + size):
                # The first entry is the type
                xref_type = get_entry(0)
                # The rest of the elements depend on the xref_type
                if xref_type == 0:
                    # linked list of free objects
                    next_free_object = get_entry(1)  # noqa: F841
                    next_generation = get_entry(2)  # noqa: F841
                elif xref_type == 1:
                    # objects that are in use but are not compressed
                    byte_offset = get_entry(1)
                    generation = get_entry(2)
                    if generation not in self.xref:
                        self.xref[generation] = {}  # type: ignore
                    if not used_before(num, generation):
                        self.xref[generation][num] = byte_offset  # type: ignore
                elif xref_type == 2:
                    # compressed objects
                    objstr_num = get_entry(1)
                    obstr_idx = get_entry(2)
                    generation = 0  # PDF spec table 18, generation is 0
                    if not used_before(num, generation):
                        self.xref_objStm[num] = (objstr_num, obstr_idx)
                elif self.strict:
                    raise PdfReadError(f"Unknown xref type: {xref_type}")

    def _zero_xref(self, generation: int) -> None:
        self.xref[generation] = {
            k - self.xref_index: v for (k, v) in list(self.xref[generation].items())
        }

    def _pairs(self, array: List[int]) -> Iterable[Tuple[int, int]]:
        i = 0
        while True:
            yield array[i], array[i + 1]
            i += 2
            if (i + 1) >= len(array):
                break

    def read_next_end_line(
        self, stream: StreamType, limit_offset: int = 0
    ) -> bytes:  # pragma: no cover
        """.. deprecated:: 2.1.0"""
        deprecate_no_replacement("read_next_end_line", removed_in="4.0.0")
        line_parts = []
        while True:
            # Prevent infinite loops in malformed PDFs
            if stream.tell() == 0 or stream.tell() == limit_offset:
                raise PdfReadError("Could not read malformed PDF file")
            x = stream.read(1)
            if stream.tell() < 2:
                raise PdfReadError("EOL marker not found")
            stream.seek(-2, 1)
            if x in (b"\n", b"\r"):  # \n = LF; \r = CR
                crlf = False
                while x in (b"\n", b"\r"):
                    x = stream.read(1)
                    if x in (b"\n", b"\r"):  # account for CR+LF
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

    def readNextEndLine(
        self, stream: StreamType, limit_offset: int = 0
    ) -> bytes:  # pragma: no cover
        """.. deprecated:: 1.28.0"""
        deprecate_no_replacement("readNextEndLine")
        return self.read_next_end_line(stream, limit_offset)

    def decrypt(self, password: Union[str, bytes]) -> PasswordType:
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
        :return: `PasswordType`.
        :rtype: int
            method.
        """
        if not self._encryption:
            raise PdfReadError("Not encrypted file")
        # TODO: raise Exception for wrong password
        return self._encryption.verify(password)

    def decode_permissions(self, permissions_code: int) -> Dict[str, bool]:
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

    @property
    def is_encrypted(self) -> bool:
        """
        Read-only boolean property showing whether this PDF file is encrypted.
        Note that this property, if true, will remain true even after the
        :meth:`decrypt()<PyPDF2.PdfReader.decrypt>` method is called.
        """
        return TK.ENCRYPT in self.trailer

    def getIsEncrypted(self) -> bool:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`is_encrypted` instead.
        """
        deprecate_with_replacement("getIsEncrypted", "is_encrypted")
        return self.is_encrypted

    @property
    def isEncrypted(self) -> bool:  # pragma: no cover
        """
        .. deprecated:: 1.28.0

            Use :py:attr:`is_encrypted` instead.
        """
        deprecate_with_replacement("isEncrypted", "is_encrypted")
        return self.is_encrypted


class PdfFileReader(PdfReader):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        deprecate_with_replacement("PdfFileReader", "PdfReader")
        if "strict" not in kwargs and len(args) < 2:
            kwargs["strict"] = True  # maintain the default
        super().__init__(*args, **kwargs)
