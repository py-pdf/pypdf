import pypdf._text_extraction as text_extraction
from pypdf._font import Font


def _font() -> Font:
    return Font(
        name="Test",
        encoding="charmap",
        character_map={},
        character_widths={"A": 600, "default": 500},
        space_width=250,
    )


def test_get_display_str_caches_repeated_character_lookups(monkeypatch) -> None:
    font = _font()
    width_calls = 0
    neutral_calls = 0
    rtl_calls = 0

    original_width = font.get_text_width
    original_neutral = text_extraction.is_char_neutral
    original_rtl = text_extraction.is_char_rtl

    def counted_width(text: str = "") -> float:
        nonlocal width_calls
        width_calls += 1
        return original_width(text)

    def counted_neutral(char: str, custom_special_characters: str = "") -> bool:
        nonlocal neutral_calls
        neutral_calls += 1
        return original_neutral(char, custom_special_characters)

    def counted_rtl(char: str, custom_rtl_min: str = "", custom_rtl_max: str = "") -> bool:
        nonlocal rtl_calls
        rtl_calls += 1
        return original_rtl(char, custom_rtl_min, custom_rtl_max)

    monkeypatch.setattr(font, "get_text_width", counted_width)
    monkeypatch.setattr(text_extraction, "is_char_neutral", counted_neutral)
    monkeypatch.setattr(text_extraction, "is_char_rtl", counted_rtl)

    operands = "A" * 10_000
    text, rtl_dir, widths = text_extraction.get_display_str(
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
    assert widths == 6_000_000
    assert width_calls == 1
    assert neutral_calls == 1
    assert rtl_calls == 1


def test_get_display_str_cache_is_scoped_to_each_call(monkeypatch) -> None:
    font = _font()
    width_calls = 0
    original_width = font.get_text_width

    def counted_width(text: str = "") -> float:
        nonlocal width_calls
        width_calls += 1
        return original_width(text)

    monkeypatch.setattr(font, "get_text_width", counted_width)

    for _ in range(2):
        text_extraction.get_display_str(
            text="",
            cm_matrix=[1, 0, 0, 1, 0, 0],
            tm_matrix=[1, 0, 0, 1, 0, 0],
            font_resource=None,
            font=font,
            text_operands="A" * 100,
            font_size=12,
            rtl_dir=False,
            visitor_text=None,
        )

    assert width_calls == 2
