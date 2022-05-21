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

import math
import uuid
from decimal import Decimal
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Union, cast

from .constants import PageAttributes as PG
from .constants import Ressources as RES
from .errors import PageSizeNotDefinedError
from .generic import (
    ArrayObject,
    ContentStream,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    RectangleObject,
    TextStringObject,
)
from .utils import (
    CompressedTransformationMatrix,
    TransformationMatrixType,
    b_,
    matrixMultiply,
)


def getRectangle(self: Any, name: str, defaults: Iterable[str]) -> RectangleObject:
    retval: Union[None, RectangleObject, IndirectObject] = self.get(name)
    if isinstance(retval, RectangleObject):
        return retval
    if retval is None:
        for d in defaults:
            retval = self.get(d)
            if retval is not None:
                break
    if isinstance(retval, IndirectObject):
        retval = self.pdf.getObject(retval)
    retval = RectangleObject(retval)  # type: ignore
    setRectangle(self, name, retval)
    return retval


def setRectangle(self: Any, name: str, value: Union[RectangleObject, float]) -> None:
    if not isinstance(name, NameObject):
        name = NameObject(name)
    self[name] = value


def deleteRectangle(self: Any, name: str) -> None:
    del self[name]


def createRectangleAccessor(name: str, fallback: Iterable[str]) -> property:
    return property(
        lambda self: getRectangle(self, name, fallback),
        lambda self, value: setRectangle(self, name, value),
        lambda self: deleteRectangle(self, name),
    )


class Transformation:
    """
    Specify a 2D transformation.

    The transformation between two coordinate systems is represented by a 3-by-3
    transformation matrix written as follows:
        a b 0
        c d 0
        e f 1
    Because a transformation matrix has only six elements that can be changed,
    it is usually specified in PDF as the six-element array [ a b c d e f ].

    Coordinate transformations are expressed as matrix multiplications:

                                 a b 0
     [ x′ y′ 1 ] = [ x y 1 ] ×   c d 0
                                 e f 1

    Usage
    -----
    >>> from PyPDF2 import Transformation
    >>> op = Transformation().scale(sx=2, sy=3).translate(tx=10, ty=20)
    >>> page.mergeTransformedPage(page2, op)
    """

    # 9.5.4 Coordinate Systems for 3D
    # 4.2.2 Common Transformations
    def __init__(self, ctm: CompressedTransformationMatrix = (1, 0, 0, 1, 0, 0)):
        self.ctm = ctm

    @property
    def matrix(self) -> TransformationMatrixType:
        return (
            (self.ctm[0], self.ctm[1], 0),
            (self.ctm[2], self.ctm[3], 0),
            (self.ctm[4], self.ctm[5], 1),
        )

    @staticmethod
    def compress(matrix: TransformationMatrixType) -> CompressedTransformationMatrix:
        return (
            matrix[0][0],
            matrix[0][1],
            matrix[1][0],
            matrix[1][1],
            matrix[0][2],
            matrix[1][2],
        )

    def translate(self, tx: float = 0, ty: float = 0) -> "Transformation":
        m = self.ctm
        return Transformation(ctm=(m[0], m[1], m[2], m[3], m[4] + tx, m[5] + ty))

    def scale(
        self, sx: Optional[float] = None, sy: Optional[float] = None
    ) -> "Transformation":
        if sx is None and sy is None:
            raise ValueError("Either sx or sy must be specified")
        if sx is None:
            sx = sy
        if sy is None:
            sy = sx
        assert sx is not None
        assert sy is not None
        op: TransformationMatrixType = ((sx, 0, 0), (0, sy, 0), (0, 0, 1))
        ctm = Transformation.compress(matrixMultiply(self.matrix, op))
        return Transformation(ctm)

    def rotate(self, rotation: float) -> "Transformation":
        rotation = math.radians(rotation)
        op: TransformationMatrixType = (
            (math.cos(rotation), math.sin(rotation), 0),
            (-math.sin(rotation), math.cos(rotation), 0),
            (0, 0, 1),
        )
        ctm = Transformation.compress(matrixMultiply(self.matrix, op))
        return Transformation(ctm)

    def __repr__(self) -> str:
        return f"Transformation(ctm={self.ctm})"


class PageObject(DictionaryObject):
    """
    PageObject represents a single page within a PDF file.

    Typically this object will be created by accessing the
    :meth:`getPage()<PyPDF2.PdfFileReader.getPage>` method of the
    :class:`PdfFileReader<PyPDF2.PdfFileReader>` class, but it is
    also possible to create an empty page with the
    :meth:`createBlankPage()<PageObject.createBlankPage>` static method.

    :param pdf: PDF file the page belongs to.
    :param indirectRef: Stores the original indirect reference to
        this object in its source PDF
    """

    def __init__(
        self,
        pdf: Optional[Any] = None,  # PdfFileReader
        indirectRef: Optional[IndirectObject] = None,
    ) -> None:
        from ._reader import PdfFileReader

        DictionaryObject.__init__(self)
        self.pdf: Optional[PdfFileReader] = pdf
        self.indirectRef = indirectRef

    @staticmethod
    def createBlankPage(
        pdf: Optional[Any] = None,  # PdfFileReader
        width: Union[float, Decimal, None] = None,
        height: Union[float, Decimal, None] = None,
    ) -> "PageObject":
        """
        Return a new blank page.

        If ``width`` or ``height`` is ``None``, try to get the page size
        from the last page of *pdf*.

        :param pdf: PDF file the page belongs to
        :param float width: The width of the new page expressed in default user
            space units.
        :param float height: The height of the new page expressed in default user
            space units.
        :return: the new blank page:
        :rtype: :class:`PageObject<PageObject>`
        :raises PageSizeNotDefinedError: if ``pdf`` is ``None`` or contains
            no page
        """
        page = PageObject(pdf)

        # Creates a new page (cf PDF Reference  7.7.3.3)
        page.__setitem__(NameObject(PG.TYPE), NameObject("/Page"))
        page.__setitem__(NameObject(PG.PARENT), NullObject())
        page.__setitem__(NameObject(PG.RESOURCES), DictionaryObject())
        if width is None or height is None:
            if pdf is not None and pdf.getNumPages() > 0:
                lastpage = pdf.getPage(pdf.getNumPages() - 1)
                width = lastpage.mediaBox.getWidth()
                height = lastpage.mediaBox.getHeight()
            else:
                raise PageSizeNotDefinedError()
        page.__setitem__(
            NameObject(PG.MEDIABOX), RectangleObject((0, 0, width, height))
        )

        return page

    def rotateClockwise(self, angle: float) -> "PageObject":
        """
        Rotate a page clockwise by increments of 90 degrees.

        :param int angle: Angle to rotate the page.  Must be an increment
            of 90 deg.
        """
        if angle % 90 != 0:
            raise ValueError("Rotation angle must be a multiple of 90")
        self._rotate(angle)
        return self

    def rotateCounterClockwise(self, angle: float) -> "PageObject":
        """
        Rotate a page counter-clockwise by increments of 90 degrees.

        :param int angle: Angle to rotate the page.  Must be an increment
            of 90 deg.
        """
        if angle % 90 != 0:
            raise ValueError("Rotation angle must be a multiple of 90")
        self._rotate(-angle)
        return self

    def _rotate(self, angle: float) -> None:
        rotate_obj = self.get(PG.ROTATE, 0)
        current_angle = (
            rotate_obj if isinstance(rotate_obj, int) else rotate_obj.getObject()
        )
        self[NameObject(PG.ROTATE)] = NumberObject(current_angle + angle)

    @staticmethod
    def _mergeResources(
        res1: DictionaryObject, res2: DictionaryObject, resource: Any
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        new_res = DictionaryObject()
        new_res.update(res1.get(resource, DictionaryObject()).getObject())
        page2res = cast(
            DictionaryObject, res2.get(resource, DictionaryObject()).getObject()
        )
        rename_res = {}
        for key in list(page2res.keys()):
            if key in new_res and new_res.raw_get(key) != page2res.raw_get(key):
                newname = NameObject(key + str(uuid.uuid4()))
                rename_res[key] = newname
                new_res[newname] = page2res[key]
            elif key not in new_res:
                new_res[key] = page2res.raw_get(key)
        return new_res, rename_res

    @staticmethod
    def _contentStreamRename(
        stream: ContentStream, rename: Dict[Any, Any], pdf: Any  # PdfFileReader
    ) -> ContentStream:
        if not rename:
            return stream
        stream = ContentStream(stream, pdf)
        for operands, _operator in stream.operations:
            if isinstance(operands, list):
                for i in range(len(operands)):
                    op = operands[i]
                    if isinstance(op, NameObject):
                        operands[i] = rename.get(op, op)
            elif isinstance(operands, dict):
                for i in operands:
                    op = operands[i]
                    if isinstance(op, NameObject):
                        operands[i] = rename.get(op, op)
            else:
                raise KeyError("type of operands is %s" % type(operands))
        return stream

    @staticmethod
    def _pushPopGS(contents: Any, pdf: Any) -> ContentStream:  # PdfFileReader
        # adds a graphics state "push" and "pop" to the beginning and end
        # of a content stream.  This isolates it from changes such as
        # transformation matricies.
        stream = ContentStream(contents, pdf)
        stream.operations.insert(0, ([], "q"))
        stream.operations.append(([], "Q"))
        return stream

    def add_transformation(
        self,
        ctm: Union[Transformation, CompressedTransformationMatrix],
        expand: bool = False,
    ) -> None:
        if isinstance(ctm, Transformation):
            ctm = ctm.ctm

        transformation_func = lambda content: PageObject._addTransformationMatrix(
            content, self.pdf, ctm  # type: ignore[arg-type]
        )

        new_content_array = ArrayObject()

        content = self.getContents()
        if content is not None:
            content = ContentStream(content, self.pdf)
            content.operations.insert(
                0,
                (
                    map(
                        FloatObject,
                        [
                            self.trimBox.getLowerLeft_x(),
                            self.trimBox.getLowerLeft_y(),
                            self.trimBox.getWidth(),
                            self.trimBox.getHeight(),
                        ],
                    ),
                    "re",
                ),
            )
            content.operations.insert(1, ([], "W"))
            content.operations.insert(2, ([], "n"))
            if transformation_func is not None:
                content = transformation_func(content)
            content = PageObject._pushPopGS(content, self.pdf)
            new_content_array.append(content)

        # if expanding the page to fit a new page, calculate the new media box size
        if expand:
            corners = [
                self.mediaBox.getLowerLeft_x().as_numeric(),
                self.mediaBox.getLowerLeft_y().as_numeric(),
                self.mediaBox.getUpperLeft_x().as_numeric(),
                self.mediaBox.getUpperLeft_y().as_numeric(),
                self.mediaBox.getUpperRight_x().as_numeric(),
                self.mediaBox.getUpperRight_y().as_numeric(),
                self.mediaBox.getLowerRight_x().as_numeric(),
                self.mediaBox.getLowerRight_y().as_numeric(),
            ]
            if ctm is not None:
                ctm = tuple(float(x) for x in ctm)  # type: ignore[assignment]
                new_x = [
                    ctm[0] * corners[i] + ctm[2] * corners[i + 1] + ctm[4]
                    for i in range(0, 8, 2)
                ]
                new_y = [
                    ctm[1] * corners[i] + ctm[3] * corners[i + 1] + ctm[5]
                    for i in range(0, 8, 2)
                ]
            else:
                new_x = corners[0:8:2]
                new_y = corners[1:8:2]
            lowerleft = [min(new_x), min(new_y)]
            upperright = [max(new_x), max(new_y)]
            lowerleft = [min(corners[0], lowerleft[0]), min(corners[1], lowerleft[1])]
            upperright = [
                max(corners[2], upperright[0]),
                max(corners[3], upperright[1]),
            ]

            self.mediaBox.setLowerLeft(lowerleft)
            self.mediaBox.setUpperRight(upperright)
        self[NameObject(PG.CONTENTS)] = ContentStream(new_content_array, self.pdf)

    @staticmethod
    def _addTransformationMatrix(
        contents: Any, pdf: Any, ctm: CompressedTransformationMatrix
    ) -> ContentStream:  # PdfFileReader
        # adds transformation matrix at the beginning of the given
        # contents stream.
        a, b, c, d, e, f = ctm
        contents = ContentStream(contents, pdf)
        contents.operations.insert(
            0,
            [
                [
                    FloatObject(a),
                    FloatObject(b),
                    FloatObject(c),
                    FloatObject(d),
                    FloatObject(e),
                    FloatObject(f),
                ],
                " cm",
            ],
        )
        return contents

    def getContents(self) -> Optional[ContentStream]:
        """
        Access the page contents.

        :return: the ``/Contents`` object, or ``None`` if it doesn't exist.
            ``/Contents`` is optional, as described in PDF Reference  7.7.3.3
        """
        if PG.CONTENTS in self:
            return self[PG.CONTENTS].getObject()  # type: ignore
        else:
            return None

    def mergePage(self, page2: "PageObject", expand: bool = False) -> None:
        """
        Merge the content streams of two pages into one.

        Resource references
        (i.e. fonts) are maintained from both pages.  The mediabox/cropbox/etc
        of this page are not altered.  The parameter page's content stream will
        be added to the end of this page's content stream, meaning that it will
        be drawn after, or "on top" of this page.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        """
        self._mergePage(page2, expand=expand)

    def _mergePage(
        self,
        page2: "PageObject",
        page2transformation: Optional[Callable[[Any], ContentStream]] = None,
        ctm: Optional[CompressedTransformationMatrix] = None,
        expand: bool = False,
    ) -> None:
        # First we work on merging the resource dictionaries.  This allows us
        # to find out what symbols in the content streams we might need to
        # rename.

        new_resources = DictionaryObject()
        rename = {}
        original_resources = cast(DictionaryObject, self[PG.RESOURCES].getObject())
        page2resources = cast(DictionaryObject, page2[PG.RESOURCES].getObject())
        new_annots = ArrayObject()

        for page in (self, page2):
            if PG.ANNOTS in page:
                annots = page[PG.ANNOTS]
                if isinstance(annots, ArrayObject):
                    for ref in annots:
                        new_annots.append(ref)

        for res in (
            RES.EXT_G_STATE,
            RES.FONT,
            RES.XOBJECT,
            RES.COLOR_SPACE,
            RES.PATTERN,
            RES.SHADING,
            RES.PROPERTIES,
        ):
            new, newrename = PageObject._mergeResources(
                original_resources, page2resources, res
            )
            if new:
                new_resources[NameObject(res)] = new
                rename.update(newrename)

        # Combine /ProcSet sets.
        new_resources[NameObject(RES.PROC_SET)] = ArrayObject(
            frozenset(
                original_resources.get(RES.PROC_SET, ArrayObject()).getObject()  # type: ignore
            ).union(
                frozenset(page2resources.get(RES.PROC_SET, ArrayObject()).getObject())  # type: ignore
            )
        )

        new_content_array = ArrayObject()

        original_content = self.getContents()
        if original_content is not None:
            new_content_array.append(PageObject._pushPopGS(original_content, self.pdf))

        page2content = page2.getContents()
        if page2content is not None:
            page2content = ContentStream(page2content, self.pdf)
            page2content.operations.insert(
                0,
                (
                    map(
                        FloatObject,
                        [
                            page2.trimBox.getLowerLeft_x(),
                            page2.trimBox.getLowerLeft_y(),
                            page2.trimBox.getWidth(),
                            page2.trimBox.getHeight(),
                        ],
                    ),
                    "re",
                ),
            )
            page2content.operations.insert(1, ([], "W"))
            page2content.operations.insert(2, ([], "n"))
            if page2transformation is not None:
                page2content = page2transformation(page2content)
            page2content = PageObject._contentStreamRename(
                page2content, rename, self.pdf
            )
            page2content = PageObject._pushPopGS(page2content, self.pdf)
            new_content_array.append(page2content)

        # if expanding the page to fit a new page, calculate the new media box size
        if expand:
            corners1 = [
                self.mediaBox.getLowerLeft_x().as_numeric(),
                self.mediaBox.getLowerLeft_y().as_numeric(),
                self.mediaBox.getUpperRight_x().as_numeric(),
                self.mediaBox.getUpperRight_y().as_numeric(),
            ]
            corners2 = [
                page2.mediaBox.getLowerLeft_x().as_numeric(),
                page2.mediaBox.getLowerLeft_y().as_numeric(),
                page2.mediaBox.getUpperLeft_x().as_numeric(),
                page2.mediaBox.getUpperLeft_y().as_numeric(),
                page2.mediaBox.getUpperRight_x().as_numeric(),
                page2.mediaBox.getUpperRight_y().as_numeric(),
                page2.mediaBox.getLowerRight_x().as_numeric(),
                page2.mediaBox.getLowerRight_y().as_numeric(),
            ]
            if ctm is not None:
                ctm = tuple(float(x) for x in ctm)  # type: ignore[assignment]
                new_x = [
                    ctm[0] * corners2[i] + ctm[2] * corners2[i + 1] + ctm[4]
                    for i in range(0, 8, 2)
                ]
                new_y = [
                    ctm[1] * corners2[i] + ctm[3] * corners2[i + 1] + ctm[5]
                    for i in range(0, 8, 2)
                ]
            else:
                new_x = corners2[0:8:2]
                new_y = corners2[1:8:2]
            lowerleft = [min(new_x), min(new_y)]
            upperright = [max(new_x), max(new_y)]
            lowerleft = [min(corners1[0], lowerleft[0]), min(corners1[1], lowerleft[1])]
            upperright = [
                max(corners1[2], upperright[0]),
                max(corners1[3], upperright[1]),
            ]

            self.mediaBox.setLowerLeft(lowerleft)
            self.mediaBox.setUpperRight(upperright)

        self[NameObject(PG.CONTENTS)] = ContentStream(new_content_array, self.pdf)
        self[NameObject(PG.RESOURCES)] = new_resources
        self[NameObject(PG.ANNOTS)] = new_annots

    def mergeTransformedPage(
        self,
        page2: "PageObject",
        ctm: Union[CompressedTransformationMatrix, Transformation],
        expand: bool = False,
    ) -> None:
        """
        mergeTransformedPage is similar to mergePage, but a transformation
        matrix is applied to the merged stream.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param tuple ctm: a 6-element tuple containing the operands of the
            transformation matrix
        :param bool expand: Whether the page should be expanded to fit the dimensions
            of the page to be merged.
        """
        if isinstance(ctm, Transformation):
            ctm = ctm.ctm
        ctm = cast(CompressedTransformationMatrix, ctm)
        self._mergePage(
            page2,
            lambda page2Content: PageObject._addTransformationMatrix(
                page2Content, page2.pdf, ctm  # type: ignore[arg-type]
            ),
            ctm,
            expand,
        )

    def mergeScaledPage(
        self, page2: "PageObject", scale: float, expand: bool = False
    ) -> None:
        """
        mergeScaledPage is similar to mergePage, but the stream to be merged
        is scaled by appling a transformation matrix.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float scale: The scaling factor
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().scale(scale, scale)
        self.mergeTransformedPage(page2, op, expand)

    def mergeRotatedPage(
        self, page2: "PageObject", rotation: float, expand: bool = False
    ) -> None:
        """
        mergeRotatedPage is similar to mergePage, but the stream to be merged
        is rotated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float rotation: The angle of the rotation, in degrees
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().rotate(rotation)
        self.mergeTransformedPage(page2, op, expand)

    def mergeTranslatedPage(
        self, page2: "PageObject", tx: float, ty: float, expand: bool = False
    ) -> None:
        """
        mergeTranslatedPage is similar to mergePage, but the stream to be
        merged is translated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis
        :param float ty: The translation on Y axis
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().translate(tx, ty)
        self.mergeTransformedPage(page2, op, expand)

    def mergeRotatedTranslatedPage(
        self,
        page2: "PageObject",
        rotation: float,
        tx: float,
        ty: float,
        expand: bool = False,
    ) -> None:
        """
        mergeRotatedTranslatedPage is similar to mergePage, but the stream to
        be merged is rotated and translated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis
        :param float ty: The translation on Y axis
        :param float rotation: The angle of the rotation, in degrees
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().translate(-tx, -ty).rotate(rotation).translate(tx, ty)
        return self.mergeTransformedPage(page2, op, expand)

    def mergeRotatedScaledPage(
        self, page2: "PageObject", rotation: float, scale: float, expand: bool = False
    ) -> None:
        """
        mergeRotatedScaledPage is similar to mergePage, but the stream to be
        merged is rotated and scaled by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float rotation: The angle of the rotation, in degrees
        :param float scale: The scaling factor
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().rotate(rotation).scale(scale, scale)
        self.mergeTransformedPage(page2, op, expand)

    def mergeScaledTranslatedPage(
        self,
        page2: "PageObject",
        scale: float,
        tx: float,
        ty: float,
        expand: bool = False,
    ) -> None:
        """
        mergeScaledTranslatedPage is similar to mergePage, but the stream to be
        merged is translated and scaled by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float scale: The scaling factor
        :param float tx: The translation on X axis
        :param float ty: The translation on Y axis
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().scale(scale, scale).translate(tx, ty)
        return self.mergeTransformedPage(page2, op, expand)

    def mergeRotatedScaledTranslatedPage(
        self,
        page2: "PageObject",
        rotation: float,
        scale: float,
        tx: float,
        ty: float,
        expand: bool = False,
    ) -> None:
        """
        mergeRotatedScaledTranslatedPage is similar to mergePage, but the
        stream to be merged is translated, rotated and scaled by appling a
        transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float tx: The translation on X axis
        :param float ty: The translation on Y axis
        :param float rotation: The angle of the rotation, in degrees
        :param float scale: The scaling factor
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        op = Transformation().rotate(rotation).scale(scale, scale).translate(tx, ty)
        self.mergeTransformedPage(page2, op, expand)

    def addTransformation(self, ctm: CompressedTransformationMatrix) -> None:
        """
        Apply a transformation matrix to the page.

        :param tuple ctm: A 6-element tuple containing the operands of the
            transformation matrix.
        """
        original_content = self.getContents()
        if original_content is not None:
            new_content = PageObject._addTransformationMatrix(
                original_content, self.pdf, ctm
            )
            new_content = PageObject._pushPopGS(new_content, self.pdf)
            self[NameObject(PG.CONTENTS)] = new_content

    def scale(self, sx: float, sy: float) -> None:
        """
        Scale a page by the given factors by appling a transformation
        matrix to its content and updating the page size.

        :param float sx: The scaling factor on horizontal axis.
        :param float sy: The scaling factor on vertical axis.
        """
        self.addTransformation((sx, 0, 0, sy, 0, 0))
        self.mediaBox = RectangleObject(
            (
                float(self.mediaBox.getLowerLeft_x()) * sx,
                float(self.mediaBox.getLowerLeft_y()) * sy,
                float(self.mediaBox.getUpperRight_x()) * sx,
                float(self.mediaBox.getUpperRight_y()) * sy,
            )
        )
        if PG.VP in self:
            viewport = self[PG.VP]
            if isinstance(viewport, ArrayObject):
                bbox = viewport[0]["/BBox"]
            else:
                bbox = viewport["/BBox"]  # type: ignore
            scaled_bbox = RectangleObject(
                (
                    float(bbox[0]) * sx,
                    float(bbox[1]) * sy,
                    float(bbox[2]) * sx,
                    float(bbox[3]) * sy,
                )
            )
            if isinstance(viewport, ArrayObject):
                self[NameObject(PG.VP)][NumberObject(0)][  # type: ignore
                    NameObject("/BBox")
                ] = scaled_bbox
            else:
                self[NameObject(PG.VP)][NameObject("/BBox")] = scaled_bbox  # type: ignore

    def scaleBy(self, factor: float) -> None:
        """
        Scale a page by the given factor by appling a transformation
        matrix to its content and updating the page size.

        :param float factor: The scaling factor (for both X and Y axis).
        """
        self.scale(factor, factor)

    def scaleTo(self, width: float, height: float) -> None:
        """
        Scale a page to the specified dimentions by appling a
        transformation matrix to its content and updating the page size.

        :param float width: The new width.
        :param float height: The new heigth.
        """
        sx = width / float(
            self.mediaBox.getUpperRight_x() - self.mediaBox.getLowerLeft_x()
        )
        sy = height / float(
            self.mediaBox.getUpperRight_y() - self.mediaBox.getLowerLeft_y()
        )
        self.scale(sx, sy)

    def compressContentStreams(self) -> None:
        """
        Compress the size of this page by joining all content streams and
        applying a FlateDecode filter.

        However, it is possible that this function will perform no action if
        content stream compression becomes "automatic" for some reason.
        """
        content = self.getContents()
        if content is not None:
            if not isinstance(content, ContentStream):
                content = ContentStream(content, self.pdf)
            self[NameObject(PG.CONTENTS)] = content.flateEncode()

    def extractText(self, Tj_sep: str = "", TJ_sep: str = "") -> str:
        """
        Locate all text drawing commands, in the order they are provided in the
        content stream, and extract the text.  This works well for some PDF
        files, but poorly for others, depending on the generator used.  This will
        be refined in the future.  Do not rely on the order of text coming out of
        this function, as it will change if this function is made more
        sophisticated.

        :return: a string object.
        """
        text = ""
        content = self[PG.CONTENTS].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pdf)
        # Note: we check all strings are TextStringObjects.  ByteStringObjects
        # are strings where the byte->string encoding was unknown, so adding
        # them to the text here would be gibberish.
        for operands, operator in content.operations:
            if operator == b_("Tj"):
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += Tj_sep
                    text += _text
                    text += "\n"
            elif operator == b_("T*"):
                text += "\n"
            elif operator == b_("'"):
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == b_('"'):
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == b_("TJ"):
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += TJ_sep
                        text += i
                    elif isinstance(i, NumberObject):
                        # a positive value decreases and the negative value increases
                        # space
                        if int(i) < 0:
                            if len(text) == 0 or text[-1] != " ":
                                text += " "
                        else:
                            if len(text) > 1 and text[-1] == " ":
                                text = text[:-1]
                text += "\n"
        return text

    mediaBox = createRectangleAccessor(PG.MEDIABOX, ())
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the boundaries of the physical medium on which the page is
    intended to be displayed or printed.
    """

    cropBox = createRectangleAccessor("/CropBox", (PG.MEDIABOX,))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the visible region of default user space.  When the page is
    displayed or printed, its contents are to be clipped (cropped) to this
    rectangle and then imposed on the output medium in some
    implementation-defined manner.  Default value: same as :attr:`mediaBox<mediaBox>`.
    """

    bleedBox = createRectangleAccessor("/BleedBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the region to which the contents of the page should be clipped
    when output in a production enviroment.
    """

    trimBox = createRectangleAccessor("/TrimBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the intended dimensions of the finished page after trimming.
    """

    artBox = createRectangleAccessor("/ArtBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the extent of the page's meaningful content as intended by the
    page's creator.
    """
