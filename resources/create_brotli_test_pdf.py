#!/usr/bin/env python
"""
Create a minimal PDF with Brotli compression for testing purposes.

This script generates a simple PDF file that uses Brotli compression
for the content stream, allowing for testing of the BrotliDecode filter
in pypdf.

Note: /BrotliDecode is not a standard PDF filter. This file is specifically
for testing PDF library support for this filter (e.g., in pypdf).
Standard PDF viewers will likely not render this file correctly.
"""

import logging
from pathlib import Path

import brotli

logging.basicConfig(level=logging.INFO, format="%(name)s: %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

content_stream = b"BT /F1 24 Tf 100 700 Td (Hello, Brotli!) Tj ET"
compressed_content = brotli.compress(content_stream, quality=5)

xref_offsets = [0] * 6
current_offset = 0
pdf_parts = []

part = b"%PDF-1.7\n%\xc2\xa5\xc2\xb1\xc3\xab\xc3\xbf\n" # Binary marker
pdf_parts.append(part)
current_offset += len(part)
xref_offsets[1] = current_offset

part = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
pdf_parts.append(part)
current_offset += len(part)
xref_offsets[2] = current_offset

part = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
pdf_parts.append(part)
current_offset += len(part)
xref_offsets[3] = current_offset

part = (
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
    b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
)
pdf_parts.append(part)
current_offset += len(part)
xref_offsets[4] = current_offset

part_header = (
    f"4 0 obj\n<< /Length {len(compressed_content)} /Filter /BrotliDecode >>\nstream\n"
).encode("ascii")
part_footer = b"\nendstream\nendobj\n"
pdf_parts.append(part_header)
pdf_parts.append(compressed_content)
pdf_parts.append(part_footer)
current_offset += len(part_header) + len(compressed_content) + len(part_footer)
xref_offsets[5] = current_offset

part = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
pdf_parts.append(part)
current_offset += len(part)
xref_table_start_offset = current_offset

xref_lines = [b"xref\n0 6\n", b"0000000000 65535 f \n"]
xref_lines.extend(
    f"{xref_offsets[i]:010d} 00000 n \n".encode("ascii") for i in range(1, 6)
)
pdf_parts.extend(xref_lines)

trailer = (
    f"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{xref_table_start_offset}\n%%EOF"
).encode("ascii")
pdf_parts.append(trailer)

script_path = Path(__file__).resolve()
output_dir = script_path.parent / "brotli-test-pdfs"
output_path = output_dir / "minimal-brotli-compressed.pdf"

output_dir.mkdir(parents=True, exist_ok=True)

try:
    with open(output_path, "wb") as f:
        for part in pdf_parts:
            f.write(part)
    logger.info(f"Created test PDF with Brotli compression at: {output_path}")
except OSError:
    logger.exception("Error writing PDF file")
