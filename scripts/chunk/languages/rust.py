"""Rust tree-sitter language spec."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_rust as tsr
from tree_sitter import Language, Node, Parser

from chunk.base import is_public_rust, make_chunk, source_text
from chunk.spec import ChunkContext, RegisteredLanguage

RUST_EXTENSIONS = frozenset({".rs"})
_PARSER: Parser | None = None


def _get_parser() -> Parser:
    global _PARSER
    if _PARSER is None:
        _PARSER = Parser(Language(tsr.language()))
    return _PARSER


def parser_for_file(_file_path: Path) -> Parser:
    return _get_parser()


def outer_doc_before(source: bytes, node: Node) -> str:
    sibling = node.prev_sibling
    lines: list[str] = []
    while sibling is not None and sibling.type == "line_comment":
        text = source_text(source, sibling)
        if text.startswith("///"):
            lines.insert(0, text.removeprefix("///").strip())
        elif text.startswith("//") and not text.startswith("//!"):
            lines.insert(0, text.removeprefix("//").strip())
        else:
            break
        sibling = sibling.prev_sibling
    return "\n".join(lines).strip()


def module_docstring(source: bytes, root: Node) -> str:
    for child in root.children:
        if child.type != "line_comment":
            break
        text = source_text(source, child)
        if text.startswith("//!"):
            return text.removeprefix("//!").strip()
    return ""


def extract_imports(source: bytes, root: Node) -> list[str]:
    imports: list[str] = []
    for child in root.children:
        if child.type == "use_declaration":
            statement = source_text(source, child).rstrip(";").strip()
            if statement:
                imports.append(statement)
    return imports


def skip_top_level(node: Node) -> bool:
    return node.type in {"use_declaration", "line_comment", "mod_item", "extern_crate_declaration"}


def unwrap_top_level(node: Node) -> Node | None:
    return node


def item_name(source: bytes, node: Node) -> str | None:
    for child in node.children:
        if child.type in {"type_identifier", "identifier", "field_identifier"}:
            return source_text(source, child)
    return None


def chunk_struct_fields(ctx: ChunkContext, node: Node, struct_name: str) -> None:
    field_list = next(
        (child for child in node.children if child.type == "field_declaration_list"),
        None,
    )
    if field_list is None:
        return
    for field in field_list.children:
        if field.type != "field_declaration":
            continue
        if not is_public_rust(field):
            continue
        name = next(
            (source_text(ctx.source, child) for child in field.children if child.type == "field_identifier"),
            None,
        )
        if not name:
            continue
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="property",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, field),
                docstring=outer_doc_before(ctx.source, field),
                imports=ctx.imports,
                bases=[],
                is_public=True,
                parent_class=struct_name,
                start_line=field.start_point[0] + 1,
            )
        )


def chunk_impl_methods(ctx: ChunkContext, node: Node, type_name_value: str) -> None:
    body = next((child for child in node.children if child.type == "declaration_list"), None)
    if body is None:
        return
    for item in body.children:
        if item.type != "function_item":
            continue
        name = item_name(ctx.source, item)
        if not name:
            continue
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="method",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, item),
                docstring=outer_doc_before(ctx.source, item),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_rust(item),
                parent_class=type_name_value,
                start_line=item.start_point[0] + 1,
            )
        )


def process_declaration(ctx: ChunkContext, node: Node) -> None:
    if node.type == "impl_item":
        name = item_name(ctx.source, node)
        if not name:
            return
        chunk_impl_methods(ctx, node, name)
        return

    if not is_public_rust(node):
        return

    name = item_name(ctx.source, node)
    if not name:
        return

    kind_map = {
        "struct_item": "class",
        "enum_item": "enum",
        "trait_item": "trait",
        "type_item": "type",
        "function_item": "function",
    }
    kind = kind_map.get(node.type)
    if kind is None:
        return

    ctx.chunks.append(
        make_chunk(
            library=ctx.library,
            symbol=name,
            kind=kind,
            mod=ctx.mod,
            relative_path=ctx.relative_path,
            source=source_text(ctx.source, node),
            docstring=outer_doc_before(ctx.source, node),
            imports=ctx.imports,
            bases=[],
            is_public=True,
            start_line=node.start_point[0] + 1,
        )
    )
    if node.type == "struct_item":
        chunk_struct_fields(ctx, node, name)


SPEC = RegisteredLanguage(
    name="rust",
    extensions=RUST_EXTENSIONS,
    parser_for_file=parser_for_file,
    extract_imports=extract_imports,
    module_docstring=module_docstring,
    skip_top_level=skip_top_level,
    unwrap_top_level=unwrap_top_level,
    process_declaration=process_declaration,
)
