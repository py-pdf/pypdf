"""Shared chunking helpers for tree-sitter language specs."""

from __future__ import annotations

from pathlib import Path

from tree_sitter import Node

from common import CodeChunk, LibraryConfig, repo_dir_for


def module_name(library: LibraryConfig, file_path: Path, repo_root: Path | None = None) -> str:
    root = repo_root if repo_root is not None else repo_dir_for(library)
    relative = file_path.relative_to(root)
    parts = relative.with_suffix("").parts
    return ".".join(parts)


def is_public_name(name: str) -> bool:
    return not name.startswith("_")


def is_public_go(name: str) -> bool:
    return bool(name) and name[0].isupper()


def is_public_rust(node: Node) -> bool:
    for child in node.children:
        if child.type == "visibility_modifier":
            return True
    return False


def source_text(source: bytes, node: Node) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8").strip()


def make_chunk(
    *,
    library: LibraryConfig,
    symbol: str,
    kind: str,
    mod: str,
    relative_path: str,
    source: str,
    docstring: str,
    imports: list[str],
    bases: list[str],
    is_public: bool,
    parent_class: str | None = None,
    start_line: int = 0,
) -> CodeChunk:
    return CodeChunk(
        library=library.name,
        symbol=symbol,
        kind=kind,
        module=mod,
        file_path=relative_path,
        source=source,
        docstring=docstring,
        imports=imports,
        bases=bases,
        is_public=is_public,
        parent_class=parent_class,
        start_line=start_line,
    )


def node_identifier(source: bytes, node: Node, types: frozenset[str]) -> str | None:
    for child in node.children:
        if child.type in types:
            return source_text(source, child)
    return None


def strip_python_string(text: str) -> str:
    text = text.strip()
    for prefix in ('"""', "'''", '"', "'"):
        if text.startswith(prefix) and text.endswith(prefix) and len(text) >= len(prefix) * 2:
            return text[len(prefix) : -len(prefix)].strip()
    return text


def block_docstring(source: bytes, block: Node) -> str:
    for child in block.children:
        if child.type != "expression_statement":
            break
        string_node = next((c for c in child.children if c.type == "string"), None)
        if string_node is None:
            break
        return strip_python_string(source_text(source, string_node))
    return ""
