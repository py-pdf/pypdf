from dataclasses import dataclass, field
from typing import Optional

from pypdf.generic import DictionaryObject


@dataclass(frozen=True)
class FontDescriptor:
    """
    Represents the FontDescriptor dictionary as defined in the PDF specification.
    This contains both descriptive and metric information.

    The defaults are derived from the mean values of the 14 core fonts, rounded
    to 100.
    """

    name: str = "Unknown"
    family: str = "Unknown"
    weight: str = "Unknown"

    ascent: float = 700.0
    descent: float = -200.0
    cap_height: float = 600.0
    x_height: float = 500.0
    italic_angle: float = 0.0  # Non-italic
    flags: int = 32  # Non-serif, non-symbolic, not fixed width
    bbox: tuple[float, float, float, float] = field(default_factory=lambda: (-100.0, -200.0, 1000.0, 900.0))

    character_widths: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_font_resource(cls, pdf_font_dict: DictionaryObject) -> "Optional[FontDescriptor]":
        from pypdf._codecs.core_fontmetrics import CORE_FONT_METRICS  # noqa: PLC0415
        # Prioritize information from the PDF font dictionary
        font_name = pdf_font_dict.get("/BaseFont", "Unknown")
        if font_name[1:] in CORE_FONT_METRICS:
            return CORE_FONT_METRICS.get(font_name[1:])
        return cls(name=font_name)
