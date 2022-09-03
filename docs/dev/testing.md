# Testing

PyPDF2 uses [`pytest`](https://docs.pytest.org/en/7.1.x/) for testing.

## Creating a Coverage Report

If you want to get a coverage report that considers the Python version specific
code, you can run [`tox`](https://tox.wiki/en/latest/).

As a prerequisite, we recommend using [`pyenv`](https://github.com/pyenv/pyenv)
so that you can install the different Python versions:

```
pyenv install pypy3.8-7.3.7
pyenv install 3.6.15
pyenv install 3.7.12
pyenv install 3.8.12
pyenv install 3.9.10
pyenv install 3.10.2
```

Then you can execute `tox` which will create a coverage report in HTML form
in the end. The execution takes about 30 minutes.
