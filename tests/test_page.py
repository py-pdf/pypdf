import json
import os
from copy import deepcopy
from io import BytesIO
from pathlib import Path

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
