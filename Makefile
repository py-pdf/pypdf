maint:
	pre-commit autoupdate
	pip-compile -U requirements/ci.in
	pip-compile -U requirements/dev.in
	pip-compile -U requirements/docs.in

changelog:
	python make_changelog.py

upload:
	make clean
	python setup.py sdist bdist_wheel && twine upload -s dist/*

clean:
	python setup.py clean --all
	pyclean .
	rm -rf Tests/__pycache__ PyPDF2/__pycache__ Image9.png htmlcov docs/_build dist dont_commit_merged.pdf dont_commit_writer.pdf PyPDF2.egg-info PyPDF2_pdfLocation.txt .pytest_cache .mypy_cache .benchmarks

test:
	pytest Tests --cov --cov-report term-missing -vv --cov-report html --durations=3 --timeout=30

mutation-test:
	mutmut run

mutmut-results:
	mutmut junitxml --suspicious-policy=ignore --untested-policy=ignore > mutmut-results.xml
	junit2html mutmut-results.xml mutmut-results.html

benchmark:
	pytest Tests/bench.py
