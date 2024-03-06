# The Deprecation Process

pypdf strives to be an excellent library for its current users and for new
ones. We are careful with introducing potentially breaking changes, but we
will do them if they provide value for the community on the long run.

We hope and think that deprecations will not happen frequently. If they do,
users can rely on the following procedure.

## Semantic Versioning

pypdf uses [semantic versioning](https://semver.org/). If you want to avoid
breaking changes, please use dependency pinning (also known as version pinning).
In Python, this is done by specifying the exact version you want to use in a
`requirements.txt` file. A tool that can support you is `pip-compile` from
[`pip-tools`](https://pypi.org/project/pip-tools/).

If you are using [Poetry](https://pypi.org/project/poetry/) it is done with the
`poetry.lock` file.

## How pypdf deprecates features

Assume the current version of pypdf is `x.y.z`. After a discussion (e.g. via
GitHub issues) we decided to remove a class / function / method. This is how
we do it:

1. `x.y.(z+1)`: Add a DeprecationWarning. If there is a replacement,
   the replacement is also introduced and the warning informs about the change
   and when it will happen.
   The docs let users know about the deprecation and when it will happen and the new function.
   The CHANGELOG informs about it.
2. `(x+1).0.0`: Remove / change the code in the breaking way by replacing
   DeprecationWarnings by DeprecationErrors.
   We do this to help people who didn't look at the warnings before.
   The CHANGELOG informs about it.
3. `(x+2).0.0`: The DeprecationErrors are removed.

This means the users have 3 warnings in the CHANGELOG, a DeprecationWarning
until the next major release and a DeprecationError until the major release
after that.

Please note that adding warnings can be a breaking change for some users; most
likely just in the CI.
This means it needs to be properly documented.
