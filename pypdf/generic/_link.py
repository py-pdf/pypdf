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


# This module contains code used by _writer.py to track links in pages
# being added to the writer until the links can be resolved.

from typing import TYPE_CHECKING, List, Optional, Tuple, Union, cast

from . import ArrayObject, DictionaryObject, IndirectObject, NullObject, PdfObject, TextStringObject

if TYPE_CHECKING:
    from .._page import PageObject
    from .._protocols import PdfCommonDocProtocol
    from .._reader import PdfReader
    from .._writer import PdfWriter
    from ..generic import Destination


class NamedReferenceLink:
    """Named reference link being preserved until we can resolve it correctly."""

    def __init__(self, reference: TextStringObject, page: "PageObject") -> None:
        """reference: TextStringObject with named reference"""
        self._reference = reference

        # to work out where the reference points we need to find the
        # source PDF which the reference is pointing to.  this *can*
        # be the PDF the page containing the link comes from, but it
        # may also be some other PDF merged into this page, so we need
        # to do a little search
        destination = self._find_page_in(page.pdf)

        if not destination:
            for src_page in page._merged_in_pages:
                destination = self._find_page_in(src_page.pdf)
                break

        if destination and not isinstance(destination.dest_array[0], NullObject):
            self._referenced_page = destination.dest_array[0]
        else:
            self._referenced_page = None

    def _find_page_in(self, pdf: "Optional[PdfCommonDocProtocol]") -> "Optional[Destination]":
        if not pdf or not hasattr(pdf, "named_destinations"):
            return None
        reader: PdfReader = cast("PdfReader", pdf)
        return reader.named_destinations.get(str(self._reference))

    def find_referenced_page(self) -> Union[IndirectObject, None]:
        if self._referenced_page:
            return self._referenced_page.indirect_reference
        return None

    def patch_reference(self, target_pdf: "PdfWriter", new_page: IndirectObject) -> None:
        """target_pdf: PdfWriter which the new link went into"""
        # point named destination in new PDF to the new page
        if str(self._reference) not in target_pdf.named_destinations:
            target_pdf.add_named_destination(str(self._reference), new_page.page_number)


class DirectReferenceLink:
    """Direct reference link being preserved until we can resolve it correctly."""

    def __init__(self, reference: ArrayObject) -> None:
        """reference: an ArrayObject whose first element is the Page indirect object"""
        self._reference = reference

    def find_referenced_page(self) -> IndirectObject:
        return self._reference[0]

    def patch_reference(self, target_pdf: "PdfWriter", new_page: IndirectObject) -> None:
        """target_pdf: PdfWriter which the new link went into"""
        self._reference[0] = new_page


ReferenceLink = Union[NamedReferenceLink, DirectReferenceLink]


def extract_links(new_page: "PageObject", old_page: "PageObject") -> List[Tuple[ReferenceLink, ReferenceLink]]:
    """Extracts links from two pages on the assumption that the two pages are
    the same. Produces one list of (new link, old link) tuples.
    """
    new_links = [_build_link(link, new_page) for link in new_page.get("/Annots", [])]
    old_links = [_build_link(link, old_page) for link in old_page.get("/Annots", [])]

    return [
        (new_link, old_link) for (new_link, old_link)
        in zip(new_links, old_links)
        if new_link and old_link
    ]


def _build_link(indirect_object: IndirectObject, page: "PageObject") -> Optional[ReferenceLink]:
    link = cast(DictionaryObject, indirect_object.get_object())
    if (not isinstance(link, DictionaryObject)) or link.get("/Subtype") != "/Link":
        return None

    if "/A" in link:
        action = cast(DictionaryObject, link["/A"])
        if action.get("/S") != "/GoTo":
            return None

        return _create_link(action["/D"], page)

    if "/Dest" in link:
        return _create_link(link["/Dest"], page)

    return None  # Nothing to do here


def _create_link(reference: PdfObject, page: "PageObject")-> Optional[ReferenceLink]:
    if isinstance(reference, TextStringObject):
        return NamedReferenceLink(reference, page)
    if isinstance(reference, ArrayObject):
        return DirectReferenceLink(reference)
    return None
