import hashlib
from typing import Any, Callable, Optional, Union

from .._utils import (
    StreamType,
    b_,
    deprecate_with_replacement,
    hex_str,
    read_non_whitespace,
)
from ..errors import STREAM_TRUNCATED_PREMATURELY, PdfReadError, PdfStreamError


class PdfObject:
    # function for calculating a hash value
    hash_func: Callable[..., "hashlib._Hash"] = hashlib.sha1

    def hash_value_data(self) -> bytes:
        return ("%s" % self).encode()

    def hash_value(self) -> bytes:
        return (
            "%s:%s"
            % (
                self.__class__.__name__,
                self.hash_func(self.hash_value_data()).hexdigest(),
            )
        ).encode()

    def get_object(self) -> Optional["PdfObject"]:
        """Resolve indirect references."""
        return self

    def getObject(self) -> Optional["PdfObject"]:  # pragma: no cover
        deprecate_with_replacement("getObject", "get_object")
        return self.get_object()

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        raise NotImplementedError


class IndirectObject(PdfObject):
    def __init__(self, idnum: int, generation: int, pdf: Any) -> None:  # PdfReader
        self.idnum = idnum
        self.generation = generation
        self.pdf = pdf

    def get_object(self) -> Optional[PdfObject]:
        obj = self.pdf.get_object(self)
        if obj is None:
            return None
        return obj.get_object()

    def __repr__(self) -> str:
        return f"IndirectObject({self.idnum!r}, {self.generation!r}, {id(self.pdf)})"

    def __eq__(self, other: Any) -> bool:
        return (
            other is not None
            and isinstance(other, IndirectObject)
            and self.idnum == other.idnum
            and self.generation == other.generation
            and self.pdf is other.pdf
        )

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:
        stream.write(b_(f"{self.idnum} {self.generation} R"))

    def writeToStream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes]
    ) -> None:  # pragma: no cover
        deprecate_with_replacement("writeToStream", "write_to_stream")
        self.write_to_stream(stream, encryption_key)

    @staticmethod
    def read_from_stream(stream: StreamType, pdf: Any) -> "IndirectObject":  # PdfReader
        idnum = b""
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                break
            idnum += tok
        generation = b""
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                if not generation:
                    continue
                break
            generation += tok
        r = read_non_whitespace(stream)
        if r != b"R":
            raise PdfReadError(
                f"Error reading indirect object reference at byte {hex_str(stream.tell())}"
            )
        return IndirectObject(int(idnum), int(generation), pdf)

    @staticmethod
    def readFromStream(
        stream: StreamType, pdf: Any  # PdfReader
    ) -> "IndirectObject":  # pragma: no cover
        deprecate_with_replacement("readFromStream", "read_from_stream")
        return IndirectObject.read_from_stream(stream, pdf)
