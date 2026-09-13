from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shlex
import sys
from typing import Any
from urllib.parse import unquote, urlparse


INSTALL_PATH_EDITABLE_CHECKOUT = "editable_checkout"
INSTALL_PATH_LOCAL_WHEEL = "local_wheel"
INSTALL_PATH_INDEX_INSTALL = "index_install"
INSTALL_PATH_UNKNOWN = "unknown"


@dataclass(frozen=True)
class PythonInstallOwner:
    manager: str
    environment: str | None = None


def read_direct_url(files: Iterable[Any] | None) -> dict[str, Any] | None:
    """Read the PEP 610 ``direct_url.json`` recorded next to a distribution.

    pip writes it for any install that did not come from an index, which is how a
    local wheel or an editable checkout can be told apart from a package fetched
    by name.
    """

    for item in files or ():
        posix = PurePosixPath(str(item))
        if not posix.as_posix().endswith("direct_url.json"):
            continue
        try:
            payload = json.loads(Path(item.locate()).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        return payload if isinstance(payload, dict) else None
    return None


def classify_install_path(direct_url: Mapping[str, Any] | None) -> str:
    """Classify where the running LoopX came from."""

    if not isinstance(direct_url, Mapping):
        return INSTALL_PATH_UNKNOWN
    dir_info = direct_url.get("dir_info")
    if isinstance(dir_info, Mapping) and dir_info.get("editable"):
        return INSTALL_PATH_EDITABLE_CHECKOUT
    url = str(direct_url.get("url") or "")
    if url.startswith("file://") and urlparse(url).path.endswith(".whl"):
        return INSTALL_PATH_LOCAL_WHEEL
    if direct_url.get("vcs_info") is None and url.startswith(("http://", "https://")):
        return INSTALL_PATH_INDEX_INSTALL
    return INSTALL_PATH_UNKNOWN


def local_wheel_path(direct_url: Mapping[str, Any] | None) -> str | None:
    """Return the wheel file a local install came from, if pip recorded one."""

    if classify_install_path(direct_url) != INSTALL_PATH_LOCAL_WHEEL:
        return None
    return unquote(urlparse(str(direct_url["url"])).path)


def wheel_reinstall_command(
    *,
    owner: PythonInstallOwner,
    python_executable: str,
    doctor_command: str,
    wheel_path: str | None,
    include_skills: bool = True,
) -> str | None:
    """Reinstall from a local wheel file. No index, no network.

    ``pipx`` is treated as an installation *tool* for the same wheel path rather
    than as a separate channel. Returns None when there is nothing concrete to
    point at, so callers stay fail-closed instead of guessing a path.
    """

    if not wheel_path:
        return None
    if owner.manager == "pipx":
        package_command = f"pipx install --force {_quote_local_path(wheel_path)}"
    elif owner.manager == "pip":
        package_command = (
            f"{_quote_local_path(python_executable)} -m pip install "
            f"--force-reinstall --no-deps {_quote_local_path(wheel_path)}"
        )
    else:
        return None
    lines = [package_command]
    if include_skills:
        lines.append("loopx workflow-skills --install")
        lines.append("loopx slash-commands --install")
    lines.append(doctor_command)
    return "\n".join(lines)


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


def distribution_upgrade_command(
    *,
    distribution_install: Mapping[str, Any] | None,
    python_executable: str,
    doctor_command: str,
) -> str | None:
    """Upgrade advice for a pip-managed install: the recorded wheel first.

    Only a package-index install (which this fork does not publish) falls back to
    the owner's own upgrade channel.
    """

    if not isinstance(distribution_install, Mapping):
        return None
    owner = PythonInstallOwner(
        str(distribution_install.get("installer") or "unknown"),
        distribution_install.get("installer_environment"),
    )
    return wheel_reinstall_command(
        owner=owner,
        python_executable=python_executable,
        doctor_command=doctor_command,
        wheel_path=(
            str(distribution_install["wheel_path"])
            if distribution_install.get("wheel_path")
            else None
        ),
    ) or python_distribution_upgrade_command(
        owner=owner,
        python_executable=python_executable,
        doctor_command=doctor_command,
    )


def install_identity_fields(
    distribution_install: Mapping[str, Any] | None,
    *,
    editable: bool,
) -> dict[str, Any]:
    """The install-kind/install-path block shared by doctor payloads."""

    return {
        "install_kind": "python_distribution" if distribution_install else "release_or_checkout",
        "install_path": (
            distribution_install.get("install_path")
            if isinstance(distribution_install, Mapping)
            else INSTALL_PATH_EDITABLE_CHECKOUT
            if editable
            else INSTALL_PATH_UNKNOWN
        ),
        "wheel_path": (
            distribution_install.get("wheel_path")
            if isinstance(distribution_install, Mapping)
            else None
        ),
    }


def _quote_local_path(value: str) -> str:
    """Quote a path for the shell the emitted command will be pasted into."""
    return shlex.quote(value)


def _editable_install_arguments() -> tuple[str, ...]:
    """Prefer an offline refresh, but never demand a build backend the env lacks.

    A fresh virtualenv on Python 3.12 ships neither setuptools nor wheel, and
    `--no-build-isolation` fails there with ModuleNotFoundError. Only ask for it when
    the running interpreter can actually satisfy it.
    """
    if importlib.util.find_spec("setuptools") is None:
        return ("install", "-e", ".", "--no-deps")
    return ("install", "-e", ".", "--no-deps", "--no-build-isolation")


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
        f"-m pip {' '.join(_editable_install_arguments())}",
    ]
    if include_skills:
        lines.append("loopx workflow-skills --install")
    lines.append(f"loopx doctor{doctor_agent_arg}")
    return "\n".join(lines)
