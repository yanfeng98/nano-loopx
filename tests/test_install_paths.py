"""Guards for the two supported install paths.

The fork supports exactly two ways to install LoopX: an in-place editable
checkout and a locally built wheel file. Both are offline; neither may advertise
a package index, a hosted installer, or the retired release-snapshot scripts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from loopx.python_install_owner import (
    INSTALL_PATH_EDITABLE_CHECKOUT,
    INSTALL_PATH_INDEX_INSTALL,
    INSTALL_PATH_LOCAL_WHEEL,
    INSTALL_PATH_UNKNOWN,
    PythonInstallOwner,
    classify_install_path,
    local_wheel_path,
    read_direct_url,
    wheel_reinstall_command,
)

EDITABLE_DIRECT_URL = {
    "dir_info": {"editable": True},
    "url": "file:///home/example/nano-loopx",
}
LOCAL_WHEEL_DIRECT_URL = {
    "archive_info": {"hash": "sha256=deadbeef"},
    "url": "file:///tmp/dist/loopx-1.1.0-py3-none-any.whl",
}
INDEX_DIRECT_URL = {
    "archive_info": {"hash": "sha256=deadbeef"},
    "url": "https://files.pythonhosted.org/packages/x/loopx-1.1.0-py3-none-any.whl",
}

FORBIDDEN_FRAGMENTS = (
    "huangruiteng",
    "install.sh",
    "github.io",
    "codeload",
    "pip install --upgrade loopx",
    "pipx upgrade",
    "scripts/install-local.sh",
)


class _FakePackagePath:
    """Minimal stand-in for importlib.metadata.PackagePath."""

    def __init__(self, recorded: str, location: Path) -> None:
        self._recorded = recorded
        self._location = location

    def __str__(self) -> str:
        return self._recorded

    def locate(self) -> Path:
        return self._location


@pytest.mark.parametrize(
    ("direct_url", "expected"),
    [
        (EDITABLE_DIRECT_URL, INSTALL_PATH_EDITABLE_CHECKOUT),
        (LOCAL_WHEEL_DIRECT_URL, INSTALL_PATH_LOCAL_WHEEL),
        (INDEX_DIRECT_URL, INSTALL_PATH_INDEX_INSTALL),
        ({"vcs_info": {"vcs": "git"}, "url": "https://example.invalid/repo"}, INSTALL_PATH_UNKNOWN),
        (None, INSTALL_PATH_UNKNOWN),
        ({}, INSTALL_PATH_UNKNOWN),
    ],
)
def test_classify_install_path(direct_url: dict | None, expected: str) -> None:
    assert classify_install_path(direct_url) == expected


def test_local_wheel_path_only_for_file_wheels() -> None:
    assert local_wheel_path(LOCAL_WHEEL_DIRECT_URL) == "/tmp/dist/loopx-1.1.0-py3-none-any.whl"
    assert local_wheel_path(INDEX_DIRECT_URL) is None
    assert local_wheel_path(EDITABLE_DIRECT_URL) is None


def test_read_direct_url_reads_the_recorded_file(tmp_path: Path) -> None:
    dist_info = tmp_path / "loopx-1.1.0.dist-info"
    dist_info.mkdir()
    (dist_info / "direct_url.json").write_text(
        json.dumps(LOCAL_WHEEL_DIRECT_URL), encoding="utf-8"
    )
    item = _FakePackagePath(
        "loopx-1.1.0.dist-info/direct_url.json", dist_info / "direct_url.json"
    )
    assert read_direct_url([item]) == LOCAL_WHEEL_DIRECT_URL
    assert read_direct_url([]) is None


def test_wheel_reinstall_command_is_offline_and_pins_the_wheel() -> None:
    command = wheel_reinstall_command(
        owner=PythonInstallOwner("pip"),
        python_executable="/usr/bin/python3",
        doctor_command="loopx doctor",
        wheel_path="/tmp/dist/loopx-1.1.0-py3-none-any.whl",
    )
    assert command is not None
    lines = command.splitlines()
    assert lines[0] == (
        "/usr/bin/python3 -m pip install --force-reinstall --no-deps "
        "/tmp/dist/loopx-1.1.0-py3-none-any.whl"
    )
    assert "loopx workflow-skills --install" in lines
    assert lines[-1] == "loopx doctor"


def test_pipx_install_is_the_same_wheel_path() -> None:
    command = wheel_reinstall_command(
        owner=PythonInstallOwner("pipx", "loopx-preview"),
        python_executable="/usr/bin/python3",
        doctor_command="loopx doctor --agent-type other-agent",
        wheel_path="/tmp/dist/loopx-1.1.0-py3-none-any.whl",
    )
    assert command is not None
    assert command.splitlines()[0] == (
        "pipx install --force /tmp/dist/loopx-1.1.0-py3-none-any.whl"
    )
    assert command.splitlines()[-1] == "loopx doctor --agent-type other-agent"


@pytest.mark.parametrize(
    "owner",
    [PythonInstallOwner("pip"), PythonInstallOwner("pipx")],
)
def test_wheel_reinstall_command_never_names_a_retired_channel(owner: PythonInstallOwner) -> None:
    command = wheel_reinstall_command(
        owner=owner,
        python_executable="/usr/bin/python3",
        doctor_command="loopx doctor",
        wheel_path="/tmp/dist/loopx-1.1.0-py3-none-any.whl",
    )
    assert command is not None
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in command, (fragment, command)


def test_missing_wheel_or_unknown_owner_is_fail_closed() -> None:
    assert (
        wheel_reinstall_command(
            owner=PythonInstallOwner("pip"),
            python_executable="/usr/bin/python3",
            doctor_command="loopx doctor",
            wheel_path=None,
        )
        is None
    )
    assert (
        wheel_reinstall_command(
            owner=PythonInstallOwner("unknown"),
            python_executable="/usr/bin/python3",
            doctor_command="loopx doctor",
            wheel_path="/tmp/dist/loopx-1.1.0-py3-none-any.whl",
        )
        is None
    )
