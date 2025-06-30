"""Test the pypdf._utils module."""
import functools
import io
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

import pypdf._utils
from pypdf._utils import (
    File,
    Version,
    _get_max_pdf_version_header,
    _human_readable_bytes,
    check_if_whitespace_only,
    classproperty,
    deprecate_with_replacement,
    deprecation_no_replacement,
    mark_location,
    matrix_multiply,
    parse_iso8824_date,
    read_block_backwards,
    read_previous_line,
    read_until_regex,
    read_until_whitespace,
    rename_kwargs,
    skip_over_comment,
    skip_over_whitespace,
)
from pypdf.errors import DeprecationError, PdfReadError, PdfStreamError

from . import is_sublist

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent
RESOURCE_ROOT = PROJECT_ROOT / "resources"


@pytest.mark.parametrize(
    ("stream", "expected"),
    [
        (io.BytesIO(b"foo"), False),
        (io.BytesIO(b""), False),
        (io.BytesIO(b" "), True),
        (io.BytesIO(b"  "), True),
        (io.BytesIO(b"  \n"), True),
        (io.BytesIO(b"    \n"), True),
        (io.BytesIO(b"\f"), True),
    ],
)
def test_skip_over_whitespace(stream, expected):
    assert skip_over_whitespace(stream) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"foo", False),
        (b" a", False),
        (b" a\n b", False),
        (b"", True),
        (b" ", True),
        (b"  ", True),
        (b"  \n", True),
        (b"    \n", True),
        (b"\f", True),
    ],
)
def test_check_if_whitespace_only(value, expected):
    assert check_if_whitespace_only(value) is expected


def test_read_until_whitespace():
    assert read_until_whitespace(io.BytesIO(b"foo"), maxchars=1) == b"f"


@pytest.mark.parametrize(
    ("stream", "remainder"),
    [
        (io.BytesIO(b"% foobar\n"), b""),
        (io.BytesIO(b""), b""),
        (io.BytesIO(b" "), b" "),
        (io.BytesIO(b"% foo%\nbar"), b"bar"),
    ],
)
def test_skip_over_comment(stream, remainder):
    skip_over_comment(stream)
    assert stream.read() == remainder


def test_read_until_regex_premature_ending_name():
    stream = io.BytesIO(b"")
    assert read_until_regex(stream, re.compile(b".")) == b""


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (((3,),), ((7,),), ((21,),)),
        (((3, 7),), ((5,), (13,)), ((3 * 5.0 + 7 * 13,),)),
        (((3,), (7,)), ((5, 13),), ((3 * 5, 3 * 13), (7 * 5, 7 * 13))),
    ],
)
def test_matrix_multiply(a, b, expected):
    assert matrix_multiply(a, b) == expected


def test_mark_location():
    stream = io.BytesIO(b"abde" * 6000)
    mark_location(stream)
    Path("pypdf_pdfLocation.txt").unlink()  # cleanup


def test_deprecate_no_replacement():
    with pytest.warns(
            expected_warning=DeprecationWarning,
            match="foo is deprecated and will be removed in pypdf 3.0.0."
    ):
        pypdf._utils.deprecate_no_replacement("foo", removed_in="3.0.0")


@pytest.mark.parametrize(
    ("dat", "pos", "to_read", "expected", "expected_pos"),
    [
        (b"abc", 1, 0, b"", 1),
        (b"abc", 1, 1, b"a", 0),
        (b"abc", 2, 1, b"b", 1),
        (b"abc", 2, 2, b"ab", 0),
        (b"abc", 3, 1, b"c", 2),
        (b"abc", 3, 2, b"bc", 1),
        (b"abc", 3, 3, b"abc", 0),
        (b"", 0, 1, None, 0),
        (b"a", 0, 1, None, 0),
        (b"abc", 0, 10, None, 0),
    ],
)
def test_read_block_backwards(dat, pos, to_read, expected, expected_pos):
    s = io.BytesIO(dat)
    s.seek(pos)
    if expected is not None:
        assert read_block_backwards(s, to_read) == expected
    else:
        with pytest.raises(PdfStreamError):
            read_block_backwards(s, to_read)
    assert s.tell() == expected_pos


def test_read_block_backwards_at_start():
    s = io.BytesIO(b"abc")
    with pytest.raises(PdfStreamError) as _:
        read_previous_line(s)


@pytest.mark.parametrize(
    ("dat", "pos", "expected", "expected_pos"),
    [
        (b"abc", 1, b"a", 0),
        (b"abc", 2, b"ab", 0),
        (b"abc", 3, b"abc", 0),
        (b"abc\n", 3, b"abc", 0),
        (b"abc\n", 4, b"", 3),
        (b"abc\n\r", 4, b"", 3),
        (b"abc\nd", 5, b"d", 3),
        # Skip over multiple CR/LF bytes
        (b"abc\n\r\ndef", 9, b"def", 3),
    ],
    ids=list(range(8)),
)
def test_read_previous_line(dat, pos, expected, expected_pos):
    s = io.BytesIO(dat)
    s.seek(pos)
    assert read_previous_line(s) == expected
    assert s.tell() == expected_pos


# for unknown reason if the parameters are passed through pytest, errors are reported
def test_read_previous_line2():
    # Include a block full of newlines...
    test_read_previous_line(
        b"abc" + b"\n" * (2 * io.DEFAULT_BUFFER_SIZE) + b"d",
        2 * io.DEFAULT_BUFFER_SIZE + 4,
        b"d",
        3,
    )
    # Include a block full of non-newline characters
    test_read_previous_line(
        b"abc\n" + b"d" * (2 * io.DEFAULT_BUFFER_SIZE),
        2 * io.DEFAULT_BUFFER_SIZE + 4,
        b"d" * (2 * io.DEFAULT_BUFFER_SIZE),
        3,
    )
    # Both
    test_read_previous_line(
        b"abcxyz"
        + b"\n" * (2 * io.DEFAULT_BUFFER_SIZE)
        + b"d" * (2 * io.DEFAULT_BUFFER_SIZE),
        4 * io.DEFAULT_BUFFER_SIZE + 6,
        b"d" * (2 * io.DEFAULT_BUFFER_SIZE),
        6,
    )


def test_get_max_pdf_version_header():
    with pytest.raises(ValueError) as exc:
        _get_max_pdf_version_header(b"", b"PDF-1.2")
    assert exc.value.args[0] == "Neither b'' nor b'PDF-1.2' are proper headers"


def test_read_block_backwards_exception():
    stream = io.BytesIO(b"foobar")
    stream.seek(6)
    with pytest.raises(PdfReadError) as exc:
        read_block_backwards(stream, 7)
    assert exc.value.args[0] == "Could not read malformed PDF file"


def test_deprecate_with_replacement():
    def foo() -> None:
        deprecate_with_replacement("foo", "bar", removed_in="4.3.2")

    with pytest.warns(
        DeprecationWarning,
        match="foo is deprecated and will be removed in pypdf 4.3.2. Use bar instead.",
    ):
        foo()


def test_deprecation_no_replacement():
    def foo() -> None:
        deprecation_no_replacement("foo", removed_in="4.3.2")

    with pytest.raises(
        DeprecationError,
        match="foo is deprecated and was removed in pypdf 4.3.2.",
    ):
        foo()


def test_rename_kwargs():
    def deprecation_bookmark_nofail(**aliases: str) -> Callable:
        """
        Decorator for deprecated term "bookmark".

        To be used for methods and function arguments
            outline_item = a bookmark
            outline = a collection of outline items.
        """

        def decoration(func: Callable) -> Any:  # type: ignore
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:  # type: ignore
                rename_kwargs(func.__name__, kwargs, aliases, fail=False)
                return func(*args, **kwargs)

            return wrapper

        return decoration

    @deprecation_bookmark_nofail(old_param="new_param")
    def foo(old_param: int = 1, baz: int = 2, new_param: int = 1) -> None:
        pass

    expected_msg = (
        "foo received both old_param and new_param as an argument. "
        "old_param is deprecated. Use new_param instead."
    )
    with pytest.raises(TypeError, match=expected_msg):
        foo(old_param=12, new_param=13)

    with pytest.warns(
        DeprecationWarning,
        match="old_param is deprecated as an argument. Use new_param instead",
    ):
        foo(old_param=12)


def test_rename_kwargs__stacklevel(tmp_path: Path) -> None:
    script = tmp_path / "script.py"
    script.write_text("""
import functools
import warnings

from pypdf._utils import rename_kwargs

def deprecation(**aliases: str):
    def decoration(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            rename_kwargs(func.__name__, kwargs, aliases, fail=False)
            return func(*args, **kwargs)

        return wrapper

    return decoration

@deprecation(old_param="new_param")
def foo(old_param: int = 1, baz: int = 2, new_param: int = 1) -> None:
    pass

warnings.simplefilter("always")
foo(old_param=12)
    """)

    result = subprocess.run([sys.executable, script], capture_output=True, text=True)  # noqa: S603
    assert result.returncode == 0
    assert result.stderr == (
        f"{script}:23: DeprecationWarning: old_param is deprecated as an argument. "
        f"Use new_param instead\n  foo(old_param=12)\n"
    )


@pytest.mark.parametrize(
    ("input_int", "expected_output"),
    [
        (123, "123 Byte"),
        (1234, "1.2 kB"),
        (123_456, "123.5 kB"),
        (1_234_567, "1.2 MB"),
        (1_234_567_890, "1.2 GB"),
        (1_234_567_890_000, "1234.6 GB"),
    ],
)
def test_human_readable_bytes(input_int, expected_output):
    """_human_readable_bytes correctly transforms the integer to a string."""
    assert _human_readable_bytes(input_int) == expected_output


def test_file_class():
    """File class can be instantiated and string representation is ok."""
    f = File(name="image.png", data=b"")
    assert str(f) == "File(name=image.png, data: 0 Byte)"
    assert repr(f) == "File(name=image.png, data: 0 Byte, hash: 0)"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("D:20210318000756", "2021-03-18T00:07:56"),
        ("20210318000756", "2021-03-18T00:07:56"),
        ("D:2021", "2021-01-01T00:00:00"),
        ("D:202103", "2021-03-01T00:00:00"),
        ("D:20210304", "2021-03-04T00:00:00"),
        ("D:2021030402", "2021-03-04T02:00:00"),
        ("D:20210408054711", "2021-04-08T05:47:11"),
        ("D:20210408054711Z", "2021-04-08T05:47:11+00:00"),
        ("D:20210408054711Z00", "2021-04-08T05:47:11+00:00"),
        ("D:20210408054711Z0000", "2021-04-08T05:47:11+00:00"),
        ("D:20210408075331+02'00'", "2021-04-08T07:53:31+02:00"),
        ("D:20210408075331-03'00'", "2021-04-08T07:53:31-03:00"),
    ],
)
def test_parse_datetime(text, expected):
    date = parse_iso8824_date(text)
    date_str = (date.isoformat() + date.strftime("%z"))[: len(expected)]
    assert date_str == expected


def test_parse_datetime_err():
    with pytest.raises(ValueError) as ex:
        parse_iso8824_date("D:20210408T054711Z")
    assert ex.value.args[0] == "Can not convert date: D:20210408T054711Z"
    assert parse_iso8824_date("D:20210408054711").tzinfo is None


def test_is_sublist():
    # Basic checks:
    assert is_sublist([0, 1], [0, 1, 2]) is True
    assert is_sublist([0, 2], [0, 1, 2]) is True
    assert is_sublist([1, 2], [0, 1, 2]) is True
    assert is_sublist([0, 3], [0, 1, 2]) is False
    # Ensure order is checked:
    assert is_sublist([1, 0], [0, 1, 2]) is False
    # Ensure duplicates are handled:
    assert is_sublist([0, 1, 1], [0, 1, 1, 2]) is True
    assert is_sublist([0, 1, 1], [0, 1, 2]) is False
    # Edge cases with empty lists:
    assert is_sublist([], [0, 1, 2]) is True
    assert is_sublist([0, 1], []) is False
    # Self-sublist edge case:
    assert is_sublist([0, 1, 2], [0, 1, 2]) is True


@pytest.mark.parametrize(
    ("left", "right", "is_less_than"),
    [
        ("1", "2", True),
        ("2", "1", False),
        ("1", "1", False),
        ("1.0", "1.1", True),
        ("1", "1.1", True),
        # Suffix left
        ("1a", "2", True),
        ("2a", "1", False),
        ("1a", "1", False),
        ("1.0a", "1.1", True),
        # I'm not sure about that, but seems special enough that it
        # probably doesn't matter:
        ("1a", "1.1", False),
        # Suffix right
        ("1", "2a", True),
        ("2", "1a", False),
        ("1", "1a", True),
        ("1.0", "1.1a", True),
        ("1", "1.1a", True),
        ("", "0.0.0", True),
        # Just suffix matters ... hm, I think this is actually wrong:
        ("1.0a", "1.0", False),
        ("1.0", "1.0a", True),
    ],
)
def test_version_compare(left, right, is_less_than):
    assert (Version(left) < Version(right)) is is_less_than


def test_version_compare_equal_str():
    a = Version("1.0")
    assert a != "1.0"


def test_version_compare_lt_str():
    a = Version("1.0")
    with pytest.raises(ValueError) as exc:
        a < "1.0"  # noqa: B015
    assert exc.value.args[0] == "Version cannot be compared against <class 'str'>"


def test_bad_version():
    assert Version("a").components == [(0, "a")]


def test_version_eq_hash():
    version1 = Version("1.0")
    version2 = Version("1.0")
    version3 = Version("1.1")
    assert version1 == version2
    assert version1 != version3
    assert hash(version1) == hash(version2)
    assert hash(version1) != hash(version3)


def test_classproperty():
    class Container:
        @classproperty
        def value1(cls) -> int:  # noqa: N805
            return 42

        @classproperty
        def value2(cls) -> int:  # noqa: N805
            return 1337

        @classproperty
        def value3(cls) -> int:  # noqa: N805
            return 1

        @value3.getter
        def value3(cls) -> int:  # noqa: N805
            return 2

    assert Container.value1 == 42
    assert Container.value2 == 1337
    assert Container.value3 == 2
    assert Container().value1 == 42
    assert Container().value2 == 1337
    assert Container().value3 == 2
