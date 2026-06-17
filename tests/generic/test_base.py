"""Test the pypdf.generic._base module."""
from io import BytesIO

import pytest

from pypdf import PdfReader, PdfWriter
from pypdf.errors import LimitReachedError
from pypdf.generic import FloatObject, NameObject, NumberObject, read_hex_string_from_stream
from tests import get_data_from_url


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (b"<00FE00FF>", "\xfe\xff"),
        (b"<00FE00FF00D6>", "\xfe\xff\xd6"),
    ]
)
def test_text_string_object__looks_like_bom(source: bytes, expected: str) -> None:
    stream = BytesIO(source)
    result = read_hex_string_from_stream(stream)
    assert result == expected


@pytest.mark.enable_socket
def test_text_string_object__wrongly_detected_bom() -> None:
    url = "https://github.com/user-attachments/files/24401507/minimal.pdf"
    name = "issue3587.pdf"
    reader = PdfReader(BytesIO(get_data_from_url(url=url, name=name)))
    reader_page = reader.pages[0]

    writer = PdfWriter()
    for page in reader.pages:
        writer_page = writer.add_blank_page(reader_page.mediabox.width, reader_page.mediabox.height)
        writer_page.merge_page(page)

        assert writer_page.extract_text() == (
            "无译形带r的参 z慧队手行 c要枪互工先调 uC一在你 k该方导最 xT况 M味政没出 v大同团\n"
            "想急压游这体构主m基重张预另做内已织程术并 U种规被中应 s过小立就公测和 F更为 BS\n"
            "把强型w利 qfJ现能您关文）己个言 VW是 Z亲社 y。说准密令K络通自力 i诸旦明量放及 I\n"
            "成战康养d都蜂多开 pE次提朋动比台有培愿 A确 l充计标去人如么 b灵 N它 g弃语看 X；j\n"
            "轮HG采共由地友入（器Y果感建切理情从集德翻a单第识任 Q模 eh目经相哪受起时着 DR\n"
            "用好o备划付信、度解效作协读 O讨高具击始者意群治扩到 P才兰网认 t马倒来本整 L们 n\n"
            "系可论，步各之但\n"
            "12"
        )


def test_number_object__read_from_stream__limits() -> None:
    stream = BytesIO(b"13.37\n")
    assert NumberObject.read_from_stream(stream) == FloatObject("13.37")

    stream = BytesIO(f"{'1' * 100}\n".encode())
    with pytest.raises(
            expected_exception=LimitReachedError,
            match=r"^Read stream length of 101 exceeds maximum allowed length of 64\.$"
    ):
        NumberObject.read_from_stream(stream)


def test_name_object__read_from_stream__limits() -> None:
    stream = BytesIO(b"/My#20Name\n")
    assert NameObject.read_from_stream(stream, pdf=None) == NameObject("/My Name")

    stream = BytesIO(f"/{'SomeName' * 5000}\n".encode())
    with pytest.raises(
            expected_exception=LimitReachedError,
            match=r"^Read stream length of 8176 exceeds maximum allowed length of 4096\.$"
    ):
        NameObject.read_from_stream(stream, pdf=None)
