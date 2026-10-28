"""
Divide pytest-benchmark results by the calibration benchmark.

Usage:

    pytest tests/bench.py --benchmark-json=output.json
    python .github/scripts/calibrate_benchmarks.py output.json [--github-json=calibrated.json]

Without ``--github-json``, only a table is printed. With it, the calibrated
results are also written in the ``customSmallerIsBetter`` format of
https://github.com/benchmark-action/github-action-benchmark
"""  # noqa: INP001

import argparse
import json
import sys
from pathlib import Path
from typing import Any

CALIBRATION = "test_calibration"
PREFIX = "test_"


def describe_machine(machine_info: dict[str, Any]) -> str:
    """Summarize the parts of the machine which influence the results."""
    cpu = machine_info.get("cpu", {})
    return (
        f"{cpu.get('brand_raw', machine_info.get('processor', 'unknown CPU'))}"
        f" ({cpu.get('count', '?')} cores), "
        f"{machine_info['python_implementation']} {machine_info['python_version']}"
    )


def calibrate(results: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the calibrated benchmarks in the format of github-action-benchmark."""
    benchmarks = {bench["name"]: bench["stats"] for bench in results["benchmarks"]}
    if CALIBRATION not in benchmarks:
        sys.exit(f"Benchmark {CALIBRATION} is missing, it is needed to calibrate the others.")
    reference = benchmarks.pop(CALIBRATION)["median"]
    machine = describe_machine(results["machine_info"])
    return [
        {
            "name": name.removeprefix(PREFIX),
            "unit": "x calibration",
            "value": round(stats["median"] / reference, 4),
            "range": f"IQR: {stats['iqr'] / reference:.4f}",
            "extra": (
                f"median: {stats['median'] * 1000:.1f} ms\n"
                f"rounds: {stats['rounds']}\n"
                f"calibration: {reference * 1000:.1f} ms\n"
                f"machine: {machine}"
            ),
        }
        for name, stats in benchmarks.items()
    ]


def main() -> None:
    """Print the calibrated results and optionally store them."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results", type=Path, help="JSON file written by pytest --benchmark-json")
    parser.add_argument("--github-json", type=Path, help="Write the calibrated results to this file")
    args = parser.parse_args()

    results = json.loads(args.results.read_text())
    calibrated = calibrate(results)

    sys.stdout.write(f"Machine: {describe_machine(results['machine_info'])}\n\n")
    sys.stdout.write(f"{'Benchmark':40} {'Median [ms]':>12} {'Calibrated':>11}\n")
    for bench, stats in zip(calibrated, (b["stats"] for b in results["benchmarks"] if b["name"] != CALIBRATION)):
        sys.stdout.write(f"{bench['name']:40} {stats['median'] * 1000:12.1f} {bench['value']:11.3f}\n")

    if args.github_json:
        args.github_json.write_text(json.dumps(calibrated, indent=2))


if __name__ == "__main__":
    main()
