from typing import Any, Union

from .._utils import StreamType, deprecate_no_replacement, deprecation_with_replacement
from ._base import NameObject
from ._data_structures import Destination


class OutlineItem(Destination):
    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(b"<<\n")
        for key in [
            NameObject(x)
            for x in ["/Title", "/Parent", "/First", "/Last", "/Next", "/Prev"]
            if x in self
        ]:
            key.write_to_stream(stream)
            stream.write(b" ")
            value = self.raw_get(key)
            value.write_to_stream(stream)
            stream.write(b"\n")
        key = NameObject("/Dest")
        key.write_to_stream(stream)
        stream.write(b" ")
        value = self.dest_array
        value.write_to_stream(stream)
        stream.write(b"\n")
        stream.write(b">>")


class Bookmark(OutlineItem):  # deprecated
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        deprecation_with_replacement("Bookmark", "OutlineItem", "3.0.0")
        super().__init__(*args, **kwargs)
