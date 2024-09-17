maint:
	pyenv local 3.7.15
	pre-commit autoupdate
	pip-compile -U requirements/ci.in
	pip-compile -U requirements/dev.in
	pip-compile -U requirements/docs.in

release:
	python make_release.py
	git commit -eF RELEASE_COMMIT_MSG.md

upload:
	make clean
	flit publish

clean:
	pyclean .
	rm -rf tests/__pycache__ pypdf/__pycache__ Image9.png htmlcov docs/_build dist dont_commit_merged.pdf dont_commit_writer.pdf pypdf.egg-info pypdf_pdfLocation.txt .pytest_cache .mypy_cache .benchmarks

test:
	pytest tests --cov --cov-report term-missing -vv --cov-report html --durations=3 --timeout=60 pypdf

testtype:
	pytest tests --cov --cov-report term-missing -vv --cov-report html --durations=3 --timeout=30 --typeguard-packages=pypdf

mutation-test:
	mutmut run

mutation-results:
	mutmut junitxml --suspicious-policy=ignore --untested-policy=ignore > mutmut-results.xml
	junit2html mutmut-results.xml mutmut-results.html

benchmark:
	pytest tests/bench.py

mypy:
	mypy pypdf --ignore-missing-imports --check-untyped --strict

pylint:
	pylint pypdf
