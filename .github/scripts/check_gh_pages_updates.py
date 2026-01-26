"""Check that all GitHub pages JavaScript dependencies are up-to-date."""  # noqa: INP001

import base64
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

JSDELIVR_RE = re.compile(
    r"(https://cdn\.jsdelivr\.net/npm/"
    r"(?P<name>[^@/]+)@(?P<version>[^/]+)"
    r"/(?P<path>[^\"']+))"
)


def fetch_json(url: str) -> dict:
    """Retrieve JSON data from the given URL."""
    with urllib.request.urlopen(url, timeout=15) as resp:  # noqa: S310  # Controlled input.
        return json.load(resp)


def fetch_bytes(url: str) -> bytes:
    """Retrieve bytes data from the given URL."""
    with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310  # Controlled input.
        return resp.read()


def get_latest_version(pkg: str) -> str:
    """Get the latest version for this package."""
    data = fetch_json(f"https://registry.npmjs.org/{pkg}")
    return data["dist-tags"]["latest"]


def sri_hash(content: bytes) -> str:
    """Calculate the SRI hash for the given content."""
    digest = hashlib.sha384(content).digest()
    return "sha384-" + base64.b64encode(digest).decode("ascii")


def scan_html(path: Path) -> list[re.Match[str]]:
    """Scan the given HTML file for external JavaScript includes."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return list(JSDELIVR_RE.finditer(text))


def main() -> None:
    """Perform the checks."""
    outdated_found = False

    for html_path in sorted(Path("gh-pages").rglob("*.html"), key=str):
        matches = scan_html(html_path)
        if not matches:
            continue

        sys.stdout.write(f"\n📄 {html_path} ...\n\n")

        for m in matches:
            pkg = m.group("name")
            current_version = m.group("version")
            full_url = m.group(1)

            try:
                latest_version = get_latest_version(pkg)
            except Exception as e:
                sys.stdout.write(f"  ⚠️  {pkg}: npm lookup failed ({e})\n")
                continue

            if current_version == latest_version:
                sys.stdout.write(f"  ✅ {pkg} {current_version}\n")
                continue

            outdated_found = True
            latest_url = full_url.replace(
                f"@{current_version}/", f"@{latest_version}/"
            )

            try:
                latest_bytes = fetch_bytes(latest_url)
                latest_sri = sri_hash(latest_bytes)
            except Exception as e:
                sys.stdout.write(f"  ⚠️  {pkg}: failed to fetch latest file ({e})\n")
                continue

            sys.stdout.write(f"  ❌ {pkg}\n")
            sys.stdout.write(f"     Current: {current_version}\n")
            sys.stdout.write(f"     Latest:  {latest_version}\n")
            sys.stdout.write(f"     Latest SRI: {latest_sri}\n")
            sys.stdout.write("\n")

    if outdated_found:
        sys.stdout.write("\n❗ Outdated dependencies detected\n")
        sys.exit(1)

    sys.stdout.write("\n🎉 All CDN dependencies are up to date\n")


if __name__ == "__main__":
    main()
