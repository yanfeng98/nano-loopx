"""Install and repair guidance for the two supported install paths.

A checkout refreshes in place; a local wheel installs from the wheel file built by
``scripts/build-wheel.sh``. This fork publishes nothing to a package index and hosts
no installer, so nothing here may name an index, a download URL or a retired script.
"""

from __future__ import annotations

from . import __version__
from .python_install_owner import (
    INSTALL_PATHS_HINT,
    current_refresh_command,
    wheel_convention_path,
)


DEFAULT_WORKFLOW_SKILL_INSTALL_COMMAND = "loopx workflow-skills --install"
DEFAULT_SLASH_COMMAND_INSTALL_COMMAND = "loopx slash-commands --install"


def install_repair_command(*, doctor_agent_type: str | None = None) -> str:
    """Repair block for the install that is running, or the two-path hint."""

    return (
        current_refresh_command(doctor_agent_type=doctor_agent_type)
        or INSTALL_PATHS_HINT
    )


def wheel_install_command(*, version: str = __version__) -> str:
    """Build and install the wheel this repository produces."""

    return (
        "bash scripts/build-wheel.sh\n"
        "python3 -m pip install --force-reinstall --no-deps "
        f"{wheel_convention_path(version)}\n"
        f"{DEFAULT_WORKFLOW_SKILL_INSTALL_COMMAND}\n"
        "loopx doctor"
    )
