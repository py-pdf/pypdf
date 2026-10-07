"""Test the pypdf.pagerange module."""
import pytest

from pypdf.pagerange import PageRange, ParseError, parse_filename_page_ranges


def test_equality():
    pr1 = PageRange(slice(0, 5))
    pr2 = PageRange(slice(0, 5))
    assert pr1 == pr2


def test_hash():
    pr1 = PageRange(slice(0, 5))
    pr2 = PageRange(slice(0, 5))
    pr3 = PageRange(slice(10, 11))
    pr4 = PageRange(slice(10, 11, 1))
    assert hash(pr1) == hash(pr2)
    assert hash(pr1) != hash(pr3)
    # Consider this different for now, although slicing with step size of 1 and `None` should be identical.
    assert hash(pr3) != hash(pr4)


@pytest.mark.parametrize(
    ("page_range", "expected"),
    [(slice(0, 5), "0:5"), (slice(0, 5, 2), "0:5:2"), ("-1", "-1:"), ("0", "0")],
)
def test_str(page_range, expected):
    assert str(PageRange(page_range)) == expected


@pytest.mark.parametrize(
    ("page_range", "expected"),
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
    ("range_str", "expected"),
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


@pytest.mark.parametrize("init_str", ["::0", "1:5:0", "0:0:0"])
def test_str_init_zero_step(init_str):
    """A zero stride selects nothing and only raised once the range was applied."""
    assert PageRange.valid(init_str) is False
    with pytest.raises(ParseError) as exc:
        PageRange(init_str)
    assert exc.value.args[0] == init_str


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (slice(1, 5), True),
        (PageRange("1:5"), True),
        ("1:5", True),
        (5, False),
        (None, False),
        (["1:5"], False),
    ],
)
def test_valid(value, expected):
    assert PageRange.valid(value) is expected


@pytest.mark.parametrize(
    ("params", "expected"),
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
    with pytest.raises(ValueError) as exc:
        parse_filename_page_ranges(["1:5", "foo.pdf"])
    assert (
        exc.value.args[0] == "The first argument must be a filename, not a page range."
    )


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (PageRange(slice(0, 5)), PageRange(slice(2, 10)), slice(0, 10)),
        (PageRange(slice(0, 5)), PageRange(slice(2, 3)), slice(0, 5)),
        (PageRange(slice(0, 5)), PageRange(slice(5, 10)), slice(0, 10)),
    ],
)
def test_addition(a, b, expected):
    pr1 = PageRange(a)
    pr2 = PageRange(b)
    assert pr1 + pr2 == PageRange(expected)
    assert pr2 + pr1 == PageRange(expected)  # addition is commutative


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (PageRange(slice(0, 5)), PageRange(slice(7, 10))),
        (PageRange(slice(7, 10)), PageRange(slice(0, 5))),
    ],
)
def test_addition_gap(a: PageRange, b: PageRange):
    with pytest.raises(ValueError) as exc:
        a + b
    assert exc.value.args[0] == "Can't add PageRanges with gap"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        # None start ("beginning") absorbs the other range's start.
        (PageRange(slice(None, 5)), PageRange(slice(2, 10)), slice(None, 10)),
        (PageRange(slice(0, 5)), PageRange(slice(None, 10)), slice(None, 10)),
        # None stop ("end") absorbs the other range's stop.
        (PageRange(slice(0, None)), PageRange(slice(2, 10)), slice(0, None)),
        # Both None on one side: fully open range swallows a bounded one.
        (PageRange(slice(None, None)), PageRange(slice(2, 5)), slice(None, None)),
        (PageRange(":"), PageRange(":"), slice(None, None)),
        # None start on one operand, None stop on the other: union covers everything.
        (PageRange(slice(0, None)), PageRange(slice(None, 5)), slice(None, None)),
    ],
)
def test_addition_none_bounds(a: PageRange, b: PageRange, expected: slice):
    assert a + b == PageRange(expected)
    assert b + a == PageRange(expected)  # addition is commutative


def test_addition_gap_with_none_start():
    # A None start ("beginning") must not be treated as covering the whole
    # range: the stop is still finite, so a real gap past it must still raise.
    a = PageRange(slice(None, 5))
    b = PageRange(slice(20, 30))
    with pytest.raises(ValueError) as exc:
        a + b
    assert exc.value.args[0] == "Can't add PageRanges with gap"


def test_addition_non_page_range():
    with pytest.raises(TypeError) as exc:
        PageRange(slice(0, 5)) + "2:7"
    assert exc.value.args[0] == "Can't add PageRange and <class 'str'>"


def test_addition_stride():
    a = PageRange(slice(0, 5, 2))
    b = PageRange(slice(7, 9))
    with pytest.raises(ValueError) as exc:
        a + b
    assert exc.value.args[0] == "Can't add PageRange with stride"
