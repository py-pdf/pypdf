"""Generic tree-sitter file and library chunking."""

from __future__ import annotations

from pathlib import Path

from common import CodeChunk, LibraryConfig, iter_library_files, repo_dir_for

from chunk.base import make_chunk, module_name
from chunk.spec import ChunkContext, RegisteredLanguage


def chunk_file(
    library: LibraryConfig,
    file_path: Path,
    spec: RegisteredLanguage,
    repo_root: Path | None = None,
) -> list[CodeChunk]:
    source_bytes = file_path.read_bytes()
    parser = spec.parser_for_file(file_path)
    tree = parser.parse(source_bytes)
    root = tree.root_node
    if root.has_error:
        return []

    root_dir = repo_root if repo_root is not None else repo_dir_for(library)
    mod = module_name(library, file_path, repo_root=root_dir)
    relative_path = file_path.relative_to(root_dir).as_posix()
    imports = spec.extract_imports(source_bytes, root)
    ctx = ChunkContext(
        library=library,
        file_path=file_path,
        source=source_bytes,
        mod=mod,
        relative_path=relative_path,
        imports=imports,
    )

    module_doc = spec.module_docstring(source_bytes, root)
    if module_doc:
        ctx.chunks.append(
            make_chunk(
                library=library,
                symbol=Path(relative_path).stem,
                kind="module",
                mod=mod,
                relative_path=relative_path,
                source=module_doc,
                docstring=module_doc,
                imports=imports,
                bases=[],
                is_public=True,
                start_line=1,
            )
        )

    for child in root.children:
        if spec.skip_top_level(child):
            continue
        declaration = spec.unwrap_top_level(child)
        if declaration is None:
            continue
        spec.process_declaration(ctx, declaration)

    return [chunk for chunk in ctx.chunks if chunk.source]


def chunk_library_with_spec(library: LibraryConfig, spec: RegisteredLanguage) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []
    for file_path in iter_library_files(library):
        if file_path.suffix.lower() not in spec.extensions:
            continue
        chunks.extend(chunk_file(library, file_path, spec))
    return chunks
