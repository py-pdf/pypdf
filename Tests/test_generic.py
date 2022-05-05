# -*- coding: utf-8 -*-
from io import BytesIO

import pytest

from PyPDF2.constants import TypFitArguments as TF
from PyPDF2.errors import PdfReadError, PdfStreamError
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
    PdfObject,
    RectangleObject,
    TextStringObject,
    createStringObject,
    encode_pdfdocencoding,
    readHexStringFromStream,
    readObject,
    readStringFromStream,
)


def test_float_object_exception():
    assert FloatObject("abc") == 0


def test_number_object_exception():
    with pytest.raises(OverflowError):
        NumberObject(1.5 * 2**10000)


def test_createStringObject_exception():
    with pytest.raises(TypeError) as exc:
        createStringObject(123)
    assert exc.value.args[0] == "createStringObject should have str or unicode arg"


@pytest.mark.parametrize(
    ("value", "expected", "tell"), [(b"true", b"true", 4), (b"false", b"false", 5)]
)
def test_boolean_object(value, expected, tell):
    stream = BytesIO(value)
    assert BooleanObject.readFromStream(stream).value == (expected == b"true")
    stream.seek(0, 0)
    assert stream.read() == expected
    assert stream.tell() == tell


def test_boolean_object_write():
    stream = BytesIO()
    boolobj = BooleanObject(None)
    boolobj.writeToStream(stream, encryption_key=None)
    stream.seek(0, 0)
    assert stream.read() == b"false"


def test_boolean_object_exception():
    stream = BytesIO(b"False")
    with pytest.raises(PdfReadError) as exc:
        BooleanObject.readFromStream(stream)
    assert exc.value.args[0] == "Could not read Boolean object"


def test_array_object_exception():
    stream = BytesIO(b"False")
    with pytest.raises(PdfReadError) as exc:
        ArrayObject.readFromStream(stream, None)
    assert exc.value.args[0] == "Could not read array"


def test_null_object_exception():
    stream = BytesIO(b"notnull")
    with pytest.raises(PdfReadError) as exc:
        NullObject.readFromStream(stream)
    assert exc.value.args[0] == "Could not read Null object"


@pytest.mark.parametrize("value", [b"", b"False", b"foo ", b"foo  ", b"foo bar"])
def test_indirect_object_premature(value):
    stream = BytesIO(value)
    with pytest.raises(PdfStreamError) as exc:
        IndirectObject.readFromStream(stream, None)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readHexStringFromStream():
    stream = BytesIO(b"a1>")
    assert readHexStringFromStream(stream) == "\x10"


def test_readHexStringFromStream_exception():
    stream = BytesIO(b"")
    with pytest.raises(PdfStreamError) as exc:
        readHexStringFromStream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readStringFromStream_exception():
    stream = BytesIO(b"x")
    with pytest.raises(PdfStreamError) as exc:
        readStringFromStream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_readStringFromStream_not_in_escapedict_no_digit():
    stream = BytesIO(b"x\\y")
    with pytest.raises(PdfReadError) as exc:
        readStringFromStream(stream)
    assert exc.value.args[0] == "Stream has ended unexpectedly"
    # "Unexpected escaped string: y"


def test_readStringFromStream_multichar_eol():
    stream = BytesIO(b"x\\\n )")
    assert readStringFromStream(stream) == " "


def test_readStringFromStream_multichar_eol2():
    stream = BytesIO(b"x\\\n\n)")
    assert readStringFromStream(stream) == ""


def test_readStringFromStream_excape_digit():
    stream = BytesIO(b"x\\1a )")
    assert readStringFromStream(stream) == "\x01 "


def test_NameObject():
    stream = BytesIO(b"x")
    with pytest.raises(PdfReadError) as exc:
        NameObject.readFromStream(stream, None)
    assert exc.value.args[0] == "name read error"


def test_destination_fit_r():
    d = Destination(
        NameObject("title"),
        PdfObject(),
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
    d.emptyTree()


def test_destination_fit_v():
    Destination(NameObject("title"), PdfObject(), NameObject(TF.FIT_V), FloatObject(0))


def test_destination_exception():
    with pytest.raises(PdfReadError):
        Destination(NameObject("title"), PdfObject(), NameObject("foo"), FloatObject(0))


def test_bookmark_write_to_stream():
    stream = BytesIO()
    bm = Bookmark(
        NameObject("title"), NameObject(), NameObject(TF.FIT_V), FloatObject(0)
    )
    bm.writeToStream(stream, None)
    stream.seek(0, 0)
    assert stream.read() == b"<<\n/Title title\n/Dest [  /FitV 0 ]\n>>"


@pytest.mark.no_py27()
def test_encode_pdfdocencoding_keyerror():
    with pytest.raises(UnicodeEncodeError) as exc:
        encode_pdfdocencoding("😀")
    assert exc.value.args[0] == "pdfdocencoding"


def test_readObject_comment_exception():
    stream = BytesIO(b"% foobar")
    pdf = None
    with pytest.raises(PdfStreamError) as exc:
        readObject(stream, pdf)
    assert exc.value.args[0] == "File ended unexpectedly."


def test_readObject_comment():
    stream = BytesIO(b"% foobar\n1 ")
    pdf = None
    out = readObject(stream, pdf)
    assert out == 1


@pytest.mark.no_py27()
def test_ByteStringObject():
    bo = ByteStringObject("stream", encoding="utf-8")
    stream = BytesIO(b"")
    bo.writeToStream(stream, encryption_key="foobar")
    stream.seek(0, 0)
    assert stream.read() == b"<1cdd628b972e>"  # TODO: how can we verify this?


def test_DictionaryObject_key_is_no_pdfobject():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    with pytest.raises(ValueError) as exc:
        do["foo"] = NameObject("/GoTo")
    assert exc.value.args[0] == "key must be PdfObject"


def test_DictionaryObject_xmp_meta():
    do = DictionaryObject({NameObject("/S"): NameObject("/GoTo")})
    assert do.xmpMetadata is None


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
    out = DictionaryObject.readFromStream(stream, pdf)
    assert out.getObject() == {NameObject("/S"): NameObject("/GoTo")}


def test_DictionaryObject_read_from_stream_broken():
    stream = BytesIO(b"< /S /GoTo >>")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.readFromStream(stream, pdf)
    assert (
        exc.value.args[0]
        == "Dictionary read error at byte 0x2: stream must begin with '<<'"
    )


def test_DictionaryObject_read_from_stream_unexpected_end():
    stream = BytesIO(b"<< \x00/S /GoTo")
    pdf = None
    with pytest.raises(PdfStreamError) as exc:
        DictionaryObject.readFromStream(stream, pdf)
    assert exc.value.args[0] == "Stream has ended unexpectedly"


def test_DictionaryObject_read_from_stream_stream_no_newline():
    stream = BytesIO(b"<< /S /GoTo >>stream")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.readFromStream(stream, pdf)
    assert exc.value.args[0] == "Stream data must be followed by a newline"


def test_DictionaryObject_read_from_stream_stream_no_stream_length():
    stream = BytesIO(b"<< /S /GoTo >>stream\n")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.readFromStream(stream, pdf)
    assert exc.value.args[0] == "Stream length not defined"


def test_DictionaryObject_read_from_stream_stream_stream_missing_endstream2():
    stream = BytesIO(b"<< /S /GoTo /Length 10 >>stream\n ")
    pdf = None
    with pytest.raises(PdfReadError) as exc:
        DictionaryObject.readFromStream(stream, pdf)
    assert (
        exc.value.args[0]
        == "Unable to find 'endstream' marker after stream at byte 0x21."
    )


def test_DictionaryObject_read_from_stream_stream_stream_valid():
    stream = BytesIO(b"<< /S /GoTo /Length 10 >>stream\nBT /F1\nendstream\n")
    pdf = None
    do = DictionaryObject.readFromStream(stream, pdf)
    # TODO: What should happen with the stream?
    assert do == {"/S": "/GoTo"}


def test_RectangleObject():
    ro = RectangleObject((1, 2, 3, 4))
    assert ro.lowerLeft == (1, 2)
    assert ro.lowerRight == (3, 2)
    assert ro.upperLeft == (1, 4)
    assert ro.upperRight == (3, 4)

    ro.lowerLeft = (5, 6)
    assert ro.lowerLeft == (5, 6)

    ro.lowerRight = (7, 8)
    assert ro.lowerRight == (7, 8)

    ro.upperLeft = (9, 11)
    assert ro.upperLeft == (9, 11)

    ro.upperRight = (13, 17)
    assert ro.upperRight == (13, 17)


def test_TextStringObject_exc():
    tso = TextStringObject("foo")
    with pytest.raises(Exception) as exc:
        tso.get_original_bytes()
    assert exc.value.args[0] == "no information about original bytes"


def test_TextStringObject_autodetect_utf16():
    tso = TextStringObject("foo")
    tso.autodetect_utf16 = True
    assert tso.get_original_bytes() == b"\xfe\xff\x00f\x00o\x00o"
