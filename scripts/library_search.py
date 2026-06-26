#!/usr/bin/env python3
"""Search indexed library source — ripgrep over repos/ and chunk cache. No vector DB."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from common import get_library_config, read_manifest, repo_dir_for

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "for",
        "to",
        "with",
        "using",
        "use",
        "how",
        "what",
        "when",
        "from",
        "into",
        "that",
        "this",
        "library",
        "code",
        "example",
        "please",
        "show",
        "write",
        "create",
        "generate",
        "implement",
        "build",
        "add",
        "script",
        "module",
        "function",
        "class",
    }
)


@dataclass
class SearchHit:
    library: str
    symbol: str
    kind: str
    module: str
    file_path: str
    document: str
    is_public: bool
    score: int
    source: str


def extract_search_terms(prompt: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\b[A-Za-z]{3,}\b", prompt)
    seen: set[str] = set()
    terms: list[str] = []
    for token in tokens:
        lower = token.lower()
        if lower in STOPWORDS or lower in seen:
            continue
        seen.add(lower)
        terms.append(token)
    if not terms:
        terms = [word for word in re.findall(r"\w+", prompt) if len(word) > 2][:5]
    return terms[:12]


def _score_text(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(lower.count(term.lower()) for term in terms)


def _repo_hits(library_name: str, terms: list[str], *, limit: int) -> list[SearchHit]:
    library = get_library_config(library_name)
    repo_root = repo_dir_for(library)
    if not repo_root.exists():
        return []

    pattern = "|".join(re.escape(term) for term in terms)
    hits: list[SearchHit] = []

    if shutil.which("rg"):
        result = subprocess.run(
            ["rg", "-n", "--no-heading", "--color=never", "-i", "-m", "1", pattern, "."],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        for line in result.stdout.splitlines()[: limit * 3]:
            try:
                location, _, content = line.partition(":")
                file_part, _, _line_no = location.partition(":")
                relative = Path(file_part)
                document = content.strip()
                score = _score_text(document, terms) + 1
                symbol = relative.stem
                hits.append(
                    SearchHit(
                        library=library_name,
                        symbol=symbol,
                        kind="source",
                        module=str(relative.with_suffix("")).replace("/", "."),
                        file_path=str(relative),
                        document=document,
                        is_public=not symbol.startswith("_"),
                        score=score,
                        source="repo",
                    )
                )
            except ValueError:
                continue
    else:
        for path in repo_root.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".go", ".rs", ".ts", ".js"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for index, line in enumerate(text.splitlines(), start=1):
                if any(term.lower() in line.lower() for term in terms):
                    relative = path.relative_to(repo_root)
                    hits.append(
                        SearchHit(
                            library=library_name,
                            symbol=path.stem,
                            kind="source",
                            module=str(relative.with_suffix("")).replace("/", "."),
                            file_path=f"{relative}:{index}",
                            document=line.strip(),
                            is_public=not path.stem.startswith("_"),
                            score=_score_text(line, terms),
                            source="repo",
                        )
                    )
                    break
            if len(hits) >= limit * 3:
                break

    hits.sort(key=lambda hit: (-hit.score, not hit.is_public, hit.file_path))
    deduped: list[SearchHit] = []
    seen_paths: set[str] = set()
    for hit in hits:
        if hit.file_path in seen_paths:
            continue
        seen_paths.add(hit.file_path)
        deduped.append(hit)
        if len(deduped) >= limit:
            break
    return deduped


def _chunk_hits(library_name: str, terms: list[str], *, limit: int) -> list[SearchHit]:
    from common import read_chunks_cache

    chunks = read_chunks_cache(library_name)
    if not chunks:
        return []

    scored: list[SearchHit] = []
    for chunk in chunks:
        blob = chunk.to_search_document()
        score = _score_text(blob, terms)
        if score <= 0:
            continue
        scored.append(
            SearchHit(
                library=library_name,
                symbol=chunk.symbol,
                kind=chunk.kind,
                module=chunk.module,
                file_path=chunk.file_path,
                document=blob,
                is_public=chunk.is_public,
                score=score + (2 if chunk.is_public else 0),
                source="chunk",
            )
        )

    scored.sort(key=lambda hit: (-hit.score, not hit.is_public, hit.symbol))
    return scored[:limit]


def search_library(
    name: str,
    prompt: str,
    *,
    top_k: int = 8,
    prefer_public: bool = True,
) -> list[SearchHit]:
    get_library_config(name)
    terms = extract_search_terms(prompt)
    chunk_results = _chunk_hits(name, terms, limit=top_k)
    repo_results = _repo_hits(name, terms, limit=top_k)

    combined = chunk_results + repo_results
    if prefer_public:
        combined.sort(key=lambda hit: (-hit.score, not hit.is_public, hit.source == "chunk"))
    else:
        combined.sort(key=lambda hit: (-hit.score, hit.symbol))

    deduped: list[SearchHit] = []
    seen: set[tuple[str, str]] = set()
    for hit in combined:
        key = (hit.symbol, hit.file_path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(hit)
        if len(deduped) >= top_k:
            break
    return deduped


def format_hits(
    name: str,
    prompt: str,
    hits: list[SearchHit],
    *,
    manifest: dict | None = None,
) -> str:
    header_lines = [
        f"# Retrieved patterns for `{name}`",
        f"Prompt: {prompt}",
        "Backend: Cursor codebase search (repos/ + chunk cache)",
    ]
    if manifest:
        header_lines.append(
            f"Index: {manifest['ref']} @ {manifest['commit'][:12]} "
            f"({manifest['chunk_count']} chunks)"
        )
    header_lines.extend(
        [
            "",
            "Tip: also use Cursor **Codebase Search** over "
            f"`repos/{name}/` and **nb-symbols** MCP for import validation.",
            "",
        ]
    )

    if not hits:
        header_lines.append(
            f"_No matches — try narrower terms or run `python scripts/index.py --library {name}`._"
        )
        return "\n".join(header_lines)

    sections: list[str] = []
    for hit in hits:
        header = (
            f"### {hit.symbol} ({hit.kind}) - {hit.module} "
            f"[{hit.source}, public={hit.is_public}]"
        )
        sections.append(f"{header}\n{hit.document}")
    return "\n".join(header_lines) + "\n\n---\n\n".join(sections)


def hits_to_json(name: str, prompt: str, hits: list[SearchHit], manifest: dict | None) -> str:
    payload = {
        "library": name,
        "prompt": prompt,
        "backend": "cursor-codebase",
        "manifest": manifest,
        "results": [
            {
                "symbol": hit.symbol,
                "kind": hit.kind,
                "module": hit.module,
                "file_path": hit.file_path,
                "is_public": hit.is_public,
                "source": hit.source,
                "score": hit.score,
                "document": hit.document,
            }
            for hit in hits
        ],
    }
    return json.dumps(payload, indent=2)
