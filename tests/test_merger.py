import os
import sys
from io import BytesIO
from pathlib import Path

import pytest

import PyPDF2
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PyPDF2.generic import Destination

from . import get_pdf_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"

sys.path.append(str(PROJECT_ROOT))


def merger_operate(merger):
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    outline = RESOURCE_ROOT / "pdflatex-outline.pdf"
    pdf_forms = RESOURCE_ROOT / "pdflatex-forms.pdf"
    pdf_pw = RESOURCE_ROOT / "libreoffice-writer-password.pdf"

    # string path:
    merger.append(pdf_path)
    merger.append(outline)
    merger.append(pdf_path, pages=PyPDF2.pagerange.PageRange(slice(0, 0)))
    merger.append(pdf_forms)
    merger.merge(0, pdf_path, import_outline=False)
    with pytest.raises(NotImplementedError) as exc:
        with open(pdf_path, "rb") as fp:
            data = fp.read()
        merger.append(data)
    assert exc.value.args[0].startswith(
        "PdfMerger.merge requires an object that PdfReader can parse. "
        "Typically, that is a Path"
    )

    # Merging an encrypted file
    reader = PyPDF2.PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    merger.append(reader)

    # PdfReader object:
    merger.append(PyPDF2.PdfReader(pdf_path), outline_item="foo")

    # File handle
    with open(pdf_path, "rb") as fh:
        merger.append(fh)

    merger.write(
        BytesIO()
    )  # to force to build outlines and ensur the add_outline_item is at end of the list
    outline_item = merger.add_outline_item("An outline item", 0)
    oi2 = merger.add_outline_item(
        "deeper", 0, parent=outline_item, italic=True, bold=True
    )
    merger.add_outline_item(
        "Let's see", 2, oi2, (255, 255, 0), True, True, "/FitBV", 12
    )
    merger.add_outline_item(
        "The XYZ fit", 0, outline_item, (255, 0, 15), True, True, "/XYZ", 10, 20, 3
    )
    merger.add_outline_item(
        "The FitH fit", 0, outline_item, (255, 0, 15), True, True, "/FitH", 10
    )
    merger.add_outline_item(
        "The FitV fit", 0, outline_item, (255, 0, 15), True, True, "/FitV", 10
    )
    merger.add_outline_item(
        "The FitR fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        "/FitR",
        10,
        20,
        30,
        40,
    )
    merger.add_outline_item(
        "The FitB fit", 0, outline_item, (255, 0, 15), True, True, "/FitB"
    )
    merger.add_outline_item(
        "The FitBH fit", 0, outline_item, (255, 0, 15), True, True, "/FitBH", 10
    )
    merger.add_outline_item(
        "The FitBV fit", 0, outline_item, (255, 0, 15), True, True, "/FitBV", 10
    )

    found_oi = merger.find_outline_item("nothing here")
    assert found_oi is None

    found_oi = merger.find_outline_item("foo")
    assert found_oi == [9]

    merger.add_metadata({"/Author": "Martin Thoma"})
    merger.add_named_destination("/Title", 0)
    merger.set_page_layout("/SinglePage")
    merger.set_page_mode("/UseThumbs")


def check_outline(tmp_path):
    # Check if outline is correct
    reader = PyPDF2.PdfReader(tmp_path)
    assert [el.title for el in reader.outline if isinstance(el, Destination)] == [
        "Foo",
        "Bar",
        "Baz",
        "Foo",
        "Bar",
        "Baz",
        "Foo",
        "Bar",
        "Baz",
        "foo",
        "An outline item",  # this has been moved to end normal???
    ]

    # TODO: There seem to be no destinations for those links?


tmp_filename = "dont_commit_merged.pdf"


def test_merger_operations_by_traditional_usage(tmp_path):
    # Arrange
    merger = PdfMerger()
    merger_operate(merger)
    path = tmp_path / tmp_filename

    # Act
    merger.write(path)
    merger.close()

    # Assert
    check_outline(path)


def test_merger_operations_by_traditional_usage_with_writer(tmp_path):
    # Arrange
    merger = PdfWriter()
    merger_operate(merger)
    path = tmp_path / tmp_filename

    # Act
    merger.write(path)
    merger.close()
    # Assert
    check_outline(path)


def test_merger_operations_by_semi_traditional_usage(tmp_path):
    path = tmp_path / tmp_filename

    with PdfMerger() as merger:
        merger_operate(merger)
        merger.write(path)  # Act

    # Assert
    assert os.path.isfile(path)
    check_outline(path)


def test_merger_operations_by_semi_traditional_usage_with_writer(tmp_path):
    path = tmp_path / tmp_filename

    with PdfWriter() as merger:
        merger_operate(merger)
        merger.write(path)  # Act

    # Assert
    assert os.path.isfile(path)
    check_outline(path)


def test_merger_operation_by_new_usage(tmp_path):
    path = tmp_path / tmp_filename
    with PdfMerger(fileobj=path) as merger:
        merger_operate(merger)
    # Assert
    assert os.path.isfile(path)
    check_outline(path)


def test_merger_operation_by_new_usage_with_writer(tmp_path):
    path = tmp_path / tmp_filename
    with PdfWriter(fileobj=path) as merger:
        merger_operate(merger)

    # Assert
    assert os.path.isfile(path)
    check_outline(path)


def test_merge_page_exception():
    merger = PyPDF2.PdfMerger()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    with pytest.raises(TypeError) as exc:
        merger.merge(0, pdf_path, pages="a:b")
    assert exc.value.args[0] == '"pages" must be a tuple of (start, stop[, step])'
    merger.close()


def test_merge_page_exception_with_writer():
    merger = PyPDF2.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    with pytest.raises(TypeError) as exc:
        merger.merge(0, pdf_path, pages="a:b")
    assert (
        exc.value.args[0]
        == '"pages" must be a tuple of (start, stop[, step]) or a list'
    )
    merger.close()


def test_merge_page_tuple():
    merger = PyPDF2.PdfMerger()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.merge(0, pdf_path, pages=(0, 1))
    merger.close()


def test_merge_page_tuple_with_writer():
    merger = PyPDF2.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.merge(0, pdf_path, pages=(0, 1))
    merger.close()


def test_merge_write_closed_fh():
    merger = PyPDF2.PdfMerger()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.append(pdf_path)

    err_closed = "close() was called and thus the writer cannot be used anymore"

    merger.close()
    with pytest.raises(RuntimeError) as exc:
        merger.write("stream.pdf")
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger.add_metadata({"author": "Martin Thoma"})
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger.set_page_layout("/SinglePage")
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger.set_page_mode("/UseNone")
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger._write_outline()
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger.add_outline_item("An outline item", 0)
    assert exc.value.args[0] == err_closed

    with pytest.raises(RuntimeError) as exc:
        merger._write_dests()
    assert exc.value.args[0] == err_closed


def test_merge_write_closed_fh_with_writer():
    merger = PyPDF2.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.append(pdf_path)

    # err_closed = "close() was called and thus the writer cannot be used anymore"

    merger.close()
    # with pytest.raises(RuntimeError) as exc:
    merger.write("stream.pdf")
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    merger.add_metadata({"author": "Martin Thoma"})
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    merger.set_page_layout("/SinglePage")
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    merger.set_page_mode("/UseNone")
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    #    merger._write_outline()
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    merger.add_outline_item("An outline item", 0)
    # assert exc.value.args[0] == err_closed

    # with pytest.raises(RuntimeError) as exc:
    #    merger._write_dests()
    # assert exc.value.args[0] == err_closed


@pytest.mark.external
def test_trim_outline_list():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/995/995175.pdf"
    name = "tika-995175.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_trim_outline_list_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/995/995175.pdf"
    name = "tika-995175.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_zoom():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/994/994759.pdf"
    name = "tika-994759.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_zoom_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/994/994759.pdf"
    name = "tika-994759.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_zoom_xyz_no_left():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/933/933322.pdf"
    name = "tika-933322.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_zoom_xyz_no_left_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/933/933322.pdf"
    name = "tika-933322.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_outline_item():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/997/997511.pdf"
    name = "tika-997511.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_outline_item_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/997/997511.pdf"
    name = "tika-997511.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_trim_outline():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/982/982336.pdf"
    name = "tika-982336.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_trim_outline_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/982/982336.pdf"
    name = "tika-982336.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test1():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/923/923621.pdf"
    name = "tika-923621.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test1_with_writer():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/923/923621.pdf"
    name = "tika-923621.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_sweep_recursion1():
    # TODO: This test looks like an infinite loop.
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf"
    name = "tika-924546.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
def test_sweep_recursion1_with_writer():
    # TODO: This test looks like an infinite loop.
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf"
    name = "tika-924546.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            # TODO: This test looks like an infinite loop.
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924794.pdf",
            "tika-924794.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf",
            "tika-924546.pdf",
        ),
    ],
)
def test_sweep_recursion2(url, name):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
@pytest.mark.slow
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            # TODO: This test looks like an infinite loop.
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924794.pdf",
            "tika-924794.pdf",
        ),
        (
            "https://corpora.tika.apache.org/base/docs/govdocs1/924/924546.pdf",
            "tika-924546.pdf",
        ),
    ],
)
def test_sweep_recursion2_with_writer(url, name):
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_sweep_indirect_list_newobj_is_none(caplog):
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/906/906769.pdf"
    name = "tika-906769.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfMerger()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()
    # used to be: assert "Object 21 0 not defined." in caplog.text

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_sweep_indirect_list_newobj_is_none_with_writer(caplog):
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/906/906769.pdf"
    name = "tika-906769.pdf"
    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write("tmp-merger-do-not-commit.pdf")
    merger.close()
    # used to be: assert "Object 21 0 not defined." in caplog.text

    reader2 = PdfReader("tmp-merger-do-not-commit.pdf")
    reader2.pages

    # cleanup
    os.remove("tmp-merger-do-not-commit.pdf")


@pytest.mark.external
def test_iss1145():
    # issue with FitH destination with null param
    url = "https://github.com/py-pdf/PyPDF2/files/9164743/file-0.pdf"
    name = "iss1145.pdf"
    merger = PdfMerger()
    merger.append(PdfReader(BytesIO(get_pdf_from_url(url, name=name))))
    merger.close()


@pytest.mark.external
def test_iss1145_with_writer():
    # issue with FitH destination with null param
    url = "https://github.com/py-pdf/PyPDF2/files/9164743/file-0.pdf"
    name = "iss1145.pdf"
    merger = PdfWriter()
    merger.append(PdfReader(BytesIO(get_pdf_from_url(url, name=name))))
    merger.close()


def test_deprecate_bookmark_decorator_warning():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    merger = PdfMerger()
    with pytest.warns(
        UserWarning,
        match="import_bookmarks is deprecated as an argument. Use import_outline instead",
    ):
        merger.merge(0, reader, import_bookmarks=True)


def test_deprecate_bookmark_decorator_warning_with_writer():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    merger = PdfWriter()
    with pytest.warns(
        UserWarning,
        match="import_bookmarks is deprecated as an argument. Use import_outline instead",
    ):
        merger.merge(0, reader, import_bookmarks=True)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_deprecate_bookmark_decorator_output():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    merger = PdfMerger()
    merger.merge(0, reader, import_bookmarks=True)
    first_oi_title = 'Valid Destination: Action /GoTo Named Destination "section.1"'
    assert merger.outline[0].title == first_oi_title


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_deprecate_bookmark_decorator_output_with_writer():
    reader = PdfReader(RESOURCE_ROOT / "outlines-with-invalid-destinations.pdf")
    merger = PdfWriter()
    merger.merge(0, reader, import_bookmarks=True)
    first_oi_title = 'Valid Destination: Action /GoTo Named Destination "section.1"'
    # TODO? :  add outline property ???
    # assert merger.outline[0].title == first_oi_title
    assert merger.find_outline_item(first_oi_title) == [0]


@pytest.mark.external
def test_iss1344(caplog):
    url = "https://github.com/py-pdf/PyPDF2/files/9549001/input.pdf"
    name = "iss1344.pdf"
    m = PdfMerger()
    m.append(PdfReader(BytesIO(get_pdf_from_url(url, name=name))))
    b = BytesIO()
    m.write(b)
    r = PdfReader(b)
    p = r.pages[0]
    assert "/DIJMAC+Arial Black" in p._debug_for_extract()
    assert "adresse où le malade peut être visité" in p.extract_text()
    assert r.threads is None


@pytest.mark.external
def test_iss1344_with_writer(caplog):
    url = "https://github.com/py-pdf/PyPDF2/files/9549001/input.pdf"
    name = "iss1344.pdf"
    m = PdfWriter()
    m.append(PdfReader(BytesIO(get_pdf_from_url(url, name=name))))
    b = BytesIO()
    m.write(b)
    p = PdfReader(b).pages[0]
    assert "/DIJMAC+Arial Black" in p._debug_for_extract()
    assert "adresse où le malade peut être visité" in p.extract_text()


@pytest.mark.external
def test_articles_with_writer(caplog):
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/924/924666.pdf"
    name = "924666.pdf"
    m = PdfWriter()
    m.append(PdfReader(BytesIO(get_pdf_from_url(url, name=name))), (2, 10))
    b = BytesIO()
    m.write(b)
    r = PdfReader(b)
    assert len(r.threads) == 4
    assert r.threads[0].get_object()["/F"]["/P"] == r.pages[0]
