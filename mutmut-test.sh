#!/bin/bash -e
pytest -x
mypy PyPDF2 --show-error-codes --disallow-untyped-defs --disallow-incomplete-defs --ignore-missing-imports
