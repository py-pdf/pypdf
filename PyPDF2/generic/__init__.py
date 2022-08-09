# Copyright (c) 2006, Mathieu Fenniak
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


"""Implementation of generic PDF objects (dictionary, number, string, ...)."""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

from typing import Any, Dict, List, Union

from .._utils import deprecate_with_replacement
from ._annotations import AnnotationBuilder
from ._base import (
    BooleanObject,
    ByteStringObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    PdfObject,
    TextStringObject,
    encode_pdfdocencoding,
)
from ._data_structures import (  # tightly coupled with those:
    ArrayObject,
    ContentStream,
    DecodedStreamObject,
    Destination,
    DictionaryObject,
    EncodedStreamObject,
    Field,
    OutlineFontFlag,
    OutlineItem,
    RectangleObject,
    StreamObject,
    TreeObject,
    read_object,
)
from ._utils import (
    create_string_object,
    decode_pdfdocencoding,
    hex_to_rgb,
    read_hex_string_from_stream,
    read_string_from_stream,
)


class Bookmark(OutlineItem):  # pragma: no cover
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        deprecate_with_replacement("Bookmark", "OutlineItem")
        super().__init__(*args, **kwargs)


def createStringObject(
    string: Union[str, bytes],
    forced_encoding: Union[None, str, List[str], Dict[int, str]] = None,
) -> Union[TextStringObject, ByteStringObject]:  # pragma: no cover
    deprecate_with_replacement("createStringObject", "create_string_object", "4.0.0")
    return create_string_object(string, forced_encoding)


__all__ = [
    # Base types
    "BooleanObject",
    "FloatObject",
    "NumberObject",
    "NameObject",
    "IndirectObject",
    "NullObject",
    "PdfObject",
    # Annotations
    "AnnotationBuilder",
    # Data structures
    "ArrayObject",
    "DictionaryObject",
    "TreeObject",
    "StreamObject",
    "DecodedStreamObject",
    "EncodedStreamObject",
    "ContentStream",
    "RectangleObject",
    "Field",
    "OutlineFontFlag",
    "OutlineItem",
    "Destination",
    # Data structures core functions
    "read_object",
    # Utility functions
    "encode_pdfdocencoding",
    "decode_pdfdocencoding",
    "hex_to_rgb",
    "read_hex_string_from_stream",
    "read_string_from_stream",
]
