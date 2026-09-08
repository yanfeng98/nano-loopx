"""Local workspace observation and bounded validation for planner-worker runtimes."""

from __future__ import annotations

import hashlib
import os
import shlex
import signal
import stat
import subprocess
from pathlib import Path

from .contract import ValidationResult
from .runtime import WorkspaceChange, WorkspaceFileType

DEFAULT_VALIDATION_EXECUTABLES = frozenset(
    {"python", "python3", "pytest", "go", "npm", "npx", "cargo"}
)


class PlannerWorkerWorkspaceError(RuntimeError):
    """Raised when the local planner-worker workspace cannot be inspected safely."""


class SubprocessValidationRunner:
    """Run bounded validation commands without shell expansion."""

    def __init__(
        self,
        *,
        timeout_seconds: float,
        approved_commands: frozenset[str],
        allowed_executables: frozenset[str] = DEFAULT_VALIDATION_EXECUTABLES,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.approved_commands = approved_commands
        self.allowed_executables = allowed_executables

    def __call__(self, command: str, cwd: Path) -> ValidationResult:
        if command not in self.approved_commands:
            return ValidationResult(command=command, passed=False, exit_code=None)
        try:
            argv = shlex.split(command)
        except ValueError:
            return ValidationResult(command=command, passed=False, exit_code=None)
        if (
            not argv
            or argv[0] != Path(argv[0]).name
            or argv[0] not in self.allowed_executables
            or "-c" in argv[1:]
        ):
            return ValidationResult(command=command, passed=False, exit_code=None)
        try:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "PYTHONPATH": str(cwd),
                },
            )
            exit_code = process.wait(timeout=self.timeout_seconds)
        except OSError:
            return ValidationResult(command=command, passed=False, exit_code=None)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            return ValidationResult(command=command, passed=False, exit_code=None)
        return ValidationResult(
            command=command,
            passed=exit_code == 0,
            exit_code=exit_code,
        )


class GitWorkspaceObserver:
    """Require a clean git fixture and report Worker changes as relative paths."""

    def __init__(self) -> None:
        self._before: dict[str, tuple[int, str, int]] | None = None

    def _snapshot(self, cwd: Path) -> dict[str, tuple[int, str, int]]:
        snapshot: dict[str, tuple[int, str, int]] = {
            ".": (0, "", cwd.lstat().st_mode)
        }
        for root, directories, filenames in os.walk(cwd, followlinks=False):
            root_path = Path(root)
            traversable_directories: list[str] = []
            for name in directories:
                path = root_path / name
                if name == ".git":
                    continue
                relative = path.relative_to(cwd).as_posix()
                if path.is_symlink():
                    payload = os.readlink(path).encode(
                        "utf-8", errors="surrogateescape"
                    )
                    snapshot[relative] = (
                        len(payload),
                        hashlib.sha256(payload).hexdigest(),
                        path.lstat().st_mode,
                    )
                    continue
                snapshot[relative] = (0, "", path.lstat().st_mode)
                traversable_directories.append(name)
            directories[:] = traversable_directories
            for filename in filenames:
                path = root_path / filename
                relative = path.relative_to(cwd).as_posix()
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    payload = os.readlink(path).encode("utf-8", errors="surrogateescape")
                elif stat.S_ISREG(mode):
                    payload = path.read_bytes()
                else:
                    payload = b""
                snapshot[relative] = (
                    len(payload),
                    hashlib.sha256(payload).hexdigest(),
                    mode,
                )
        return snapshot

    def assert_clean(self, cwd: Path) -> None:
        probe = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0 or probe.stdout.strip() != "true":
            raise PlannerWorkerWorkspaceError("planner-worker workspace must be a git worktree")
        if self.changed_files(cwd):
            raise PlannerWorkerWorkspaceError(
                "planner-worker workspace must be clean before Planner execution"
            )
        self._before = self._snapshot(cwd)

    @staticmethod
    def _workspace_change(
        entry: tuple[int, str, int] | None,
    ) -> WorkspaceChange:
        if entry is None:
            return {"size": None, "file_type": "deleted"}
        size, _, mode = entry
        file_type: WorkspaceFileType
        if stat.S_ISREG(mode):
            file_type = "regular"
        elif stat.S_ISLNK(mode):
            file_type = "symlink"
        elif stat.S_ISDIR(mode):
            file_type = "directory"
        else:
            file_type = "special"
        return {
            "size": size if file_type in {"regular", "symlink"} else None,
            "file_type": file_type,
        }

    def changed_files(self, cwd: Path) -> dict[str, WorkspaceChange]:
        if self._before is not None:
            after = self._snapshot(cwd)
            changed_paths = {
                path
                for path in {*self._before, *after}
                if self._before.get(path) != after.get(path)
                and not (
                    path not in self._before
                    and path in after
                    and stat.S_ISDIR(after[path][2])
                )
            }
            snapshot_changes: dict[str, WorkspaceChange] = {}
            for path in sorted(changed_paths):
                snapshot_changes[path] = self._workspace_change(after.get(path))
            return snapshot_changes
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
            cwd=cwd,
            check=False,
            capture_output=True,
        )
        if result.returncode != 0:
            raise PlannerWorkerWorkspaceError("unable to inspect planner-worker git changes")
        status_changes: dict[str, WorkspaceChange] = {}
        entries = [entry for entry in result.stdout.split(b"\0") if entry]
        index = 0
        while index < len(entries):
            entry = entries[index].decode("utf-8", errors="replace")
            status = entry[:2]
            path = entry[3:]
            if status[0] in {"R", "C"} and index + 1 < len(entries):
                index += 1
            file_path = cwd / path
            try:
                mode = file_path.lstat().st_mode
            except FileNotFoundError:
                status_changes[path] = self._workspace_change(None)
            else:
                if stat.S_ISREG(mode):
                    payload_size = file_path.stat().st_size
                elif stat.S_ISLNK(mode):
                    payload_size = len(
                        os.readlink(file_path).encode(
                            "utf-8",
                            errors="surrogateescape",
                        )
                    )
                else:
                    payload_size = 0
                status_changes[path] = self._workspace_change((payload_size, "", mode))
            index += 1
        return dict(sorted(status_changes.items()))
