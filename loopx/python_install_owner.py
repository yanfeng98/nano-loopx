from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shlex
import sys


@dataclass(frozen=True)
class PythonInstallOwner:
    manager: str
    environment: str | None = None


def resolve_python_install_owner(
    *,
    default_installer: str,
    prefix: Path,
) -> PythonInstallOwner:
    """Preserve pipx ownership instead of treating its internal pip as plain pip."""

    metadata_path = prefix / "pipx_metadata.json"
    if not metadata_path.is_file():
        return PythonInstallOwner(manager=default_installer)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        metadata = {}
    recorded_environment = metadata.get("environment") if isinstance(metadata, dict) else None
    environment = (
        recorded_environment
        if isinstance(recorded_environment, str) and recorded_environment
        else prefix.name
    )
    return PythonInstallOwner(manager="pipx", environment=environment)


def python_distribution_upgrade_command(
    *,
    owner: PythonInstallOwner,
    python_executable: str,
    doctor_command: str,
) -> str | None:
    if owner.manager == "pipx":
        package_command = f"pipx upgrade {shlex.quote(owner.environment or 'loopx')}"
    elif owner.manager == "pip":
        package_command = f"{shlex.quote(python_executable)} -m pip install --upgrade loopx"
    else:
        return None
    return (
        f"{package_command}\n"
        "loopx workflow-skills --install\n"
        "loopx slash-commands --install\n"
        f"{doctor_command}"
    )


def _quote_local_path(value: str) -> str:
    """Quote a path for the shell the emitted command will be pasted into."""
    if os.name == "nt":
        # cmd.exe and PowerShell both accept double-quoted paths; shlex's single
        # quotes would only survive in PowerShell.
        return f'"{value}"'
    return shlex.quote(value)


def is_editable_source_checkout(repo_root: Path, release_root: Path | None) -> bool:
    """True when the running LoopX is a git checkout rather than a release snapshot."""
    return release_root is None and (repo_root / ".git").exists()


def editable_dev_refresh_command(
    repo_root: Path,
    *,
    python_executable: str | None = None,
    doctor_agent_type: str | None = None,
    include_skills: bool = True,
) -> str:
    """Refresh an editable source checkout in place instead of installing a release.

    This fork develops in place through an editable install, so a checkout must never be
    pointed at `scripts/install-local.sh` or the archive installer: both copy a release
    snapshot into `~/.local/bin`, which usually wins the PATH race and silently takes
    over `loopx`. See operation-logs/031.
    """
    doctor_agent_arg = (
        f" --agent-type {shlex.quote(doctor_agent_type)}" if doctor_agent_type else ""
    )
    lines = [
        f"cd {_quote_local_path(str(repo_root))}",
        f"{_quote_local_path(python_executable or sys.executable)} "
        "-m pip install -e . --no-deps --no-build-isolation",
    ]
    if include_skills:
        lines.append("loopx workflow-skills --install")
    lines.append(f"loopx doctor{doctor_agent_arg}")
    return "\n".join(lines)
