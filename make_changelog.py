"""Internal tool to update the changelog."""

import subprocess
from datetime import datetime
from typing import List

from dataclasses import dataclass


@dataclass(frozen=True)
class Change:
    commit_hash: str
    prefix: str
    message: str


def main(changelog_path: str):
    changelog = get_changelog(changelog_path)
    git_tag = get_most_recent_git_tag()
    changes = get_formatted_changes(git_tag)
    print("-" * 80)
    print(changes)
    # TODO: Write changes to changelog
    new_version = version_bump(git_tag)
    today = datetime.now()
    header = f"Version {new_version}, {today:%Y-%m-%d}\n"
    header = header + "-" * (len(header) - 1) + "\n"
    trailer = f"\nFull Changelog: https://github.com/py-pdf/PyPDF2/compare/{git_tag}...{new_version}\n\n"
    new_entry = header + changes + trailer
    print(new_entry)

    # TODO: Make idempotent - multiple calls to this script
    # should not change the changelog
    new_changelog = new_entry + changelog
    write_changelog(new_changelog, changelog_path)


def version_bump(git_tag: str) -> str:
    # just assume a patch version change
    major, minor, patch = git_tag.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def get_changelog(changelog_path: str) -> str:
    with open(changelog_path, "r") as fh:
        changelog = fh.read()
    return changelog


def write_changelog(new_changelog: str, changelog_path: str) -> None:
    with open(changelog_path, "w") as fh:
        fh.write(new_changelog)


def get_formatted_changes(git_tag: str) -> str:
    commits = get_git_commits_since_tag(git_tag)

    # Group by prefix
    grouped = {}
    for commit in commits:
        if commit.prefix not in grouped:
            grouped[commit.prefix] = []
        grouped[commit.prefix].append({"msg": commit.message})

    # Order prefixes
    order = ["DEP", "ENH", "BUG", "ROB", "DOC", "DEV", "MAINT", "TST", "STY"]
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


def get_most_recent_git_tag():
    git_tag = str(
        subprocess.check_output(
            ["git", "describe", "--abbrev=0"], stderr=subprocess.STDOUT
        )
    ).strip("'b\\n")
    return git_tag


def get_git_commits_since_tag(git_tag) -> List[Change]:
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


def parse_commit_line(line) -> Change:
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
    main("CHANGELOG")
