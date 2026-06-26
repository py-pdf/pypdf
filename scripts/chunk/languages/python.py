"""Python tree-sitter language spec."""

from __future__ import annotations

from pathlib import Path

import tree_sitter_python as tsp
from tree_sitter import Language, Node, Parser

from chunk.base import (
    block_docstring,
    is_public_name,
    make_chunk,
    source_text,
    strip_python_string,
)
from chunk.spec import ChunkContext, RegisteredLanguage

PY_EXTENSIONS = frozenset({".py"})
_PARSER: Parser | None = None


def _get_parser() -> Parser:
    global _PARSER
    if _PARSER is None:
        _PARSER = Parser(Language(tsp.language()))
    return _PARSER


def parser_for_file(_file_path: Path) -> Parser:
    return _get_parser()


def node_name(source: bytes, node: Node) -> str | None:
    for child in node.children:
        if child.type == "identifier":
            return source_text(source, child)
    return None


def class_bases(source: bytes, node: Node) -> list[str]:
    bases: list[str] = []
    for child in node.children:
        if child.type != "argument_list":
            continue
        for arg in child.children:
            if arg.type == "identifier":
                bases.append(source_text(source, arg))
            elif arg.type == "attribute":
                for part in arg.children:
                    if part.type == "identifier":
                        bases.append(source_text(source, part))
                        break
    return bases


def class_node(node: Node) -> Node | None:
    if node.type == "class_definition":
        return node
    if node.type == "decorated_definition":
        for child in node.children:
            if child.type == "class_definition":
                return child
    return None


def function_node(node: Node) -> Node | None:
    if node.type == "function_definition":
        return node
    if node.type == "decorated_definition":
        for child in node.children:
            if child.type == "function_definition":
                return child
    return None


def python_member_kind(source: bytes, node: Node) -> str:
    fn = function_node(node)
    if fn is None:
        return "method"
    parent = node if node.type == "decorated_definition" else fn
    if parent.type != "decorated_definition":
        return "method"
    for child in parent.children:
        if child.type != "decorator":
            continue
        text = source_text(source, child)
        if text == "@property":
            return "property"
        if text.endswith(".setter"):
            return "property_setter"
        if text.endswith(".deleter"):
            return "property_deleter"
    return "method"


def module_docstring(source: bytes, root: Node) -> str:
    for child in root.children:
        if child.type in {"import_statement", "import_from_statement", "comment"}:
            continue
        if child.type != "expression_statement":
            break
        string_node = next((c for c in child.children if c.type == "string"), None)
        if string_node is None:
            break
        return strip_python_string(source_text(source, string_node))
    return ""


def extract_imports(source: bytes, root: Node) -> list[str]:
    imports: list[str] = []
    for child in root.children:
        if child.type == "import_statement":
            statement = source_text(source, child).strip()
            if statement:
                imports.append(statement)
        elif child.type == "import_from_statement":
            statement = source_text(source, child).strip()
            if statement:
                imports.append(statement)
    return imports


def skip_top_level(node: Node) -> bool:
    return node.type in {"import_statement", "import_from_statement", "comment"}


def unwrap_top_level(node: Node) -> Node | None:
    return node


def chunk_class_body(ctx: ChunkContext, class_node: Node, class_name: str) -> None:
    block = next((child for child in class_node.children if child.type == "block"), None)
    if block is None:
        return
    for member in block.children:
        fn = function_node(member)
        if fn is None:
            continue
        name = node_name(ctx.source, fn)
        if not name:
            continue
        block = next((child for child in fn.children if child.type == "block"), None)
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind=python_member_kind(ctx.source, member),
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(ctx.source, member),
                docstring=block_docstring(ctx.source, block) if block else "",
                imports=ctx.imports,
                bases=[],
                is_public=is_public_name(name),
                parent_class=class_name,
                start_line=member.start_point[0] + 1,
            )
        )


def _docstring_for_definition(source: bytes, node: Node) -> str:
    block = next((child for child in node.children if child.type == "block"), None)
    if block is None:
        return ""
    return block_docstring(source, block)


def process_declaration(ctx: ChunkContext, node: Node) -> None:
    source = ctx.source
    cls = class_node(node)
    if cls is not None:
        name = node_name(source, cls)
        if not name:
            return
        outer = node if node.type == "decorated_definition" else cls
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="class",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(source, outer),
                docstring=_docstring_for_definition(source, cls),
                imports=ctx.imports,
                bases=class_bases(source, cls),
                is_public=is_public_name(name),
                start_line=outer.start_point[0] + 1,
            )
        )
        chunk_class_body(ctx, cls, name)
        return

    fn = function_node(node)
    if fn is not None:
        name = node_name(source, fn)
        if not name:
            return
        outer = node if node.type == "decorated_definition" else fn
        ctx.chunks.append(
            make_chunk(
                library=ctx.library,
                symbol=name,
                kind="function",
                mod=ctx.mod,
                relative_path=ctx.relative_path,
                source=source_text(source, outer),
                docstring=_docstring_for_definition(source, fn),
                imports=ctx.imports,
                bases=[],
                is_public=is_public_name(name),
                start_line=outer.start_point[0] + 1,
            )
        )


SPEC = RegisteredLanguage(
    name="python",
    extensions=PY_EXTENSIONS,
    parser_for_file=parser_for_file,
    extract_imports=extract_imports,
    module_docstring=module_docstring,
    skip_top_level=skip_top_level,
    unwrap_top_level=unwrap_top_level,
    process_declaration=process_declaration,
)
