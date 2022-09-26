import json
import os
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import List, Tuple

import pytest

from PyPDF2 import PdfReader, PdfWriter, Transformation
from PyPDF2._page import PageObject, set_custom_rtl
from PyPDF2.constants import PageAttributes as PG
from PyPDF2.errors import PdfReadWarning
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    RectangleObject,
    TextStringObject,
)

from . import get_pdf_from_url, normalize_warnings

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"
EXTERNAL_ROOT = PROJECT_ROOT / "sample-files"


def get_all_sample_files():
    with open(EXTERNAL_ROOT / "files.json") as fp:
        data = fp.read()
    meta = json.loads(data)
    return meta


all_files_meta = get_all_sample_files()


@pytest.mark.external()
@pytest.mark.parametrize(
    "meta",
    [m for m in all_files_meta["data"] if not m["encrypted"]],
    ids=[m["path"] for m in all_files_meta["data"] if not m["encrypted"]],
)
@pytest.mark.filterwarnings("ignore::PyPDF2.errors.PdfReadWarning")
def test_read(meta):
    pdf_path = EXTERNAL_ROOT / meta["path"]
    reader = PdfReader(pdf_path)
    try:
        reader.pages[0]
    except Exception:
        return
    assert len(reader.pages) == meta["pages"]


@pytest.mark.parametrize(
    ("pdf_path", "password"),
    [
        ("crazyones.pdf", None),
        ("attachment.pdf", None),
        (
            "libreoffice-writer-password.pdf",
            "openpassword",
        ),
        ("imagemagick-images.pdf", None),
        ("imagemagick-lzw.pdf", None),
        ("reportlab-inline-image.pdf", None),
        ("https://arxiv.org/pdf/2201.00029.pdf", None),
    ],
)
def test_page_operations(pdf_path, password):
    """
    This test just checks if the operation throws an exception.

    This should be done way more thoroughly: It should be checked if the
    output is as expected.
    """
    if pdf_path.startswith("http"):
        pdf_path = BytesIO(get_pdf_from_url(pdf_path, pdf_path.split("/")[-1]))
    else:
        pdf_path = RESOURCE_ROOT / pdf_path
    reader = PdfReader(pdf_path)

    if password:
        reader.decrypt(password)

    page: PageObject = reader.pages[0]

    t = Transformation().translate(50, 100).rotate(90)
    assert abs(t.ctm[4] + 100) < 0.01
    assert abs(t.ctm[5] - 50) < 0.01

    transformation = Transformation().rotate(90).scale(1).translate(1, 1)
    page.add_transformation(transformation, expand=True)
    page.add_transformation((1, 0, 0, 0, 0, 0))
    page.scale(2, 2)
    page.scale_by(0.5)
    page.scale_to(100, 100)
    page.compress_content_streams()
    page.extract_text()
    page.scale_by(0.5)
    page.scale_to(100, 100)
    page.extract_text()


def test_transformation_equivalence():
    pdf_path = RESOURCE_ROOT / "labeled-edges-center-image.pdf"
    reader_base = PdfReader(pdf_path)
    page_base = reader_base.pages[0]

    pdf_path = RESOURCE_ROOT / "box.pdf"
    reader_add = PdfReader(pdf_path)
    page_box = reader_add.pages[0]

    op = Transformation().scale(2).rotate(45)

    # Option 1: The new way
    page_box1 = deepcopy(page_box)
    page_base1 = deepcopy(page_base)
    page_box1.add_transformation(op, expand=True)
    page_base1.merge_page(page_box1, expand=False)

    # Option 2: The old way
    page_box2 = deepcopy(page_box)
    page_base2 = deepcopy(page_base)
    with pytest.warns(PendingDeprecationWarning):
        page_base2.mergeTransformedPage(page_box2, op, expand=False)

    # Should be the same
    assert page_base1[NameObject(PG.CONTENTS)] == page_base2[NameObject(PG.CONTENTS)]
    assert page_base1.mediabox == page_base2.mediabox
    assert page_base1.trimbox == page_base2.trimbox
    assert page_base1[NameObject(PG.ANNOTS)] == page_base2[NameObject(PG.ANNOTS)]
    compare_dict_objects(
        page_base1[NameObject(PG.RESOURCES)], page_base2[NameObject(PG.RESOURCES)]
    )


def test_get_user_unit_property():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    assert reader.pages[0].user_unit == 1


def compare_dict_objects(d1, d2):
    assert sorted(d1.keys()) == sorted(d2.keys())
    for k in d1.keys():
        if isinstance(d1[k], DictionaryObject):
            compare_dict_objects(d1[k], d2[k])
        else:
            assert d1[k] == d2[k]


def test_page_transformations():
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)

    page: PageObject = reader.pages[0]
    with pytest.warns(PendingDeprecationWarning):
        page.mergeRotatedPage(page, 90, expand=True)
    with pytest.warns(PendingDeprecationWarning):
        page.mergeRotatedScaledPage(page, 90, 1, expand=True)
    with pytest.warns(PendingDeprecationWarning):
        page.mergeRotatedScaledTranslatedPage(
            page, 90, scale=1, tx=1, ty=1, expand=True
        )
    with pytest.warns(PendingDeprecationWarning):
        page.mergeRotatedTranslatedPage(page, 90, 100, 100, expand=False)
    with pytest.warns(PendingDeprecationWarning):
        page.mergeScaledPage(page, 2, expand=False)
    with pytest.warns(PendingDeprecationWarning):
        page.mergeScaledTranslatedPage(page, 1, 1, 1)
    with pytest.warns(PendingDeprecationWarning):
        page.mergeTranslatedPage(page, 100, 100, expand=False)
    page.add_transformation((1, 0, 0, 0, 0, 0))


@pytest.mark.parametrize(
    ("pdf_path", "password"),
    [
        (RESOURCE_ROOT / "crazyones.pdf", None),
        (RESOURCE_ROOT / "attachment.pdf", None),
        (RESOURCE_ROOT / "side-by-side-subfig.pdf", None),
        (
            RESOURCE_ROOT / "libreoffice-writer-password.pdf",
            "openpassword",
        ),
    ],
)
def test_compress_content_streams(pdf_path, password):
    reader = PdfReader(pdf_path)
    if password:
        reader.decrypt(password)
    for page in reader.pages:
        page.compress_content_streams()


def test_page_properties():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    page = reader.pages[0]
    assert page.mediabox == RectangleObject((0, 0, 612, 792))
    assert page.cropbox == RectangleObject((0, 0, 612, 792))
    assert page.bleedbox == RectangleObject((0, 0, 612, 792))
    assert page.trimbox == RectangleObject((0, 0, 612, 792))
    assert page.artbox == RectangleObject((0, 0, 612, 792))

    page.bleedbox = RectangleObject((0, 1, 100, 101))
    assert page.bleedbox == RectangleObject((0, 1, 100, 101))


def test_page_rotation():
    reader = PdfReader(RESOURCE_ROOT / "crazyones.pdf")
    page = reader.pages[0]
    with pytest.raises(ValueError) as exc:
        page.rotate(91)
    assert exc.value.args[0] == "Rotation angle must be a multiple of 90"

    # test rotation
    assert page.rotation == 0
    page.rotation = 180
    assert page.rotation == 180
    page.rotation += 190
    assert page.rotation == 0

    # test transfer_rotate_to_content
    page.rotation -= 90
    page.transfer_rotation_to_content()
    assert (
        abs(float(page.mediabox.left) - 0) < 0.1
        and abs(float(page.mediabox.bottom) - 0) < 0.1
        and abs(float(page.mediabox.right) - 792) < 0.1
        and abs(float(page.mediabox.top) - 612) < 0.1
    )


def test_page_scale():
    op = Transformation()
    with pytest.raises(ValueError) as exc:
        op.scale()
    assert exc.value.args[0] == "Either sx or sy must be specified"

    assert op.scale(sx=2).ctm == (2, 0, 0, 2, 0, 0)
    assert op.scale(sy=3).ctm == (3, 0, 0, 3, 0, 0)


def test_add_transformation_on_page_without_contents():
    page = PageObject()
    page.add_transformation(Transformation())


def test_multi_language():
    reader = PdfReader(RESOURCE_ROOT / "multilang.pdf")
    txt = reader.pages[0].extract_text()
    assert "Hello World" in txt, "English not correctly extracted"
    # iss #1296
    assert "مرحبا بالعالم" in txt, "Arabic not correctly extracted"
    assert "Привет, мир" in txt, "Russian not correctly extracted"
    assert "你好世界" in txt, "Chinese not correctly extracted"
    assert "สวัสดีชาวโลก" in txt, "Thai not correctly extracted"
    assert "こんにちは世界" in txt, "Japanese not correctly extracted"
    # check customizations
    set_custom_rtl(None, None, "Russian:")
    assert (
        ":naissuR" in reader.pages[0].extract_text()
    ), "(1) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(None, None, [ord(x) for x in "Russian:"])
    assert (
        ":naissuR" in reader.pages[0].extract_text()
    ), "(2) CUSTOM_RTL_SPECIAL_CHARS failed"
    set_custom_rtl(0, 255, None)
    assert ":hsilgnE" in reader.pages[0].extract_text(), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl("A", "z", [])
    assert ":hsilgnE" in reader.pages[0].extract_text(), "CUSTOM_RTL_MIN/MAX failed"
    set_custom_rtl(-1, -1, [])  # to prevent further errors


def test_extract_text_single_quote_op():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/964/964029.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name="tika-964029.pdf")))
    for page in reader.pages:
        page.extract_text()


def test_no_ressources_on_text_extract():
    url = "https://github.com/py-pdf/PyPDF2/files/9428434/TelemetryTX_EM.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name="tika-964029.pdf")))
    for page in reader.pages:
        page.extract_text()


def test_iss_1142():
    # check fix for problem of context save/restore (q/Q)
    url = "https://github.com/py-pdf/PyPDF2/files/9150656/ST.2019.PDF"
    name = "st2019.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    txt = reader.pages[3].extract_text()
    assert txt.find("有限公司郑州分公司") > 0


@pytest.mark.parametrize(
    ("url", "name"),
    [
        # keyerror_potentially_empty_page
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/964/964029.pdf",
            "tika-964029.pdf",
        ),
        # 1140 / 1141:
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/932/932446.pdf",
            "tika-932446.pdf",
        ),
        # iss 1134:
        (
            "https://github.com/py-pdf/PyPDF2/files/9150656/ST.2019.PDF",
            "iss_1134.pdf",
        ),
        # iss 1:
        (
            "https://github.com/py-pdf/PyPDF2/files/9432350/Work.Flow.From.Check.to.QA.pdf",
            "WFCA.pdf",
        ),
    ],
)
def test_extract_text_page_pdf(url, name):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_extract_text_page_pdf_impossible_decode_xform(caplog):
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/972/972962.pdf"
    name = "tika-972962.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()
    warn_msgs = normalize_warnings(caplog.text)
    assert warn_msgs == [""]  # text extraction recognise no text


def test_extract_text_operator_t_star():  # L1266, L1267
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/967/967943.pdf"
    name = "tika-967943.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_extract_text_visitor_callbacks():
    """
    Extract text in rectangle-objects or simple tables.

    This test uses GeoBase_NHNC1_Data_Model_UML_EN.pdf.
    It extracts the labels of package-boxes in Figure 2.
    It extracts the texts in table "REVISION HISTORY".

    """
    import logging

    class PositionedText:
        """Specify a text with coordinates, font-dictionary and font-size.

        The font-dictionary may be None in case of an unknown font.
        """

        def __init__(self, text, x, y, font_dict, font_size) -> None:
            # TODO \0-replace: Encoding issue in some files?
            self.text = text.replace("\0", "")
            self.x = x
            self.y = y
            self.font_dict = font_dict
            self.font_size = font_size

        def get_base_font(self) -> str:
            """Gets the base font of the text.

            Return UNKNOWN in case of an unknown font."""
            if (self.font_dict is None) or "/BaseFont" not in self.font_dict:
                return "UNKNOWN"
            return self.font_dict["/BaseFont"]

    class Rectangle:
        """Specify a rectangle."""

        def __init__(self, x, y, w, h) -> None:
            self.x = x.as_numeric()
            self.y = y.as_numeric()
            self.w = w.as_numeric()
            self.h = h.as_numeric()

        def contains(self, x, y) -> bool:
            return (
                x >= self.x
                and x <= (self.x + self.w)
                and y >= self.y
                and y <= (self.y + self.h)
            )

    def extract_text_and_rectangles(
        page: PageObject, rect_filter=None
    ) -> Tuple[List[PositionedText], List[Rectangle]]:
        """
        Extracts texts and rectangles of a page of type PyPDF2._page.PageObject.

        This function supports simple coordinate transformations only.
        The optional rect_filter-lambda can be used to filter wanted rectangles.
        rect_filter has Rectangle as argument and must return a boolean.

        It returns a tuple containing a list of extracted texts and
        a list of extracted rectangles.
        """

        logger = logging.getLogger("extract_text_and_rectangles")

        rectangles = []
        texts = []

        def print_op_b(op, args, cm_matrix, tm_matrix):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"before: {op} at {cm_matrix}, {tm_matrix}")
            if op == b"re":
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"  add rectangle: {args}")
                w = args[2]
                h = args[3]
                r = Rectangle(args[0], args[1], w, h)
                if (rect_filter is None) or rect_filter(r):
                    rectangles.append(r)

        def print_visi(text, cm_matrix, tm_matrix, font_dict, font_size):
            if text.strip() != "":
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"at {cm_matrix}, {tm_matrix}, font size={font_size}")
                texts.append(
                    PositionedText(
                        text, tm_matrix[4], tm_matrix[5], font_dict, font_size
                    )
                )

        visitor_before = print_op_b
        visitor_text = print_visi

        page.extract_text(
            visitor_operand_before=visitor_before, visitor_text=visitor_text
        )

        return (texts, rectangles)

    def extract_table(
        texts: List[PositionedText], rectangles: List[Rectangle]
    ) -> List[List[List[PositionedText]]]:
        """
        Extracts a table containing text.

        It is expected that each cell is marked by a rectangle-object.
        It is expected that the page contains one table only.
        It is expected that the table contains at least 3 columns and 2 rows.

        A list of rows is returned.
        Each row contains a list of cells.
        Each cell contains a list of PositionedText-elements.
        """
        logger = logging.getLogger("extractTable")

        # Step 1: Count number of x- and y-coordinates of rectangles.
        # Remove duplicate rectangles. The new list is rectangles_filtered.
        col2count = {}
        row2count = {}
        key2rectangle = {}
        rectangles_filtered = []
        for r in rectangles:
            # Coordinates may be inaccurate, we have to round.
            # cell: x=72.264, y=386.57, w=93.96, h=46.584
            # cell: x=72.271, y=386.56, w=93.96, h=46.59
            key = f"{round(r.x, 0)} {round(r.y, 0)} {round(r.w, 0)} {round(r.h, 0)}"
            if key in key2rectangle:
                # Ignore duplicate rectangles
                continue
            key2rectangle[key] = r
            if r.x not in col2count:
                col2count[r.x] = 0
            if r.y not in row2count:
                row2count[r.y] = 0
            col2count[r.x] += 1
            row2count[r.y] += 1
            rectangles_filtered.append(r)

        # Step 2: Look for texts in rectangles.
        rectangle2texts = {}
        for text in texts:
            for r in rectangles_filtered:
                if r.contains(text.x, text.y):
                    if r not in rectangle2texts:
                        rectangle2texts[r] = []
                    rectangle2texts[r].append(text)
                    break

        # PDF: y = 0 is expected at the bottom of the page.
        # So the header-row is expected to have the highest y-value.
        rectangles.sort(key=lambda r: (-r.y, r.x))

        # Step 3: Build the list of rows containing list of cell-texts.
        rows = []
        row_nr = 0
        col_nr = 0
        curr_y = None
        curr_row = None
        for r in rectangles_filtered:
            if col2count[r.x] < 3 or row2count[r.y] < 2:
                # We expect at least 3 columns and 2 rows.
                continue
            if curr_y is None or r.y != curr_y:
                # next row
                curr_y = r.y
                col_nr = 0
                row_nr += 1
                curr_row = []
                rows.append(curr_row)
            col_nr += 1
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"cell: x={r.x}, y={r.y}, w={r.w}, h={r.h}")
            if r not in rectangle2texts:
                curr_row.append("")
                continue
            cell_texts = [t for t in rectangle2texts[r]]
            curr_row.append(cell_texts)

        return rows

    def extract_cell_text(cell_texts: List[PositionedText]) -> str:
        """Joins the text-objects of a cell."""
        return ("".join(t.text for t in cell_texts)).strip()

    # Test 1: We test the analysis of page 7 "2.1 LRS model".
    reader = PdfReader(RESOURCE_ROOT / "GeoBase_NHNC1_Data_Model_UML_EN.pdf")
    page_lrs_model = reader.pages[6]

    # We ignore the invisible large rectangles.
    def ignore_large_rectangles(r):
        return r.w < 400 and r.h < 400

    (texts, rectangles) = extract_text_and_rectangles(
        page_lrs_model, rect_filter=ignore_large_rectangles
    )

    # We see ten rectangles (5 tabs, 5 boxes) but there are 64 rectangles (including some invisible ones).
    assert 60 == len(rectangles)
    rectangle2texts = {}
    for t in texts:
        for r in rectangles:
            if r.contains(t.x, t.y):
                texts = rectangle2texts.setdefault(r, [])
                texts.append(t.text.strip())
                break
    # Five boxes and the figure-description below.
    assert 6 == len(rectangle2texts)
    box_texts = [" ".join(texts) for texts in rectangle2texts.values()]
    assert "Hydro Network" in box_texts
    assert "Hydro Events" in box_texts
    assert "Metadata" in box_texts
    assert "Hydrography" in box_texts
    assert "Toponymy (external model)" in box_texts

    # Test 2: Parse table "REVISION HISTORY" on page 3.
    page_revisions = reader.pages[2]
    # We ignore the second table, therefore: r.y > 350

    def filter_first_table(r):
        return r.w > 1 and r.h > 1 and r.w < 400 and r.h < 400 and r.y > 350

    (texts, rectangles) = extract_text_and_rectangles(
        page_revisions, rect_filter=filter_first_table
    )
    rows = extract_table(texts, rectangles)

    assert len(rows) == 9
    assert extract_cell_text(rows[0][0]) == "Date"
    assert extract_cell_text(rows[0][1]) == "Version"
    assert extract_cell_text(rows[0][2]) == "Description"
    assert extract_cell_text(rows[1][0]) == "September 2002"
    # The line break between "English review;"
    # and "Remove" is not detected.
    assert (
        extract_cell_text(rows[6][2])
        == "English review;Remove the UML model for the Segmented view."
    )
    assert extract_cell_text(rows[7][2]) == "Update from the March Workshop comments."

    # Check the fonts. We check: /F2 9.96 Tf [...] [(Dat)-2(e)] TJ
    text_dat_of_date = rows[0][0][0]
    assert text_dat_of_date.font_dict is not None
    assert text_dat_of_date.font_dict["/Name"] == "/F2"
    assert text_dat_of_date.get_base_font() == "/Arial,Bold"
    assert text_dat_of_date.font_dict["/Encoding"] == "/WinAnsiEncoding"
    assert text_dat_of_date.font_size == 9.96
    # Check: /F1 9.96 Tf [...] [(S)4(ep)4(t)-10(em)-20(be)4(r)-3( 20)4(02)] TJ
    texts = rows[1][0][0]
    assert texts.font_dict is not None
    assert texts.font_dict["/Name"] == "/F1"
    assert texts.get_base_font() == "/Arial"
    assert texts.font_dict["/Encoding"] == "/WinAnsiEncoding"
    assert text_dat_of_date.font_size == 9.96


@pytest.mark.parametrize(
    ("pdf_path", "password", "embedded", "unembedded"),
    [
        (
            RESOURCE_ROOT / "crazyones.pdf",
            None,
            {
                "/HHXGQB+SFTI1440",
                "/TITXYI+SFRM0900",
                "/YISQAD+SFTI1200",
            },
            set(),
        ),
        (
            RESOURCE_ROOT / "attachment.pdf",
            None,
            {
                "/HHXGQB+SFTI1440",
                "/TITXYI+SFRM0900",
                "/YISQAD+SFTI1200",
            },
            set(),
        ),
        (
            RESOURCE_ROOT / "libreoffice-writer-password.pdf",
            "openpassword",
            {"/BAAAAA+DejaVuSans"},
            set(),
        ),
        (
            RESOURCE_ROOT / "imagemagick-images.pdf",
            None,
            set(),
            {"/Helvetica"},
        ),
        (RESOURCE_ROOT / "imagemagick-lzw.pdf", None, set(), set()),
        (
            RESOURCE_ROOT / "reportlab-inline-image.pdf",
            None,
            set(),
            {"/Helvetica"},
        ),
    ],
)
def test_get_fonts(pdf_path, password, embedded, unembedded):
    reader = PdfReader(pdf_path, password=password)
    a = set()
    b = set()
    for page in reader.pages:
        a_tmp, b_tmp = page._get_fonts()
        a = a.union(a_tmp)
        b = b.union(b_tmp)
    assert (a, b) == (embedded, unembedded)


def test_annotation_getter():
    pdf_path = RESOURCE_ROOT / "commented.pdf"
    reader = PdfReader(pdf_path)
    annotations = reader.pages[0].annotations
    assert annotations is not None
    assert isinstance(annotations[0], IndirectObject)

    annot_dict = dict(annotations[0].get_object())
    assert "/P" in annot_dict
    assert isinstance(annot_dict["/P"], IndirectObject)
    del annot_dict["/P"]

    annot_dict["/Popup"] = annot_dict["/Popup"].get_object()
    del annot_dict["/Popup"]["/P"]
    del annot_dict["/Popup"]["/Parent"]
    assert annot_dict == {
        "/Type": "/Annot",
        "/Subtype": "/Text",
        "/Rect": ArrayObject(
            [
                270.75,
                596.25,
                294.75,
                620.25,
            ]
        ),
        "/Contents": "Note in second paragraph",
        "/C": ArrayObject([1, 1, 0]),
        "/M": "D:20220406191858+02'00",
        "/Popup": DictionaryObject(
            {
                "/M": "D:20220406191847+02'00",
                "/Rect": ArrayObject([294.75, 446.25, 494.75, 596.25]),
                "/Subtype": "/Popup",
                "/Type": "/Annot",
            }
        ),
        "/T": "moose",
    }


def test_annotation_setter():
    # Arange
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    writer = PdfWriter()
    writer.add_page(page)

    # Act
    page_number = 0
    page_link = writer.get_object(writer._pages)["/Kids"][page_number]
    annot_dict = {
        NameObject("/P"): page_link,
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Text"),
        NameObject("/Rect"): ArrayObject(
            [
                FloatObject(270.75),
                FloatObject(596.25),
                FloatObject(294.75),
                FloatObject(620.25),
            ]
        ),
        NameObject("/Contents"): TextStringObject("Note in second paragraph"),
        NameObject("/C"): ArrayObject([FloatObject(1), FloatObject(1), FloatObject(0)]),
        NameObject("/M"): TextStringObject("D:20220406191858+02'00"),
        NameObject("/Popup"): DictionaryObject(
            {
                NameObject("/M"): TextStringObject("D:20220406191847+02'00"),
                NameObject("/Rect"): ArrayObject(
                    [
                        FloatObject(294.75),
                        FloatObject(446.25),
                        FloatObject(494.75),
                        FloatObject(596.25),
                    ]
                ),
                NameObject("/Subtype"): NameObject("/Popup"),
                NameObject("/Type"): TextStringObject("/Annot"),
            }
        ),
        NameObject("/T"): TextStringObject("moose"),
    }
    arr = ArrayObject()
    page.annotations = arr

    # Delete Annotations
    page.annotations = None

    d = DictionaryObject(annot_dict)
    ind_obj = writer._add_object(d)
    arr.append(ind_obj)

    # Assert manually
    target = "annot-out.pdf"
    with open(target, "wb") as fp:
        writer.write(fp)

    # Cleanup
    os.remove(target)  # remove for testing


@pytest.mark.xfail(reason="#1091")
def test_text_extraction_issue_1091():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/966/966635.pdf"
    name = "tika-966635.pdf"
    stream = BytesIO(get_pdf_from_url(url, name=name))
    with pytest.warns(PdfReadWarning):
        reader = PdfReader(stream)
    for page in reader.pages:
        page.extract_text()


def test_empyt_password_1088():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/941/941536.pdf"
    name = "tika-941536.pdf"
    stream = BytesIO(get_pdf_from_url(url, name=name))
    reader = PdfReader(stream)
    len(reader.pages)


@pytest.mark.xfail(reason="#1088 / #1126")
def test_arab_text_extraction():
    reader = PdfReader(EXTERNAL_ROOT / "015-arabic/habibi.pdf")
    assert reader.pages[0].extract_text() == "habibi حَبيبي"


def test_read_link_annotation():
    reader = PdfReader(EXTERNAL_ROOT / "016-libre-office-link/libre-office-link.pdf")
    assert len(reader.pages[0].annotations) == 1
    annot = dict(reader.pages[0].annotations[0].get_object())
    expected = {
        "/Type": "/Annot",
        "/Subtype": "/Link",
        "/A": DictionaryObject(
            {
                "/S": "/URI",
                "/Type": "/Action",
                "/URI": "https://martin-thoma.com/",
            }
        ),
        "/Border": ArrayObject([0, 0, 0]),
        "/Rect": [
            92.043,
            771.389,
            217.757,
            785.189,
        ],
    }

    assert set(expected.keys()) == set(annot.keys())
    del expected["/Rect"]
    del annot["/Rect"]
    assert annot == expected


def test_no_resources():
    url = "https://github.com/py-pdf/PyPDF2/files/9572045/108.pdf"
    name = "108.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    page_one = reader.pages[0]
    page_two = reader.pages[0]
    page_one.merge_page(page_two)
