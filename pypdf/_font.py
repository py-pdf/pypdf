from dataclasses import dataclass


@dataclass(frozen=True)
class FontDescriptor:
    """
    Represents the FontDescriptor dictionary as defined in the PDF specification.
    This contains both descriptive and metric information.
    """

    name: str
    family: str
    weight: str

    ascent: float
    descent: float
    cap_height: float
    x_height: float
    italic_angle: float
    flags: int
    bbox: tuple[float, float, float, float]

    character_widths: dict[str, int]
