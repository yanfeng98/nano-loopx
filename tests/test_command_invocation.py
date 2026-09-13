from __future__ import annotations

import os
from pathlib import Path

import pytest

from loopx.command_invocation import command_argv, resolve_command_path


def test_resolve_command_path_finds_an_executable_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script = tmp_path / "loopx"
    script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    script.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path) + os.pathsep + os.environ.get("PATH", ""))

    resolved = resolve_command_path("loopx")

    assert resolved == script
    assert command_argv(resolved, ["alpha", "two words"]) == [str(script), "alpha", "two words"]


def test_resolve_command_path_returns_none_for_an_unknown_name(tmp_path: Path) -> None:
    assert (
        resolve_command_path("loopx-not-installed-here", env={"PATH": str(tmp_path)}) is None
    )
