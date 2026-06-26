"""TypeScript tree-sitter language spec."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_typescript as tst
from tree_sitter import Language, Node, Parser

from chunk.base import is_public_name, make_chunk, source_text
from chunk.spec import ChunkContext, RegisteredLanguage

TS_EXTENSIONS = frozenset({".ts", ".tsx", ".mts", ".cts"})
_TS_PARSER: Parser | None = None
_TSX_PARSER: Parser | None = None


def _parser_for_suffix(suffix: str) -> Parser:
    global _TS_PARSER, _TSX_PARSER
    if suffix == ".tsx":
        if _TSX_PARSER is None:
            _TSX_PARSER = Parser(Language(tst.language_tsx()))
        return _TSX_PARSER
    if _TS_PARSER is None:
        _TS_PARSER = Parser(Language(tst.language_typescript()))
    return _TS_PARSER


def parser_for_file(file_path: Path) -> Parser:
    return _parser_for_suffix(file_path.suffix.lower())


def clean_jsdoc(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("/**"):
            stripped = stripped[3:].strip()
        elif stripped.startswith("*/"):
            stripped = stripped[2:].strip()
        elif stripped.endswith("*/"):
            stripped = stripped[:-2].strip()
        if stripped.startswith("*"):
            stripped = stripped[1:].strip()
        if stripped:
            lines.append(stripped)
    return "\n".join(lines).strip()


def jsdoc_before(source: bytes, node: Node) -> str:
    sibling = node.prev_sibling
    while sibling is not None and sibling.type == "comment":
        text = source_text(source, sibling)
        if text.startswith("/**"):
            return clean_jsdoc(text)
        sibling = sibling.prev_sibling
    return ""


def module_docstring(source: bytes, root: Node) -> str:
    for child in root.children:
        if child.type == "comment":
            text = source_text(source, child)
            if text.startswith("/**"):
                return clean_jsdoc(text)
            continue
        if child.type == "import_statement":
            continue
        break
    return ""


def extract_imports(source: bytes, root: Node) -> list[str]:
    imports: list[str] = []
    for child in root.children:
        if child.type == "import_statement":
            statement = source_text(source, child).rstrip(";").strip()
            if statement:
                imports.append(statement)
    return imports


def node_name(source: bytes, node: Node) -> str | None:
    for child in node.children:
        if child.type in {"identifier", "type_identifier", "property_identifier"}:
            return source_text(source, child)
    return None


def declaration_bases(source: bytes, node: Node) -> list[str]:
    bases: list[str] = []
    for child in node.children:
        if child.type == "class_heritage":
            for clause in child.children:
                if clause.type == "extends_clause":
                    for base in clause.children:
                        if base.type in {"identifier", "type_identifier"}:
                            bases.append(source_text(source, base))
                elif clause.type == "implements_clause":
                    for base in clause.children:
                        if base.type == "type_identifier":
                            bases.append(source_text(source, base))
        elif child.type == "extends_type_clause":
            for base in child.children:
                if base.type == "type_identifier":
                    bases.append(source_text(source, base))
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


def skip_top_level(node: Node) -> bool:
    return node.type in {"import_statement", "comment", ";"}


def unwrap_top_level(node: Node) -> Node | None:
    if node.type != "export_statement":
        return node
    for child in node.children:
        if child.type in {"export", "default", ";"}:
            continue
        return child
    return None


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
        elif member.type == "public_field_definition":
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
    elif node.type == "interface_declaration":
        name = node_name(source, node)
        if not name:
            return
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="interface",
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
    elif node.type == "type_alias_declaration":
        name = node_name(source, node)
        if not name:
            return
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="type",
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
    elif node.type == "function_signature":
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


SPEC = RegisteredLanguage(
    name="typescript",
    extensions=TS_EXTENSIONS,
    parser_for_file=parser_for_file,
    extract_imports=extract_imports,
    module_docstring=module_docstring,
    skip_top_level=skip_top_level,
    unwrap_top_level=unwrap_top_level,
    process_declaration=process_declaration,
)
