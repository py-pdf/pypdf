"""Language specification for tree-sitter chunking."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from tree_sitter import Node, Parser

from common import CodeChunk, LibraryConfig


@dataclass
class ChunkContext:
    library: LibraryConfig
    file_path: Path
    source: bytes
    mod: str
    relative_path: str
    imports: list[str]
    chunks: list[CodeChunk] = field(default_factory=list)


@dataclass
class RegisteredLanguage:
    name: str
    extensions: frozenset[str]
    parser_for_file: Callable[[Path], Parser]
    extract_imports: Callable[[bytes, Node], list[str]]
    module_docstring: Callable[[bytes, Node], str]
    skip_top_level: Callable[[Node], bool]
    unwrap_top_level: Callable[[Node], Node | None]
    process_declaration: Callable[[ChunkContext, Node], None]
