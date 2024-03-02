"""Helpers for working with PDF types."""

from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple, Union

try:
    # Python 3.8+: https://peps.python.org/pep-0586
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore[assignment]

from ._utils import StrByteType, StreamType


class PdfObjectProtocol(Protocol):
    indirect_reference: Any

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Union[Tuple[str, ...], List[str], None] = (),
    ) -> Any:
        ...

    def _reference_clone(self, clone: Any, pdf_dest: Any) -> Any:
        ...

    def get_object(self) -> Optional["PdfObjectProtocol"]:
        ...

    def hash_value(self) -> bytes:
        ...

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        ...


class PdfCommonDocProtocol(Protocol):  # deprecated
    @property
    def pdf_header(self) -> str:
        ...

    @property
    def pages(self) -> List[Any]:
        ...

    @property
    def root_object(self) -> PdfObjectProtocol:
        ...

    def get_object(self, indirect_reference: Any) -> Optional[PdfObjectProtocol]:
        ...


class PdfReaderProtocol(PdfCommonDocProtocol, Protocol):  # deprecated
    @property
    def strict(self) -> bool:
        ...

    @property
    def xref(self) -> Dict[int, Dict[int, Any]]:
        ...

    @property
    def trailer(self) -> Dict[str, Any]:
        ...


class PdfWriterProtocol(PdfCommonDocProtocol, Protocol):  # deprecated
    _objects: List[Any]
    _id_translated: Dict[int, Dict[int, int]]

    def write(self, stream: Union[Path, StrByteType]) -> Tuple[bool, IO[Any]]:
        ...

    def _add_object(self, obj: Any) -> Any:
        ...
