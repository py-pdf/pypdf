"""Test the `make_release.py` script."""
from pathlib import Path
from unittest import mock

import pytest

DATA_PATH = Path(__file__).parent.resolve() / "data"


GIT_LOG__VERSION_4_0_1 = """
b7bfd0d7eddfd0865a94cc9e7027df6596242cf7:::BUG: Use NumberObject for /Border elements of annotations (#2451):::rsinger417
8cacb0fc8fee9920b0515d1289e6ee8191eb3f21:::DOC: Document easier way to update metadata (#2454):::Stefan
3fb63f7e3839ce39ac98978c996f3086ba230a20:::TST: Avoid catching not emitted warnings (#2429):::Stefan
61b73d49778e8f0fb172d5323e67677c9974e420:::DOC: Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426):::CWKSC
f851a532a5ec23b572d86bd7185b327a3fac6b58:::DEV: Bump codecov/codecov-action from 3 to 4 (#2430):::dependabot[bot]""".encode()  # noqa: E501

COMMITS__VERSION_4_0_1 = DATA_PATH.joinpath("commits__version_4_0_1.json")


def test_get_git_commits_since_tag():
    make_release = pytest.importorskip("make_release")

    with open(COMMITS__VERSION_4_0_1, mode="rb") as commits, mock.patch(
        "urllib.request.urlopen", side_effect=lambda n: commits
    ), mock.patch("subprocess.check_output", return_value=GIT_LOG__VERSION_4_0_1):
        commits = make_release.get_git_commits_since_tag("4.0.1")
    assert commits == [
        make_release.Change(
            commit_hash="b7bfd0d7eddfd0865a94cc9e7027df6596242cf7",
            prefix="BUG",
            message=" Use NumberObject for /Border elements of annotations (#2451)",
            author="rsinger417",
            author_login="rsinger417",
        ),
        make_release.Change(
            commit_hash="8cacb0fc8fee9920b0515d1289e6ee8191eb3f21",
            prefix="DOC",
            message=" Document easier way to update metadata (#2454)",
            author="Stefan",
            author_login="stefan6419846",
        ),
        make_release.Change(
            commit_hash="3fb63f7e3839ce39ac98978c996f3086ba230a20",
            prefix="TST",
            message=" Avoid catching not emitted warnings (#2429)",
            author="Stefan",
            author_login="stefan6419846",
        ),
        make_release.Change(
            commit_hash="61b73d49778e8f0fb172d5323e67677c9974e420",
            prefix="DOC",
            message=" Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426)",
            author="CWKSC",
            author_login="CWKSC",
        ),
        make_release.Change(
            commit_hash="f851a532a5ec23b572d86bd7185b327a3fac6b58",
            prefix="DEV",
            message=" Bump codecov/codecov-action from 3 to 4 (#2430)",
            author="dependabot[bot]",
            author_login="dependabot[bot]",
        ),
    ]


def test_get_formatted_changes():
    make_release = pytest.importorskip("make_release")

    with open(COMMITS__VERSION_4_0_1, mode="rb") as commits, mock.patch(
        "urllib.request.urlopen", side_effect=lambda n: commits
    ), mock.patch("subprocess.check_output", return_value=GIT_LOG__VERSION_4_0_1):
        output, output_with_user = make_release.get_formatted_changes("4.0.1")

    assert (
        output
        == """
### Bug Fixes (BUG)
-  Use NumberObject for /Border elements of annotations (#2451)

### Documentation (DOC)
-  Document easier way to update metadata (#2454)
-  Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426)

### Developer Experience (DEV)
-  Bump codecov/codecov-action from 3 to 4 (#2430)

### Testing (TST)
-  Avoid catching not emitted warnings (#2429)
"""
    )
    assert (
        output_with_user
        == """
### Bug Fixes (BUG)
-  Use NumberObject for /Border elements of annotations (#2451) by @rsinger417

### Documentation (DOC)
-  Document easier way to update metadata (#2454) by @stefan6419846
-  Typo `Polyline` → `PolyLine` in adding-pdf-annotations.md (#2426) by @CWKSC

### Developer Experience (DEV)
-  Bump codecov/codecov-action from 3 to 4 (#2430) by @dependabot[bot]

### Testing (TST)
-  Avoid catching not emitted warnings (#2429) by @stefan6419846
"""
    )
