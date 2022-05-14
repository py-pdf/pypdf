# -*- coding: utf-8 -*-
#
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
import warnings

from PyPDF2 import utils
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.constants import Ressources as RES
from PyPDF2.errors import PageSizeNotDefinedError
from PyPDF2.generic import (
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
from PyPDF2.utils import DEPR_MSG, DEPR_MSG_NO_REPLACEMENT, b_, u_


def _get_rectangle(self, name, defaults):
    retval = self.get(name)
    if isinstance(retval, RectangleObject):
        return retval
    if retval is None:
        for d in defaults:
            retval = self.get(d)
            if retval is not None:
                break
    if isinstance(retval, IndirectObject):
        retval = self.pdf.get_object(retval)
    retval = RectangleObject(retval)
    _set_rectangle(self, name, retval)
    return retval


def getRectangle(self, name, defaults):
    warnings.warn(
        DEPR_MSG_NO_REPLACEMENT.format("getRectangle"),
        PendingDeprecationWarning,
    )
    return _get_rectangle(self, name, defaults)


def _set_rectangle(self, name, value):
    if not isinstance(name, NameObject):
        name = NameObject(name)
    self[name] = value


def setRectangle(self, name, value):
    warnings.warn(
        DEPR_MSG_NO_REPLACEMENT.format("setRectangle"),
        PendingDeprecationWarning,
    )
    _set_rectangle(self, name, value)


def _delete_rectangle(self, name):
    del self[name]


def deleteRectangle(self, name):
    warnings.warn(
        DEPR_MSG_NO_REPLACEMENT.format("deleteRectangle"),
        PendingDeprecationWarning,
    )
    del self[name]


def _create_rectangle_accessor(name, fallback):
    return property(
        lambda self: _get_rectangle(self, name, fallback),
        lambda self, value: _set_rectangle(self, name, value),
        lambda self: _delete_rectangle(self, name),
    )


def createRectangleAccessor(name, fallback):
    warnings.warn(
        DEPR_MSG_NO_REPLACEMENT.format("createRectangleAccessor"),
        PendingDeprecationWarning,
    )
    return _create_rectangle_accessor(name, fallback)


class PageObject(DictionaryObject):
    """
    PageObject represents a single page within a PDF file.

    Typically this object will be created by accessing the
    :meth:`get_page()<PyPDF2.PdfReader.get_page>` method of the
    :class:`PdfReader<PyPDF2.PdfReader>` class, but it is
    also possible to create an empty page with the
    :meth:`createBlankPage()<PageObject.createBlankPage>` static method.

    :param pdf: PDF file the page belongs to.
    :param indirectRef: Stores the original indirect reference to
        this object in its source PDF
    """

    def __init__(self, pdf=None, indirectRef=None):
        DictionaryObject.__init__(self)
        self.pdf = pdf
        self.indirectRef = indirectRef

    @staticmethod
    def create_blank_page(pdf=None, width=None, height=None):
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
                lastpage = pdf.get_page(pdf.getNumPages() - 1)
                width = lastpage.mediaBox.getWidth()
                height = lastpage.mediaBox.getHeight()
            else:
                raise PageSizeNotDefinedError()
        page.__setitem__(
            NameObject(PG.MEDIABOX), RectangleObject([0, 0, width, height])
        )

        return page

    @staticmethod
    def createBlankPage(pdf=None, width=None, height=None):
        warnings.warn(
            DEPR_MSG.format("createBlankPage", "create_blank_page"),
            PendingDeprecationWarning,
        )
        return PageObject.create_blank_page(pdf, width, height)

    def rotate_clockwise(self, angle):
        """
        Rotate a page clockwise by increments of 90 degrees.

        :param int angle: Angle to rotate the page.  Must be an increment
            of 90 deg.
        """
        if angle % 90 != 0:
            raise ValueError("Rotation angle must be a multiple of 90")
        self._rotate(angle)
        return self

    def rotateClockwise(self, angle):
        warnings.warn(
            DEPR_MSG.format("rotateClockwise", "rotate_clockwise"),
            PendingDeprecationWarning,
        )
        return self.rotate_clockwise(angle)

    def rotateCounterClockwise(self, angle):
        warnings.warn(
            DEPR_MSG.format("rotateCounterClockwise", "rotate_clockwise"),
            PendingDeprecationWarning,
        )
        if angle % 90 != 0:
            raise ValueError("Rotation angle must be a multiple of 90")
        self._rotate(-angle)
        return self

    def _rotate(self, angle):
        rotate_obj = self.get(PG.ROTATE, 0)
        current_angle = (
            rotate_obj if isinstance(rotate_obj, int) else rotate_obj.get_object()
        )
        self[NameObject(PG.ROTATE)] = NumberObject(current_angle + angle)

    @staticmethod
    def _merge_resources(res1, res2, resource):
        new_res = DictionaryObject()
        new_res.update(res1.get(resource, DictionaryObject()).get_object())
        page2res = res2.get(resource, DictionaryObject()).get_object()
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
    def _content_stream_rename(stream, rename, pdf):
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
    def _push_pop_gs(contents, pdf):
        # adds a graphics state "push" and "pop" to the beginning and end
        # of a content stream.  This isolates it from changes such as
        # transformation matricies.
        stream = ContentStream(contents, pdf)
        stream.operations.insert(0, [[], "q"])
        stream.operations.append([[], "Q"])
        return stream

    @staticmethod
    def _add_transformation_matrix(contents, pdf, ctm):
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

    def get_contents(self):
        """
        Access the page contents.

        :return: the ``/Contents`` object, or ``None`` if it doesn't exist.
            ``/Contents`` is optional, as described in PDF Reference  7.7.3.3
        """
        if PG.CONTENTS in self:
            return self[PG.CONTENTS].get_object()
        else:
            return None

    def getContents(self):
        warnings.warn(
            DEPR_MSG.format("getContents", "get_contents"),
        )
        return self.get_contents()

    def merge_page(self, page2):
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
        self._merge_page(page2)

    def mergePage(self, page2):
        warnings.warn(
            DEPR_MSG.format("mergePage", "merge_page"),
        )
        return self.merge_page(page2)

    def _merge_page(self, page2, page2transformation=None, ctm=None, expand=False):
        # First we work on merging the resource dictionaries.  This allows us
        # to find out what symbols in the content streams we might need to
        # rename.

        new_resources = DictionaryObject()
        rename = {}
        original_resources = self[PG.RESOURCES].get_object()
        page2resources = page2[PG.RESOURCES].get_object()
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
            new, newrename = PageObject._merge_resources(
                original_resources, page2resources, res
            )
            if new:
                new_resources[NameObject(res)] = new
                rename.update(newrename)

        # Combine /ProcSet sets.
        new_resources[NameObject(RES.PROC_SET)] = ArrayObject(
            frozenset(
                original_resources.get(RES.PROC_SET, ArrayObject()).get_object()
            ).union(
                frozenset(page2resources.get(RES.PROC_SET, ArrayObject()).get_object())
            )
        )

        new_content_array = ArrayObject()

        original_content = self.get_contents()
        if original_content is not None:
            new_content_array.append(
                PageObject._push_pop_gs(original_content, self.pdf)
            )

        page2content = page2.getContents()
        if page2content is not None:
            page2content = ContentStream(page2content, self.pdf)
            page2content.operations.insert(
                0,
                [
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
                ],
            )
            page2content.operations.insert(1, [[], "W"])
            page2content.operations.insert(2, [[], "n"])
            if page2transformation is not None:
                page2content = page2transformation(page2content)
            page2content = PageObject._content_stream_rename(
                page2content, rename, self.pdf
            )
            page2content = PageObject._push_pop_gs(page2content, self.pdf)
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
                ctm = [float(x) for x in ctm]
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

    def mergeTransformedPage(self, page2, ctm, expand=False):
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
        self._merge_page(
            page2,
            lambda page2Content: PageObject._add_transformation_matrix(
                page2Content, page2.pdf, ctm
            ),
            ctm,
            expand,
        )

    def mergeScaledPage(self, page2, scale, expand=False):
        """
        mergeScaledPage is similar to mergePage, but the stream to be merged
        is scaled by appling a transformation matrix.

        :param PageObject page2: The page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float scale: The scaling factor
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        # CTM to scale : [ sx 0 0 sy 0 0 ]
        return self.mergeTransformedPage(page2, [scale, 0, 0, scale, 0, 0], expand)

    def mergeRotatedPage(self, page2, rotation, expand=False):
        """
        mergeRotatedPage is similar to mergePage, but the stream to be merged
        is rotated by appling a transformation matrix.

        :param PageObject page2: the page to be merged into this one. Should be
            an instance of :class:`PageObject<PageObject>`.
        :param float rotation: The angle of the rotation, in degrees
        :param bool expand: Whether the page should be expanded to fit the
            dimensions of the page to be merged.
        """
        rotation = math.radians(rotation)
        return self.mergeTransformedPage(
            page2,
            [
                math.cos(rotation),
                math.sin(rotation),
                -math.sin(rotation),
                math.cos(rotation),
                0,
                0,
            ],
            expand,
        )

    def mergeTranslatedPage(self, page2, tx, ty, expand=False):
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
        return self.mergeTransformedPage(page2, [1, 0, 0, 1, tx, ty], expand)

    def mergeRotatedTranslatedPage(self, page2, rotation, tx, ty, expand=False):
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

        translation = [[1, 0, 0], [0, 1, 0], [-tx, -ty, 1]]
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1],
        ]
        rtranslation = [[1, 0, 0], [0, 1, 0], [tx, ty, 1]]
        ctm = utils.matrix_multiply(translation, rotating)
        ctm = utils.matrix_multiply(ctm, rtranslation)

        return self.mergeTransformedPage(
            page2,
            [ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]],
            expand,
        )

    def mergeRotatedScaledPage(self, page2, rotation, scale, expand=False):
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
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1],
        ]
        scaling = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]]
        ctm = utils.matrix_multiply(rotating, scaling)

        return self.mergeTransformedPage(
            page2,
            [ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]],
            expand,
        )

    def mergeScaledTranslatedPage(self, page2, scale, tx, ty, expand=False):
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

        translation = [[1, 0, 0], [0, 1, 0], [tx, ty, 1]]
        scaling = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]]
        ctm = utils.matrix_multiply(scaling, translation)

        return self.mergeTransformedPage(
            page2,
            [ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]],
            expand,
        )

    def mergeRotatedScaledTranslatedPage(
        self, page2, rotation, scale, tx, ty, expand=False
    ):
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
        translation = [[1, 0, 0], [0, 1, 0], [tx, ty, 1]]
        rotation = math.radians(rotation)
        rotating = [
            [math.cos(rotation), math.sin(rotation), 0],
            [-math.sin(rotation), math.cos(rotation), 0],
            [0, 0, 1],
        ]
        scaling = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]]
        ctm = utils.matrix_multiply(rotating, scaling)
        ctm = utils.matrix_multiply(ctm, translation)

        return self.mergeTransformedPage(
            page2,
            [ctm[0][0], ctm[0][1], ctm[1][0], ctm[1][1], ctm[2][0], ctm[2][1]],
            expand,
        )

    def add_transformation(self, ctm):
        """
        Apply a transformation matrix to the page.

        :param tuple ctm: A 6-element tuple containing the operands of the
            transformation matrix.
        """
        original_content = self.get_contents()
        if original_content is not None:
            new_content = PageObject._add_transformation_matrix(
                original_content, self.pdf, ctm
            )
            new_content = PageObject._push_pop_gs(new_content, self.pdf)
            self[NameObject(PG.CONTENTS)] = new_content

    def addTransformation(self, ctm):
        warnings.warn(
            DEPR_MSG.format("addTransformation", "add_transformation"),
            PendingDeprecationWarning,
        )
        self.add_transformation(ctm)

    def scale(self, sx, sy):
        """
        Scale a page by the given factors by appling a transformation
        matrix to its content and updating the page size.

        :param float sx: The scaling factor on horizontal axis.
        :param float sy: The scaling factor on vertical axis.
        """
        self.add_transformation([sx, 0, 0, sy, 0, 0])
        self.mediaBox = RectangleObject(
            [
                float(self.mediaBox.getLowerLeft_x()) * sx,
                float(self.mediaBox.getLowerLeft_y()) * sy,
                float(self.mediaBox.getUpperRight_x()) * sx,
                float(self.mediaBox.getUpperRight_y()) * sy,
            ]
        )
        if PG.VP in self:
            viewport = self[PG.VP]
            if isinstance(viewport, ArrayObject):
                bbox = viewport[0]["/BBox"]
            else:
                bbox = viewport["/BBox"]
            scaled_bbox = RectangleObject(
                [
                    float(bbox[0]) * sx,
                    float(bbox[1]) * sy,
                    float(bbox[2]) * sx,
                    float(bbox[3]) * sy,
                ]
            )
            if isinstance(viewport, ArrayObject):
                self[NameObject(PG.VP)][NumberObject(0)][
                    NameObject("/BBox")
                ] = scaled_bbox
            else:
                self[NameObject(PG.VP)][NameObject("/BBox")] = scaled_bbox

    def scale_by(self, factor):
        """
        Scale a page by the given factor by appling a transformation
        matrix to its content and updating the page size.

        :param float factor: The scaling factor (for both X and Y axis).
        """
        self.scale(factor, factor)

    def scaleBy(self, factor):
        warnings.warn(
            DEPR_MSG.format("Page.scaleBy", "Page.scale_by"),
            PendingDeprecationWarning,
        )
        self.scale(factor, factor)

    def scale_to(self, width, height):
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

    def scaleTo(self, width, height):
        warnings.warn(
            DEPR_MSG.format("Page.scaleTo", "Page.scale_to"),
            PendingDeprecationWarning,
        )
        self.scale_to(width, height)

    def compress_content_streams(self):
        """
        Compress the size of this page by joining all content streams and
        applying a FlateDecode filter.

        However, it is possible that this function will perform no action if
        content stream compression becomes "automatic" for some reason.
        """
        content = self.get_contents()
        if content is not None:
            if not isinstance(content, ContentStream):
                content = ContentStream(content, self.pdf)
            self[NameObject(PG.CONTENTS)] = content.flateEncode()

    def compressContentStreams(self):
        warnings.warn(
            DEPR_MSG.format(
                "Page.compressContentStreams", "Page.compress_content_streams"
            ),
            PendingDeprecationWarning,
        )
        self.compress_content_streams()

    def extract_text(self, Tj_sep="", TJ_sep=""):
        """
        Locate all text drawing commands, in the order they are provided in the
        content stream, and extract the text.  This works well for some PDF
        files, but poorly for others, depending on the generator used.  This will
        be refined in the future.  Do not rely on the order of text coming out of
        this function, as it will change if this function is made more
        sophisticated.

        :return: a unicode string object.
        """
        text = u_("")
        content = self[PG.CONTENTS].get_object()
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

    def extractText(self, Tj_sep="", TJ_sep=""):
        warnings.warn(
            DEPR_MSG.format("Page.extractText", "Page.extract_text"),
        )
        return self.extract_text(Tj_sep=Tj_sep, TJ_sep=TJ_sep)

    mediaBox = _create_rectangle_accessor(PG.MEDIABOX, ())
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the boundaries of the physical medium on which the page is
    intended to be displayed or printed.
    """

    cropBox = _create_rectangle_accessor("/CropBox", (PG.MEDIABOX,))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the visible region of default user space.  When the page is
    displayed or printed, its contents are to be clipped (cropped) to this
    rectangle and then imposed on the output medium in some
    implementation-defined manner.  Default value: same as :attr:`mediaBox<mediaBox>`.
    """

    bleedBox = _create_rectangle_accessor("/BleedBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the region to which the contents of the page should be clipped
    when output in a production enviroment.
    """

    trimBox = _create_rectangle_accessor("/TrimBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the intended dimensions of the finished page after trimming.
    """

    artBox = _create_rectangle_accessor("/ArtBox", ("/CropBox", PG.MEDIABOX))
    """
    A :class:`RectangleObject<PyPDF2.generic.RectangleObject>`, expressed in default user space units,
    defining the extent of the page's meaningful content as intended by the
    page's creator.
    """
