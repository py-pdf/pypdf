from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Union


@dataclass
class Color:
    """
    A factory class to generate one of class GrayscaleColor, RGBColor or CMYKColor. Call with
    Color.from_normalized_values() on a tuple of length 1 for grayscale, 3 for RGB, or 4 for CMYK.
    """
    color_operator: str = field(init=False)
    _ordered_fields: tuple[str, ...] = field(init=False)

    @classmethod
    def from_normalized_values(
        cls,
        color: Union[Sequence[float], None]
    ) -> Union["Color", None]:
        """
        Method to instantiate a color class. Can be called with value of None for cases where an appearance
        characteristics dictionary contains an empty "/BG" or "/BC" value,  which returns None and signifies
        transparent color. See Table 189, "Entries in an appearance characteristics dictionary" of the PDF
        specification 1.7.

        Args:
            color: A sequence of 1 (for DeviceGray), 3 (for DeviceRGB) or 4 (for DeviceCMYK) float values
                in the range of 0.0 to 1.0 (representing normalized color channel values), or None to return None.
        """
        color_types: dict[int, type[Color]] = {
            1: DeviceGray,
            3: DeviceRGB,
            4: DeviceCMYK,
        }

        if (
            color is not None
            and (color_length := len(color)) in color_types
            and all(isinstance(val, (int, float)) and 0.0 <= val <= 1.0 for val in color)
        ):
            # Create instance of the appropriate subclass
            color_subclass = color_types[color_length]
            kwargs = dict(zip(color_subclass._ordered_fields, color))
            return color_subclass(**kwargs)

        return None

    def as_operator(self, stroke: bool = False) -> str:
        """
        Returns the PDF color operator as a string.

        Args:
            stroke: Returns stroke (i.e., uppercase) color operator if True
        """
        values = [f"{round(getattr(self, field), 3):g}" for field in self._ordered_fields]
        return f"{' '.join(values)} {self.color_operator.upper() if stroke else self.color_operator}"


@dataclass
class DeviceGray(Color):
    gray: float = 0.0

    color_operator = "g"
    _ordered_fields = ("gray",)


@dataclass
class DeviceRGB(Color):
    red: float = 0.0
    green: float = 0.0
    blue: float = 0.0

    color_operator = "rg"
    _ordered_fields = ("red", "green", "blue")


@dataclass
class DeviceCMYK(Color):
    cyan: float = 0.0
    magenta: float = 0.0
    yellow: float = 0.0
    black: float = 1.0

    color_operator = "k"
    _ordered_fields = ("cyan", "magenta", "yellow", "black")
