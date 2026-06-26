#!/usr/bin/env python3
"""Launch nb-symbols MCP — workspace root, venv Python, and MCP package bootstrap."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _has_workspace_markers(path: Path) -> bool:
    return (
        (path / "scripts" / "doctor.py").is_file()
        or (path / ".newbie" / "libraries.yaml").is_file()
        or (path / "config" / "libraries.yaml").is_file()
    )


def resolve_workspace(start: Path | None = None) -> Path:
    for key in ("NB_PROJECT_ROOT", "CURSOR_PROJECT_DIR", "VSCODE_CWD"):
        override = os.environ.get(key)
        if override:
            candidate = Path(override).expanduser().resolve()
            if _has_workspace_markers(candidate):
                return candidate

    override = os.environ.get("NB_PROJECT_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    origins: list[Path] = []
    if start is not None:
        resolved = start.resolve()
        origins.append(resolved)
        origins.extend(resolved.parents)
    origins.append(Path.cwd())

    seen: set[Path] = set()
    for origin in origins:
        for path in [origin, *origin.parents]:
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if _has_workspace_markers(resolved):
                return resolved
            scaffold = resolved / "scaffold"
            if _has_workspace_markers(scaffold):
                return scaffold

    return Path.cwd().resolve()


def resolve_scripts_dir(workspace: Path) -> Path:
    candidates = [
        workspace / "scripts",
        workspace / "scaffold" / "scripts",
    ]
    launcher = Path(__file__).resolve()
    candidates.extend(
        [
            launcher.parent,
            launcher.parent / "runtime",
            launcher.parent.parent / "runtime",
        ]
    )
    for candidate in candidates:
        if (candidate / "mcp_symbols_server.py").is_file():
            return candidate
    return workspace / "scripts"


def resolve_python(workspace: Path) -> str:
    launcher_root = Path(__file__).resolve().parent.parent
    for base in (workspace / ".venv" / "bin", launcher_root / ".venv" / "bin"):
        for name in ("python3", "python"):
            candidate = base / name
            if candidate.is_file():
                return str(candidate)
    return sys.executable


def ensure_mcp(python: str) -> None:
    probe = subprocess.run(
        [python, "-c", "import mcp.server.fastmcp"],
        capture_output=True,
    )
    if probe.returncode == 0:
        return

    install = subprocess.run(
        [python, "-m", "pip", "install", "mcp>=1.2.0", "-q"],
        capture_output=True,
        text=True,
    )
    if install.returncode != 0:
        sys.stderr.write(
            "nb-symbols MCP needs the `mcp` package. Install Newbie dependencies:\n"
            "  python -m venv .venv && source .venv/bin/activate\n"
            "  pip install -r requirements.txt\n"
        )
        if install.stderr:
            sys.stderr.write(install.stderr)
        raise SystemExit(1)


def main() -> None:
    workspace = resolve_workspace(start=Path(__file__))
    os.environ["NB_PROJECT_ROOT"] = str(workspace)
    python = resolve_python(workspace)
    ensure_mcp(python)

    scripts_dir = resolve_scripts_dir(workspace)
    server = scripts_dir / "mcp_symbols_server.py"
    if not server.is_file():
        sys.stderr.write(
            f"Missing {server}. Run `/nb-init` to materialize Newbie scripts in this workspace.\n"
        )
        raise SystemExit(1)

    # Forward CLI args, and translate NB_MCP_TRANSPORT into a flag so the same
    # launcher works for desktop (stdio) and Cloud Agents (http) installs.
    argv = [python, str(server), *sys.argv[1:]]
    transport = os.environ.get("NB_MCP_TRANSPORT")
    if transport and not any(arg.startswith("--transport") for arg in sys.argv[1:]):
        argv.extend(["--transport", transport])

    os.chdir(workspace)
    os.execv(python, argv)


if __name__ == "__main__":
    main()
