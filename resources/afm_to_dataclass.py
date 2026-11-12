# ruff: noqa: T201, INP001
"""
Generate pypdf modules from the AFM files of the 14 Adobe Core fonts.

Without arguments, print the Font dataclasses for the 14 Adobe Core fonts:

    python resources/afm_to_dataclass.py > pypdf/_codecs/core_font_metrics.py

With --encoding, print the built-in encoding of the Symbol or ZapfDingbats font instead.
The character codes and glyph names are taken from the AFM file, the Unicode values
of the glyph names from the Adobe Glyph List:

    python resources/afm_to_dataclass.py --encoding Symbol > pypdf/_codecs/symbol.py
    python resources/afm_to_dataclass.py --encoding ZapfDingbats > pypdf/_codecs/zapfding.py
"""
import argparse
import re
import textwrap
import urllib.request
from io import BytesIO
from typing import cast
from zipfile import ZipFile

from pypdf._codecs.adobe_glyphs import adobe_glyphs
from pypdf.constants import FontFlags

# FONT_LOC = "web.archive.org/web/20110531171921if_/http://www.adobe.com/content/dam/Adobe/en/devnet/font/pdfs/Core14_AFMs.zip"
FONT_LOC = "download.macromedia.com/pub/developer/opentype/tech-notes/Core14_AFMs.zip"
PROTOCOL = "https://"
FONT_URL = PROTOCOL + FONT_LOC

# The same revision of the Adobe Glyph List as used for pypdf/_codecs/adobe_glyphs.py.
GLYPH_LIST_COMMIT = "4036a9ca80a62f64f9de4f7321a9a045ad0ecfd6"
GLYPH_LIST_URL = f"https://github.com/adobe-type-tools/agl-aglfn/blob/{GLYPH_LIST_COMMIT}"

# Fonts with a built-in encoding: the font name, the source file and the variable name in the generated module.
ENCODINGS = {
    "Symbol": ("Symbol.afm", "_symbol_encoding"),
    "ZapfDingbats": ("ZapfDingbats.afm", "_zapfding_encoding"),
}

# The Adobe Glyph List maps the glyph name "mu" to U+00B5 MICRO SIGN. In the Symbol font, it is
# the Greek letter between "lambda" and "nu", so map it to U+03BC GREEK SMALL LETTER MU instead.
SYMBOL_GLYPH_OVERRIDES = {"mu": "μ"}


def read_glyph_list(file_name: str) -> tuple[str, dict[str, str]]:
    """Read an Adobe Glyph List file and return its license notice and the glyph name to Unicode mapping."""
    with urllib.request.urlopen(
        f"https://raw.githubusercontent.com/adobe-type-tools/agl-aglfn/{GLYPH_LIST_COMMIT}/{file_name}"
    ) as connection:
        lines = connection.read().decode("utf-8").splitlines()
    # The license notice is the first comment block, enclosed by two lines of dashes.
    separators = [i for i, line in enumerate(lines) if line.startswith("# ---")]
    notice = "\n".join(lines[separators[0]:separators[1] + 1])
    glyphs: dict[str, str] = {}
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        name, code_points = line.split(";")
        glyphs.setdefault(name, "".join(chr(int(code_point, 16)) for code_point in code_points.split()))
    return notice, glyphs


class Parser:
    def __init__(self) -> None:
        self.license_information = ""
        self.files: dict[str, str] = {}
        self.encodings: dict[str, dict[int, str]] = {}

    def get_fonts(self) -> None:
        with urllib.request.urlopen(
            f"https://{FONT_LOC}"
        ) as connection, ZipFile(BytesIO(
            connection.read())
        ) as font_zip:
            for filename in font_zip.namelist():
                if filename.lower().endswith(".afm"):
                    with font_zip.open(filename, mode="r") as afm_font_file:
                        self.files[filename] = afm_font_file.read().decode("utf-8")
                else:
                    with font_zip.open(filename, mode="r") as afm_font_file:
                        self.license_information = afm_font_file.read().decode("utf-8")

    def get_disclaimer(self, width: int = 95) -> str:
        pre = (
            "# This file is based upon the 14 core AFM files provided by Adobe/Macromedia at\n# " +
            FONT_URL +
            "\n# The original copyright follows:\n#\n# " +
            "-" * width +
            "\n"
        )
        title = "# " + self.license_information.split("<title>")[1].split("</title>")[0]
        text = self.license_information.split('<td width="300">')[1].split("<font color")[0]
        post = "\n# " + "-" * width + "\n\n"
        return pre + title + "\n#\n# " + "\n# ".join(textwrap.wrap(text=text, width=width)) + post

    @staticmethod
    def _parse_character_metrics(line: str) -> tuple[int, int, str]:
        # C integer ; WX number ; N name; C is the code in the font's built-in encoding, -1 if unencoded.
        character_code = -1
        character_width_x = -1
        character_name = "dummy"
        for pair in line.split(";"):
            if not pair.strip():
                continue
            key_of_pair, value_of_pair = pair.strip().split(" ", maxsplit=1)
            if key_of_pair == "C":
                character_code = int(value_of_pair)
            if key_of_pair == "WX":
                character_width_x = int(value_of_pair)
            if key_of_pair == "N":
                character_name = value_of_pair
        return character_code, character_width_x, character_name

    def _handle_font(self, file_name: str, font_data: str) -> list[str]:
        # AFM specification: https://adobe-type-tools.github.io/font-tech-notes/pdfs/5004.AFM_Spec.pdf
        copyrights: list[str] = []
        name: str = ""
        family: str = ""
        weight: str = ""
        ascent: float = 0.0
        descent: float = 0.0
        cap_height: float = 0.0
        x_height: float = 0.0
        italic_angle: float = 0.0
        flags: int = 0
        bbox: tuple[float, float, float, float] = (0, 0, 0, 0)
        character_widths: dict[str, int] = {}
        encoding: dict[int, str] = {}

        for line in font_data.splitlines(keepends=False):
            if not line.strip():
                continue

            if " " not in line:
                continue
            key, value = line.split(" ", maxsplit=1)
            if not key:
                continue

            if key == "FontName":
                name = value
                if "Times" in value:
                    flags |= FontFlags.SERIF
            if key == "Weight":
                weight = value
            if key == "FamilyName":
                family = value

            if key == "Ascender":
                ascent = cast(float, value)
            if key == "Descender":
                descent = cast(float, value)
            if key == "CapHeight":
                cap_height = cast(float, value)
            if key == "XHeight":
                x_height = cast(float, value)
            if key == "ItalicAngle":
                italic_angle = cast(float, value)
                if value != "0":
                    flags |= FontFlags.ITALIC
            if key == "IsFixedPitch" and value.lower() == "true":
                flags |= FontFlags.FIXED_PITCH
            if key == "FontBBox":
                bbox = tuple(map(float, value.split(" ")[:4]))  # type: ignore[assignment]
            if key == "EncodingScheme":
                if value == "FontSpecific":
                    flags |= FontFlags.SYMBOLIC
                else:
                    flags |= FontFlags.NONSYMBOLIC

            # Add copyright information. This is available in two fields: "Comment" and "Notice".
            # However, all information available in "Comment" is also available in "Notice", and
            # the information under "Notice" is more complete. Ignore "Comment" and only copy
            # information from "Notice", to avoid adding the same information twice.
            if key == "Notice" and value.startswith("Copyright"):
                copyrights.append(re.sub(r"\.([A-Z])", r".  \1", value))  # Take care of missing space after period.

            if key == "C":
                character_code, character_width_x, character_name = self._parse_character_metrics(line)
                if character_code >= 0:
                    encoding[character_code] = character_name
                glyph = adobe_glyphs[f"/{character_name}"]
                character_widths[glyph.encode("unicode_escape").decode("utf-8")] = character_width_x
            if key == "CH":
                raise NotImplementedError(name, line)
            # Add default width
            try:
                if (flags & FontFlags.FIXED_PITCH) == FontFlags.FIXED_PITCH:
                    character_widths["default"] = character_widths[" "]
                else:
                    character_widths["default"] = 2 * character_widths[" "]
            except KeyError:
                pass

        self.encodings[file_name] = encoding
        result = [
            f"    # Generated from {file_name}"
        ]
        for copyright_entry in sorted(set(copyrights)):
            result.extend(f"    # {line}" for line in textwrap.wrap(text=copyright_entry, width=95))
        result.append(f'    "{name}": CoreFontMetrics(')
        result.append("        font_descriptor=FontDescriptor(")
        result.append(f'            name="{name}",')
        result.append(f'            family="{family}",')
        result.append(f'            weight="{weight}",')
        result.append(f"            ascent={ascent},")
        result.append(f"            descent={descent},")
        result.append(f"            cap_height={cap_height},")
        result.append(f"            x_height={x_height},")
        result.append(f"            italic_angle={italic_angle},")
        result.append(f"            flags={flags},")
        result.append(f"            bbox=({', '.join(map(str, bbox))}),")
        result.append("        ),")
        result.append("        character_widths={")
        for character, width in character_widths.items():
            d = '"'
            try:
                if ord(character) == 34:  # Double quotation mark
                    d = "'"
            except TypeError:
                pass
            result.append(f"            {d}{character}{d}: {width},")
        result.append("        },")
        result.append("    ),")
        return result

    def get_font_data(self) -> str:
        data = [
            (
                "from pypdf.generic._font import CoreFontMetrics, FontDescriptor\n\n"
                "CORE_FONT_METRICS: dict[str, CoreFontMetrics] = {"
            ),
        ]
        for name, font_data in self.files.items():
            data.extend(self._handle_font(name, font_data))
        data.append("}\n")
        return "\n".join(data)

    def get_encoding_data(self, font: str) -> str:
        """
        Generate the built-in encoding of a symbolic font as a list of 256 Unicode characters.

        The character codes and glyph names come from the AFM file of the font, the Unicode values
        of the glyph names from the Adobe Glyph List. Codes without a glyph map to themselves.
        """
        file_name, variable_name = ENCODINGS[font]
        self._handle_font(file_name, self.files[file_name])

        glyph_list_files = ["glyphlist.txt"]
        glyph_list_notice, glyphs = read_glyph_list("glyphlist.txt")
        if font == "Symbol":
            glyphs.update(SYMBOL_GLYPH_OVERRIDES)
        if font == "ZapfDingbats":
            # The glyph names of ZapfDingbats (a1, a2, ...) are only listed in the dedicated glyph list.
            # Its "space" glyph is not, so fall back to the generic list for that one.
            glyph_list_files.insert(0, "zapfdingbats.txt")
            _, zapf_dingbats_glyphs = read_glyph_list("zapfdingbats.txt")
            glyphs = {**glyphs, **zapf_dingbats_glyphs}

        characters = [chr(code) for code in range(256)]
        for code, glyph_name in self.encodings[file_name].items():
            characters[code] = glyphs[glyph_name]
            assert len(characters[code]) == 1, (glyph_name, characters[code])

        header = [
            f"# Generated by resources/afm_to_dataclass.py from the character codes and glyph names in {file_name}",
            "# and the Unicode values of the glyph names in the Adobe Glyph List:",
            *(f"# {GLYPH_LIST_URL}/{glyph_list_file}" for glyph_list_file in glyph_list_files),
            "#",
        ]
        if font == "Symbol":
            header.append("# The glyph name mu is mapped to U+03BC GREEK SMALL LETTER MU instead of U+00B5 MICRO SIGN.")
            header.append("#")
        data = [
            "\n".join(header),
            self.get_disclaimer().rstrip("\n"),
            "#",
            "# The Adobe Glyph List carries the following copyright notice:",
            "#",
            glyph_list_notice,
            "",
            f"{variable_name} = [",
            *(f'    "\\u{ord(character):04X}",' for character in characters),
            "]",
            f"assert len({variable_name}) == 256",
            "",
        ]
        return "\n".join(data)


argument_parser = argparse.ArgumentParser(
    description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
)
argument_parser.add_argument(
    "--encoding",
    choices=ENCODINGS,
    help="print the built-in encoding of this font instead of the metrics of all core fonts",
)
arguments = argument_parser.parse_args()

parser = Parser()
parser.get_fonts()

if arguments.encoding:
    print(parser.get_encoding_data(arguments.encoding), end="")
else:
    print(parser.get_disclaimer())
    print(parser.get_font_data())
