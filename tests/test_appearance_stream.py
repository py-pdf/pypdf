"""Test the pypdf.generic._appearance_stream module."""

from pypdf.generic._appearance_stream import TextStreamAppearance


def test_comb():
    rectangle = (0.0, 0.0, 197.285, 18.455)
    font_size = 10.0
    text = "01234567"
    max_length = 10
    is_comb = True
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_comb=is_comb, max_length=max_length
    )
    assert appearance_stream.get_data() == (
        b"q\n/Tx BMC \nq\n1 1 196.285 17.455 re\nW\nBT\n/Helv 10.0 Tf 0 g\n"
        b"7.084250000000001 7.454999999999998 Td\n(0) Tj\n"
        b"19.7285 0.0 Td\n(1) Tj\n"
        b"19.728500000000004 0.0 Td\n(2) Tj\n"
        b"19.728499999999997 0.0 Td\n(3) Tj\n"
        b"19.728499999999997 0.0 Td\n(4) Tj\n"
        b"19.728499999999997 0.0 Td\n(5) Tj\n"
        b"19.72850000000001 0.0 Td\n(6) Tj\n"
        b"19.728499999999997 0.0 Td\n(7) Tj\nET\nQ\nEMC\nQ\n"
    )

    rectangle = (0.0, 0.0, 20.852, 20.84)
    text = "AA"
    max_length = 1
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_comb=is_comb, max_length=max_length
    )
    assert appearance_stream.get_data() == (
        b"q\n/Tx BMC \nq\n1 1 19.852 19.84 re\nW\nBT\n/Helv 10.0 Tf 0 g\n7.091 9.84 Td\n(A) Tj\nET\nQ\nEMC\nQ\n"
    )


def test_scale_text():
    rectangle = (0, 0, 9.1, 55.4)
    font_size = 10.1
    text = "Hello World"
    is_multiline = False
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"10.1 Tf" in appearance_stream.get_data()

    text = "This is a very very long sentence that probably will scale below the minimum font size"
    font_size = 0.0
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"4.0 Tf" in appearance_stream.get_data()

    rectangle = (0, 0, 160, 360)
    font_size = 0.0
    text = """Welcome to pypdf
pypdf is a free and open source pure-python PDF library capable of splitting, merging, cropping, and
transforming the pages of PDF files. It can also add custom data, viewing options, and passwords to PDF
files. pypdf can retrieve text and metadata from PDFs as well.

See pdfly for a CLI application that uses pypdf to interact with PDFs.
    """
    is_multiline = True
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"12 Tf" in appearance_stream.get_data()
    assert b"pypdf is a free and open" in appearance_stream.get_data()

    rectangle = (0, 0, 160, 160)
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"8.8 Tf" in appearance_stream.get_data()

    rectangle = (0, 0, 160, 12)
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    text = """Option A
Option B
Option C
Option D
"""
    selection = "Option A"
    assert b"4.0 Tf" in appearance_stream.get_data()

    text = "pneumonoultramicroscopicsilicovolcanoconiosis"
    appearance_stream = TextStreamAppearance(
        text, selection, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"7.2 Tf" in appearance_stream.get_data()

    rectangle = (0, 0, 10, 100)
    text = "OneWord"
    appearance_stream = TextStreamAppearance(
        text, rectangle=rectangle, font_size=font_size, is_multiline=is_multiline
    )
    assert b"OneWord" in appearance_stream.get_data()
