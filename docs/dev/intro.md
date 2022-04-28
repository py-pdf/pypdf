# Developer Intro

PyPDF2 is a library and hence its users are developers. This document is not for
the users, but for people who want to work on PyPDF2 itself.

## Installing Requirements

```
pip install -r requirements/dev.txt
```

## Running Tests

```
pytest .
```

We have the following pytest markers defined:

* `no_py27`: Flag for tests that fail under Python 2.7 only
* `external`: Tests which use files from [the `sample-files` git submodule](https://github.com/py-pdf/sample-files)

You can locally choose not to run those via `pytest -m "not external"`.

## The sample-files git submodule
The reason for having the submodule `sample-files` is that we want to keep
the size of the PyPDF2 repository small while we also want to have an extensive
test suite. Those two goals contradict each other.

The `Resources` folder should contain a select set of core examples that cover
most cases we typically want to test for. The `sample-files` might cover a lot
more edge cases, the behavior we get when file sizes get bigger, different
PDF producers.

## Tools: git and pre-commit

Git is a command line application for version control. If you don't know it,
you can [play ohmygit](https://ohmygit.org/) to learn it.

Github is the service where the PyPDF2 project is hosted. While git is free and
open source, Github is a paid service by Microsoft - but for free in lot of
cases.

[pre-commit](https://pypi.org/project/pre-commit/) is a command line application
that uses git hooks to automatically execute code. This allows you to avoid
style issues and other code quality issues. After you entered `pre-commit install`
once in your local copy of PyPDF2, it will automatically be executed when
you `git commit`.

## Commit Messages

Having a clean commit message helps people to quickly understand what the commit
was about, witout actually looking at the changes. The first line of the
commit message is used to [auto-generate the CHANGELOG](https://github.com/py-pdf/PyPDF2/blob/main/make_changelog.py). For this reason, the format should be:

```
PREFIX: DESCRIPTION

BODY
```

The `PREFIX` can be:

* `BUG`: A bug was fixed. Likely there is one or multiple issues. Then write in
   the `BODY`: `Closes #123` where 123 is the issue number on Github.
   It would be absolutely amazing if you could write a regression test in those
   cases. That is a test that would fail without the fix.
* `ENH`: A new feature! Describe in the body what it can be used for.
* `DEP`: A deprecation - either marking something as "this is going to be removed"
   or actually removing it.
* `ROB`: A robustness change. Dealing better with broken PDF files.
* `DOC`: A documentation change.
* `TST`: Adding / adjusting tests.
* `DEV`: Developer experience improvements - e.g. pre-commit or setting up CI
* `MAINT`: Quite a lot of different stuff. Performance improvements are for sure
           the most interesting changes in here. Refactorings as well.
* `STY`: A style change. Something that makes PyPDF2 code more consistent.
         Typically a small change.

## Benchmarks

We need to keep an eye on performance and thus we have a few benchmarks.

See [py-pdf.github.io/PyPDF2/dev/bench](https://py-pdf.github.io/PyPDF2/dev/bench/)
