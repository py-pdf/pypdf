"""Tests for unified tree-sitter chunking."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS_DIR))

from chunk.languages.go import SPEC as GO_SPEC  # noqa: E402
from chunk.languages.javascript import SPEC as JAVASCRIPT_SPEC  # noqa: E402
from chunk.languages.python import SPEC as PYTHON_SPEC  # noqa: E402
from chunk.languages.rust import SPEC as RUST_SPEC  # noqa: E402
from chunk.languages.typescript import SPEC as TYPESCRIPT_SPEC  # noqa: E402
from chunk.treesitter import chunk_file  # noqa: E402
from common import (  # noqa: E402
    LibraryConfig,
    get_library_config,
    load_libraries_config,
    repo_dir_for,
)


@dataclass
class FakeLibrary(LibraryConfig):
    pass


def _fake_library(language: str) -> LibraryConfig:
    return FakeLibrary(
        name="fixture",
        repo=str(FIXTURES_DIR),
        ref="test",
        language=language,
        include=["**/*"],
        exclude=[],
    )


def _normalize_chunks(chunks):
    return [
        {
            "symbol": c.symbol,
            "kind": c.kind,
            "is_public": c.is_public,
            "parent_class": c.parent_class,
            "has_docstring": bool(c.docstring),
        }
        for c in chunks
    ]


def _chunk_fixture(filename: str, spec, language: str):
    library = _fake_library(language)
    file_path = FIXTURES_DIR / filename
    return chunk_file(library, file_path, spec, repo_root=FIXTURES_DIR)


def test_python_fixture_chunks():
    chunks = _chunk_fixture("sample.py", PYTHON_SPEC, "python")
    normalized = _normalize_chunks(chunks)
    symbols = {(c["symbol"], c["kind"], c["parent_class"]) for c in normalized}

    assert ("sample", "module", None) in symbols
    assert ("PublicClass", "class", None) in symbols
    assert ("DataclassConfig", "class", None) in symbols
    assert ("public_method", "method", "PublicClass") in symbols
    assert ("value", "property", "PublicClass") in symbols
    assert ("public_function", "function", None) in symbols
    assert ("_private_method", "method", "PublicClass") in symbols
    assert ("_private_function", "function", None) in symbols
    assert any(c["has_docstring"] for c in normalized if c["kind"] == "module")


def test_typescript_fixture_chunks():
    chunks = _chunk_fixture("sample.ts", TYPESCRIPT_SPEC, "typescript")
    normalized = _normalize_chunks(chunks)
    symbols = {(c["symbol"], c["kind"], c["parent_class"]) for c in normalized}

    assert ("sample", "module", None) in symbols
    assert ("PublicClass", "class", None) in symbols
    assert ("publicMethod", "method", "PublicClass") in symbols
    assert ("PublicInterface", "interface", None) in symbols
    assert ("PublicType", "type", None) in symbols
    assert ("publicFunction", "function", None) in symbols
    assert ("publicArrow", "function", None) in symbols
    assert ("_PrivateClass", "class", None) in symbols
    assert not any(c["is_public"] for c in normalized if c["symbol"] == "_privateMethod")


def test_javascript_fixture_chunks():
    chunks = _chunk_fixture("sample.js", JAVASCRIPT_SPEC, "javascript")
    normalized = _normalize_chunks(chunks)
    symbols = {(c["symbol"], c["kind"], c["parent_class"]) for c in normalized}

    assert ("sample", "module", None) in symbols
    assert ("PublicClass", "class", None) in symbols
    assert ("publicMethod", "method", "PublicClass") in symbols
    assert ("publicFunction", "function", None) in symbols
    assert ("publicArrow", "function", None) in symbols
    assert ("_PrivateClass", "class", None) in symbols
    assert not any(c["is_public"] for c in normalized if c["symbol"] == "_privateMethod")
    assert any(c["has_docstring"] for c in normalized if c["kind"] == "module")


def test_go_fixture_chunks():
    chunks = _chunk_fixture("sample.go", GO_SPEC, "go")
    normalized = _normalize_chunks(chunks)
    symbols = {(c["symbol"], c["kind"], c["parent_class"]) for c in normalized}

    assert ("sample", "module", None) in symbols
    assert ("PublicStruct", "class", None) in symbols
    assert ("PublicField", "property", "PublicStruct") in symbols
    assert ("PublicFunc", "function", None) in symbols
    assert ("PublicInterface", "interface", None) in symbols
    assert ("PublicMethod", "method", "PublicStruct") in symbols
    assert ("privateFunc", "function", None) in symbols
    assert not any(c["is_public"] for c in normalized if c["symbol"] == "privateField")
    assert any(c["has_docstring"] for c in normalized if c["kind"] == "module")


def test_rust_fixture_chunks():
    chunks = _chunk_fixture("sample.rs", RUST_SPEC, "rust")
    normalized = _normalize_chunks(chunks)
    symbols = {(c["symbol"], c["kind"], c["parent_class"]) for c in normalized}

    assert ("sample", "module", None) in symbols
    assert ("PublicStruct", "class", None) in symbols
    assert ("field", "property", "PublicStruct") in symbols
    assert ("public_fn", "function", None) in symbols
    assert ("PublicTrait", "trait", None) in symbols
    assert ("method", "method", "PublicStruct") in symbols
    assert ("private_fn", "function", None) not in symbols
    assert not any(c["is_public"] for c in normalized if c["symbol"] == "private_method")
    assert any(c["has_docstring"] for c in normalized if c["kind"] == "module")


def test_pypdf_symbol_regression():
    baseline_path = Path(__file__).resolve().parent / "pypdf_symbols_baseline.json"
    if not baseline_path.exists():
        pytest.skip("baseline not present")
    configured = {library.name for library in load_libraries_config()}
    if "pypdf" not in configured:
        pytest.skip("pypdf not configured in config/libraries.yaml")
    if not repo_dir_for(get_library_config("pypdf")).exists():
        pytest.skip("pypdf repo not crawled")
    baseline = set(json.loads(baseline_path.read_text())["symbols"])

    from chunk_ast import chunk_library

    chunks = chunk_library("pypdf")
    current = {c.symbol for c in chunks if c.is_public}
    assert current == baseline
