import pytest

from PyPDF2.pagerange import PageRange, ParseError, parse_filename_page_ranges


def test_equality():
    pr1 = PageRange(slice(0, 5))
    pr2 = PageRange(slice(0, 5))
    assert pr1 == pr2


@pytest.mark.parametrize(
    "page_range,expected", [(slice(0, 5), "0:5"), (slice(0, 5, 2), "0:5:2")]
)
def test_str(page_range, expected):
    assert str(PageRange(page_range)) == expected


@pytest.mark.parametrize(
    "page_range,expected",
    [(slice(0, 5), "PageRange('0:5')"), (slice(0, 5, 2), "PageRange('0:5:2')")],
)
def test_repr(page_range, expected):
    assert repr(PageRange(page_range)) == expected


def test_equality_other_objectc():
    pr1 = PageRange(slice(0, 5))
    pr2 = "PageRange(slice(0, 5))"
    assert pr1 != pr2


def test_idempotency():
    pr = PageRange(slice(0, 5))
    pr2 = PageRange(pr)
    assert pr == pr2


@pytest.mark.parametrize(
    "range_str,expected",
    [
        ("42", slice(42, 43)),
        ("1:2", slice(1, 2)),
    ],
)
def test_str_init(range_str, expected):
    pr = PageRange(range_str)
    assert pr._slice == expected
    assert PageRange.valid


def test_str_init_error():
    init_str = "1-2"
    assert PageRange.valid(init_str) is False
    with pytest.raises(ParseError) as exc:
        PageRange(init_str)
    assert exc.value.args[0] == "1-2"


@pytest.mark.parametrize(
    "params,expected",
    [
        (["foo.pdf", "1:5"], [("foo.pdf", PageRange("1:5"))]),
        (
            ["foo.pdf", "1:5", "bar.pdf"],
            [("foo.pdf", PageRange("1:5")), ("bar.pdf", PageRange(":"))],
        ),
    ],
)
def test_parse_filename_page_ranges(params, expected):
    assert parse_filename_page_ranges(params) == expected


def test_parse_filename_page_ranges_err():
    with pytest.raises(ValueError):
        parse_filename_page_ranges(["1:5", "foo.pdf"])


def test_page_range_help():
    from PyPDF2.pagerange import PAGE_RANGE_HELP

    assert len(PAGE_RANGE_HELP) > 20
    assert "0:3" in PAGE_RANGE_HELP
    assert PAGE_RANGE_HELP.endswith("\n")
