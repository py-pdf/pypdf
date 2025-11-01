# Documentation

This documentation is build with [Sphinx](https://www.sphinx-doc.org/) and
hosted by [Read the Docs](https://about.readthedocs.com/)

## Testing code snippets

Almost all python code snippets in documentation tested using Sphinx's extension
[sphinx.ext.doctest](https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html).
This allows to make sure that we have no typos, missed imports and other problems in:
- code snippets marked with `testcode` directive in `*.md` files
- code snippets from python's docstrings imported via `autoclass` directive in `*.rst` files

CI pipeline is configured run Sphinx's `doctest` build automatically for each PR.
It is also possible to run it locally:

1. First you need to install docs requrements

   ```bash
   pip install -r requirements/docs.txt
   ```

2. Make sure you have `sphinx-build` command line tool avaliable in your venv.

   ```bash
   sphinx-build --version
   ```

3. Change current directory

   ```bash
   cd docs
   ```

4. Run `doctest` build. If you have issues check [Sphinx's docs](https://www.sphinx-doc.org/en/master/usage/quickstart.html#running-the-build)

   ```bash
   make doctest
   ```

5. If everything is Okay you should see in output `Doctest summary` wihout failures

## API Reference

### Method / Function Docstrings

We use Google-Style Docstrings:

```
def example(param1: int, param2: str) -> bool:
    """
    Example function with PEP 484 type annotations.

    Args:
      param1: The first parameter.
      param2: The second parameter.

    Returns:
      The return value. True for success, False otherwise.

    Raises:
      AttributeError: The ``Raises`` section is a list of all exceptions
        that are relevant to the interface.
      ValueError: If `param2` is equal to `param1`.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> print([i for i in example_generator(4)])
        [0, 1, 2, 3]
    """
```

* The order of sections is (1) Args (2) Returns (3) Raises (4) Examples
* If there is no return value, remove the 'Returns' block
* Properties should not have any sections


## Issues and PRs

An issue can be used to discuss what we want to achieve.

A PR can be used to discuss how we achieve it.

## Commit Messages

We want to have descriptive commits in the `main` branch. For this reason, every
pull request (PR) is squashed. That means no matter how many commits a PR has,
in the end only one combined commit will be in `main`.

The title of the PR will be used as the first line of that combined commit message.

The first comment within the commit will be used as the message body.

See [developer intro](intro.md#commit-messages) for more details.
