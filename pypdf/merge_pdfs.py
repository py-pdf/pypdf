"""Merge two PDF files into one."""

import argparse
from pathlib import Path

from pypdf import PdfWriter


def merge_pdfs(first: Path, second: Path, output: Path) -> None:
    """Merge two PDF files and write the result to output."""
    writer = PdfWriter()
    writer.append(first)
    writer.append(second)
    writer.write(output)


def main() -> None:
    """Parse CLI arguments and merge two PDF files."""
    parser = argparse.ArgumentParser(description="Merge two PDF files into one.")
    parser.add_argument("first", type=Path, help="First PDF file")
    parser.add_argument("second", type=Path, help="Second PDF file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output PDF file path",
    )
    args = parser.parse_args()

    for path in (args.first, args.second):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    merge_pdfs(args.first, args.second, args.output)


if __name__ == "__main__":
    main()
