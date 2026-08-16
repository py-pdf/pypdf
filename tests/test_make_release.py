"""Tests for the release helper script."""

import pytest

from make_release import has_minor_changes, version_bump

ENH_CHANGES = """
### New Features (ENH)
- Add a shiny thing

### Bug Fixes (BUG)
- Fix a thing
"""

DEP_CHANGES = """
### Deprecations (DEP)
- Deprecate an old thing
"""

PATCH_CHANGES = """
### Bug Fixes (BUG)
- Fix a thing

### Code Style (STY)
- Reformat a thing
"""


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        pytest.param(ENH_CHANGES, True, id="enhancement"),
        pytest.param(DEP_CHANGES, True, id="deprecation"),
        pytest.param(PATCH_CHANGES, False, id="regular-changes"),
        pytest.param("", False, id="no-changes"),
        # The prefix only counts as a section header, not anywhere in the text.
        pytest.param("### Bug Fixes (BUG)\n- Mention ENH in a message\n", False, id="prefix-inside-message"),
    ],
)
def test_has_minor_changes(changes: str, expected: bool) -> None:
    assert has_minor_changes(changes) is expected


@pytest.mark.parametrize(
    ("tag", "changes", "expected"),
    [
        pytest.param("6.16.1", PATCH_CHANGES, "6.16.2", id="patch-bump"),
        pytest.param("6.16.1", ENH_CHANGES, "6.17.0", id="minor-bump-resets-patch"),
        pytest.param("6.15.0", DEP_CHANGES, "6.16.0", id="deprecation-bumps-minor"),
        pytest.param("6.9.9", ENH_CHANGES, "6.10.0", id="minor-rolls-over"),
        # Without the changes the old behaviour is kept.
        pytest.param("6.16.1", "", "6.16.2", id="defaults-to-patch"),
    ],
)
def test_version_bump(tag: str, changes: str, expected: str) -> None:
    assert version_bump(tag, changes) == expected
