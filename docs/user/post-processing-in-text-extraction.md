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
    ligatures_dict = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "ft",
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

```python
class FooterRemover:
    def fit(self, extracted_texts: List[str]) -> None:
        # Detect the common footer
        return

    def extract(self, extracted_text: str) -> str:
        # Remove the detected footer
        return extracted_text
```


## Community General Purpose Recommendation

```python
from typing import List


def postprocess(extracted_texts: List[str]) -> str:
    """Pass a list of all extracted texts from all pages."""
    extracted_texts = [replace_ligatures(t) for t in extracted_texts]
    extracted_texts = [remove_hyphens(t) for t in extracted_texts]
    footer_remover = FooterRemover().fit(extracted_texts)

    return "\n".join(extracted_texts)
```
