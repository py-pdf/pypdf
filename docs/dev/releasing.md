# Releasing

A `pypdf` release contains the following artifacts:

* A new [release on PyPI](https://pypi.org/project/pypdf/)
* A [release commit](https://github.com/py-pdf/pypdf/commit/91391b18bb8ec9e6e561e2795d988e8634a01a50)
    * Containing a changelog update
    * A new [git tag](https://github.com/py-pdf/pypdf/tags)
        * A [Github release](https://github.com/py-pdf/pypdf/releases/tag/3.15.0)

## Who does it?

`pypdf` should typically only be released by one of the core maintainers / the
core maintainer. At the moment, this is either Martin Thoma or pubpub-zz and stefan6419846.

Any owner of the py-pdf organization also has the technical permissions to
release.

## How is it done?

### With direct push permissions

This is the typical way for the core maintainer/benevolent dictator.

The release contains the following steps:

1. Update the CHANGELOG.md and the _version.py via `python make_release.py`.
   This also prepares the release commit message.
2. Create a release commit: `git commit -eF RELEASE_COMMIT_MSG.md`.
3. Push commit: `git push`.
4. CI now builds a source and a wheels package which it pushes to PyPI. It also
   creates the corresponding tag and a GitHub release.

![](../_static/releasing.drawio.png)

### Using a Pull Request

This is the typical way for collaborators which do not have direct push permissions for
the `main` branch.

The release contains the following steps:

1. Update the CHANGELOG.md and the _version.py via `python make_release.py`.
   This also prepares the release commit message.
2. Push the changes to a dedicated branch.
3. Open a pull request starting with `REL: `, followed by the new version number.
4. Wait for the approval of another eligible maintainer.
5. Merge the pull request with the name being the PR title and the body being
   the content of `RELEASE_COMMIT_MSG.md`.
7. CI now builds a source and a wheels package which it pushes to PyPI. It also
   creates the corresponding tag and a GitHub release.

### The Release Tag

* Use the release version as the tag name. No need for a leading "v".
* Use the changelog entry as the body.


## When are releases done?

There is no need to wait for anything. If the CI is green (all tests succeeded),
we can release.

I (Martin Thoma) typically only release once a week, because it costs a little
bit of time and I don't want to spam users with too many releases.
