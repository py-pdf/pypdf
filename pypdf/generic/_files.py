from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, cast

from pypdf._utils import format_iso8824_date, parse_iso8824_date
from pypdf.constants import CatalogAttributes as CA
from pypdf.constants import FileSpecificationDictionaryEntries
from pypdf.constants import PageAttributes as PG
from pypdf.errors import PdfReadError
from pypdf.generic import (
    ArrayObject,
    ByteStringObject,
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
    NullObject,
    NumberObject,
    StreamObject,
    TextStringObject,
    is_null_or_none,
)

if TYPE_CHECKING:
    import datetime
    from collections.abc import Generator

    from pypdf._writer import PdfWriter


class EmbeddedFile:
    """
    Container holding the information on an embedded file.

    Attributes are evaluated lazily if possible.

    Further information on embedded files can be found in section 7.11 of the PDF 2.0 specification.
    """
    def __init__(self, name: str, pdf_object: DictionaryObject) -> None:
        """
        Args:
            name: The (primary) name as provided in the name tree.
            pdf_object: The corresponding PDF object to allow retrieving further data.
        """
        self._name = name
        self.pdf_object = pdf_object

    @property
    def name(self) -> str:
        """The (primary) name of the embedded file as provided in the name tree."""
        return self._name

    @classmethod
    def _create_new(cls, writer: PdfWriter, name: str, content: str | bytes) -> EmbeddedFile:
        """
        Create a new embedded file and add it to the PdfWriter.

        Args:
            writer: The PdfWriter instance to add the embedded file to.
            name: The filename to display.
            content: The data in the file.

        Returns:
            EmbeddedFile instance for the newly created embedded file.
        """
        # Convert string content to bytes if needed
        if isinstance(content, str):
            content = content.encode("latin-1")

        # Create the file entry (the actual embedded file stream)
        file_entry = DecodedStreamObject()
        file_entry.set_data(content)
        file_entry.update({NameObject(PG.TYPE): NameObject("/EmbeddedFile")})

        # Create the /EF entry
        ef_entry = DictionaryObject()
        ef_entry.update({NameObject("/F"): writer._add_object(file_entry)})

        # Create the filespec dictionary
        from pypdf.generic import create_string_object  # noqa: PLC0415
        filespec = DictionaryObject()
        filespec.update(
            {
                NameObject(PG.TYPE): NameObject("/Filespec"),
                NameObject(FileSpecificationDictionaryEntries.F): create_string_object(name),
                NameObject(FileSpecificationDictionaryEntries.EF): ef_entry,
            }
        )

        # Add to the catalog's names tree
        if CA.NAMES not in writer._root_object:
            writer._root_object[NameObject(CA.NAMES)] = writer._add_object(DictionaryObject())

        names_dict = cast(DictionaryObject, writer._root_object[CA.NAMES])
        if "/EmbeddedFiles" not in names_dict:
            embedded_files_names_dictionary = DictionaryObject(
                {NameObject(CA.NAMES): ArrayObject()}
            )
            names_dict[NameObject("/EmbeddedFiles")] = writer._add_object(embedded_files_names_dictionary)
        else:
            embedded_files_names_dictionary = cast(DictionaryObject, names_dict["/EmbeddedFiles"])

        # Add the name and filespec to the names array
        names_array = cast(ArrayObject, embedded_files_names_dictionary[CA.NAMES])
        names_array.extend([create_string_object(name), filespec])

        # Return an EmbeddedFile instance
        return cls(name=name, pdf_object=filespec)

    @property
    def alternative_name(self) -> str | None:
        """Retrieve the alternative name (file specification)."""
        for key in [FileSpecificationDictionaryEntries.UF, FileSpecificationDictionaryEntries.F]:
            # PDF 2.0 reference, table 43:
            #   > A PDF reader shall use the value of the UF key, when present, instead of the F key.
            if key in self.pdf_object:
                value = self.pdf_object[key].get_object()
                if not is_null_or_none(value):
                    return cast(str, value)
        return None

    @alternative_name.setter
    def alternative_name(self, value: TextStringObject | None) -> None:
        """Set the alternative name (file specification)."""
        if value is None:
            if FileSpecificationDictionaryEntries.UF in self.pdf_object:
                self.pdf_object[NameObject(FileSpecificationDictionaryEntries.UF)] = NullObject()
            if FileSpecificationDictionaryEntries.F in self.pdf_object:
                self.pdf_object[NameObject(FileSpecificationDictionaryEntries.F)] = NullObject()
        else:
            if FileSpecificationDictionaryEntries.UF in self.pdf_object:
                self.pdf_object[NameObject(FileSpecificationDictionaryEntries.UF)] = value
            if FileSpecificationDictionaryEntries.F in self.pdf_object:
                self.pdf_object[NameObject(FileSpecificationDictionaryEntries.F)] = value

    @property
    def description(self) -> str | None:
        """Retrieve the description."""
        value = self.pdf_object.get(FileSpecificationDictionaryEntries.DESC)
        if is_null_or_none(value):
            return None
        return value

    @description.setter
    def description(self, value: TextStringObject | None) -> None:
        """Set the description."""
        if value is None:
            self.pdf_object[NameObject(FileSpecificationDictionaryEntries.DESC)] = NullObject()
        else:
            self.pdf_object[NameObject(FileSpecificationDictionaryEntries.DESC)] = value

    @property
    def associated_file_relationship(self) -> str:
        """Retrieve the relationship of the referring document to this embedded file."""
        return self.pdf_object.get("/AFRelationship", "/Unspecified")

    @associated_file_relationship.setter
    def associated_file_relationship(self, value: NameObject) -> None:
        """Set the relationship of the referring document to this embedded file."""
        self.pdf_object[NameObject("/AFRelationship")] = value

    @property
    def _embedded_file(self) -> StreamObject:
        """Retrieve the actual embedded file stream."""
        if "/EF" not in self.pdf_object:
            raise PdfReadError(f"/EF entry not found: {self.pdf_object}")
        ef = cast(DictionaryObject, self.pdf_object["/EF"])
        for key in [FileSpecificationDictionaryEntries.UF, FileSpecificationDictionaryEntries.F]:
            if key in ef:
                return cast(StreamObject, ef[key].get_object())
        raise PdfReadError(f"No /(U)F key found in file dictionary: {ef}")

    @property
    def _params(self) -> DictionaryObject:
        """Retrieve the file-specific parameters."""
        return self._embedded_file.get("/Params", DictionaryObject()).get_object()

    @cached_property
    def _ensure_params(self) -> DictionaryObject:
        """Ensure the /Params dictionary exists and return it."""
        embedded_file = self._embedded_file
        if "/Params" not in embedded_file:
            embedded_file[NameObject("/Params")] = DictionaryObject()
        return cast(DictionaryObject, embedded_file["/Params"])

    @property
    def subtype(self) -> str | None:
        """Retrieve the subtype. This is a MIME media type, prefixed by a slash."""
        value = self._embedded_file.get("/Subtype")
        if is_null_or_none(value):
            return None
        return value

    @subtype.setter
    def subtype(self, value: NameObject | None) -> None:
        """Set the subtype. This should be a MIME media type, prefixed by a slash."""
        embedded_file = self._embedded_file
        if value is None:
            embedded_file[NameObject("/Subtype")] = NullObject()
        else:
            embedded_file[NameObject("/Subtype")] = value

    @property
    def content(self) -> bytes:
        """Retrieve the actual file content."""
        return self._embedded_file.get_data()

    @content.setter
    def content(self, value: str | bytes) -> None:
        """Set the file content."""
        if isinstance(value, str):
            value = value.encode("latin-1")
        self._embedded_file.set_data(value)

    @property
    def size(self) -> int | None:
        """Retrieve the size of the uncompressed file in bytes."""
        value = self._params.get("/Size")
        if is_null_or_none(value):
            return None
        return value

    @size.setter
    def size(self, value: NumberObject | None) -> None:
        """Set the size of the uncompressed file in bytes."""
        params = self._ensure_params
        if value is None:
            params[NameObject("/Size")] = NullObject()
        else:
            params[NameObject("/Size")] = value

    @property
    def creation_date(self) -> datetime.datetime | None:
        """Retrieve the file creation datetime."""
        return parse_iso8824_date(self._params.get("/CreationDate"))

    @creation_date.setter
    def creation_date(self, value: datetime.datetime | None) -> None:
        """Set the file creation datetime."""
        params = self._ensure_params
        if value is None:
            params[NameObject("/CreationDate")] = NullObject()
        else:
            date_str = format_iso8824_date(value)
            params[NameObject("/CreationDate")] = TextStringObject(date_str)

    @property
    def modification_date(self) -> datetime.datetime | None:
        """Retrieve the datetime of the last file modification."""
        return parse_iso8824_date(self._params.get("/ModDate"))

    @modification_date.setter
    def modification_date(self, value: datetime.datetime | None) -> None:
        """Set the datetime of the last file modification."""
        params = self._ensure_params
        if value is None:
            params[NameObject("/ModDate")] = NullObject()
        else:
            date_str = format_iso8824_date(value)
            params[NameObject("/ModDate")] = TextStringObject(date_str)

    @property
    def checksum(self) -> bytes | None:
        """Retrieve the MD5 checksum of the (uncompressed) file."""
        value = self._params.get("/CheckSum")
        if is_null_or_none(value):
            return None
        return value

    @checksum.setter
    def checksum(self, value: ByteStringObject | None) -> None:
        """Set the MD5 checksum of the (uncompressed) file."""
        params = self._ensure_params
        if value is None:
            params[NameObject("/CheckSum")] = NullObject()
        else:
            params[NameObject("/CheckSum")] = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"

    @classmethod
    def _load_from_names(cls, names: ArrayObject) -> Generator[EmbeddedFile]:
        """
        Convert the given name tree into class instances.

        Args:
            names: The name tree to load the data from.

        Returns:
            Iterable of class instances for the files found.
        """
        # This is a name tree of the format [name_1, reference_1, name_2, reference_2, ...]
        for i, name in enumerate(names):
            if not isinstance(name, str):
                # Skip plain strings and retrieve them as `direct_name` by index.
                file_dictionary = name.get_object()
                direct_name = names[i - 1].get_object()
                yield EmbeddedFile(name=direct_name, pdf_object=file_dictionary)

    @classmethod
    def _load(cls, catalog: DictionaryObject) -> Generator[EmbeddedFile]:
        """
        Load the embedded files for the given document catalog.

        This method and its signature are considered internal API and thus not exposed publicly for now.

        Args:
            catalog: The document catalog to load from.

        Returns:
            Iterable of class instances for the files found.
        """
        try:
            container = cast(
                DictionaryObject,
                cast(DictionaryObject, catalog["/Names"])["/EmbeddedFiles"],
            )
        except KeyError:
            return

        if "/Kids" in container:
            for kid in cast(ArrayObject, container["/Kids"].get_object()):
                # There might be further (nested) kids here.
                # Wait for an example before evaluating an implementation.
                kid = kid.get_object()
                if "/Names" in kid:
                    yield from cls._load_from_names(cast(ArrayObject, kid["/Names"]))
        if "/Names" in container:
            yield from cls._load_from_names(cast(ArrayObject, container["/Names"]))
