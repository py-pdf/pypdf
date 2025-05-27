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


# This module contains classes used by _writer.py to track links in
# pages being added to the writer until the links can be resolved.

from typing import TYPE_CHECKING, Union

from . import ArrayObject, IndirectObject, TextStringObject

if TYPE_CHECKING:
    from .._reader import PdfReader
    from .._writer import PdfWriter


class NamedRefLink:
    """Named reference link being preserved until we can resolve it correctly."""

    def __init__(self, ref: TextStringObject, source_pdf: "PdfReader") -> None:
        """ref: TextStringObject with named reference"""
        self._ref = ref
        self._source_pdf = source_pdf

    def find_referenced_page(self) -> Union[IndirectObject,None]:
        dest = self._source_pdf.named_destinations.get(str(self._ref))
        return dest.page if dest else None

    def patch_reference(self, target_pdf: "PdfWriter", new_page: IndirectObject) -> None:
        """target_pdf: PdfWriter which the new link went into"""
        # point named destination in new PDF to the new page
        if str(self._ref) not in target_pdf.named_destinations:
            target_pdf.add_named_destination(str(self._ref), new_page.page_number)


class DirectRefLink:
    """Direct reference link being preserved until we can resolve it correctly."""

    def __init__(self, ref: ArrayObject) -> None:
        """ref: an ArrayObject whose first element is the Page indir obj"""
        self._ref = ref

    def find_referenced_page(self) -> IndirectObject:
        return self._ref[0]

    def patch_reference(self, target_pdf: "PdfWriter", new_page: IndirectObject) -> None:
        """target_pdf: PdfWriter which the new link went into"""
        self._ref[0] = new_page


RefLink = Union[NamedRefLink,DirectRefLink]
