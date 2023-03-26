from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from ..constants import AnnotationFlag
from ._base import (
    BooleanObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)
from ._data_structures import ArrayObject, DictionaryObject
from ._fit import DEFAULT_FIT, Fit
from ._rectangle import RectangleObject
from ._utils import hex_to_rgb, logger_warning

NO_FLAGS = AnnotationFlag(0)


def _get_bounding_rectangle(vertices: List[Tuple[float, float]]) -> RectangleObject:
    x_min, y_min = vertices[0][0], vertices[0][1]
    x_max, y_max = vertices[0][0], vertices[0][1]
    for x, y in vertices:
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = min(x_max, x)
        y_max = min(y_max, y)
    rect = RectangleObject((x_min, y_min, x_max, y_max))
    return rect


class AnnotationBuilder:
    """
    The AnnotationBuilder creates dictionaries representing PDF annotations.

    Those dictionaries can be modified before they are added to a PdfWriter
    instance via ``writer.add_annotation``.

    See `adding PDF annotations <../user/adding-pdf-annotations.html>`_ for
    it's usage combined with PdfWriter.
    """

    from ..types import FitType, ZoomArgType

    @staticmethod
    def text(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        text: str,
        open: bool = False,
        flags: int = 0,
    ) -> DictionaryObject:
        """
        Add text annotation.

        Args:
            rect: array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the clickable rectangular area
            text: The text that is added to the document
            open:
            flags:

        Returns:
            A dictionary object representing the annotation.
        """
        # TABLE 8.23 Additional entries specific to a text annotation
        text_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Text"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/Contents"): TextStringObject(text),
                NameObject("/Open"): BooleanObject(open),
                NameObject("/Flags"): NumberObject(flags),
            }
        )
        return text_obj

    @staticmethod
    def free_text(
        text: str,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        font: str = "Helvetica",
        bold: bool = False,
        italic: bool = False,
        font_size: str = "14pt",
        font_color: str = "000000",
        border_color: Optional[str] = "000000",
        background_color: Optional[str] = "ffffff",
    ) -> DictionaryObject:
        """
        Add text in a rectangle to a page.

        Args:
            text: Text to be added
            rect: array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the clickable rectangular area
            font: Name of the Font, e.g. 'Helvetica'
            bold: Print the text in bold
            italic: Print the text in italic
            font_size: How big the text will be, e.g. '14pt'
            font_color: Hex-string for the color, e.g. cdcdcd
            border_color: Hex-string for the border color, e.g. cdcdcd.
                Use ``None`` for no border.
            background_color: Hex-string for the background of the annotation,
                e.g. cdcdcd. Use ``None`` for transparent background.

        Returns:
            A dictionary object representing the annotation.
        """
        font_str = "font: "
        if bold is True:
            font_str = f"{font_str}bold "
        if italic is True:
            font_str = f"{font_str}italic "
        font_str = f"{font_str}{font} {font_size}"
        font_str = f"{font_str};text-align:left;color:#{font_color}"

        default_appearance_string = ""
        if border_color:
            for st in hex_to_rgb(border_color):
                default_appearance_string = f"{default_appearance_string}{st} "
            default_appearance_string = f"{default_appearance_string}rg"

        free_text = DictionaryObject()
        free_text.update(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/FreeText"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/Contents"): TextStringObject(text),
                # font size color
                NameObject("/DS"): TextStringObject(font_str),
                NameObject("/DA"): TextStringObject(default_appearance_string),
            }
        )
        if border_color is None:
            # Border Style
            free_text[NameObject("/BS")] = DictionaryObject(
                {
                    # width of 0 means no border
                    NameObject("/W"): NumberObject(0)
                }
            )
        if background_color is not None:
            free_text[NameObject("/C")] = ArrayObject(
                [FloatObject(n) for n in hex_to_rgb(background_color)]
            )
        return free_text

    @staticmethod
    def popup(
        *,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        flags: AnnotationFlag = NO_FLAGS,
        parent: Optional[DictionaryObject] = None,
        open: bool = False,
    ) -> DictionaryObject:
        """
        Add a popup to the document.

        Args:
            rect:
                Specifies the clickable rectangular area as `[xLL, yLL, xUR, yUR]`
            flags:
                1 - invisible, 2 - hidden, 3 - print, 4 - no zoom,
                5 - no rotate, 6 - no view, 7 - read only, 8 - locked,
                9 - toggle no view, 10 - locked contents
            open:
                Whether the popup should be shown directly (default is False).
            parent:
                The contents of the popup. Create this via the AnnotationBuilder.

        Returns:
            A dictionary object representing the annotation.
        """
        popup_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Popup"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/Open"): BooleanObject(open),
                NameObject("/F"): NumberObject(flags),
            }
        )
        if parent:
            # This needs to be an indirect object
            try:
                popup_obj[NameObject("/Parent")] = parent.indirect_reference
            except AttributeError:
                logger_warning(
                    "Unregistered Parent object : No Parent field set",
                    __name__,
                )

        return popup_obj

    @staticmethod
    def line(
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        text: str = "",
        title_bar: str = "",
    ) -> DictionaryObject:
        """
        Draw a line on the PDF.

        Args:
            p1: First point
            p2: Second point
            rect: array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the clickable rectangular area
            text: Text to be displayed as the line annotation
            title_bar: Text to be displayed in the title bar of the
                annotation; by convention this is the name of the author

        Returns:
            A dictionary object representing the annotation.
        """
        line_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Line"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/T"): TextStringObject(title_bar),
                NameObject("/L"): ArrayObject(
                    [
                        FloatObject(p1[0]),
                        FloatObject(p1[1]),
                        FloatObject(p2[0]),
                        FloatObject(p2[1]),
                    ]
                ),
                NameObject("/LE"): ArrayObject(
                    [
                        NameObject(None),
                        NameObject(None),
                    ]
                ),
                NameObject("/IC"): ArrayObject(
                    [
                        FloatObject(0.5),
                        FloatObject(0.5),
                        FloatObject(0.5),
                    ]
                ),
                NameObject("/Contents"): TextStringObject(text),
            }
        )
        return line_obj

    @staticmethod
    def polyline(
        vertices: List[Tuple[float, float]],
    ) -> DictionaryObject:
        """
        Draw a polyline on the PDF.

        Args:
            vertices: Array specifying the vertices (x, y) coordinates of the poly-line.

        Returns:
            A dictionary object representing the annotation.
        """
        if len(vertices) == 0:
            raise ValueError("A polygon needs at least 1 vertex with two coordinates")
        coord_list = []
        for x, y in vertices:
            coord_list.append(NumberObject(x))
            coord_list.append(NumberObject(y))
        polyline_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/PolyLine"),
                NameObject("/Vertices"): ArrayObject(coord_list),
                NameObject("/Rect"): RectangleObject(_get_bounding_rectangle(vertices)),
            }
        )
        return polyline_obj

    @staticmethod
    def rectangle(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        interiour_color: Optional[str] = None,
    ) -> DictionaryObject:
        """
        Draw a rectangle on the PDF.

        This method uses the /Square annotation type of the PDF format.

        Args:
            rect: array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the clickable rectangular area
            interiour_color: None or hex-string for the color, e.g. cdcdcd
                If None is used, the interiour is transparent.

        Returns:
            A dictionary object representing the annotation.
        """
        square_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Square"),
                NameObject("/Rect"): RectangleObject(rect),
            }
        )

        if interiour_color:
            square_obj[NameObject("/IC")] = ArrayObject(
                [FloatObject(n) for n in hex_to_rgb(interiour_color)]
            )

        return square_obj

    @staticmethod
    def highlight(
        *,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        quad_points: ArrayObject,
        highlight_color: str = "ff0000",
    ) -> DictionaryObject:
        """
        Add a highlight annotation to the document.

        Args:
            rect: Array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the highlighted area
            quad_points: An ArrayObject of 8 FloatObjects. Must match a word or
                a group of words, otherwise no highlight will be shown.
            highlight_color: The color used for the hightlight

        Returns:
            A dictionary object representing the annotation.
        """
        obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Highlight"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/QuadPoints"): quad_points,
                NameObject("/C"): ArrayObject(
                    [FloatObject(n) for n in hex_to_rgb(highlight_color)]
                ),
            }
        )
        return obj

    @staticmethod
    def ellipse(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        interiour_color: Optional[str] = None,
    ) -> DictionaryObject:
        """
        Draw a rectangle on the PDF.

        This method uses the /Circle annotation type of the PDF format.

        Args:
            rect: array of four integers ``[xLL, yLL, xUR, yUR]`` specifying
                the bounding box of the ellipse
            interiour_color: None or hex-string for the color, e.g. cdcdcd
                If None is used, the interiour is transparent.

        Returns:
            A dictionary object representing the annotation.
        """
        ellipse_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Circle"),
                NameObject("/Rect"): RectangleObject(rect),
            }
        )

        if interiour_color:
            ellipse_obj[NameObject("/IC")] = ArrayObject(
                [FloatObject(n) for n in hex_to_rgb(interiour_color)]
            )

        return ellipse_obj

    @staticmethod
    def polygon(vertices: List[Tuple[float, float]]) -> DictionaryObject:
        if len(vertices) == 0:
            raise ValueError("A polygon needs at least 1 vertex with two coordinates")

        coord_list = []
        for x, y in vertices:
            coord_list.append(NumberObject(x))
            coord_list.append(NumberObject(y))
        obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Polygon"),
                NameObject("/Vertices"): ArrayObject(coord_list),
                NameObject("/IT"): NameObject("PolygonCloud"),
                NameObject("/Rect"): RectangleObject(_get_bounding_rectangle(vertices)),
            }
        )
        return obj

    @staticmethod
    def link(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        border: Optional[ArrayObject] = None,
        url: Optional[str] = None,
        target_page_index: Optional[int] = None,
        fit: Fit = DEFAULT_FIT,
    ) -> DictionaryObject:
        """
        Add a link to the document.

        The link can either be an external link or an internal link.

        An external link requires the URL parameter.
        An internal link requires the target_page_index, fit, and fit args.

        Args:
            rect: array of four integers ``[xLL, yLL, xUR, yUR]``
                specifying the clickable rectangular area
            border: if provided, an array describing border-drawing
                properties. See the PDF spec for details. No border will be
                drawn if this argument is omitted.
                - horizontal corner radius,
                - vertical corner radius, and
                - border width
                - Optionally: Dash
            url: Link to a website (if you want to make an external link)
            target_page_index: index of the page to which the link should go
                (if you want to make an internal link)
            fit: Page fit or 'zoom' option.

        Returns:
            A dictionary object representing the annotation.
        """
        if TYPE_CHECKING:
            from ..types import BorderArrayType

        is_external = url is not None
        is_internal = target_page_index is not None
        if not is_external and not is_internal:
            raise ValueError(
                "Either 'url' or 'target_page_index' have to be provided. Both were None."
            )
        if is_external and is_internal:
            raise ValueError(
                "Either 'url' or 'target_page_index' have to be provided. "
                f"url={url}, target_page_index={target_page_index}"
            )

        border_arr: BorderArrayType
        if border is not None:
            border_arr = [NameObject(n) for n in border[:3]]
            if len(border) == 4:
                dash_pattern = ArrayObject([NameObject(n) for n in border[3]])
                border_arr.append(dash_pattern)
        else:
            border_arr = [NumberObject(0)] * 3

        link_obj = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Annot"),
                NameObject("/Subtype"): NameObject("/Link"),
                NameObject("/Rect"): RectangleObject(rect),
                NameObject("/Border"): ArrayObject(border_arr),
            }
        )
        if is_external:
            link_obj[NameObject("/A")] = DictionaryObject(
                {
                    NameObject("/S"): NameObject("/URI"),
                    NameObject("/Type"): NameObject("/Action"),
                    NameObject("/URI"): TextStringObject(url),
                }
            )
        if is_internal:
            # This needs to be updated later!
            dest_deferred = DictionaryObject(
                {
                    "target_page_index": NumberObject(target_page_index),
                    "fit": NameObject(fit.fit_type),
                    "fit_args": fit.fit_args,
                }
            )
            link_obj[NameObject("/Dest")] = dest_deferred
        return link_obj
