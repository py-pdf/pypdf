# Post-Processing of Text Extraction

Post-processing can recognizably improve the results of text extraction. It is,
however, outside of the scope of pypdf itself. Hence the library will not give
any direct support for it. It is a natural language processing (NLP) task.

This page lists a few examples what can be done as well as a community recipe
that can be used as a general purpose post-processing step. If you know more
about the specific domain of your documents, e.g. the language, it is likely
that you can find custom solutions that work better in your context.

## Ligature Replacement

```python
def replace_ligatures(text: str) -> str:
    ligatures = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "ft",
        "ﬆ": "st",
        # "Ꜳ": "AA",
        # "Æ": "AE",
        "ꜳ": "aa",
    }
    for search, replace in ligatures.items():
        text = text.replace(search, replace)
    return text
```

## Dehyphenation

Hyphens are used to break words up so that the appearance of the page is nicer.

```python
from typing import List


def remove_hyphens(text: str) -> str:
    """

    This fails for:
    * Natural dashes: well-known, self-replication, use-cases, non-semantic,
                      Post-processing, Window-wise, viewpoint-dependent
    * Trailing math operands: 2 - 4
    * Names: Lopez-Ferreras, VGG-19, CIFAR-100
    """
    lines = [line.rstrip() for line in text.split("\n")]

    # Find dashes
    line_numbers = []
    for line_no, line in enumerate(lines[:-1]):
        if line.endswith("-"):
            line_numbers.append(line_no)

    # Replace
    for line_no in line_numbers:
        lines = dehyphenate(lines, line_no)

    return "\n".join(lines)


def dehyphenate(lines: List[str], line_no: int) -> List[str]:
    next_line = lines[line_no + 1]
    word_suffix = next_line.split(" ")[0]

    lines[line_no] = lines[line_no][:-1] + word_suffix
    lines[line_no + 1] = lines[line_no + 1][len(word_suffix) :]
    return lines
```

## Header/Footer Removal

The following header/footer removal has several drawbacks:

* False-positives, e.g. for the first page when there is a date like 2024.
* False-negatives in many cases:
    * Dynamic part, e.g. page label is in the header.
    * Even/odd pages have different headers.
    * Some pages, e.g. the first one or chapter pages, do not have a header.

```python
def remove_footer(extracted_texts: list[str], page_labels: list[str]):
    def remove_page_labels(extracted_texts, page_labels):
        processed = []
        for text, label in zip(extracted_texts, page_labels):
            text_left = text.lstrip()
            if text_left.startswith(label):
                text = text_left[len(label) :]

            text_right = text.rstrip()
            if text_right.endswith(label):
                text = text_right[: -len(label)]

            processed.append(text)
        return processed

    extracted_texts = remove_page_labels(extracted_texts, page_labels)
    return extracted_texts
```

## Other ideas

* Whitespaces in units: Between a number and its unit should be a space.
  ([source](https://tex.stackexchange.com/questions/20962/should-i-put-a-space-between-a-number-and-its-unit)).
  That means: 42 ms, 42 GHz, 42 GB.
* Percent: English style guides prescribe writing the percent sign following the number without any space between (e.g. 50%).
* Whitespaces before dots: Should typically be removed.
* Whitespaces after dots: Should typically be added.
