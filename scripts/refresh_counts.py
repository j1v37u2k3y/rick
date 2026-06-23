#!/usr/bin/env python3
"""Sync count placeholders in README.md and SKILLS.md.

Single source of truth for tool / resource / skill / test counts and version. Anything
else (CLAUDE.md, ACHIEVEMENTS.md, etc.) should NOT duplicate these — point at
`rick_capabilities` for live state instead.

Tagged regions look like:

    Version <!-- counts:version -->v3.12<!-- /counts:version -->
    <!-- counts:tools -->46<!-- /counts:tools --> tools.

Shield.io badges that mirror a count are synced too — the number lives inside the image URL
where an HTML comment can't go, e.g. the `tests-721%20passed` badge tracks the test count.

Run modes:

    python scripts/refresh_counts.py             # rewrite stale tags in place
    python scripts/refresh_counts.py --check     # exit 1 if anything would change (CI)
    python scripts/refresh_counts.py --skip-tests  # don't run pytest collection
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGETS = [
    ROOT / "README.md",
    ROOT / ".claude" / "skills" / "SKILLS.md",
]


def read_version() -> str:
    text = (ROOT / "__version__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        raise RuntimeError("__version__ not found in __version__.py")
    return m.group(1)


def short_version(full: str) -> str:
    """3.12.0 -> v3.12 (README headline style)."""
    parts = full.split(".")
    return f"v{parts[0]}.{parts[1]}"


def count_registered(module_dir: Path, kind: str) -> int:
    """Count `mcp.{kind}(` invocations across .py files in dir (excluding __init__.py)."""
    pattern = re.compile(rf"\bmcp\.{kind}\(")
    total = 0
    for py in sorted(module_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        total += len(pattern.findall(py.read_text(encoding="utf-8")))
    return total


def count_skills() -> int:
    skills_dir = ROOT / ".claude" / "skills"
    return sum(1 for p in skills_dir.iterdir() if p.is_dir())


def count_tests() -> int:
    """Run `pytest --collect-only -q` via the current Python interpreter and parse the
    trailing summary line.

    Uses `sys.executable -m pytest` rather than resolving a `pytest` binary via PATH or
    a venv-relative path — sys.executable is always absolute (no PATH-hijack surface),
    runs pytest as a module (no reliance on console-script entry points), and uses the
    same Python that invoked this script (no interpreter mismatch).
    """
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
    result = subprocess.run(  # noqa: S603 — sys.executable (absolute) + literal flags, no untrusted input
        cmd, cwd=ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"pytest collection failed (exit {result.returncode}):\n{result.stderr}")
    # Last non-empty line, e.g. "721 tests collected in 0.42s"
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("pytest produced no output")
    m = re.match(r"(\d+)\s+tests?\s+collected", lines[-1])
    if not m:
        raise RuntimeError(f"unparseable pytest summary: {lines[-1]!r}")
    return int(m.group(1))


def compute_counts(skip_tests: bool) -> dict[str, str]:
    version_full = read_version()
    counts: dict[str, str] = {
        "version": short_version(version_full),
        "version-full": version_full,
        "tools": str(count_registered(ROOT / "rick_mcp" / "tools", "tool")),
        "resources": str(count_registered(ROOT / "rick_mcp" / "resources", "resource")),
        "skills": str(count_skills()),
    }
    if not skip_tests:
        counts["tests"] = str(count_tests())
    return counts


def replace_tags(text: str, counts: dict[str, str]) -> str:
    for key, value in counts.items():
        pattern = re.compile(
            rf"<!--\s*counts:{re.escape(key)}\s*-->.*?<!--\s*/counts:{re.escape(key)}\s*-->",
            re.DOTALL,
        )
        replacement = f"<!-- counts:{key} -->{value}<!-- /counts:{key} -->"
        text = pattern.sub(replacement, text)
    return text


# Shield.io badges embed a count directly in the image URL, where the `<!-- counts:* -->`
# comment markers can't live. Each entry maps a count key to a regex with three capture
# groups — (prefix)(number)(suffix) — and only the middle number is rewritten.
BADGE_PATTERNS = {
    "tests": re.compile(r"(tests-)(\d+)(%20passed)"),
}


def replace_badges(text: str, counts: dict[str, str]) -> str:
    for key, pattern in BADGE_PATTERNS.items():
        if key not in counts:
            continue
        value = counts[key]
        text = pattern.sub(lambda m, v=value: f"{m.group(1)}{v}{m.group(3)}", text)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if any tagged region would change; do not rewrite files.",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest collection (faster; the `tests` tag is left untouched).",
    )
    args = parser.parse_args()

    counts = compute_counts(skip_tests=args.skip_tests)
    print("Counts:")
    for key, value in counts.items():
        print(f"  {key}: {value}")

    drift = False
    for path in TARGETS:
        original = path.read_text(encoding="utf-8")
        updated = replace_badges(replace_tags(original, counts), counts)
        rel = path.relative_to(ROOT)
        if original == updated:
            print(f"  OK    {rel}")
            continue
        drift = True
        if args.check:
            print(f"  DRIFT {rel}")
        else:
            path.write_text(updated, encoding="utf-8")
            print(f"  WROTE {rel}")

    if args.check and drift:
        print("\nDrift detected. Run `make refresh-counts` to sync.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
