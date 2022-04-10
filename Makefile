maint:
	pre-commit autoupdate
	pip-compile -U requirements/ci.in
	pip-compile -U requirements/dev.in
	pip-compile -U requirements/docs.in

upload:
	make clean
	python setup.py sdist bdist_wheel && twine upload -s dist/*

clean:
	python setup.py clean --all
	pyclean .
	rm -rf Tests/__pycache__ PyPDF2/__pycache__ Image9.png htmlcov docs/_build dist dont_commit_merged.pdf dont_commit_writer.pdf PyPDF2.egg-info PyPDF2_pdfLocation.txt

test:
	pytest Tests/tests.py Tests --cov --cov-report term-missing -vv --cov-report html
