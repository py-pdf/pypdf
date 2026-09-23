"""Tests for text-extraction character lookup caching."""

import pypdf._text_extraction as text_extraction
from pypdf._font import Font


def _create_test_font() -> Font:
    return Font(
        name="Test",
        encoding="charmap",
        character_map={},
        character_widths={"A": 600, "default": 500},
        space_width=250,
    )


def test_get_display_str_caches_repeated_character_lookups(monkeypatch) -> None:
    font = _create_test_font()
    neutral_calls = 0
    rtl_calls = 0

    original_neutral = text_extraction.is_char_neutral
    original_rtl = text_extraction.is_char_rtl

    def counted_neutral(char: str, custom_special_characters: str = "") -> bool:
        nonlocal neutral_calls
        neutral_calls += 1
        return original_neutral(char, custom_special_characters)

    def counted_rtl(char: str, custom_rtl_min: str = "", custom_rtl_max: str = "") -> bool:
        nonlocal rtl_calls
        rtl_calls += 1
        return original_rtl(char, custom_rtl_min, custom_rtl_max)

    monkeypatch.setattr(text_extraction, "is_char_neutral", counted_neutral)
    monkeypatch.setattr(text_extraction, "is_char_rtl", counted_rtl)

    operands = "A" * 10_000
    text, rtl_dir = text_extraction.get_display_str(
        text="",
        cm_matrix=[1, 0, 0, 1, 0, 0],
        tm_matrix=[1, 0, 0, 1, 0, 0],
        font_resource=None,
        font=font,
        text_operands=operands,
        font_size=12,
        rtl_dir=False,
        visitor_text=None,
    )

    assert text == operands
    assert rtl_dir is False
    assert neutral_calls == 1
    assert rtl_calls == 1


def test_get_text_operands_cache_is_scoped_to_each_call(monkeypatch) -> None:
    font = _create_test_font()
    width_calls = 0
    original_width = font.get_text_width

    def counted_width(text: str = "") -> float:
        nonlocal width_calls
        width_calls += 1
        return original_width(text)

    monkeypatch.setattr(font, "get_text_width", counted_width)

    for _ in range(2):
        text_extraction.get_text_operands(
            operands=["A" * 100],
            cm_matrix=[1, 0, 0, 1, 0, 0],
            tm_matrix=[1, 0, 0, 1, 0, 0],
            font=font,
            orientations=(0,),
        )

    assert width_calls == 2


def test_get_display_str_invalidates_caches_after_visitor_callback(monkeypatch) -> None:
    font = _create_test_font()
    neutral_calls = 0
    original_neutral = text_extraction.is_char_neutral

    def counted_neutral(char: str, custom_special_characters: str = "") -> bool:
        nonlocal neutral_calls
        neutral_calls += 1
        return original_neutral(char, custom_special_characters)

    def visitor_text(text, cm, tm, font_resource, font_size) -> None:
        pass

    monkeypatch.setattr(text_extraction, "is_char_neutral", counted_neutral)

    text_extraction.get_display_str(
        text="",
        cm_matrix=[1, 0, 0, 1, 0, 0],
        tm_matrix=[1, 0, 0, 1, 0, 0],
        font_resource=None,
        font=font,
        text_operands="AאA",
        font_size=12,
        rtl_dir=False,
        visitor_text=visitor_text,
    )

    # 2 unique characters ('A' and 'א') evaluated before visitor,
    # then cache cleared upon visitor call, triggering a 2nd lookup for 'A'
    assert neutral_calls == 3


def test_get_text_operands_caches_repeated_character_lookups(monkeypatch) -> None:
    font = _create_test_font()
    width_calls = 0

    original_width = font.get_text_width

    def counted_width(text: str = "") -> float:
        nonlocal width_calls
        width_calls += 1
        return original_width(text)

    monkeypatch.setattr(font, "get_text_width", counted_width)

    operands = ["A" * 10_000]
    text, is_str_operands, widths = text_extraction.get_text_operands(
        operands=operands,
        cm_matrix=[1, 0, 0, 1, 0, 0],
        tm_matrix=[1, 0, 0, 1, 0, 0],
        font=font,
        orientations=(0,),
    )

    assert text == operands[0]
    assert is_str_operands is True
    assert widths == 6_000_000.0  # 10,000 * 600
    assert width_calls == 1  # Standard character "A" is cached after first lookup


def test_get_text_operands_dict_encoding_byte_caching(monkeypatch) -> None:
    font = _create_test_font()
    # Dict encoding uses integer byte keys in font.encoding
    font.encoding = {65: "A"}
    width_calls = 0
    original_width = font.get_text_width

    def counted_width(text: str = "") -> float:
        nonlocal width_calls
        width_calls += 1
        return original_width(text)

    monkeypatch.setattr(font, "get_text_width", counted_width)

    # Byte 65 is 'A' (100 repetitions)
    operands = [b"A" * 100]
    text, is_str_operands, widths = text_extraction.get_text_operands(
        operands=operands,
        cm_matrix=[1, 0, 0, 1, 0, 0],
        tm_matrix=[1, 0, 0, 1, 0, 0],
        font=font,
        orientations=(0,),
    )

    assert text == "A" * 100
    assert is_str_operands is False
    assert widths == 60_000.0  # 100 * 600
    assert width_calls == 1  # Raw byte character chr(65) cached after 1st byte
