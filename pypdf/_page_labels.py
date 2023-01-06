"""
Page labels are shown by PDF viewers as "the page number".

A page has a numeric index, starting with 0. Additionally to that, the page
has a label. In the most simple case:
    label = index + 1

However, the title page and the table of contents might have roman numerals as
page label. This makes things more complicated.

Example 1
---------

>>> reader.trailer["/Root"]["/PageLabels"]["/Nums"]
[0, IndirectObject(18, 0, 139929798197504),
 8, IndirectObject(19, 0, 139929798197504)]
>>> reader.get_object(reader.trailer["/Root"]["/PageLabels"]["/Nums"][1])
{'/S': '/r'}
>>> reader.get_object(reader.trailer["/Root"]["/PageLabels"]["/Nums"][3])
{'/S': '/D'}

Example 2
---------
The following example shows a document with pages labeled
i, ii, iii, iv, 1, 2, 3, A-8, A-9, ...

1 0 obj
    << /Type /Catalog
    /PageLabels << /Nums [
            0 << /S /r >>
            4 << /S /D >>
            7 << /S /D
            /P ( A- )
            /St 8
            >>
            % A number tree containing
            % three page label dictionaries
        ]
        >>
    ...
    >>
endobj


PDF Specification 1.7
=====================

Table 159 – Entries in a page label dictionary
----------------------------------------------
The S-key:
D       Decimal arabic numerals
R       Uppercase roman numerals
r       Lowercase roman numerals
A       Uppercase letters (A to Z for the first 26 pages,
                           AA to ZZ for the next 26, and so on)
a       Lowercase letters (a to z for the first 26 pages,
                           aa to zz for the next 26, and so on)
"""

from typing import Iterator

from ._protocols import PdfReaderProtocol
from ._utils import logger_warning


def number2uppercase_roman_numeral(num: int) -> str:
    roman = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    def roman_num(num: int) -> Iterator[str]:
        for decimal, roman_repr in roman:
            x, _ = divmod(num, decimal)
            yield roman_repr * x
            num -= decimal * x
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])


def number2lowercase_roman_numeral(number: int) -> str:
    return number2uppercase_roman_numeral(number).lower()


def number2uppercase_letter(number: int) -> str:
    if number <= 0:
        raise ValueError("Expecting a positive number")
    alphabet = [chr(i) for i in range(ord("A"), ord("Z") + 1)]
    rep = ""
    while number > 0:
        remainder = number % 26
        if remainder == 0:
            remainder = 26
        rep = alphabet[remainder - 1] + rep
        # update
        number -= remainder
        number = number // 26
    return rep


def number2lowercase_letter(number: int) -> str:
    return number2uppercase_letter(number).lower()


def index2label(reader: PdfReaderProtocol, index: int) -> str:
    """
    See 7.9.7 "Number Trees".

    Args:
        reader: The PdfReader
        index: The index of the page

    Returns:
        The label of the page, e.g. "iv" or "4".
    """
    root = reader.trailer["/Root"]
    if "/PageLabels" not in root:
        return str(index + 1)  # Fallback
    number_tree = root["/PageLabels"]
    if "/Nums" in number_tree:
        # [Nums] shall be an array of the form
        #   [ key 1 value 1 key 2 value 2 ... key n value n ]
        # where each key_i is an integer and the corresponding
        # value_i shall be the object associated with that key.
        # The keys shall be sorted in numerical order,
        # analogously to the arrangement of keys in a name tree
        # as described in 7.9.6, "Name Trees."
        nums = number_tree["/Nums"]
        i = 0
        value = None
        start_index = 0
        while i < len(nums):
            start_index = nums[i]
            value = nums[i + 1]
            if i + 2 == len(nums):
                break
            if nums[i + 2] > index:
                break
            i += 2
        m = {
            "/D": lambda n: str(n),
            "/R": number2uppercase_roman_numeral,
            "/r": number2lowercase_roman_numeral,
            "/A": number2uppercase_letter,
            "/a": number2lowercase_letter,
        }
        if not isinstance(value, dict):
            value = reader.get_object(value)
        if not isinstance(value, dict):
            return str(index + 1)  # Fallback
        return m[value["/S"]](index - start_index + 1)
    if "/Kids" in number_tree or "/Limits" in number_tree:
        logger_warning(
            (
                "/Kids or /Limits found in PageLabels. "
                "Please share this PDF with pypdf: "
                "https://github.com/py-pdf/pypdf/pull/1519"
            ),
            __name__,
        )
    # TODO: Implement /Kids and /Limits for number tree
    return str(index + 1)  # Fallback
