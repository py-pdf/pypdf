"""
Move the results from before the calibration out of dev/bench/data.js.

Run it in the root of a checkout of the gh-pages branch. The old suites go
unchanged into dev/bench/archive/before-calibration.js, which nothing writes
to afterwards. Running it again does nothing.
"""  # noqa: INP001

import json
import sys
from pathlib import Path

OLD_SUITES = ("CPython Benchmark", "PyPy Benchmark")
DATA = Path("dev/bench/data.js")
ARCHIVE = Path("dev/bench/archive/before-calibration.js")
DATA_PREFIX = "window.BENCHMARK_DATA = "
ARCHIVE_PREFIX = "window.BENCHMARK_ARCHIVE = "


def main() -> None:
    """Move the old suites, unless that happened already."""
    if ARCHIVE.exists():
        sys.stdout.write(f"{ARCHIVE} exists already, nothing to do.\n")
        return
    data = json.loads(DATA.read_text().removeprefix(DATA_PREFIX))
    entries = {name: data["entries"].pop(name) for name in OLD_SUITES if name in data["entries"]}
    if not entries:
        sys.stdout.write(f"{DATA} contains none of {OLD_SUITES}, nothing to do.\n")
        return
    archive = {"lastUpdate": data["lastUpdate"], "repoUrl": data["repoUrl"], "entries": entries}
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVE.write_text(ARCHIVE_PREFIX + json.dumps(archive, indent=2, ensure_ascii=False) + "\n")
    DATA.write_text(DATA_PREFIX + json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    for name, runs in entries.items():
        sys.stdout.write(f"Archived {name}: {len(runs)} runs\n")


if __name__ == "__main__":
    main()
