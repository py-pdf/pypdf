from typing import Union

from .._utils import StreamType
from ._base import NameObject
from ._data_structures import Destination


class OutlineItem(Destination):
    def write_to_stream(
        self, stream: StreamType
    ) -> None:
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
