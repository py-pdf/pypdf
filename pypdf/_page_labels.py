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
import math
import string
from bisect import bisect_left, bisect_right
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, cast

from ._protocols import PdfCommonDocProtocol
from ._utils import logger_warning
from .generic import (
    ArrayObject,
    DictionaryObject,
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


def _get_label(value: Any, start_index: Any, index: int) -> str:
    m: dict[str | None, Callable[[int], str]] = {
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


def get_label_from_nums(dictionary_object: DictionaryObject, index: int) -> str:
    # [Nums] shall be an array of the form
    #   [ key_1 value_1 key_2 value_2 ... key_n value_n ]
    # where each key_i is an integer and the corresponding
    # value_i shall be the object associated with that key.
    # The keys shall be sorted in numerical order,
    # analogously to the arrangement of keys in a name tree
    # as described in 7.9.6, "Name Trees."
    nums = dictionary_object["/Nums"]
    if not isinstance(nums, ArrayObject):
        logger_warning(
            "Page label numbers are not an array: %(nums)s",
            source=__name__,
            nums=nums,
        )
        return str(index + 1)  # Fallback
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
    return _get_label(value, start_index, index)


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


def _get_labels_from_nums(nums: ArrayObject, indexes: Iterable[int]) -> list[str]:
    """
    Labels for increasing page indexes, as ``get_label_from_nums`` would return them.

    ``get_label_from_nums`` stops at the first pair whose next key is above the page index.
    As that pair can only move forward when the page index grows, the array is read once
    for all pages instead of from the start for every page, and each value is resolved
    when its pair is first reached.
    """
    nums_length = len(nums)
    labels = []
    i = 0
    resolved = -1
    start_index: Any = 0
    value: Any = None
    for index in indexes:
        is_key_malformed = False
        while i < nums_length:
            if i + 1 >= nums_length:
                logger_warning("Ignoring last /Nums key without a value.", source=__name__)
                break
            if resolved != i:
                start_index = nums[i]
                value = nums[i + 1].get_object()
                resolved = i
            if i + 2 == nums_length:
                break
            next_key = nums[i + 2]
            if not isinstance(next_key, (int, float)):
                logger_warning(
                    "Ignoring malformed page label key %(key)r in /Nums.",
                    source=__name__,
                    key=next_key,
                )
                is_key_malformed = True
                break
            if next_key > index:
                break
            i += 2
        labels.append(str(index + 1) if is_key_malformed else _get_label(value, start_index, index))
    return labels


def _get_page_range(limits: list[Any], page_count: int) -> tuple[int, int] | None:
    """Get the first and last page index between the two ``/Limits`` values, if any."""
    low, high = limits[0], limits[1]
    if any(isinstance(limit, float) and math.isnan(limit) for limit in (low, high)):
        return None
    if low > page_count - 1 or high < 0:
        return None
    first = 0 if low <= 0 else math.ceil(low)
    last = page_count - 1 if high >= page_count - 1 else math.floor(high)
    return (first, last) if first <= last else None


class _FirstKidFinder:
    """
    Find the kid ``index2label`` picks for a page index: the first kid in order whose
    ``/Limits`` contain it.

    Like ``index2label``, kids are read in order and only as far as needed. The pages
    covered by the kids read so far are kept as sorted ranges, so that each kid is read
    once instead of once per page. A kid which cannot be read is returned as the
    exception, which ``index2label`` raises for every page that reaches this kid.
    """

    def __init__(self, kids: ArrayObject, page_count: int) -> None:
        self._kids = kids
        self._page_count = page_count
        self._next_kid = 0
        # Pages covered by any kid read so far, as merged ranges.
        self._covered_starts: list[int] = []
        self._covered_ends: list[int] = []
        # Ranges of pages with the same first kid.
        self._starts: list[int] = []
        self._ends: list[int] = []
        self._first_kids: list[DictionaryObject | Exception] = []

    def find(self, index: int) -> DictionaryObject | Exception | None:
        while True:
            position = bisect_right(self._starts, index) - 1
            if position >= 0 and index <= self._ends[position]:
                return self._first_kids[position]
            if self._next_kid >= len(self._kids):
                return None
            kid_range = self._read_kid(self._kids[self._next_kid])
            self._next_kid += 1
            if kid_range is not None:
                self._cover(*kid_range)

    def _read_kid(self, kid: Any) -> tuple[int, int, DictionaryObject | Exception] | None:
        try:
            kid = kid.get_object()
            limits = kid.get("/Limits", NullObject()).get_object() if isinstance(kid, DictionaryObject) else None
        except Exception as exception:
            return 0, self._page_count - 1, exception
        if not isinstance(kid, DictionaryObject):
            logger_warning("Ignoring kid which is not a dictionary in /PageLabels.", source=__name__)
            return None
        if (
            not isinstance(limits, list)
            or len(limits) < 2
            or not all(isinstance(limit, (int, float)) for limit in limits[:2])
        ):
            logger_warning("Ignoring kid with missing or malformed /Limits in /PageLabels.", source=__name__)
            return None
        page_range = _get_page_range(limits, self._page_count)
        return None if page_range is None else (*page_range, kid)

    def _cover(self, first: int, last: int, kid: DictionaryObject | Exception) -> None:
        """Make ``kid`` the first kid of the pages from ``first`` to ``last`` which no earlier kid covers."""
        start = bisect_left(self._covered_ends, first)
        end = bisect_right(self._covered_starts, last)
        gaps = []
        position = first
        for covered_start, covered_end in zip(self._covered_starts[start:end], self._covered_ends[start:end]):
            if covered_start > position:
                gaps.append((position, covered_start - 1))
            position = max(position, covered_end + 1)
        if position <= last:
            gaps.append((position, last))
        if start < end:
            first = min(first, self._covered_starts[start])
            last = max(last, self._covered_ends[end - 1])
        self._covered_starts[start:end] = [first]
        self._covered_ends[start:end] = [last]
        for gap_start, gap_end in gaps:
            position = bisect_left(self._starts, gap_start)
            self._starts.insert(position, gap_start)
            self._ends.insert(position, gap_end)
            self._first_kids.insert(position, kid)


def _get_labels_from_kids(number_tree: DictionaryObject, page_count: int) -> list[str]:
    """
    Labels of the first ``page_count`` pages of a ``/Kids`` number tree, as ``index2label`` would return them.

    Instead of walking the tree from the root for every page, each ``/Kids`` array is
    indexed once and each ``/Nums`` array is read once for all of its pages. Warnings
    about malformed kids are logged once per array instead of once per page.
    """
    finders: dict[int, tuple[ArrayObject, _FirstKidFinder]] = {}
    leaves: dict[int, tuple[ArrayObject | None, DictionaryObject, list[int]]] = {}
    unmatched: list[int] = []
    nodes = [(number_tree, list(range(page_count)), 0)]
    while nodes:
        node, indexes, level = nodes.pop()
        kids = node["/Kids"].get_object()
        if not isinstance(kids, ArrayObject):
            logger_warning("Page label kids are not an array: %(kids)s", source=__name__, kids=kids)
            unmatched.extend(indexes)
            continue
        if id(kids) not in finders:
            finders[id(kids)] = (kids, _FirstKidFinder(kids, page_count))
        finder = finders[id(kids)][1]
        groups: dict[int, tuple[DictionaryObject, list[int]]] = {}
        for index in indexes:
            kid = finder.find(index)
            if isinstance(kid, Exception):
                raise kid
            if kid is None:
                unmatched.append(index)
            else:
                groups.setdefault(id(kid), (kid, []))[1].append(index)
        for kid, kid_indexes in groups.values():
            if not is_null_or_none(kid.get("/Kids", None)):
                if level + 1 == 100:  # pragma: no cover
                    raise NotImplementedError("Too deep nesting is not supported.")
                nodes.append((kid, kid_indexes, level + 1))
                continue
            # Leaves sharing a /Nums array are read together.
            nums = kid["/Nums"]
            if isinstance(nums, ArrayObject):
                leaves.setdefault(id(nums), (nums, kid, []))[2].extend(kid_indexes)
            else:
                leaves.setdefault(id(kid), (None, kid, []))[2].extend(kid_indexes)

    labels = [""] * page_count
    for leaf_nums, leaf, leaf_indexes in leaves.values():
        leaf_indexes.sort()
        leaf_labels = (
            _get_labels_from_nums(leaf_nums, leaf_indexes)
            if leaf_nums is not None
            else [get_label_from_nums(leaf, index) for index in leaf_indexes]
        )
        for index, label in zip(leaf_indexes, leaf_labels):
            labels[index] = label
    for index in sorted(unmatched):
        logger_warning("Could not reliably determine page label for %(index)d.", source=__name__, index=index)
        labels[index] = str(index + 1)
    return labels


def _index2labels_page_by_page(pdf: PdfCommonDocProtocol, page_count: int) -> list[str]:
    return [index2label(pdf, index) for index in range(page_count)]


def index2labels(pdf: PdfCommonDocProtocol, page_count: int) -> list[str]:
    """
    Labels of the first ``page_count`` pages, as ``index2label`` would return them.

    Number trees are read once for all pages instead of from the start for every page.
    """
    if page_count <= 0:
        return []
    root = cast(DictionaryObject, pdf.root_object)
    if "/PageLabels" not in root:
        return _index2labels_page_by_page(pdf, page_count)
    number_tree = root["/PageLabels"].get_object()
    if not isinstance(number_tree, DictionaryObject):
        return _index2labels_page_by_page(pdf, page_count)
    if "/Nums" in number_tree:
        nums = number_tree["/Nums"]
        if not isinstance(nums, ArrayObject):
            return [get_label_from_nums(number_tree, index) for index in range(page_count)]
        return _get_labels_from_nums(nums, range(page_count))
    if "/Kids" in number_tree and not isinstance(number_tree["/Kids"], NullObject):
        return _get_labels_from_kids(number_tree, page_count)
    return _index2labels_page_by_page(pdf, page_count)


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
) -> tuple[NumberObject | None, DictionaryObject | None]:
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
