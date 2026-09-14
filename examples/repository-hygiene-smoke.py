#!/usr/bin/env python3
"""Thin repository-hygiene smoke for this fork's checkout."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from loopx.contract import scan_public_boundary  # noqa: E402


# This fork deliberately ships without the upstream public-project paperwork: on
# 2026-09-07 it removed LICENSE / LICENSE-MIT (c88509106) and the whole .github/
# tree (6a9bebc75) — CI workflows, security policy, pull-request and issue
# templates. The assertions that required those files are dropped here rather
# than satisfied with placeholder paperwork; the public/private boundary scan
# and the release-timeline check below remain the live contract.
REQUIRED_TRACKED_FILES = ("CONTRIBUTING.md",)
RELEASE_TIMELINE = REPO_ROOT / "docs" / "product" / "release-readiness.md"
FIRST_PUBLIC_RELEASE = (0, 1, 3)
VERSION_TAG_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
# A "`v0.2.6` 于 2026-07-16" style release entry.
DATED_VERSION_ENTRY = re.compile(r"`v\d+\.\d+\.\d+`\s*于\s*20\d\d")


def tracked_files() -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "-z"],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            "repository-hygiene-smoke requires a git worktree: "
            f"{completed.stderr.strip() or 'git ls-files failed'}"
        )
    return {line for line in completed.stdout.split("\0") if line}


def validate_required_tracked_files(files: set[str]) -> None:
    missing = [name for name in REQUIRED_TRACKED_FILES if name not in files]
    if missing:
        raise AssertionError(f"missing tracked repository-hygiene files: {sorted(missing)}")


def validate_public_private_boundary() -> None:
    boundary = scan_public_boundary([REPO_ROOT], registry={})
    hits = list(boundary.get("hits") or [])
    if hits:
        detail = "\n".join(hits)
        raise AssertionError(f"public/private boundary violations:\n{detail}")
    if not boundary.get("ok"):
        raise AssertionError(
            f"public/private boundary scan failed: {boundary.get('ok')}"
        )


def release_tags() -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "tag", "--list", "--sort=version:refname", "v*"],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"cannot list git tags: {completed.stderr.strip()}")
    tags: list[str] = []
    for tag in completed.stdout.splitlines():
        match = VERSION_TAG_RE.match(tag.strip())
        if not match:
            continue
        version = tuple(int(part) for part in match.groups())
        if version >= FIRST_PUBLIC_RELEASE:
            tags.append(tag.strip())
    return tags


def validate_release_timeline() -> None:
    """The named-version contract must describe only releases this fork cut.

    With tags present the document has to carry an entry for each of them. With no
    tags the document must carry none: a dated version entry that no tag backs is a
    release history borrowed from somewhere else, which is the failure this guards.
    """

    if not RELEASE_TIMELINE.is_file():
        raise AssertionError(f"missing release timeline: {RELEASE_TIMELINE.relative_to(REPO_ROOT)}")
    timeline = RELEASE_TIMELINE.read_text(encoding="utf-8")
    tags = release_tags()
    if not tags:
        dated = DATED_VERSION_ENTRY.findall(timeline)
        if dated:
            raise AssertionError(
                "release-readiness names dated versions this repository never tagged: "
                + ", ".join(sorted(set(dated)))
            )
        return
    missing = [tag for tag in tags if f"`{tag}`" not in timeline]
    if missing:
        raise AssertionError(
            "release timeline is missing version entries: "
            + ", ".join(missing)
        )


def main() -> int:
    files = tracked_files()
    validate_required_tracked_files(files)
    validate_public_private_boundary()
    validate_release_timeline()
    print("repository-hygiene-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
