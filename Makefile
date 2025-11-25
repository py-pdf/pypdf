maint:
	pre-commit autoupdate
	pip-compile -U requirements/ci.in
	pip-compile -U requirements/dev.in
	pip-compile -U requirements/docs.in

release:
	python make_release.py
	git commit -eF RELEASE_COMMIT_MSG.md

clean:
	python -m pip install pyclean
	pyclean .
	rm -rf tests/__pycache__ pypdf/__pycache__ htmlcov docs/_build dist pypdf.egg-info .pytest_cache .mypy_cache .benchmarks

test:
	pytest tests --cov --cov-report term-missing -vv --cov-report html --durations=3 --timeout=60 pypdf

testtype:
	pytest tests --cov --cov-report term-missing -vv --cov-report html --durations=3 --timeout=30 --typeguard-packages=pypdf

benchmark:
	pytest tests/bench.py

mypy:
	mypy pypdf --ignore-missing-imports --check-untyped --strict

ruff:
	ruff check pypdf tests make_release.py
