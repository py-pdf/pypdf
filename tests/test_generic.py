import os
from io import BytesIO

import pytest

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.constants import TypFitArguments as TF
from PyPDF2.errors import PdfReadError, PdfReadWarning, PdfStreamError
from PyPDF2.generic import (
    ArrayObject,
    Bookmark,
    BooleanObject,
    ByteStringObject,
    Destination,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    RectangleObject,
    TextStringObject,
    TreeObject,
    create_string_object,
    encode_pdfdocencoding,
    read_hex_string_from_stream,
    read_object,
    read_string_from_stream,
)

from . import get_pdf_from_url

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TESTS_ROOT)
RESOURCE_ROOT = os.path.join(PROJECT_ROOT, "resources")


def test_float_object_exception():
    assert FloatObject("abc") == 0


def test_number_object_exception():
    with pytest.raises(OverflowError):
        NumberObject(1.5 * 2**10000)


def test_create_string_object_exception():
    with pytest.raises(TypeError) as exc:
        create_string_object(123)
    assert (  # typeguard is not running
        exc.value.args[0] == "create_string_object should have str or unicode arg"
    ) or (  # typeguard is enabled
        'type of argument "string" must be one of (str, bytes); got int instead'
        in exc.value.args[0]
    )


@pytest.mark.parametrize(
    ("value", "expected", "tell"), [(b"true", b"true", 4), (b"false", b"false", 5)]
)
def test_boolean_object(value, expected, tell):
    stream = BytesIO(value)
    assert BooleanObject.read_from_stream(stream).value == (expected == b"true")
    stream.seek(0, 0)
    assert stream.read() == expected
    assert stream.tell() == tell


def test_boolean_object_write():
    stream = BytesIO()
    boolobj = BooleanObject(None)
    boolobj.write_to_stream(stream, encryption_key=None)
    stream.seek(0, 0)
    assert stream.read() == b"false"


def test_boolean_eq():
    boolobj = BooleanObject(True)
    assert (boolobj == True) is True  # noqa: E712
    assert (boolobj == False) is False  # noqa: E712
    assert (boolobj == "True") is False

    boolobj = BooleanObject(False)
    assert (boolobj == True) is False  # noqa: E712
    assert (boolobj == False) is True  # noqa: E712
    assert (boolobj == "True") is False


def test_boolean_object_exception():
    stream = BytesIO(b"False")
    with pytest.raises(PdfReadError) as exc:
        BooleanObject.read_from_stream(stream)
    assert exc.value.args[0] == "Could not read Boolean object"


def test_array_object_exception():
    stream = BytesIO(b"False")
    with pytest.raises(PdfReadError) as exc:
        ArrayObject.read_from_stream(stream, None)
    assert exc.value.args[0] == "Could not read array"


def test_null_object_exception():
    stream = BytesIO(b"notnull")
    with pytest.raises(PdfReadError) as exc:
        NullObject.read_from_stream(stream)
    assert exc.value.args[0] == "Could not read Null object"


@pytest.mark.parametrize("value", [b"", b"False", b"foo ", b"foo  ", b"foo bar"])
def test_indirect_object_premature(value):
    stream = BytesIO(value)
    with pytest.raises(PdfStreamError) as exc:
        IndirectObject.read_from_stream(stream, None)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readHexStringFromStream():
    stream = BytesIO(b"a1>")
    assert read_hex_string_from_stream(stream) == "\x10"


def test_readHexStringFromStream_exception():
    stream = BytesIO(b"")
    with pytest.raises(PdfStreamError) as exc:
        read_hex_string_from_stream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readStringFromStream_exception():
    stream = BytesIO(b"x")
    with pytest.raises(PdfStreamError) as exc:
        read_string_from_stream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readStringFromStream_not_in_escapedict_no_digit():
    stream = BytesIO(b"x\\y")
    with pytest.raises(PdfReadError) as exc:
        read_string_from_stream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readStringFromStream_multichar_eol():
    stream = BytesIO(b"x\\\n )")
    assert read_string_from_stream(stream) == " "


def test_readStringFromStream_multichar_eol2():
    stream = BytesIO(b"x\\\n\n)")
    assert read_string_from_stream(stream) == ""


def test_readStringFromStream_excape_digit():
    stream = BytesIO(b"x\\1a )")
    assert read_string_from_stream(stream) == "\x01 "


def test_NameObject():
    stream = BytesIO(b"x")
    with pytest.raises(PdfReadError) as exc:
        NameObject.read_from_stream(stream, None)
    assert exc.value.args[0] == "name read error"


def test_destination_fit_r():
    d = Destination(
        NameObject("title"),
        NullObject(),
        NameObject(TF.FIT_R),
        FloatObject(0),
        FloatObject(0),
        FloatObject(0),
        FloatObject(0),
    )
    assert d.title == NameObject("title")
    assert d.typ == "/FitR"
    assert d.zoom is None
    assert d.left == FloatObject(0)
    assert d.right == FloatObject(0)
    assert d.top == FloatObject(0)
    assert d.bottom == FloatObject(0)
    assert list(d) == []
    d.empty_tree()


def test_destination_fit_v():
    Destination(NameObject("title"), NullObject(), NameObject(TF.FIT_V), FloatObject(0))


def test_destination_exception():
    with pytest.raises(PdfReadError):
        Destination(
            NameObject("title"), NullObject(), NameObject("foo"), FloatObject(0)
        )


def test_bookmark_write_to_stream():
    stream = BytesIO()
    bm = Bookmark(
        NameObject("title"), NullObject(), NameObject(TF.FIT_V), FloatObject(0)
    )
    bm.write_to_stream(stream, None)
    stream.seek(0, 0)
    assert stream.read() == b"<<\n/Title title\n/Dest [ null /FitV 0 ]\n>>"


def test_encode_pdfdocencoding_keyerror():
    with pytest.raises(UnicodeEncodeError) as exc:
        encode_pdfdocencoding("😀")
    assert exc.value.args[0] == "pdfdocencoding"


def test_read_object_comment_exception():
    stream = BytesIO(b"% foobar")
    pdf = None
    with pytest.raises(PdfStreamError) as exc:
        read_object(stream, pdf)
    assert exc.value.args[0] == "File ended unexpectedly."


def test_read_object_comment():
    stream = BytesIO(b"% foobar\n1 ")
    pdf = None
    out = read_object(stream, pdf)
    assert out == 1


def test_ByteStringObject():
    bo = ByteStringObject("stream", encoding="utf-8")
    stream = BytesIO(b"")
    bo.write_to_stream(stream, encryption_key="foobar")
    stream.seek(0, 0)
    assert stream.read() == b"<1cdd628b972e>"  # TODO: how can we verify this?


def test_DictionaryObject_key_is_no_pdfobject():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    with pytest.raises(ValueError) as exc:
        do["foo"] = NameObject("/GoTo")
    assert exc.value.args[0] == "key must be PdfObject"


def test_DictionaryObject_xmp_meta():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    assert do.xmp_metadata is None


def test_DictionaryObject_value_is_no_pdfobject():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    with pytest.raises(ValueError) as exc:
        do[NameObject("/S")] = "/GoTo"
    assert exc.value.args[0] == "value must be PdfObject"


def test_DictionaryObject_setdefault_key_is_no_pdfobject():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    with pytest.raises(ValueError) as exc:
        do.setdefault("foo", NameObject("/GoTo"))
    assert exc.value.args[0] == "key must be PdfObject"


def test_DictionaryObject_setdefault_value_is_no_pdfobject():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    with pytest.raises(ValueError) as exc:
        do.setdefault(NameObject("/S"), "/GoTo")
    assert exc.value.args[0] == "value must be PdfObject"


def test_DictionaryObject_setdefault_value():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    do.setdefault(NameObject("/S"), NameObject("/GoTo"))


def test_DictionaryObject_read_from_stream():
    stream = BytesIO(b"<< /S /GoTo >>")
    pdf = None
    out = DictionaryObject.read_from_stream(stream, pdf)
    assert out.get_object() == {NameObject("/S"): NameObject("/GoTo")}


def test_DictionaryObject_read_from_stream_broken():
    stream = BytesIO(b"< /S /GoTo >>")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.read_from_stream(stream, pdf)
    assert (
        exc.value.args[0]
        == "Dictionary read error at byte 0x2: stream must begin with '<<'"
    )


def test_DictionaryObject_read_from_stream_unexpected_end():
    stream = BytesIO(b"<< \x00/S /GoTo")
    pdf = None
    with pytest.raises(PdfStreamError) as exc:
        DictionaryObject.read_from_stream(stream, pdf)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_DictionaryObject_read_from_stream_stream_no_newline():
    stream = BytesIO(b"<< /S /GoTo >>stream")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.read_from_stream(stream, pdf)
    assert exc.value.args[0] == "Stream data must be followed by a newline"


@pytest.mark.parametrize(("strict"), [(True), (False)])
def test_DictionaryObject_read_from_stream_stream_no_stream_length(strict):
    stream = BytesIO(b"<< /S /GoTo >>stream\n")

    class Tst:  # to replace pdf
        strict = False

    pdf = Tst()
    pdf.strict = strict
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.read_from_stream(stream, pdf)
    assert exc.value.args[0] == "Stream length not defined"


@pytest.mark.parametrize(
    ("strict", "length", "should_fail"),
    [
        (True, 6, False),
        (True, 10, False),
        (True, 4, True),
        (False, 6, False),
        (False, 10, False),
    ],
)
def test_DictionaryObject_read_from_stream_stream_stream_valid(
    strict, length, should_fail
):
    stream = BytesIO(b"<< /S /GoTo /Length %d >>stream\nBT /F1\nendstream\n" % length)

    class Tst:  # to replace pdf
        strict = True

    pdf = Tst()
    pdf.strict = strict
    with pytest.raises(PdfReadError) as exc:
        do = DictionaryObject.read_from_stream(stream, pdf)
        # TODO: What should happen with the stream?
        assert do == {"/S": "/GoTo"}
        if length in (6, 10):
            assert b"BT /F1" in do._StreamObject__data
        raise PdfReadError("__ALLGOOD__")
    print(exc.value)
    assert should_fail ^ (exc.value.args[0] == "__ALLGOOD__")


def test_RectangleObject():
    ro = RectangleObject((1, 2, 3, 4))
    assert ro.lower_left == (1, 2)
    assert ro.lower_right == (3, 2)
    assert ro.upper_left == (1, 4)
    assert ro.upper_right == (3, 4)

    ro.lower_left = (5, 6)
    assert ro.lower_left == (5, 6)

    ro.lower_right = (7, 8)
    assert ro.lower_right == (7, 8)

    ro.upper_left = (9, 11)
    assert ro.upper_left == (9, 11)

    ro.upper_right = (13, 17)
    assert ro.upper_right == (13, 17)


def test_TextStringObject_exc():
    tso = TextStringObject("foo")
    with pytest.raises(Exception) as exc:
        tso.get_original_bytes()
    assert exc.value.args[0] == "no information about original bytes"


def test_TextStringObject_autodetect_utf16():
    tso = TextStringObject("foo")
    tso.autodetect_utf16 = True
    assert tso.get_original_bytes() == b"\xfe\xff\x00f\x00o\x00o"


def test_remove_child_not_in_tree():
    tree = TreeObject()
    with pytest.raises(ValueError) as exc:
        tree.remove_child(NameObject("foo"))
    assert exc.value.args[0] == "Removed child does not appear to be a tree item"


def test_remove_child_in_tree():
    pdf = os.path.join(RESOURCE_ROOT, "form.pdf")

    tree = TreeObject()
    reader = PdfReader(pdf)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])
    writer.add_bookmark("foo", pagenum=0)
    obj = writer._objects[-1]
    tree.add_child(obj, writer)
    tree.remove_child(obj)
    tree.add_child(obj, writer)
    tree.empty_tree()


def test_dict_read_from_stream():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/984/984877.pdf"
    name = "tika-984877.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        with pytest.warns(PdfReadWarning):
            page.extract_text()


def test_parse_content_stream_peek_percentage():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/985/985770.pdf"
    name = "tika-985770.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_read_inline_image_no_has_q():
    # pdf/df7e1add3156af17a372bc165e47a244.pdf
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/998/998719.pdf"
    name = "tika-998719.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()


def test_read_inline_image_loc_neg_1():
    url = "https://corpora.tika.apache.org/base/docs/govdocs1/935/935066.pdf"
    name = "tika-935066.pdf"

    reader = PdfReader(BytesIO(get_pdf_from_url(url, name=name)))
    for page in reader.pages:
        page.extract_text()
