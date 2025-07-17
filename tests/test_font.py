"""Test font-related functionality."""


from pypdf._codecs.core_fontmetrics import FONT_METRICS


def test_font_metrics():
    font_name = "Helvetica"
    my_font = FONT_METRICS[font_name]
    assert my_font.family == "Helvetica"
    assert my_font.weight == "Medium"
    assert my_font.ascent == 718
    assert my_font.descent == -207

    test_string = "This is a long sentence. !@%%^€€€. çûįö¶´"
    charwidth = sum(my_font.character_widths[char] for char in test_string)
    assert charwidth == 19251

    font_name = "Courier-Bold"
    my_font = FONT_METRICS[font_name]
    assert my_font.italic_angle == 0
    assert my_font.flags == 64
    assert my_font.bbox == (-113.0, -250.0, 749.0, 801.0)
