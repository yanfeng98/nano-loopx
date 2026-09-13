from __future__ import annotations

from enum import StrEnum
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from .doctor import collect_doctor
from .python_install_owner import (
    INSTALL_PATH_EDITABLE_CHECKOUT,
    INSTALL_PATH_INDEX_INSTALL,
    INSTALL_PATH_LOCAL_WHEEL,
)


UPDATE_PLAN_SCHEMA_VERSION = "loopx_update_plan_v0"


class UpdateAction(StrEnum):
    """Stable operator intent for the self-update boundary."""

    CHECK = "check"
    PLAN = "plan"
    APPLY = "apply"


def resolve_update_action(
    action: UpdateAction | str | None = None,
    *,
    check: bool = False,
    dry_run: bool = False,
    execute: bool = False,
) -> UpdateAction:
    """Resolve explicit actions and legacy flag aliases without ambiguity."""

    explicit = UpdateAction(action) if action is not None else None
    legacy_actions = [
        candidate
        for enabled, candidate in (
            (check, UpdateAction.CHECK),
            (dry_run, UpdateAction.PLAN),
            (execute, UpdateAction.APPLY),
        )
        if enabled
    ]
    if len(legacy_actions) > 1:
        raise ValueError("choose one update action: check, plan, or apply")
    legacy = legacy_actions[0] if legacy_actions else None
    if explicit is not None and legacy is not None and explicit != legacy:
        raise ValueError(
            f"update action `{explicit.value}` conflicts with the legacy option for "
            f"`{legacy.value}`; use `loopx update {explicit.value}` alone"
        )
    return explicit or legacy or UpdateAction.PLAN


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _install_lifecycle(doctor_payload: dict[str, Any]) -> dict[str, Any]:
    """Describe who owns the running install, for exactly two supported paths.

    A local wheel file is reinstalled from that file; a checkout refreshes in
    place. Anything else (an index install, or an install whose origin cannot be
    determined) is reported as unsupported instead of being guessed at.
    """

    package = (
        doctor_payload.get("package")
        if isinstance(doctor_payload.get("package"), dict)
        else {}
    )
    freshness = (
        doctor_payload.get("install_freshness")
        if isinstance(doctor_payload.get("install_freshness"), dict)
        else {}
    )
    install_path = freshness.get("install_path")
    installer = freshness.get("python_distribution_installer")
    installer_environment = freshness.get("python_distribution_installer_environment")
    if not isinstance(installer, str) or not installer:
        distribution = (
            package.get("python_distribution")
            if isinstance(package.get("python_distribution"), dict)
            else {}
        )
        installer = distribution.get("installer")
        installer_environment = distribution.get("installer_environment")
    wheel_path = freshness.get("wheel_path")
    has_wheel = isinstance(wheel_path, str) and bool(wheel_path)

    if install_path == INSTALL_PATH_LOCAL_WHEEL and has_wheel:
        owner = "local_wheel_install"
        install_kind = "python_distribution"
        apply_supported = installer in {"pip", "pipx"}
        execution_driver = (
            "python_pipx"
            if installer == "pipx"
            else "python_pip"
            if installer == "pip"
            else None
        )
        reason = (
            "LoopX can reinstall the recorded local wheel with the owning package manager"
            if apply_supported
            else (
                f"the active Python environment is owned by {installer or 'an unknown installer'}; "
                "reinstall the recorded wheel with that package manager directly"
            )
        )
        owner_command = freshness.get("upgrade_command")
    elif install_path == INSTALL_PATH_INDEX_INSTALL:
        owner = "unsupported_index_install"
        install_kind = "python_distribution"
        apply_supported = False
        execution_driver = None
        reason = (
            "this fork does not publish to a package index; build a local wheel and install "
            "that file instead"
        )
        owner_command = None
    elif install_path == INSTALL_PATH_EDITABLE_CHECKOUT:
        owner = "source_checkout"
        install_kind = "live_checkout"
        apply_supported = False
        execution_driver = None
        reason = (
            "the active checkout owns its own updates; refresh it in place instead of "
            "replacing it"
        )
        owner_command = freshness.get("upgrade_command") or freshness.get(
            "contributor_upgrade_command"
        )
    else:
        owner = "unknown_install"
        install_kind = "unknown"
        apply_supported = False
        execution_driver = None
        reason = (
            "the install path could not be determined; run `loopx doctor` and reinstall from "
            "the checkout or a local wheel"
        )
        owner_command = None

    return {
        "install_kind": install_kind,
        "owner": owner,
        "loopx_apply_supported": apply_supported,
        "execution_driver": execution_driver,
        "package_manager": installer if install_kind == "python_distribution" else None,
        "package_manager_environment": (
            installer_environment if install_kind == "python_distribution" else None
        ),
        "wheel_path": wheel_path if has_wheel else None,
        "reason": reason,
        "owner_upgrade_command": owner_command,
    }


def build_update_plan(
    *,
    action: UpdateAction | str | None = None,
    check_only: bool = False,
    execute: bool = False,
    doctor_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Report what `loopx update` would do for the two supported install paths.

    Read-only: it touches no network and mutates nothing. A local wheel install can
    be reapplied from its recorded wheel file; a checkout is refreshed in place by
    the operator; anything else is reported as unsupported rather than guessed at.
    """

    requested_action = resolve_update_action(action, check=check_only, execute=execute)
    check_only = requested_action is UpdateAction.CHECK
    execute = requested_action is UpdateAction.APPLY
    doctor = doctor_payload or collect_doctor()
    install_freshness = _as_dict(doctor.get("install_freshness"))
    release_manifest = _as_dict(doctor.get("release_manifest"))
    release_manifest_body = _as_dict(release_manifest.get("manifest"))
    lifecycle = _install_lifecycle(doctor)
    apply_supported = bool(lifecycle["loopx_apply_supported"])
    owner_upgrade_command = lifecycle.get("owner_upgrade_command")
    path = _as_dict(doctor.get("path"))
    requires_upgrade = install_freshness.get("requires_upgrade")
    current_version = install_freshness.get("current_version")
    commands = {
        "check": "loopx update check",
        "plan": "loopx update plan",
        "apply": "loopx update apply" if apply_supported else None,
        "owner_upgrade": owner_upgrade_command,
    }
    backup = {
        "available": False,
        "reason": (
            "this fork keeps no previous install to roll back to; keep the previous wheel "
            "file or checkout revision yourself"
        ),
        "rollback_command": None,
    }
    if execute and not apply_supported:
        recommended_action = (
            f"use the active {lifecycle['owner']} path:\n{owner_upgrade_command}"
            if owner_upgrade_command
            else f"no apply path is available: {lifecycle['reason']}"
        )
    elif execute:
        recommended_action = (
            "review the execution result and the post-update doctor output"
        )
    elif apply_supported:
        recommended_action = (
            "run `loopx update apply` to reinstall the recorded local wheel, then review "
            "the host-material readback"
        )
    elif owner_upgrade_command:
        recommended_action = (
            f"use the active {lifecycle['owner']} path:\n{owner_upgrade_command}"
        )
    else:
        recommended_action = f"no update path is available: {lifecycle['reason']}"
    if execute and apply_supported:
        next_action = {
            "kind": "review_execution",
            "command": "loopx doctor",
            "mutating": False,
            "requires_explicit_approval": False,
            "reason": recommended_action,
        }
    elif apply_supported:
        next_action = {
            "kind": "apply_update",
            "command": commands["apply"],
            "mutating": True,
            "requires_explicit_approval": True,
            "reason": recommended_action,
        }
    else:
        next_action = {
            "kind": "use_installation_owner",
            "command": owner_upgrade_command,
            "mutating": bool(owner_upgrade_command),
            "requires_explicit_approval": bool(owner_upgrade_command),
            "reason": recommended_action,
        }
    return {
        "ok": not execute or apply_supported,
        "schema_version": UPDATE_PLAN_SCHEMA_VERSION,
        "mode": "update",
        "requested_action": requested_action.value,
        "check_only": check_only,
        "dry_run": not execute,
        "execute_requested": execute,
        "changes_applied": False,
        "install_lifecycle": lifecycle,
        "commands": commands,
        "next_action": next_action,
        "current": {
            "loopx_command": path.get("loopx"),
            "loopx_realpath": path.get("loopx_realpath"),
            "current_version": current_version,
            "current_version_tag": install_freshness.get("current_version_tag"),
            "manifest_package_version": install_freshness.get(
                "manifest_package_version"
            ),
            "manifest_package_version_tag": install_freshness.get(
                "manifest_package_version_tag"
            ),
            "manifest_package_version_matches_runtime": install_freshness.get(
                "manifest_package_version_matches_runtime"
            ),
            "release_id": install_freshness.get("release_id"),
            "install_freshness_status": install_freshness.get("status"),
            "install_path": install_freshness.get("install_path"),
            "wheel_path": install_freshness.get("wheel_path"),
            "requires_upgrade": requires_upgrade,
            "reason": install_freshness.get("reason"),
            "release_manifest_available": release_manifest.get("available"),
            "release_manifest_path": release_manifest.get("path"),
            "release_manifest": release_manifest_body,
        },
        "plan": {
            "action": "check_only"
            if check_only
            else "execute_installer"
            if execute
            else "dry_run",
            "apply_supported": apply_supported,
            "blocked_reason": lifecycle["reason"]
            if execute and not apply_supported
            else None,
            "install_command": owner_upgrade_command,
            "post_update_validation": "loopx doctor",
            "mutates_loopx_runtime_state": False,
            "mutates_release_install": execute and apply_supported,
            "backup": backup,
        },
        "execution": None,
        "error": (
            f"`loopx update apply` cannot mutate an installation owned by {lifecycle['owner']}"
            if execute and not apply_supported
            else None
        ),
        "recommended_action": recommended_action,
    }


def restart_managed_loopx_services() -> list[str]:
    """Best-effort restart of user LaunchAgent-managed LoopX services on macOS.

    After ``loopx update`` replaces the installed release, running status/chat
    services still belong to the previous release. Restarting the managed
    LaunchAgents makes them run the new ``loopx`` immediately, so the dashboard
    and desktop shell keep working without a release-identity mismatch.
    """
    if sys.platform != "darwin":
        return []
    agents_dir = Path.home() / "Library" / "LaunchAgents"
    if not agents_dir.is_dir():
        return []
    labels: list[str] = []
    for plist in sorted(agents_dir.glob("*.plist")):
        stem = plist.stem.lower()
        if "loopx" not in stem and "goal-harness" not in stem:
            continue
        if not (stem.endswith(".status") or stem.endswith(".chat")):
            continue
        labels.append(plist.stem)
    restarted: list[str] = []
    uid = os.getuid() if hasattr(os, "getuid") else 0
    for label in labels:
        result = subprocess.run(
            ["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            restarted.append(label)
    return restarted


def _execute_python_distribution_update(
    payload: dict[str, Any],
    *,
    timeout_seconds: int,
) -> dict[str, Any]:
    lifecycle = (
        payload.get("install_lifecycle")
        if isinstance(payload.get("install_lifecycle"), dict)
        else {}
    )
    driver = lifecycle.get("execution_driver")
    wheel_path = lifecycle.get("wheel_path")
    wheel_source = str(wheel_path) if isinstance(wheel_path, str) and wheel_path else None
    if wheel_source is None:
        # Fail closed: without the recorded wheel file there is nothing concrete to
        # reinstall, and guessing an index name is exactly what this fork forbids.
        updated = dict(payload)
        updated["ok"] = False
        updated["changes_applied"] = False
        updated["execution"] = {
            "status": "missing_wheel_source",
            "owner": lifecycle.get("owner"),
            "reason": (
                "the install does not record the wheel file it came from; rebuild the wheel "
                "and reinstall it explicitly"
            ),
        }
        return updated
    install_command = (
        ["pipx", "install", "--force", wheel_source]
        if driver == "python_pipx"
        else [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--no-deps",
            wheel_source,
        ]
    )
    commands = {
        "install": install_command,
        "workflow_skills": [
            sys.executable,
            "-m",
            "loopx.cli",
            "workflow-skills",
            "--install",
            "--format",
            "json",
        ],
        "slash_commands": [
            sys.executable,
            "-m",
            "loopx.cli",
            "slash-commands",
            "--install",
            "--format",
            "json",
        ],
        "doctor": [
            sys.executable,
            "-m",
            "loopx.cli",
            "doctor",
            "--format",
            "json",
        ],
        "extension_doctor": [
            sys.executable,
            "-m",
            "loopx.cli",
            "extension",
            "doctor",
            "--all-enabled",
            "--execute",
            "--format",
            "json",
        ],
    }
    results: dict[str, subprocess.CompletedProcess[str]] = {}
    results["install"] = subprocess.run(
        commands["install"],
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    if results["install"].returncode == 0:
        for step in ("workflow_skills", "slash_commands", "doctor"):
            results[step] = subprocess.run(
                commands[step],
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
        if all(
            results[step].returncode == 0
            for step in ("workflow_skills", "slash_commands", "doctor")
        ):
            results["extension_doctor"] = subprocess.run(
                commands["extension_doctor"],
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )

    execution: dict[str, Any] = {
        "driver": driver,
        "python_executable": sys.executable,
        "install_returncode": results["install"].returncode,
        "install_stdout_tail": results["install"].stdout[-2000:],
        "install_stderr_tail": results["install"].stderr[-2000:],
    }
    for step in ("workflow_skills", "slash_commands", "doctor", "extension_doctor"):
        result = results.get(step)
        if result is None:
            execution[f"{step}_status"] = "skipped_prior_step_failed"
            continue
        execution[f"{step}_returncode"] = result.returncode
        execution[f"{step}_stdout_tail"] = result.stdout[-2000:]
        execution[f"{step}_stderr_tail"] = result.stderr[-2000:]

    required_steps = (
        "install",
        "workflow_skills",
        "slash_commands",
        "doctor",
        "extension_doctor",
    )
    ok = all(
        step in results and results[step].returncode == 0 for step in required_steps
    )
    updated = dict(payload)
    updated["execution"] = execution
    updated["ok"] = ok
    updated["changes_applied"] = results["install"].returncode == 0
    if ok:
        execution["restarted_services"] = restart_managed_loopx_services()
        updated["recommended_action"] = (
            "local wheel reinstall and host-material readback passed; use the new LoopX process"
        )
        updated["next_action"] = {
            "kind": "use_updated_runtime",
            "command": "loopx doctor",
            "mutating": False,
            "requires_explicit_approval": False,
            "reason": updated["recommended_action"],
        }
    else:
        updated["recommended_action"] = (
            "inspect the failed step, then reinstall the previous wheel file or the "
            "previous checkout revision"
        )
        updated["next_action"] = {
            "kind": "review_failed_update",
            "command": None,
            "mutating": False,
            "requires_explicit_approval": False,
            "reason": updated["recommended_action"],
        }
    return updated


def execute_update_plan(
    payload: dict[str, Any], *, timeout_seconds: int = 600
) -> dict[str, Any]:
    """Apply the plan for a local wheel install; every other owner stays untouched."""

    lifecycle = _as_dict(payload.get("install_lifecycle"))
    driver = lifecycle.get("execution_driver")
    if driver in {"python_pip", "python_pipx"}:
        return _execute_python_distribution_update(
            payload,
            timeout_seconds=timeout_seconds,
        )
    updated = dict(payload)
    updated["ok"] = False
    updated["changes_applied"] = False
    updated["execution"] = {
        "status": "unsupported_install_owner",
        "owner": lifecycle.get("owner"),
        "reason": lifecycle.get("reason"),
    }
    return updated

def render_update_plan_markdown(payload: dict[str, Any]) -> str:
    current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
    plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else {}
    backup = plan.get("backup") if isinstance(plan.get("backup"), dict) else {}
    next_action = (
        payload.get("next_action")
        if isinstance(payload.get("next_action"), dict)
        else {}
    )
    notice = (
        "> **No update was applied.** This is a read-only check/plan."
        if not payload.get("execute_requested")
        else "> **Apply was requested.** Review the execution and validation result below."
    )
    lines = [
        "# LoopX Update",
        "",
        notice,
        "",
        "## Next Action",
        "",
        f"- Kind: `{next_action.get('kind')}`",
        f"- Mutating: `{next_action.get('mutating')}`",
        f"- Requires explicit approval: `{next_action.get('requires_explicit_approval')}`",
    ]
    next_command = next_action.get("command")
    if next_command:
        lines.extend(["", "```bash", str(next_command), "```"])
    lines.extend(
        [
            "",
            "## Details",
            "",
            f"- OK: `{payload.get('ok')}`",
            f"- Requested action: `{payload.get('requested_action')}`",
            f"- Changes applied: `{payload.get('changes_applied')}`",
            f"- Mode: `{plan.get('action')}`",
            f"- Dry run: `{payload.get('dry_run')}`",
            f"- Current version: `{current.get('current_version')}`",
            f"- Current version tag: `{current.get('current_version_tag')}`",
            f"- Manifest package version: `{current.get('manifest_package_version')}`",
            f"- Manifest package version tag: `{current.get('manifest_package_version_tag')}`",
            f"- Manifest package matches runtime: `{current.get('manifest_package_version_matches_runtime')}`",
            f"- Freshness: `{current.get('install_freshness_status')}`",
            f"- Requires upgrade: `{current.get('requires_upgrade')}`",
            f"- Runtime state mutation: `{plan.get('mutates_loopx_runtime_state')}`",
            f"- Release install mutation: `{plan.get('mutates_release_install')}`",
            f"- Install kind: `{(payload.get('install_lifecycle') or {}).get('install_kind')}`",
            f"- Install owner: `{(payload.get('install_lifecycle') or {}).get('owner')}`",
            f"- Apply supported: `{plan.get('apply_supported')}`",
            f"- Rollback available: `{backup.get('available')}`",
            f"- Recommended action: {payload.get('recommended_action')}",
            "",
            "## Planned Installation-owner Command",
            "",
            "```bash",
            str(plan.get("install_command") or ""),
            "```",
        ]
    )
    commands = (
        payload.get("commands") if isinstance(payload.get("commands"), dict) else {}
    )
    lines.extend(
        [
            "",
            "## Intent Commands",
            "",
            f"- Check: `{commands.get('check')}`",
            f"- Plan: `{commands.get('plan')}`",
            f"- Apply: `{commands.get('apply')}`",
        ]
    )
    execution = payload.get("execution")
    if isinstance(execution, dict):
        lines.extend(
            [
                "",
                "## Execution",
                "",
                f"- Install return code: `{execution.get('install_returncode')}`",
                f"- Doctor return code: `{execution.get('doctor_returncode')}`",
            ]
        )
    return "\n".join(lines) + "\n"
