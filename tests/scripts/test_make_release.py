"""Test the `make_release.py` script."""
import sys
from pathlib import Path
from unittest import mock

import pytest

DATA_PATH = Path(__file__).parent.resolve() / "data"

# line starting with \ and ending with " have been observed on windows
GIT_LOG__VERSION_4_0_1 = """
b7bfd0d7eddfd0865a94cc9e7027df6596242cf7:::BUG: Use NumberObject for /Border elements of annotations (#2451):::rsinger417
8cacb0fc8fee9920b0515d1289e6ee8191eb3f21:::DOC: Document easier way to update metadata (#2454):::Stefan
3fb63f7e3839ce39ac98978c996f3086ba230a20:::TST: Avoid catching not emitted warnings (#2429):::Stefan
\\61b73d49778e8f0fb172d5323e67677c9974e420:::DOC: Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426):::CWKSC"
f851a532a5ec23b572d86bd7185b327a3fac6b58:::DEV: Bump codecov/codecov-action from 3 to 4 (#2430):::dependabot[bot]""".encode()  # noqa: E501

COMMITS__VERSION_4_0_1 = DATA_PATH.joinpath("commits__version_4_0_1.json")
VERSION_3_9_PLUS = sys.version_info[:2] >= (3, 9)


@pytest.mark.skipif(not VERSION_3_9_PLUS, reason="Function uses method removeprefix added in Python 3.9")
@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ("", ""),
        ("# CHANGELOG", ""),
        ("# CHANGELOG ", ""),
        ("# CHANGELOG  ", ""),
        ("## CHANGELOG", "## CHANGELOG"),
        ("CHANGELOG", "CHANGELOG"),
        ("# CHANGELOG #", "#"),
    ]
)
def test_strip_header(data, expected):
    """Removal of the 'CHANGELOG' header."""
    make_release = pytest.importorskip("make_release")
    assert make_release.strip_header(data) == expected


def test_get_git_commits_since_tag():
    make_release = pytest.importorskip("make_release")

    with open(COMMITS__VERSION_4_0_1, mode="rb") as commits, mock.patch(
        "urllib.request.urlopen", side_effect=lambda _: commits
    ), mock.patch("subprocess.check_output", return_value=GIT_LOG__VERSION_4_0_1):
        commits = make_release.get_git_commits_since_tag("4.0.1")
    assert commits == [
        make_release.Change(
            commit_hash="b7bfd0d7eddfd0865a94cc9e7027df6596242cf7",
            prefix="BUG",
            message="Use NumberObject for /Border elements of annotations (#2451)",
            author="rsinger417",
            author_login="rsinger417",
        ),
        make_release.Change(
            commit_hash="8cacb0fc8fee9920b0515d1289e6ee8191eb3f21",
            prefix="DOC",
            message="Document easier way to update metadata (#2454)",
            author="Stefan",
            author_login="stefan6419846",
        ),
        make_release.Change(
            commit_hash="3fb63f7e3839ce39ac98978c996f3086ba230a20",
            prefix="TST",
            message="Avoid catching not emitted warnings (#2429)",
            author="Stefan",
            author_login="stefan6419846",
        ),
        make_release.Change(
            commit_hash="61b73d49778e8f0fb172d5323e67677c9974e420",
            prefix="DOC",
            message="Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426)",
            author="CWKSC",
            author_login="CWKSC",
        ),
        make_release.Change(
            commit_hash="f851a532a5ec23b572d86bd7185b327a3fac6b58",
            prefix="DEV",
            message="Bump codecov/codecov-action from 3 to 4 (#2430)",
            author="dependabot[bot]",
            author_login="dependabot[bot]",
        ),
    ]


def test_get_formatted_changes():
    make_release = pytest.importorskip("make_release")

    with open(COMMITS__VERSION_4_0_1, mode="rb") as commits, mock.patch(
        "urllib.request.urlopen", side_effect=lambda _: commits
    ), mock.patch("subprocess.check_output", return_value=GIT_LOG__VERSION_4_0_1):
        output, output_with_user = make_release.get_formatted_changes("4.0.1")

    assert (
        output
        == """
### Bug Fixes (BUG)
- Use NumberObject for /Border elements of annotations (#2451)

### Documentation (DOC)
- Document easier way to update metadata (#2454)
- Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426)

### Developer Experience (DEV)
- Bump codecov/codecov-action from 3 to 4 (#2430)

### Testing (TST)
- Avoid catching not emitted warnings (#2429)
"""
    )
    assert (
        output_with_user
        == """
### Bug Fixes (BUG)
- Use NumberObject for /Border elements of annotations (#2451) by @rsinger417

### Documentation (DOC)
- Document easier way to update metadata (#2454) by @stefan6419846
- Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426) by @CWKSC

### Developer Experience (DEV)
- Bump codecov/codecov-action from 3 to 4 (#2430) by @dependabot[bot]

### Testing (TST)
- Avoid catching not emitted warnings (#2429) by @stefan6419846
"""
    )


def test_get_formatted_changes__other():
    make_release = pytest.importorskip("make_release")

    changes = [
        make_release.Change(
            commit_hash="f20c36eabd59ea661f30c5da35af7c9e435c7de9",
            prefix="",
            message="Improve lossless compression example (#2488)",
            author="j-t-1",
            author_login="j-t-1",
        ),
        make_release.Change(
            commit_hash="afbee382f8fd2b39588db6470b9b2b2c82905318",
            prefix="ENH",
            message="Add reattach_fields function (#2480)",
            author="pubpub-zz",
            author_login="pubpub-zz",
        ),
        make_release.Change(
            commit_hash="cd705f959064d8125397ddf4f7bdd2ea296f889f",
            prefix="FIX",
            message="Broken test due to expired test file URL (#2468)",
            author="pubpub-zz",
            author_login="pubpub-zz",
        ),
    ]
    with mock.patch.object(
        make_release, "get_git_commits_since_tag", return_value=changes
    ):
        output, output_with_user = make_release.get_formatted_changes("dummy")

    assert (
        output
        == """
### New Features (ENH)
- Add reattach_fields function (#2480)

### Other
- : Improve lossless compression example (#2488)
- FIX: Broken test due to expired test file URL (#2468)
"""
    )

    assert (
        output_with_user
        == """
### New Features (ENH)
- Add reattach_fields function (#2480) by @pubpub-zz

### Other
- : Improve lossless compression example (#2488) by @j-t-1
- FIX: Broken test due to expired test file URL (#2468) by @pubpub-zz
"""
    )
