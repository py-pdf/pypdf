# Post-Processing in Text Extraction

Post-processing can recognizably improve the results of text extraction.
It is, however, outside of the scope of pypdf itself. Hence the library will
not give any direct support for it. It is a natural language processing (NLP)
task.

This page lists a few examples what can be done as well as a community
recipie that can be used as a best-practice general purpose post processing
step. If you know more about the specific domain of your documents, e.g. the
language, it is likely that you can find custom solutions that work better in
your context

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

## De-Hyphenation

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

## Footer Removal

TODO: The following doesn't quite work. It should maybe also take page labels.

```python
class FooterRemover:
    def __init__(self):
        self.footer = None

    def fit(self, extracted_texts: List[str]) -> None:
        """
        Find the common footer by comparing all extracted texts
        and finding the common suffix.
        We assume that the footer appears at the end of each text.
        """
        common_suffix = None
        for text in extracted_texts:
            if common_suffix is None:
                common_suffix = text
            else:
                i = 1
                while i <= min(len(common_suffix), len(text)):
                    if common_suffix[-i:] != text[-i:]:
                        break
                    i += 1
                common_suffix = common_suffix[-(i - 1) :]

        self.footer = common_suffix

    def extract(self, extracted_text: str) -> str:
        """Remove the detected footer from the extracted text."""
        if self.footer is not None and extracted_text.endswith(self.footer):
            return extracted_text[: -len(self.footer)]
        return extracted_text
```

## Other ideas

* Whitespaces between Units: Between a number and it's unit should be a space
  ([source](https://tex.stackexchange.com/questions/20962/should-i-put-a-space-between-a-number-and-its-unit)).
  That means: 42 ms, 42 GHz, 42 GB.
* Percent: English style guides prescribe writing the percent sign following the number without any space between (e.g. 50%).
* Whitespaces before dots: Should typically be removed
* Whitespaces after dots: Should typically be added


## Community General Purpose Recommendation

```python
from typing import List


def postprocess(extracted_texts: List[str]) -> str:
    """Pass a list of all extracted texts from all pages."""
    extracted_texts = [replace_ligatures(t) for t in extracted_texts]
    extracted_texts = [remove_hyphens(t) for t in extracted_texts]
    footer_remover = FooterRemover()
    footer_remover.fit(extracted_texts)
    extracted_texts = [footer_remover.extract(t) for t in extracted_texts]

    return "\n".join(extracted_texts)


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
    for search, replace in ligatures_dict.items():
        text = text.replace(search, replace)
    return text


def remove_hyphens(text: str) -> str:
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


class FooterRemover:
    def __init__(self):
        self.footer = None

    def fit(self, extracted_texts: List[str]) -> None:
        """
        Find the common footer by comparing all extracted texts
        and finding the common suffix.
        We assume that the footer appears at the end of each text.
        """
        common_suffix = None
        for text in extracted_texts:
            if common_suffix is None:
                common_suffix = text
            else:
                i = 1
                while i <= min(len(common_suffix), len(text)):
                    if common_suffix[-i:] != text[-i:]:
                        break
                    i += 1
                common_suffix = common_suffix[-(i - 1) :]

        self.footer = common_suffix

    def extract(self, extracted_text: str) -> str:
        """Remove the detected footer from the extracted text."""
        if self.footer is not None and extracted_text.endswith(self.footer):
            return extracted_text[: -len(self.footer)]
        return extracted_text
```
