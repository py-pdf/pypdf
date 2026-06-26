#The static single source of truth (paths, schemas, globs). No logic is run here directly.
"""Shared utilities for Newbie."""

from __future__ import annotations

import fnmatch
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

def _resolve_project_root() -> Path:
    override = os.environ.get("NB_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    here = Path(__file__).resolve()
    seen: set[Path] = set()
    for path in [here.parent, *here.parents]:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / "scripts" / "doctor.py").is_file():
            return resolved
        scaffold = resolved / "scaffold"
        if (scaffold / "scripts" / "doctor.py").is_file():
            return scaffold
        if (resolved / ".newbie" / "libraries.yaml").is_file() or (
            resolved / "config" / "libraries.yaml"
        ).is_file():
            return resolved

    return here.parent.parent


PROJECT_ROOT = _resolve_project_root()

NB_HOME = PROJECT_ROOT / ".newbie"


def _legacy_root_layout() -> bool:
    """Detect pre-existing installs / the dev monorepo that keep Newbie state at
    the repo root (``config/``, ``store/``, ``repos/``).

    New customer repos get a single ``.newbie/`` folder instead, so everything
    Newbie generates lives in one place and is excluded by a single
    ``.gitignore`` entry — nothing else lands in the customer's git history.
    """
    return (
        (PROJECT_ROOT / "config" / "libraries.yaml").is_file()
        or (PROJECT_ROOT / "store").is_dir()
        or (PROJECT_ROOT / "repos").is_dir()
    )


USE_NB_HOME = not _legacy_root_layout()
# Single base for every artifact Newbie generates.
NB_STATE_DIR = NB_HOME if USE_NB_HOME else PROJECT_ROOT
CONFIG_DIR = NB_HOME if USE_NB_HOME else (PROJECT_ROOT / "config")

CONFIG_PATH = CONFIG_DIR / "libraries.yaml"
REPOS_DIR = NB_STATE_DIR / "repos"
STORE_DIR = NB_STATE_DIR / "store"
CHUNKS_DIR = STORE_DIR / "chunks"
MANIFESTS_DIR = STORE_DIR / "manifests"
# Per-user snapshots and team reports always live at repo-root ``reports/`` so
# engineers can commit ``reports/users/<id>.json`` via the pre-push hook even
# in thin (``.newbie/``) installs. The event log stays private under .newbie/.
REPORTS_DIR = PROJECT_ROOT / "reports"


def _resolve_events_dir() -> Path:
    """Single, consistent location for the local metrics event log.

    The event log used to land in ``.nb/metrics`` for legacy root installs and
    ``.newbie/metrics`` for new ``.newbie/`` installs, which split telemetry
    across two directories. Standardize on ``<root>/.newbie/metrics`` everywhere
    so hooks, ``sync_metrics.py``, and CI/cloud runs all read and write the same
    file. ``NB_METRICS_DIR`` overrides it (useful in CI/cloud sandboxes).
    """
    override = os.environ.get("NB_METRICS_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return NB_HOME / "metrics"


EVENTS_DIR = _resolve_events_dir()
# Legacy location kept for read-only back-compat (pre-standardization installs).
LEGACY_EVENTS_DIR = PROJECT_ROOT / ".nb" / "metrics"
CONVENTIONS_DIR = CONFIG_DIR / "conventions"


def resolve_config_path() -> Path:
    """Prefer the config file that actually lists libraries (.newbie or legacy config/)."""
    newbie = NB_HOME / "libraries.yaml"
    config = PROJECT_ROOT / "config" / "libraries.yaml"

    def _library_count(path: Path) -> int:
        if not path.is_file():
            return 0
        with path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        return len(raw.get("libraries") or [])

    newbie_count = _library_count(newbie)
    config_count = _library_count(config)
    if newbie_count > 0 and config_count == 0:
        return newbie
    if config_count > 0:
        return config
    if newbie.is_file():
        return newbie
    return CONFIG_PATH

MAX_SEARCH_DOCUMENT_CHARS = 20_000
TRUNCATION_SUFFIX = "\n... [truncated]"


def truncate_search_document(document: str) -> str:
    if len(document) > MAX_SEARCH_DOCUMENT_CHARS:
        return document[:MAX_SEARCH_DOCUMENT_CHARS] + TRUNCATION_SUFFIX
    return document


def chunks_cache_path(library_name: str) -> Path:
    return CHUNKS_DIR / f"{library_name}.jsonl"


def write_chunks_cache(library: LibraryConfig, chunks: list[CodeChunk]) -> Path:
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    path = chunks_cache_path(library.name)
    with path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk_to_dict(chunk)) + "\n")
    return path


def read_chunks_cache(library_name: str) -> list[CodeChunk]:
    path = chunks_cache_path(library_name)
    if not path.exists():
        return []
    chunks: list[CodeChunk] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        chunks.append(CodeChunk(**raw))
    return chunks


def delete_chunks_cache(library_name: str) -> bool:
    path = chunks_cache_path(library_name)
    if not path.exists():
        return False
    path.unlink()
    return True


@dataclass
class LibraryConfig:
    name: str
    repo: str
    ref: str
    language: str
    include: list[str]
    exclude: list[str]


@dataclass
class CodeChunk:
    library: str
    symbol: str
    kind: str
    module: str
    file_path: str
    source: str
    docstring: str
    imports: list[str]
    bases: list[str]
    is_public: bool
    parent_class: str | None = None
    start_line: int = 0

    @property
    def chunk_id(self) -> str:
        parts = [self.library, self.module]
        if self.parent_class:
            parts.extend([self.parent_class, self.kind])
        parts.append(self.symbol)
        if self.start_line:
            parts.append(f"L{self.start_line}")
        return "::".join(parts)

    def to_search_document(self) -> str:
        lines = [
            f"Library: {self.library}",
            f"Symbol: {self.symbol}",
            f"Kind: {self.kind}",
            f"Module: {self.module}",
            f"File: {self.file_path}",
            f"Public: {self.is_public}",
        ]
        if self.parent_class:
            lines.append(f"Parent class: {self.parent_class}")
        if self.bases:
            lines.append(f"Bases: {', '.join(self.bases)}")
        if self.imports:
            lines.append(f"Imports: {', '.join(self.imports)}")
        if self.docstring:
            lines.append(f"Docstring: {self.docstring}")
        lines.append("Code:")
        lines.append(self.source)
        return truncate_search_document("\n".join(lines))

    def to_metadata(self) -> dict[str, Any]:
        return {
            "library": self.library,
            "symbol": self.symbol,
            "kind": self.kind,
            "module": self.module,
            "file_path": self.file_path,
            "is_public": self.is_public,
            "parent_class": self.parent_class or "",
            "docstring": self.docstring[:500],
        }


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def load_libraries_config() -> list[LibraryConfig]:
    with resolve_config_path().open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    entries = raw.get("libraries") or []
    libraries = []
    for entry in entries:
        libraries.append(
            LibraryConfig(
                name=entry["name"],
                repo=entry["repo"],
                ref=entry["ref"],
                language=entry.get("language", "python"),
                include=list(entry.get("include", ["**/*.py"])),
                exclude=list(entry.get("exclude", [])),
            )
        )
    return libraries


def get_library_config(name: str) -> LibraryConfig:
    for library in load_libraries_config():
        if library.name == name:
            return library
    known = ", ".join(lib.name for lib in load_libraries_config()) or "(none)"
    raise SystemExit(f"Unknown library '{name}'. Known libraries: {known}")


def repo_dir_for(library: LibraryConfig) -> Path:
    return REPOS_DIR / library.name


def path_matches_patterns(path: Path, patterns: list[str]) -> bool:
    relative = path.as_posix()
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def iter_library_files(library: LibraryConfig) -> list[Path]:
    root = repo_dir_for(library)
    if not root.exists():
        raise SystemExit(
            f"Repository for '{library.name}' not found at {root}. "
            f"Run: python scripts/crawl.py --library {library.name}"
        )

    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if library.exclude and path_matches_patterns(relative, library.exclude):
            continue
        if library.include and not path_matches_patterns(relative, library.include):
            continue
        files.append(path)
    return files


def write_manifest(library: LibraryConfig, commit: str, chunk_count: int) -> Path:
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "library": library.name,
        "ref": library.ref,
        "commit": commit,
        "chunk_count": chunk_count,
        "index_backend": "cursor-codebase",
        "source_root": (REPOS_DIR / library.name).relative_to(PROJECT_ROOT).as_posix(),
        "indexed_at": datetime.now(timezone.utc).isoformat(),
    }
    path = MANIFESTS_DIR / f"{library.name}.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def read_manifest(library_name: str) -> dict[str, Any] | None:
    path = MANIFESTS_DIR / f"{library_name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def symbols_manifest_path(library_name: str) -> Path:
    return MANIFESTS_DIR / f"{library_name}.symbols.json"


def write_symbols_manifest(library: LibraryConfig, chunks: list[CodeChunk]) -> Path:
    """Write a CI-friendly symbol list derived from indexed chunks."""
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    symbols = sorted({chunk.symbol for chunk in chunks if chunk.is_public})
    modules = sorted({chunk.module for chunk in chunks})
    payload = {
        "library": library.name,
        "ref": library.ref,
        "symbols": symbols,
        "modules": modules,
        "symbol_count": len(symbols),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    path = symbols_manifest_path(library.name)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def read_symbols_manifest(library_name: str) -> dict[str, Any] | None:
    path = symbols_manifest_path(library_name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def chunk_to_dict(chunk: CodeChunk) -> dict[str, Any]:
    return asdict(chunk)
