#!/bin/bash -e
pytest -x
mypy pypdf --show-error-codes --disallow-untyped-defs --disallow-incomplete-defs --ignore-missing-imports
