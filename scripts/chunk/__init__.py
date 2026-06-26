"""Unified tree-sitter chunking for indexed library sources."""

from __future__ import annotations

from chunk.languages import get_language_spec
from chunk.treesitter import chunk_library_with_spec

__all__ = ["chunk_library_with_spec", "get_language_spec"]
