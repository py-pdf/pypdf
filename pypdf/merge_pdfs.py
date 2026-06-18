"""Merge multiple PDF documents into a single file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._writer import PdfWriter
from .errors import PdfReadError


class MergeError(Exception):
    """Raised when PDF merge inputs or output are invalid."""


def merge_pdfs(paths: list[str | Path], output: str | Path) -> None:
    """Merge PDF files into a single document.

    Args:
        paths: Input PDF paths in merge order.
        output: Destination file path.

    Raises:
        MergeError: If inputs are invalid or a PDF cannot be read.
    """
    input_paths = [Path(path) for path in paths]
    output_path = Path(output)

    if len(input_paths) < 2:
        msg = "At least two PDF documents are required to merge."
        raise MergeError(msg)

    for path in input_paths:
        if not path.exists():
            msg = f"Input file not found: {path}"
            raise MergeError(msg)
        if not path.is_file():
            msg = f"Input path is not a file: {path}"
            raise MergeError(msg)

    writer = PdfWriter()
    temp_path = output_path.with_name(f"{output_path.name}.merge_tmp")

    try:
        for path in input_paths:
            try:
                writer.append(path)
            except (PdfReadError, OSError) as exc:
                msg = f"Cannot read PDF: {path}"
                raise MergeError(msg) from exc

        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer.write(temp_path)
        temp_path.replace(output_path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    finally:
        writer.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge two or more PDF documents into a single file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path for the merged PDF output file.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input PDF paths in merge order (at least two).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the merge-PDFs command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        merge_pdfs(args.inputs, args.output)
    except MergeError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
