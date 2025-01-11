"""Test the pypdf._merger module."""
import sys
from io import BytesIO
from pathlib import Path

import pytest

import pypdf
from pypdf import PdfMerger, PdfReader, PdfWriter
from pypdf.errors import DeprecationError
from pypdf.generic import Destination, Fit

from . import get_data_from_url

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"

sys.path.append(str(PROJECT_ROOT))


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def merger_operate(merger):
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    outline = RESOURCE_ROOT / "pdflatex-outline.pdf"
    pdf_forms = RESOURCE_ROOT / "pdflatex-forms.pdf"
    pdf_pw = RESOURCE_ROOT / "libreoffice-writer-password.pdf"

    # string path:
    merger.append(pdf_path)
    merger.append(outline)
    merger.append(pdf_path, pages=pypdf.pagerange.PageRange(slice(0, 0)))
    merger.append(pdf_forms)
    merger.merge(0, pdf_path, import_outline=False)
    with pytest.raises(NotImplementedError) as exc:
        with open(pdf_path, "rb") as fp:
            data = fp.read()
        merger.append(data)
    assert exc.value.args[0].startswith(
        "Merging requires an object that PdfReader can parse. "
        "Typically, that is a Path"
    )

    # Merging an encrypted file
    reader = pypdf.PdfReader(pdf_pw)
    reader.decrypt("openpassword")
    merger.append(reader)

    # PdfReader object:
    r = pypdf.PdfReader(pdf_path)
    merger.append(r, outline_item="foo", pages=list(range(len(r.pages))))

    # File handle
    with open(pdf_path, "rb") as fh:
        merger.append(fh)

    # to force to build outlines and ensure the add_outline_item is
    # at end of the list
    merger.write(BytesIO())
    outline_item = merger.add_outline_item("An outline item", 0)
    oi2 = merger.add_outline_item(
        "deeper", 0, parent=outline_item, italic=True, bold=True
    )
    merger.add_outline_item(
        "Let's see", 2, oi2, (255, 255, 0), True, True, Fit.fit_box_vertically(left=12)
    )
    merger.add_outline_item(
        "The XYZ fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.xyz(left=10, top=20, zoom=3),
    )
    merger.add_outline_item(
        "The FitH fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.fit_horizontally(top=10),
    )
    merger.add_outline_item(
        "The FitV fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.fit_vertically(left=10),
    )
    merger.add_outline_item(
        "The FitR fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.fit_rectangle(left=10, bottom=20, right=30, top=40),
    )
    merger.add_outline_item(
        "The FitB fit", 0, outline_item, (255, 0, 15), True, True, Fit.fit_box()
    )
    merger.add_outline_item(
        "The FitBH fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.fit_box_horizontally(top=10),
    )
    merger.add_outline_item(
        "The FitBV fit",
        0,
        outline_item,
        (255, 0, 15),
        True,
        True,
        Fit.fit_box_vertically(left=10),
    )

    found_oi = merger.find_outline_item("nothing here")
    assert found_oi is None

    found_oi = merger.find_outline_item("foo")
    assert found_oi == [9]

    merger.add_metadata({"/Author": "Martin Thoma"})
    merger.add_named_destination("/Title", 0)
    merger.set_page_layout("/SinglePage")
    merger.page_mode = "/UseThumbs"


def check_outline(tmp_path):
    # Check if outline is correct
    reader = pypdf.PdfReader(tmp_path)
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


def test_merger_operations_by_semi_traditional_usage_with_writer(tmp_path):
    path = tmp_path / tmp_filename

    with PdfWriter() as merger:
        merger_operate(merger)
        merger.write(path)  # Act

    # Assert
    assert Path(path).is_file()
    check_outline(path)


def test_merger_operation_by_new_usage_with_writer(tmp_path):
    path = tmp_path / tmp_filename
    with PdfWriter(fileobj=path) as merger:
        merger_operate(merger)

    # Assert
    assert Path(path).is_file()
    check_outline(path)


def test_merge_page_exception_with_writer():
    merger = pypdf.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    with pytest.raises(TypeError) as exc:
        merger.merge(0, pdf_path, pages="a:b")
    assert (
        exc.value.args[0]
        == '"pages" must be a tuple of (start, stop[, step]) or a list'
    )
    merger.close()


def test_merge_page_tuple_with_writer():
    merger = pypdf.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.merge(0, pdf_path, pages=(0, 1))
    merger.close()


def test_merge_write_closed_fh_with_writer(pdf_file_path):
    merger = pypdf.PdfWriter()
    pdf_path = RESOURCE_ROOT / "crazyones.pdf"
    merger.append(pdf_path)

    merger.close()
    merger.write(pdf_file_path)
    merger.add_metadata({"author": "Martin Thoma"})
    merger.set_page_layout("/SinglePage")
    merger.page_mode = "/UseNone"
    merger.add_outline_item("An outline item", 0)


@pytest.mark.enable_socket
def test_trim_outline_list_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381771/tika-995175.pdf"
    name = "tika-995175.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.add_outline_item_dict(merger.outline[0])
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
def test_zoom_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381769/tika-994759.pdf"
    name = "tika-994759.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_zoom_xyz_no_left_with_add_page(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381704/tika-933322.pdf"
    name = "tika-933322.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    for p in reader.pages:
        merger.add_page(p)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
def test_zoom_xyz_no_left_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381704/tika-933322.pdf"
    name = "tika-933322.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.slow
def test_outline_item_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381773/tika-997511.pdf"
    name = "tika-997511.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.slow
def test_trim_outline_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381759/tika-982336.pdf"
    name = "tika-982336.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.slow
def test1_with_writer(pdf_file_path):
    url = "https://github.com/user-attachments/files/18381696/tika-923621.pdf"
    name = "tika-923621.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()


@pytest.mark.enable_socket
@pytest.mark.slow
def test_sweep_recursion1_with_writer(pdf_file_path):
    # TODO: This test looks like an infinite loop.
    url = "https://github.com/user-attachments/files/18381697/tika-924546.pdf"
    name = "tika-924546.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()

    reader2 = PdfReader(pdf_file_path)
    reader2.pages


@pytest.mark.enable_socket
@pytest.mark.slow
@pytest.mark.parametrize(
    ("url", "name"),
    [
        (
            # TODO: This test looks like an infinite loop.
            "https://github.com/user-attachments/files/18381700/tika-924794.pdf",
            "tika-924794.pdf",
        ),
        (
            "https://github.com/user-attachments/files/18381697/tika-924546.pdf",
            "tika-924546.pdf",
        ),
    ],
)
def test_sweep_recursion2_with_writer(url, name, pdf_file_path):
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()

    reader2 = PdfReader(pdf_file_path)
    reader2.pages


@pytest.mark.enable_socket
def test_sweep_indirect_list_newobj_is_none_with_writer(caplog, pdf_file_path):
    url = "https://github.com/user-attachments/files/18381681/tika-906769.pdf"
    name = "tika-906769.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url, name=name)))
    merger = PdfWriter()
    merger.append(reader)
    merger.write(pdf_file_path)
    merger.close()
    # used to be: assert "Object 21 0 not defined." in caplog.text

    reader2 = PdfReader(pdf_file_path)
    reader2.pages


@pytest.mark.enable_socket
def test_iss1145_with_writer():
    # issue with FitH destination with null param
    url = "https://github.com/py-pdf/pypdf/files/9164743/file-0.pdf"
    name = "iss1145.pdf"
    merger = PdfWriter()
    merger.append(PdfReader(BytesIO(get_data_from_url(url, name=name))))
    merger.close()


@pytest.mark.enable_socket
def test_iss1344_with_writer(caplog):
    url = "https://github.com/py-pdf/pypdf/files/9549001/input.pdf"
    name = "iss1344.pdf"
    m = PdfWriter()
    m.append(PdfReader(BytesIO(get_data_from_url(url, name=name))))
    b = BytesIO()
    m.write(b)
    p = PdfReader(b).pages[0]
    assert "/DIJMAC+Arial Black" in p._debug_for_extract()
    assert "adresse où le malade peut être visité" in p.extract_text()


@pytest.mark.enable_socket
def test_articles_with_writer(caplog):
    url = "https://github.com/user-attachments/files/18381699/tika-924666.pdf"
    name = "924666.pdf"
    m = PdfWriter()
    m.append(PdfReader(BytesIO(get_data_from_url(url, name=name))), (2, 10))
    b = BytesIO()
    m.write(b)
    r = PdfReader(b)
    assert len(r.threads) == 4
    assert r.threads[0].get_object()["/F"]["/P"] == r.pages[0]


def test_deprecate_pdfmerger():
    with pytest.raises(DeprecationError), PdfMerger() as merger:
        merger.append(RESOURCE_ROOT / "crazyones.pdf")


def test_get_reference():
    writer = PdfWriter(RESOURCE_ROOT / "crazyones.pdf")
    assert writer.get_reference(writer.pages[0]) == writer.pages[0].indirect_reference
