"""Language registry for tree-sitter chunking."""

from __future__ import annotations

from chunk.languages.go import SPEC as GO_SPEC
from chunk.languages.javascript import SPEC as JAVASCRIPT_SPEC
from chunk.languages.python import SPEC as PYTHON_SPEC
from chunk.languages.rust import SPEC as RUST_SPEC
from chunk.languages.typescript import SPEC as TYPESCRIPT_SPEC
from chunk.spec import RegisteredLanguage

LANGUAGE_REGISTRY: dict[str, RegisteredLanguage] = {
    "python": PYTHON_SPEC,
    "typescript": TYPESCRIPT_SPEC,
    "javascript": JAVASCRIPT_SPEC,
    "go": GO_SPEC,
    "rust": RUST_SPEC,
}

IMPLEMENTED_LANGUAGES = frozenset({"python", "typescript", "javascript", "go", "rust"})


def get_language_spec(language: str) -> RegisteredLanguage:
    try:
        spec = LANGUAGE_REGISTRY[language]
    except KeyError as exc:
        known = ", ".join(sorted(LANGUAGE_REGISTRY)) or "(none)"
        raise SystemExit(f"Unknown indexing language '{language}'. Known: {known}") from exc
    if language not in IMPLEMENTED_LANGUAGES:
        raise SystemExit(
            f"Indexing for '{language}' is not implemented yet. "
            f"Implemented: {', '.join(sorted(IMPLEMENTED_LANGUAGES))}"
        )
    return spec
