"""JavaScript tree-sitter language spec."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_javascript as tsj
from tree_sitter import Language, Node, Parser

from chunk.base import is_public_name, make_chunk, source_text
from chunk.languages.typescript import (
    extract_imports,
    jsdoc_before,
    module_docstring,
    skip_top_level,
    unwrap_top_level,
)
from chunk.spec import ChunkContext, RegisteredLanguage

JS_EXTENSIONS = frozenset({".js", ".jsx", ".mjs", ".cjs"})
_PARSER: Parser | None = None


def _get_parser() -> Parser:
    global _PARSER
    if _PARSER is None:
        _PARSER = Parser(Language(tsj.language()))
    return _PARSER


def parser_for_file(_file_path: Path) -> Parser:
    return _get_parser()


def node_name(source: bytes, node: Node) -> str | None:
    for child in node.children:
        if child.type in {"identifier", "property_identifier"}:
            return source_text(source, child)
    return None


def declaration_bases(source: bytes, node: Node) -> list[str]:
    bases: list[str] = []
    for child in node.children:
        if child.type != "class_heritage":
            continue
        for clause in child.children:
            if clause.type != "extends_clause":
                continue
            for base in clause.children:
                if base.type == "identifier":
                    bases.append(source_text(source, base))
                elif base.type == "member_expression":
                    parts = [
                        source_text(source, part)
                        for part in base.children
                        if part.type in {"identifier", "property_identifier"}
                    ]
                    if parts:
                        bases.append(".".join(parts))
    return bases


def member_kind(node: Node) -> str:
    if node.type != "method_definition":
        return "method"
    for child in node.children:
        if child.type == "get":
            return "property"
        if child.type == "set":
            return "property_setter"
    return "method"


def chunk_class_body(ctx: ChunkContext, class_node: Node, class_name: str) -> None:
    body = next((child for child in class_node.children if child.type == "class_body"), None)
    if body is None:
        return
    for member in body.children:
        if member.type == "method_definition":
            name = node_name(ctx.source, member)
            if not name:
                continue
            ctx.chunks.append(
                make_chunk(
                    library=ctx.library,
                    symbol=name,
                    kind=member_kind(member),
                    mod=ctx.mod,
                    relative_path=ctx.relative_path,
                    source=source_text(ctx.source, member),
                    docstring=jsdoc_before(ctx.source, member),
                    imports=ctx.imports,
                    bases=[],
                    is_public=is_public_name(name),
                    parent_class=class_name,
                    start_line=member.start_point[0] + 1,
                )
            )
        elif member.type == "field_definition":
            name = node_name(ctx.source, member)
            if not name:
                continue
            ctx.chunks.append(
                make_chunk(
                    library=ctx.library,
                    symbol=name,
                    kind="property",
                    mod=ctx.mod,
                    relative_path=ctx.relative_path,
                    source=source_text(ctx.source, member),
                    docstring=jsdoc_before(ctx.source, member),
                    imports=ctx.imports,
                    bases=[],
                    is_public=is_public_name(name),
                    parent_class=class_name,
                    start_line=member.start_point[0] + 1,
                )
            )


def process_declaration(ctx: ChunkContext, node: Node) -> None:
    source = ctx.source
    if node.type == "class_declaration":
        name = node_name(source, node)
        if not name:
            return
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="class",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(source, node),
                docstring=jsdoc_before(source, node),
                imports=ctx.imports,
                bases=declaration_bases(source, node),
                is_public=is_public_name(name),
                start_line=node.start_point[0] + 1,
            )
        )
        chunk_class_body(ctx, node, name)
    elif node.type == "function_declaration":
        name = node_name(source, node)
        if not name:
            return
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="function",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(source, node),
                docstring=jsdoc_before(source, node),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_name(name),
                start_line=node.start_point[0] + 1,
            )
        )
    elif node.type == "lexical_declaration":
        for child in node.children:
            if child.type != "variable_declarator":
                continue
            name = node_name(source, child)
            value = next(
                (
                    grandchild
                    for grandchild in child.children
                    if grandchild.type in {"arrow_function", "function"}
                ),
                None,
            )
            if not name or value is None:
                continue
            ctx.chunks.append(
                make_chunk(
                    library=ctx.library,
                    symbol=name,
                    kind="function",
                    mod=ctx.mod,
                    relative_path=ctx.relative_path,
                    source=source_text(source, child),
                    docstring=jsdoc_before(source, node),
                    imports=ctx.imports,
                    bases=[],
                    is_public=is_public_name(name),
                    start_line=child.start_point[0] + 1,
                )
            )


SPEC = RegisteredLanguage(
    name="javascript",
    extensions=JS_EXTENSIONS,
    parser_for_file=parser_for_file,
    extract_imports=extract_imports,
    module_docstring=module_docstring,
    skip_top_level=skip_top_level,
    unwrap_top_level=unwrap_top_level,
    process_declaration=process_declaration,
)
