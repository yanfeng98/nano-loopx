"""Guards for `loopx update` in the two-path world.

This fork supports an in-place editable checkout and a locally built wheel file.
`loopx update` never touches the network: a local wheel install is reapplied from
the wheel file pip recorded, a checkout is refreshed in place by the operator, and
anything else is reported as unsupported instead of being guessed at.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from unittest import mock

from loopx import __version__
import pytest

from loopx.self_update import (
    UpdateAction,
    build_update_plan,
    execute_update_plan,
    resolve_update_action,
    restart_managed_loopx_services,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WHEEL = "/tmp/dist/loopx-1.1.0-py3-none-any.whl"
FORBIDDEN_FRAGMENTS = (
    "huangruiteng",
    "install.sh",
    "github.io",
    "codeload",
    "pip install --upgrade loopx",
    "pipx upgrade",
    "install-local.sh",
    "git pull",
)


def doctor_payload(
    *,
    install_path: str | None = "local_wheel",
    installer: str = "pip",
    environment: str | None = None,
    wheel: str | None = WHEEL,
    upgrade_command: str | None = None,
) -> dict[str, object]:
    return {
        "path": {"loopx": "/managed/venv/bin/loopx"},
        "package": {"install_kind": "python_distribution"},
        "install_freshness": {
            "status": "python_distribution",
            "requires_upgrade": False,
            "current_version": __version__,
            "current_version_tag": f"v{__version__}",
            "install_kind": "python_distribution",
            "install_path": install_path,
            "wheel_path": wheel,
            "python_distribution_installer": installer,
            "python_distribution_installer_environment": environment,
            "upgrade_command": upgrade_command,
            "contributor_upgrade_command": None,
            "reason": "LoopX is installed as a managed Python distribution",
        },
    }


def wheel_upgrade_command(installer: str = "pip") -> str:
    first = (
        f"pipx install --force {WHEEL}"
        if installer == "pipx"
        else f"{sys.executable} -m pip install --force-reinstall --no-deps {WHEEL}"
    )
    return (
        f"{first}\n"
        "loopx workflow-skills --install\n"
        "loopx slash-commands --install\n"
        "loopx doctor"
    )


def test_update_actions_are_explicit_and_legacy_flags_remain_compatible() -> None:
    assert resolve_update_action("check") is UpdateAction.CHECK
    assert resolve_update_action("plan") is UpdateAction.PLAN
    assert resolve_update_action("apply") is UpdateAction.APPLY
    assert resolve_update_action(check=True) is UpdateAction.CHECK
    assert resolve_update_action(dry_run=True) is UpdateAction.PLAN
    assert resolve_update_action(execute=True) is UpdateAction.APPLY
    assert resolve_update_action() is UpdateAction.PLAN

    with pytest.raises(ValueError, match="conflicts with the legacy option"):
        resolve_update_action("check", execute=True)


def test_local_wheel_plan_reinstalls_the_recorded_wheel_file() -> None:
    doctor = doctor_payload(upgrade_command=wheel_upgrade_command())

    payload = build_update_plan(action="plan", doctor_payload=doctor)

    lifecycle = payload["install_lifecycle"]
    assert lifecycle["owner"] == "local_wheel_install"
    assert lifecycle["execution_driver"] == "python_pip"
    assert lifecycle["wheel_path"] == WHEEL
    assert payload["commands"]["apply"] == "loopx update apply"
    assert payload["plan"]["apply_supported"] is True
    assert payload["plan"]["backup"]["available"] is False
    assert payload["plan"]["install_command"] == lifecycle["owner_upgrade_command"]
    rendered = json.dumps(payload)
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in rendered, fragment


def test_local_wheel_apply_runs_pip_force_reinstall() -> None:
    doctor = doctor_payload(upgrade_command=wheel_upgrade_command())
    payload = build_update_plan(action="apply", doctor_payload=doctor)

    passed = subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")
    with (
        mock.patch(
            "loopx.self_update.subprocess.run",
            side_effect=[passed, passed, passed, passed, passed],
        ) as run,
        mock.patch(
            "loopx.self_update.restart_managed_loopx_services",
            return_value=["com.loopx.status"],
        ),
    ):
        result = execute_update_plan(payload)

    assert result["ok"] is True
    assert result["changes_applied"] is True
    assert result["execution"]["driver"] == "python_pip"
    assert result["execution"]["restarted_services"] == ["com.loopx.status"]
    assert run.call_args_list[0].args[0] == [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--force-reinstall",
        "--no-deps",
        WHEEL,
    ]
    assert run.call_args_list[1].args[0][3:5] == ["workflow-skills", "--install"]
    assert run.call_args_list[2].args[0][3:5] == ["slash-commands", "--install"]


def test_pipx_local_wheel_apply_uses_pipx_install_force() -> None:
    doctor = doctor_payload(
        installer="pipx",
        environment="loopx-preview",
        upgrade_command=wheel_upgrade_command("pipx"),
    )
    payload = build_update_plan(action="apply", doctor_payload=doctor)

    assert payload["install_lifecycle"]["execution_driver"] == "python_pipx"
    assert payload["install_lifecycle"]["package_manager_environment"] == "loopx-preview"

    passed = subprocess.CompletedProcess([], 0, '{"ok": true}', "")
    with (
        mock.patch(
            "loopx.self_update.subprocess.run",
            side_effect=[passed, passed, passed, passed, passed],
        ) as run,
        mock.patch(
            "loopx.self_update.restart_managed_loopx_services",
            return_value=[],
        ),
    ):
        result = execute_update_plan(payload)

    assert result["ok"] is True
    assert run.call_args_list[0].args[0] == ["pipx", "install", "--force", WHEEL]


def test_apply_without_a_recorded_wheel_fails_closed() -> None:
    doctor = doctor_payload(wheel=None)
    payload = build_update_plan(action="apply", doctor_payload=doctor)

    # Without a recorded wheel file there is no local path to reinstall, so the
    # install is reported as undetermined rather than guessed at.
    assert payload["install_lifecycle"]["owner"] == "unknown_install"
    assert payload["plan"]["apply_supported"] is False
    assert payload["commands"]["apply"] is None

    # And even a hand-built plan never invents an install command.
    forged = {
        "install_lifecycle": {
            "execution_driver": "python_pip",
            "owner": "local_wheel_install",
            "wheel_path": None,
        },
        "plan": {"backup": {}},
    }
    updated = execute_update_plan(forged)
    assert updated["ok"] is False
    assert updated["execution"]["status"] == "missing_wheel_source"


def test_live_checkout_apply_never_mutates_git_or_switches_install_channels() -> None:
    doctor = doctor_payload(
        install_path="editable_checkout",
        wheel=None,
        upgrade_command=(
            "cd /workspace/loopx\n"
            "/workspace/venv/bin/python -m pip install -e . --no-deps --no-build-isolation\n"
            "loopx workflow-skills --install\n"
            "loopx doctor"
        ),
    )

    payload = build_update_plan(action="apply", doctor_payload=doctor)

    assert payload["ok"] is False
    assert payload["install_lifecycle"]["owner"] == "source_checkout"
    assert payload["install_lifecycle"]["execution_driver"] is None
    assert payload["commands"]["apply"] is None
    install_command = payload["plan"]["install_command"]
    assert install_command.startswith("cd /workspace/loopx\n")
    assert "pip install -e ." in install_command
    assert payload["changes_applied"] is False
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in install_command, fragment


def test_index_install_is_unsupported_and_names_no_index() -> None:
    doctor = doctor_payload(install_path="index_install", wheel=None)

    payload = build_update_plan(action="apply", doctor_payload=doctor)

    assert payload["ok"] is False
    assert payload["install_lifecycle"]["owner"] == "unsupported_index_install"
    assert payload["install_lifecycle"]["execution_driver"] is None
    assert payload["commands"]["apply"] is None
    assert payload["commands"]["owner_upgrade"] is None
    assert payload["next_action"]["command"] is None
    assert "does not publish to a package index" in payload["recommended_action"]
    rendered = json.dumps(payload)
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in rendered, fragment


def test_cli_rejects_conflicting_named_and_legacy_actions() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "loopx.cli",
            "update",
            "check",
            "--execute",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1, (result.stdout, result.stderr)
    payload = json.loads(result.stdout)
    assert payload["changes_applied"] is False
    assert "conflicts with the legacy option" in payload["error"]


def test_restart_managed_loopx_services_restarts_only_loopx_launchagents(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("loopx.self_update.sys.platform", "darwin")
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    agents = tmp_path / "Library" / "LaunchAgents"
    agents.mkdir(parents=True)
    for name in (
        "com.loopx.status.plist",
        "com.loopx.chat.plist",
        "com.goal-harness.status.plist",
        "unrelated.plist",
    ):
        (agents / name).write_text("<plist/>", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr("loopx.self_update.subprocess.run", fake_run)

    restarted = restart_managed_loopx_services()
    assert set(restarted) == {
        "com.loopx.status",
        "com.loopx.chat",
        "com.goal-harness.status",
    }
    assert len(calls) == 3
    assert all(call[0] == "launchctl" for call in calls)


def test_successful_update_revalidates_enabled_extensions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "install_lifecycle": {
            "execution_driver": "python_pip",
            "owner": "local_wheel_install",
            "wheel_path": WHEEL,
        },
        "plan": {"backup": {}},
    }
    calls: list[list[str]] = []

    def fake_run(
        args: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, '{"ok": true}', "")

    monkeypatch.setattr("loopx.self_update.subprocess.run", fake_run)
    monkeypatch.setattr(
        "loopx.self_update.restart_managed_loopx_services", lambda: []
    )

    updated = execute_update_plan(payload)

    assert updated["ok"] is True
    assert updated["execution"]["install_returncode"] == 0
    assert calls[0] == [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--force-reinstall",
        "--no-deps",
        WHEEL,
    ]
    assert calls[-1] == [
        sys.executable,
        "-m",
        "loopx.cli",
        "extension",
        "doctor",
        "--all-enabled",
        "--execute",
        "--format",
        "json",
    ]
