#!/usr/bin/env python
"""
Create a minimal PDF with Brotli compression for testing purposes.

This script generates a simple PDF file that uses Brotli compression
for the content stream, allowing for testing of the BrotliDecode filter
in pypdf.
"""

import brotli
import os

# Simple PDF structure with Brotli-compressed content stream
# The content stream will contain a simple "Hello, Brotli!" text
content_stream = b"BT /F1 24 Tf 100 700 Td (Hello, Brotli!) Tj ET"
compressed_content = brotli.compress(content_stream, quality=5)

# PDF structure
pdf = [
    b"%PDF-1.7\n",
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
    b"4 0 obj\n<< /Length " + str(len(compressed_content)).encode() + b" /Filter /BrotliDecode >>\nstream\n" + compressed_content + b"\nendstream\nendobj\n",
    b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000115 00000 n \n0000000234 00000 n \n" + 
    (b"0000000" + str(334 + len(compressed_content)).encode() + b" 00000 n \n"),
    b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n" + str(400 + len(compressed_content)).encode() + b"\n%%EOF"
]

# Write PDF to file
# Define paths relative to the script's location (resources/)
script_dir = os.path.dirname(__file__)
output_dir = os.path.join(script_dir, "brotli-test")
output_path = os.path.join(output_dir, "brotli-compressed.pdf")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)
with open(output_path, "wb") as f:
    for part in pdf:
        f.write(part)

print(f"Created test PDF with Brotli compression at: {output_path}")
