# ruff: noqa: T201, INP001, D100
# Use this file to generate Font dataclasses for the 14 Adobe Core fonts.
import re
import textwrap
import urllib.request
from io import BytesIO
from typing import cast
from zipfile import ZipFile

from pypdf._codecs.adobe_glyphs import adobe_glyphs

# FONT_LOC = "web.archive.org/web/20110531171921if_/http://www.adobe.com/content/dam/Adobe/en/devnet/font/pdfs/Core14_AFMs.zip"
FONT_LOC = "download.macromedia.com/pub/developer/opentype/tech-notes/Core14_AFMs.zip"
PROTOCOL = "https://"
FONT_URL = PROTOCOL + FONT_LOC

class Parser:
    def __init__(self) -> None:
        self.license_information = ""
        self.files: dict[str, str] = {}

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
                    flags += 2
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
                    flags += 64
            if key == "IsFixedPitch":
                flags += int(value.lower() == "true")
            if key == "FontBBox":
                bbox = tuple(map(float, value.split(" ")[:4]))  # type: ignore
            if key == "EncodingScheme":
                if value == "FontSpecific":
                    flags += 4
                else:
                    flags += 32

            # Add copyright information. This is available in two fields: "Comment" and "Notice".
            # However, all information available in "Comment" is also available in "Notice", and
            # the information under "Notice" is more complete. Ignore "Comment" and only copy
            # information from "Notice", to avoid adding the same information twice.
            if key == "Notice" and value.startswith("Copyright"):
                copyrights.append(re.sub(r"\.([A-Z])", r".  \1", value))  # Take care of missing space after period.

            if key == "C":
                # C integer ; WX number ; N name; We're ignoring C.
                key_value_pairs = line.split(";")
                character_width_x = -1
                character_name = "dummy"
                for pair in key_value_pairs:
                    if not pair.strip():
                        continue
                    key_of_pair, value_of_pair = pair.strip().split(" ", maxsplit=1)
                    if key_of_pair == "WX":
                        character_width_x = int(value_of_pair)
                    if key_of_pair == "N":
                        character_name = value_of_pair
                glyph = adobe_glyphs[f"/{character_name}"]
                character_widths[glyph.encode("unicode_escape").decode("utf-8")] = character_width_x
            if key == "CH":
                raise NotImplementedError(name, line)

        result = [
            f"    # Generated from {file_name}"
        ]
        for copyright_entry in sorted(set(copyrights)):
            result.extend(f"    # {line}" for line in textwrap.wrap(text=copyright_entry, width=95))
        result.append(f'    "{name}": FontDescriptor(')
        result.append(f'        name="{name}",')
        result.append(f'        family="{family}",')
        result.append(f'        weight="{weight}",')
        result.append(f"        ascent={ascent},")
        result.append(f"        descent={descent},")
        result.append(f"        cap_height={cap_height},")
        result.append(f"        x_height={x_height},")
        result.append(f"        italic_angle={italic_angle},")
        result.append(f"        flags={flags},")
        result.append(f"        bbox=({', '.join(map(str, bbox))}),")
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
            "from pypdf._font import FontDescriptor\n\n"
            "CORE_FONT_METRICS: dict[str, FontDescriptor] = {",
        ]
        for name, font_data in self.files.items():
            data.extend(self._handle_font(name, font_data))
        data.append("}\n")
        return "\n".join(data)


parser = Parser()
parser.get_fonts()

print(parser.get_disclaimer())
print(parser.get_font_data())
