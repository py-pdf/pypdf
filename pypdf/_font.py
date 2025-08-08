from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Font:
    name: str
    family: str
    weight: str

    ascent: float
    descent: float
    cap_height: float
    x_height: float
    italic_angle: float
    flags: int
    bbox: Tuple[float, float, float, float]

    character_widths: Dict[str, int]
