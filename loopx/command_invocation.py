from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Mapping, Sequence


def resolve_command_path(
    name: str,
    *,
    env: Mapping[str, str] | None = None,
) -> Path | None:
    """Resolve a command from PATH."""

    source_env = os.environ if env is None else env
    resolved = shutil.which(name, path=source_env.get("PATH"))
    return Path(resolved).expanduser() if resolved else None


def command_argv(command_path: Path, args: Sequence[str]) -> list[str]:
    """Build the subprocess argv for the resolved executable."""

    return [str(command_path), *args]
