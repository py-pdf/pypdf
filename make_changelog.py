"""Internal tool to update the changelog."""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class Change:
    """Capture the data of a git commit."""

    commit_hash: str
    prefix: str
    message: str


def main(changelog_path: str) -> None:
    """
    Create a changelog.

    Args:
        changelog_path: The location of the CHANGELOG file
    """
    changelog = get_changelog(changelog_path)
    git_tag = get_most_recent_git_tag()
    changes = get_formatted_changes(git_tag)
    print("-" * 80)
    print(changes)

    new_version = version_bump(git_tag)
    today = datetime.now()
    header = f"Version {new_version}, {today:%Y-%m-%d}\n"
    header = header + "-" * (len(header) - 1) + "\n"
    url = f"https://github.com/py-pdf/pypdf/compare/{git_tag}...{new_version}"
    trailer = f"\n[Full Changelog]({url})\n\n"
    new_entry = header + changes + trailer
    print(new_entry)

    # TODO: Make idempotent - multiple calls to this script
    # should not change the changelog
    new_changelog = new_entry + changelog
    write_changelog(new_changelog, changelog_path)


def version_bump(git_tag: str) -> str:
    """
    Increase the patch version of the git tag by one.

    Args:
        git_tag: Old version tag

    Returns:
        The new version where the patch version is bumped.
    """
    # just assume a patch version change
    major, minor, patch = git_tag.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def get_changelog(changelog_path: str) -> str:
    """
    Read the changelog.

    Args:
        changelog_path: Path to the CHANGELOG file

    Returns:
        Data of the CHANGELOG
    """
    with open(changelog_path) as fh:
        changelog = fh.read()
    return changelog


def write_changelog(new_changelog: str, changelog_path: str) -> None:
    """
    Write the changelog.

    Args:
        new_changelog: Contents of the new CHANGELOG
        changelog_path: Path where the CHANGELOG file is
    """
    with open(changelog_path, "w") as fh:
        fh.write(new_changelog)


def get_formatted_changes(git_tag: str) -> str:
    """
    Format the changes done since the last tag.

    Args:
        git_tag: the reference tag

    Returns:
        Changes done since git_tag
    """
    commits = get_git_commits_since_tag(git_tag)

    # Group by prefix
    grouped = {}
    for commit in commits:
        if commit.prefix not in grouped:
            grouped[commit.prefix] = []
        grouped[commit.prefix].append({"msg": commit.message})

    # Order prefixes
    order = ["DEP", "ENH", "PI", "BUG", "ROB", "DOC", "DEV", "MAINT", "TST", "STY"]
    abbrev2long = {
        "DEP": "Deprecations",
        "ENH": "New Features",
        "BUG": "Bug Fixes",
        "ROB": "Robustness",
        "DOC": "Documentation",
        "DEV": "Developer Experience",
        "MAINT": "Maintenance",
        "TST": "Testing",
        "STY": "Code Style",
        "PI": "Performance Improvements",
    }

    # Create output
    output = ""
    for prefix in order:
        if prefix not in grouped:
            continue
        output += f"\n{abbrev2long[prefix]} ({prefix}):\n"  # header
        for commit in grouped[prefix]:
            output += f"- {commit['msg']}\n"
        del grouped[prefix]

    if grouped:
        print("@" * 80)
        output += "\nYou forgot something!:\n"
        for prefix in grouped:
            output += f"- {prefix}: {grouped[prefix]}\n"
        print("@" * 80)

    return output


def get_most_recent_git_tag() -> str:
    """
    Get the git tag most recently created.

    Returns:
        Most recently created git tag.
    """
    git_tag = str(
        subprocess.check_output(
            ["git", "describe", "--abbrev=0"], stderr=subprocess.STDOUT
        )
    ).strip("'b\\n")
    return git_tag


def get_git_commits_since_tag(git_tag: str) -> List[Change]:
    """
    Get all commits since the last tag.

    Args:
        git_tag: Reference tag from which the changes to the current commit are
            fetched.

    Returns:
        List of all changes since git_tag.
    """
    commits = str(
        subprocess.check_output(
            [
                "git",
                "--no-pager",
                "log",
                f"{git_tag}..HEAD",
                '--pretty=format:"%h%x09%s"',
            ],
            stderr=subprocess.STDOUT,
        )
    ).strip("'b\\n")
    return [parse_commit_line(line) for line in commits.split("\\n")]


def parse_commit_line(line: str) -> Change:
    """
    Parse the first line of a git commit message.

    Args:
        line: The first line of a git commit message.

    Returns:
        The parsed Change object

    Raises:
        ValueError: The commit line is not well-structured
    """
    if "\\t" not in line:
        raise ValueError(f"Invalid commit line: {line}")
    commit_hash, rest = line.split("\\t", 1)
    if ":" in rest:
        prefix, message = rest.split(":", 1)
    else:
        prefix = ""
        message = rest

    # Standardize
    message.strip()

    if message.endswith('"'):
        message = message[:-1]

    prefix = prefix.strip()
    if prefix == "DOCS":
        prefix = "DOC"

    return Change(commit_hash=commit_hash, prefix=prefix, message=message)


if __name__ == "__main__":
    main("CHANGELOG.md")
