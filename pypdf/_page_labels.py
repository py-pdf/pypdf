"""
Page labels are shown by PDF viewers as "the page number".

A page has a numeric index, starting at 0. Additionally, the page
has a label. In the most simple case:

    label = index + 1

However, the title page and the table of contents might have Roman numerals as
page labels. This makes things more complicated.

Example 1
---------

>>> reader.root_object["/PageLabels"]["/Nums"]
[0, IndirectObject(18, 0, 139929798197504),
 8, IndirectObject(19, 0, 139929798197504)]
>>> reader.get_object(reader.root_object["/PageLabels"]["/Nums"][1])
{'/S': '/r'}
>>> reader.get_object(reader.root_object["/PageLabels"]["/Nums"][3])
{'/S': '/D'}

Example 2
---------
The following is a document with pages labeled
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


§12.4.2 PDF Specification 1.7 and 2.0
=====================================

Entries in a page label dictionary
----------------------------------
The /S key:
D       Decimal Arabic numerals
R       Uppercase Roman numerals
r       Lowercase Roman numerals
A       Uppercase letters (A to Z for the first 26 pages,
                           AA to ZZ for the next 26, and so on)
a       Lowercase letters (a to z for the first 26 pages,
                           aa to zz for the next 26, and so on)
"""
import string
from typing import TYPE_CHECKING, Optional, cast

from ._protocols import PdfCommonDocProtocol
from ._utils import logger_warning
from .generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    is_null_or_none,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# The largest number one can represent using the usual symbols
# and subtractive notation without additional conventions.
# Aligns with https://github.com/AA-Turner/roman-numerals/blob/master/python/roman_numerals/__init__.py
MAXIMUM_ROMAN_NUMERAL = 3_999

# Allow values of up to 512 * 26 = 13_312 for the `/A` and `/a`.
# Please note that this limit is somehow arbitrary and some trade-off
# between rather restrictive <= 256 output bytes per label and the possibly
# unrealistic 1000 output bytes per label.
MAXIMUM_PAGE_LABEL_LENGTH = 512


def number2uppercase_roman_numeral(num: int) -> str:
    if num <= 0:
        raise ValueError("Expecting a positive number.")
    if num > MAXIMUM_ROMAN_NUMERAL:
        raise ValueError("Number is out of range.")
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

    result = []
    for value, symbol in roman:
        count, num = divmod(num, value)
        result.append(symbol * count)

    return "".join(result)


def number2lowercase_roman_numeral(number: int) -> str:
    return number2uppercase_roman_numeral(number).lower()


def number2uppercase_letter(number: int) -> str:
    if number <= 0:
        raise ValueError("Expecting a positive number.")
    # A to Z, then the same letter repeated: AA to ZZ, AAA to ZZZ, and so on.
    repetitions, position = divmod(number - 1, 26)
    length = repetitions + 1
    if length > MAXIMUM_PAGE_LABEL_LENGTH:
        raise ValueError("Number is too large.")
    return string.ascii_uppercase[position] * (repetitions + 1)


def number2lowercase_letter(number: int) -> str:
    return number2uppercase_letter(number).lower()


def get_label_from_nums(dictionary_object: DictionaryObject, index: int) -> str:
    # [Nums] shall be an array of the form
    #   [ key_1 value_1 key_2 value_2 ... key_n value_n ]
    # where each key_i is an integer and the corresponding
    # value_i shall be the object associated with that key.
    # The keys shall be sorted in numerical order,
    # analogously to the arrangement of keys in a name tree
    # as described in 7.9.6, "Name Trees."
    nums = cast(ArrayObject, dictionary_object["/Nums"])
    nums_length = len(nums)
    i = 0
    value = None
    start_index = 0
    while i < nums_length:
        if i + 1 >= nums_length:
            logger_warning(
                "Ignoring last /Nums key without a value.", source=__name__
            )
            break
        start_index = nums[i]
        value = nums[i + 1].get_object()
        if i + 2 == nums_length:
            break
        next_key = nums[i + 2]
        if not isinstance(next_key, (int, float)):
            logger_warning(
                "Ignoring malformed page label key %(key)r in /Nums.",
                source=__name__,
                key=next_key,
            )
            return str(index + 1)  # Fallback
        if next_key > index:
            break
        i += 2
    m: dict[Optional[str], Callable[[int], str]] = {
        None: lambda _: "",
        "/D": str,
        "/R": number2uppercase_roman_numeral,
        "/r": number2lowercase_roman_numeral,
        "/A": number2uppercase_letter,
        "/a": number2lowercase_letter,
    }
    # if /Nums array is not following the specification or if /Nums is empty
    if not isinstance(value, dict):
        return str(index + 1)  # Fallback
    start = value.get("/St", 1)
    prefix = cast(str, value.get("/P", ""))
    mapping_function = m.get(value.get("/S"))
    if mapping_function is None:
        # Unknown /S numbering style; fall back to the page position.
        logger_warning(
            "Ignoring unknown page label numbering style %(style)r in /Nums.",
            source=__name__,
            style=value.get("/S"),
        )
        return str(index + 1)  # Fallback
    try:
        return prefix + mapping_function(index - start_index + start)
    except (TypeError, ValueError) as exception:
        # Malformed /St or /P value; fall back to the page position.
        logger_warning(
            "Ignoring malformed page label entry in /Nums (/St=%(start)r, /P=%(prefix)r): %(exception)s",
            source=__name__,
            start=start,
            prefix=prefix,
            exception=exception,
        )
        return str(index + 1)  # Fallback


def index2label(reader: PdfCommonDocProtocol, index: int) -> str:
    """
    See 7.9.7 "Number Trees".

    Args:
        reader: The PdfReader
        index: The index of the page

    Returns:
        The label of the page, e.g. "iv" or "4".

    """
    root = cast(DictionaryObject, reader.root_object)
    if "/PageLabels" not in root:
        return str(index + 1)  # Fallback
    number_tree = root["/PageLabels"].get_object()
    if not isinstance(number_tree, DictionaryObject):
        logger_warning(
            "Page labels are not a dictionary: %(number_tree)s",
            source=__name__,
            number_tree=number_tree,
        )
        return str(index + 1)  # Fallback
    if "/Nums" in number_tree:
        return get_label_from_nums(number_tree, index)
    if "/Kids" in number_tree and not isinstance(number_tree["/Kids"], NullObject):
        # number_tree = {'/Kids': [IndirectObject(7333, 0, 140132998195856), ...]}
        # Limit maximum depth.
        level = 0
        while level < 100:
            kids = number_tree["/Kids"].get_object()
            if not isinstance(kids, ArrayObject):
                logger_warning(
                    "Page label kids are not an array: %(kids)s",
                    source=__name__,
                    kids=kids,
                )
                break
            for kid in kids:
                # kid = {'/Limits': [0, 63], '/Nums': [0, {'/P': 'C1'}, ...]}
                kid = kid.get_object()
                if not isinstance(kid, DictionaryObject):
                    logger_warning(
                        "Ignoring kid which is not a dictionary in /PageLabels.",
                        source=__name__,
                    )
                    continue
                limits = kid.get("/Limits", NullObject()).get_object()
                if not isinstance(limits, list) or len(limits) < 2:
                    # Skip kids whose /Limits range is missing or malformed.
                    logger_warning(
                        "Ignoring kid with missing or malformed /Limits in /PageLabels.",
                        source=__name__,
                    )
                    continue
                if limits[0] <= index <= limits[1]:
                    if not is_null_or_none(kid.get("/Kids", None)):
                        # Recursive definition.
                        level += 1
                        if level == 100:  # pragma: no cover
                            raise NotImplementedError(
                                "Too deep nesting is not supported."
                            )
                        number_tree = kid
                        # Exit the inner `for` loop and continue at the next level with the
                        # next iteration of the `while` loop.
                        break
                    return get_label_from_nums(kid, index)
            else:
                # When there are no kids, make sure to exit the `while` loop directly
                # and continue with the fallback.
                break

    logger_warning("Could not reliably determine page label for %(index)d.", source=__name__, index=index)
    return str(index + 1)  # Fallback if neither /Nums nor /Kids is in the number_tree


def _get_single_pass_nums_length(nums: ArrayObject, page_count: int) -> Optional[int]:
    """
    Get how much of a flat ``/Nums`` array labels the first ``page_count`` pages.

    ``get_label_from_nums`` always reads the first pair, then stops at the first
    key above the page index, so only the array up to the first key at or above
    ``page_count`` after the first pair matters. Returns ``None`` unless that
    part consists of pairs of increasing integer keys and direct values, which
    is what lets ``index2labels`` read it once for all pages.
    """
    nums_length = len(nums)
    previous = None
    for i in range(0, nums_length, 2):
        key = nums[i]
        if (
            i + 1 >= nums_length
            or not isinstance(key, NumberObject)
            or isinstance(nums[i + 1], IndirectObject)
            or (previous is not None and key <= previous)
        ):
            return None
        if key >= page_count and i > 0:
            return i + 2
        previous = key
    return nums_length or None


def _index2labels_page_by_page(pdf: PdfCommonDocProtocol, page_count: int) -> list[str]:
    return [index2label(pdf, index) for index in range(page_count)]


def index2labels(pdf: PdfCommonDocProtocol, page_count: int) -> list[str]:
    """
    Labels of the first ``page_count`` pages, as ``index2label`` would return them.

    A flat ``/Nums`` array with integer keys in increasing order and direct
    values is walked once for all pages instead of from the start for every
    page. Any other number tree is resolved page by page.
    """
    if page_count <= 0:
        return []
    root = cast(DictionaryObject, pdf.root_object)
    if "/PageLabels" not in root:
        return _index2labels_page_by_page(pdf, page_count)
    number_tree = root["/PageLabels"].get_object()
    if not isinstance(number_tree, DictionaryObject) or "/Nums" not in number_tree:
        return _index2labels_page_by_page(pdf, page_count)
    nums = number_tree["/Nums"]
    if not isinstance(nums, ArrayObject):
        return _index2labels_page_by_page(pdf, page_count)
    nums_length = _get_single_pass_nums_length(nums, page_count)
    if nums_length is None:
        return _index2labels_page_by_page(pdf, page_count)

    labels = []
    position = 0
    for index in range(page_count):
        while position + 2 < nums_length and nums[position + 2] <= index:
            position += 2
        entry = DictionaryObject({NameObject("/Nums"): ArrayObject(nums[position : position + 2])})
        labels.append(get_label_from_nums(entry, index))
    return labels


def nums_insert(
    key: NumberObject,
    value: DictionaryObject,
    nums: ArrayObject,
) -> None:
    """
    Insert a key, value pair in a Nums array.

    See 7.9.7 "Number Trees".

    Args:
        key: number key of the entry
        value: value of the entry
        nums: Nums array to modify

    """
    if len(nums) % 2 != 0:
        raise ValueError("A nums like array must have an even number of elements")

    i = len(nums)
    while i != 0 and key <= nums[i - 2]:
        i = i - 2

    if i < len(nums) and key == nums[i]:
        nums[i + 1] = value
    else:
        nums.insert(i, key)
        nums.insert(i + 1, value)


def nums_clear_range(
    key: NumberObject,
    page_index_to: int,
    nums: ArrayObject,
) -> None:
    """
    Remove all entries in a number tree in a range after an entry.

    See 7.9.7 "Number Trees".

    Args:
        key: number key of the entry before the range
        page_index_to: The page index of the upper limit of the range
        nums: Nums array to modify

    """
    if len(nums) % 2 != 0:
        raise ValueError("A nums like array must have an even number of elements")
    if page_index_to < key:
        raise ValueError("page_index_to must be greater or equal than key")

    i = nums.index(key) + 2
    while i < len(nums) and nums[i] <= page_index_to:
        nums.pop(i)
        nums.pop(i)


def nums_next(
    key: NumberObject,
    nums: ArrayObject,
) -> tuple[Optional[NumberObject], Optional[DictionaryObject]]:
    """
    Return the (key, value) pair of the entry after the given one.

    See 7.9.7 "Number Trees".

    Args:
        key: number key of the entry
        nums: Nums array

    """
    if len(nums) % 2 != 0:
        raise ValueError("A nums like array must have an even number of elements")

    i = nums.index(key) + 2
    if i < len(nums):
        return nums[i], nums[i + 1]
    return None, None
