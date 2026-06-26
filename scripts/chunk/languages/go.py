"""Go tree-sitter language spec."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_go as tsg
from tree_sitter import Language, Node, Parser

from chunk.base import is_public_go, make_chunk, source_text
from chunk.spec import ChunkContext, RegisteredLanguage

GO_EXTENSIONS = frozenset({".go"})
_PARSER: Parser | None = None


def _get_parser() -> Parser:
    global _PARSER
    if _PARSER is None:
        _PARSER = Parser(Language(tsg.language()))
    return _PARSER


def parser_for_file(_file_path: Path) -> Parser:
    return _get_parser()


def comment_before(source: bytes, node: Node) -> str:
    sibling = node.prev_sibling
    while sibling is not None and sibling.type == "comment":
        text = source_text(source, sibling)
        if text.startswith("//") or text.startswith("/*"):
            return text.removeprefix("//").strip()
        sibling = sibling.prev_sibling
    return ""


def module_docstring(source: bytes, root: Node) -> str:
    for child in root.children:
        if child.type != "comment":
            break
        text = source_text(source, child).removeprefix("//").strip()
        if text.startswith("Package "):
            return text
    return ""


def extract_imports(source: bytes, root: Node) -> list[str]:
    imports: list[str] = []
    for child in root.children:
        if child.type == "import_declaration":
            statement = source_text(source, child).strip()
            if statement:
                imports.append(statement)
    return imports


def skip_top_level(node: Node) -> bool:
    return node.type in {"package_clause", "import_declaration", "comment"}


def unwrap_top_level(node: Node) -> Node | None:
    return node


def type_spec(node: Node) -> Node | None:
    if node.type != "type_declaration":
        return None
    return next((child for child in node.children if child.type == "type_spec"), None)


def type_name(source: bytes, spec: Node) -> str | None:
    for child in spec.children:
        if child.type == "type_identifier":
            return source_text(source, child)
    return None


def receiver_type_name(source: bytes, node: Node) -> str | None:
    params = next((child for child in node.children if child.type == "parameter_list"), None)
    if params is None:
        return None
    for param in params.children:
        if param.type != "parameter_declaration":
            continue
        for child in param.children:
            if child.type == "type_identifier":
                return source_text(source, child)
            if child.type == "pointer_type":
                for part in child.children:
                    if part.type == "type_identifier":
                        return source_text(source, part)
    return None


def method_name(source: bytes, node: Node) -> str | None:
    if node.type == "method_declaration":
        for child in node.children:
            if child.type == "field_identifier":
                return source_text(source, child)
        return None
    for child in node.children:
        if child.type == "identifier":
            return source_text(source, child)
    return None


def chunk_struct_fields(ctx: ChunkContext, spec: Node, struct_name: str) -> None:
    struct_type = next((child for child in spec.children if child.type == "struct_type"), None)
    if struct_type is None:
        return
    field_list = next(
        (child for child in struct_type.children if child.type == "field_declaration_list"),
        None,
    )
    if field_list is None:
        return
    for field in field_list.children:
        if field.type != "field_declaration":
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
                docstring=comment_before(ctx.source, field),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_go(name),
                parent_class=struct_name,
                start_line=field.start_point[0] + 1,
            )
        )


def chunk_interface_methods(ctx: ChunkContext, spec: Node, interface_name: str) -> None:
    interface_type = next((child for child in spec.children if child.type == "interface_type"), None)
    if interface_type is None:
        return
    for child in interface_type.children:
        if child.type != "method_elem":
            continue
        name = next(
            (source_text(ctx.source, part) for part in child.children if part.type == "field_identifier"),
            None,
        )
        if not name:
            continue
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="method",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, child),
                docstring="",
                imports=ctx.imports,
                bases=[],
                is_public=is_public_go(name),
                parent_class=interface_name,
                start_line=child.start_point[0] + 1,
            )
        )


def process_type_declaration(ctx: ChunkContext, node: Node) -> None:
    spec = type_spec(node)
    if spec is None:
        return
    name = type_name(ctx.source, spec)
    if not name:
        return

    if any(child.type == "struct_type" for child in spec.children):
        kind = "class"
    elif any(child.type == "interface_type" for child in spec.children):
        kind = "interface"
    else:
        kind = "type"

    ctx.chunks.append(
        make_chunk(
            library=ctx.library,
            symbol=name,
            kind=kind,
            mod=ctx.mod,
            relative_path=ctx.relative_path,
            source=source_text(ctx.source, node),
            docstring=comment_before(ctx.source, node),
            imports=ctx.imports,
            bases=[],
            is_public=is_public_go(name),
            start_line=node.start_point[0] + 1,
        )
    )
    if kind == "class":
        chunk_struct_fields(ctx, spec, name)
    elif kind == "interface":
        chunk_interface_methods(ctx, spec, name)


def process_declaration(ctx: ChunkContext, node: Node) -> None:
    if node.type == "type_declaration":
        process_type_declaration(ctx, node)
        return

    name = method_name(ctx.source, node)
    if not name:
        return

    if node.type == "method_declaration":
        parent = receiver_type_name(ctx.source, node)
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="method",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, node),
                docstring=comment_before(ctx.source, node),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_go(name),
                parent_class=parent,
                start_line=node.start_point[0] + 1,
            )
        )
    elif node.type == "function_declaration":
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="function",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, node),
                docstring=comment_before(ctx.source, node),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_go(name),
                start_line=node.start_point[0] + 1,
            )
        )


SPEC = RegisteredLanguage(
    name="go",
    extensions=GO_EXTENSIONS,
    parser_for_file=parser_for_file,
    extract_imports=extract_imports,
    module_docstring=module_docstring,
    skip_top_level=skip_top_level,
    unwrap_top_level=unwrap_top_level,
    process_declaration=process_declaration,
)
