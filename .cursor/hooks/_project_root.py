"""Locate the Newbie workspace root from hook script paths."""

from __future__ import annotations

from pathlib import Path


def _has_doctor(path: Path) -> bool:
    return (path / "scripts" / "doctor.py").is_file()


def _has_newbie_config(path: Path) -> bool:
    return (path / ".newbie" / "libraries.yaml").is_file() or (
        path / "config" / "libraries.yaml"
    ).is_file()


def find_project_root(*, start: Path | None = None) -> Path:
    """Return the Newbie workspace root (directory with scripts/doctor.py or .newbie config)."""
    candidates: list[Path] = [Path.cwd()]
    if start is not None:
        candidates.extend(start.resolve().parents)
    seen: set[Path] = set()
    for origin in candidates:
        for path in [origin, *origin.parents]:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if _has_doctor(resolved):
                return resolved
            scaffold = resolved / "scaffold"
            if _has_doctor(scaffold):
                return scaffold
            if _has_newbie_config(resolved):
                return resolved
    return Path.cwd()


def find_scripts_dir(*, start: Path | None = None) -> Path:
    """Return the directory containing Newbie indexing scripts."""
    root = find_project_root(start=start)
    direct = root / "scripts"
    if (direct / "doctor.py").is_file():
        return direct
    monorepo = root.parent / "scaffold" / "scripts"
    if root.name != "scaffold" and (monorepo / "doctor.py").is_file():
        return monorepo
    nested = root / "scaffold" / "scripts"
    if (nested / "doctor.py").is_file():
        return nested
    bundled = Path(__file__).resolve().parent / "runtime"
    if (bundled / "doctor.py").is_file():
        return bundled
    plugin_runtime = Path(__file__).resolve().parents[2] / "runtime" / "scripts"
    if (plugin_runtime / "doctor.py").is_file():
        return plugin_runtime
    return direct
