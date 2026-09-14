from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import subprocess
from pathlib import Path

import pytest

from loopx import __version__
from loopx.doctor import (
    REQUIRED_INSTALLED_SKILL_PHRASES,
    build_install_freshness,
    current_script_invocation_path,
    git_revision_relation,
    installed_skill_summary,
    python_distribution_install,
    trusted_release_ref_for_root,
)


class _FakeDistributionFile:
    def __init__(self, module_path: Path) -> None:
        self._module_path = module_path

    def as_posix(self) -> str:
        return "loopx/doctor.py"

    def locate(self) -> Path:
        return self._module_path


class _FakeDistribution:
    version = "0.4.8"

    def __init__(self, module_path: Path, root: Path) -> None:
        self.files = [_FakeDistributionFile(module_path)]
        self._root = root

    def read_text(self, name: str) -> str:
        assert name == "INSTALLER"
        return "pip"

    def locate_file(self, _name: str) -> Path:
        return self._root


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(root: Path, text: str) -> str:
    (root / "fixture.txt").write_text(text, encoding="utf-8")
    _git(root, "add", "fixture.txt")
    _git(root, "commit", "-m", text)
    return _git(root, "rev-parse", "HEAD")


def _write_required_skills(root: Path) -> None:
    for skill_name, phrases in REQUIRED_INSTALLED_SKILL_PHRASES.items():
        skill_path = root / skill_name / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text("\n".join(phrases) + "\n", encoding="utf-8")


def _freshness(
    tmp_path: Path,
    *,
    installed_commit: str,
    comparison_commit: str,
    revision_relation: str,
    freshness_commit: str | None = None,
    freshness_relation: str | None = None,
    source_ref: str | None = None,
) -> dict[str, object]:
    return build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=tmp_path / "releases" / "20260713T030000Z",
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
        release_manifest={
            "available": True,
            "manifest": {
                "package": {"version": __version__},
                "source": {
                    "git_commit": installed_commit,
                    "ref": source_ref,
                },
            },
        },
        comparison_source={
            "label": "loopx-canary",
            "root": str(tmp_path),
            "git_commit": comparison_commit,
            "revision_relation": revision_relation,
        },
        freshness_source=(
            {
                "label": "loopx/loopx@main",
                "root": str(tmp_path),
                "git_commit": freshness_commit,
                "git_ref": "origin/main",
                "revision_relation": freshness_relation,
            }
            if freshness_commit
            else None
        ),
        now=datetime(2026, 7, 13, 4, tzinfo=timezone.utc),
    )


def test_older_canary_does_not_stale_newer_default_release(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "loopx@example.invalid")
    _git(tmp_path, "config", "user.name", "LoopX Test")
    older = _commit(tmp_path, "older")
    newer = _commit(tmp_path, "newer")

    relation = git_revision_relation(
        tmp_path,
        installed_commit=newer,
        comparison_commit=older,
    )
    freshness = _freshness(
        tmp_path,
        installed_commit=newer,
        comparison_commit=older,
        revision_relation=relation,
        freshness_commit=newer,
        freshness_relation="same",
    )

    assert relation == "installed_ahead"
    assert freshness["status"] == "fresh"
    assert freshness["requires_upgrade"] is False
    assert freshness["manifest_source_matches_comparison"] is False
    assert freshness["manifest_source_comparison_relation"] == "installed_ahead"


def test_newer_canary_does_not_stale_current_default_release(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "loopx@example.invalid")
    _git(tmp_path, "config", "user.name", "LoopX Test")
    older = _commit(tmp_path, "older")
    newer = _commit(tmp_path, "newer")

    relation = git_revision_relation(
        tmp_path,
        installed_commit=older,
        comparison_commit=newer,
    )
    freshness = _freshness(
        tmp_path,
        installed_commit=older,
        comparison_commit=newer,
        revision_relation=relation,
        freshness_commit=older,
        freshness_relation="same",
    )

    assert relation == "installed_behind"
    assert freshness["status"] == "fresh"
    assert freshness["requires_upgrade"] is False
    assert freshness["manifest_source_comparison_relation"] == "installed_behind"
    assert freshness["manifest_source_freshness_relation"] == "same"


def test_trusted_main_ref_stales_older_default_release(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "loopx@example.invalid")
    _git(tmp_path, "config", "user.name", "LoopX Test")
    older = _commit(tmp_path, "older")
    newer = _commit(tmp_path, "newer")

    freshness = _freshness(
        tmp_path,
        installed_commit=older,
        comparison_commit=newer,
        revision_relation="diverged",
        freshness_commit=newer,
        freshness_relation="installed_behind",
    )

    assert freshness["status"] == "stale"
    assert freshness["requires_upgrade"] is True
    assert "is behind loopx/loopx@main" in str(freshness["reason"])


def test_unclassified_install_advertises_the_two_paths(tmp_path: Path) -> None:
    """A snapshot-style install (no distribution, no checkout) gets the two-path hint.

    The archive/canary upgrade channel was removed in operation log 036, so nothing
    may name a hosted installer or a package index any more.
    """

    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
    )

    assert "no_clone_upgrade_command" not in freshness
    command = str(freshness["upgrade_command"])
    # The advice describes the install that is running: either the in-place
    # editable refresh or the two-path hint. Neither may name a retired channel.
    assert "pip install -e ." in command or "editable checkout" in command, command
    for forbidden in (
        "huangruiteng",
        "install.sh",
        "codeload",
        "pip install --upgrade loopx",
        "pipx upgrade",
        "scripts/install-local.sh",
    ):
        assert forbidden not in command, (forbidden, command)


def test_unknown_canary_relation_does_not_stale_current_default_release(
    tmp_path: Path,
) -> None:
    current = "a" * 40
    freshness = _freshness(
        tmp_path,
        installed_commit=current,
        comparison_commit="b" * 40,
        revision_relation="unknown",
        freshness_commit=current,
        freshness_relation="same",
    )

    assert freshness["status"] == "fresh"
    assert freshness["requires_upgrade"] is False
    assert freshness["manifest_source_comparison_relation"] == "unknown"
    assert freshness["manifest_source_freshness_relation"] == "same"


def test_other_agent_freshness_does_not_require_codex_skill_directory(
    tmp_path: Path,
) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={
            "loopx-project": {
                "exists": False,
                "required_phrases": False,
            }
        },
        require_installed_skills=False,
        doctor_agent_type="other-agent",
    )

    assert freshness["status"] == "live_checkout"
    assert freshness["requires_upgrade"] is False
    assert freshness["installed_skills_required"] is False
    assert freshness["doctor_after_upgrade"] == "loopx doctor --agent-type other-agent"
    assert str(freshness["upgrade_command"]).endswith("loopx doctor --agent-type other-agent")


def test_external_agents_skill_root_is_accepted_without_copying(tmp_path: Path) -> None:
    codex_skills = tmp_path / ".codex" / "skills"
    agents_skills = tmp_path / ".agents" / "skills"
    _write_required_skills(agents_skills)

    skills = installed_skill_summary((codex_skills, agents_skills))
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills=skills,
    )

    assert all(skill["exists"] for skill in skills.values())
    assert all(skill["required_phrases"] for skill in skills.values())
    assert all(skill["managed_externally"] for skill in skills.values())
    assert all(skill["route_count"] == 1 for skill in skills.values())
    assert freshness["status"] == "live_checkout"
    assert freshness["externally_managed_skills"] is True
    # Externally managed skills are not re-delivered by the refresh command.
    assert "workflow-skills --install" not in str(freshness["upgrade_command"])
    assert "workflow-skills --install" not in str(freshness["contributor_upgrade_command"])


def test_duplicate_skill_routes_fail_closed(tmp_path: Path) -> None:
    codex_skills = tmp_path / ".codex" / "skills"
    agents_skills = tmp_path / ".agents" / "skills"
    _write_required_skills(codex_skills)
    _write_required_skills(agents_skills)

    skills = installed_skill_summary((codex_skills, agents_skills))
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills=skills,
    )

    assert all(skill["route_conflict"] for skill in skills.values())
    assert all(skill["route_count"] == 2 for skill in skills.values())
    assert all(not skill["required_phrases"] for skill in skills.values())
    assert freshness["status"] == "repair_recommended"
    assert freshness["externally_managed_skills"] is False


def test_python_distribution_without_a_recorded_wheel_gets_the_hint(
    tmp_path: Path,
) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={
            "loopx-project": {
                "exists": True,
                "required_phrases": True,
            }
        },
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "0.4.8",
            "installer": "pip",
        },
    )

    assert freshness["status"] == "python_distribution"
    assert freshness["requires_upgrade"] is False
    assert freshness["install_kind"] == "python_distribution"
    assert freshness["python_distribution_version"] == "0.4.8"
    # No recorded wheel and no index channel: the hint names the two paths.
    assert "editable checkout" in str(freshness["upgrade_command"])
    assert "install.sh" not in str(freshness["upgrade_command"])


def test_local_wheel_distribution_reinstalls_the_recorded_wheel(tmp_path: Path) -> None:
    wheel = "/tmp/dist/loopx-1.1.0-py3-none-any.whl"
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "1.1.0",
            "installer": "pip",
            "install_path": "local_wheel",
            "wheel_path": wheel,
        },
    )

    assert freshness["install_path"] == "local_wheel"
    assert freshness["wheel_path"] == wheel
    command = str(freshness["upgrade_command"])
    assert f"--force-reinstall --no-deps {wheel}" in command, command
    assert command.endswith("loopx doctor"), command


def test_pipx_distribution_preserves_the_pipx_owner(tmp_path: Path) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={
            "loopx-project": {
                "exists": True,
                "required_phrases": True,
            }
        },
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "0.4.8",
            "installer": "pipx",
            "installer_environment": "loopx-preview",
        },
    )

    assert freshness["python_distribution_installer"] == "pipx"
    assert freshness["python_distribution_installer_environment"] == "loopx-preview"
    # pipx is the tool for the same wheel path, not a separate channel; without a
    # recorded wheel the advice is the two-path hint, never `pipx upgrade`.
    assert "pipx upgrade" not in str(freshness["upgrade_command"])
    wheel_freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "1.1.0",
            "installer": "pipx",
            "installer_environment": "loopx-preview",
            "install_path": "local_wheel",
            "wheel_path": "/tmp/dist/loopx-1.1.0-py3-none-any.whl",
        },
    )
    assert str(wheel_freshness["upgrade_command"]).startswith(
        "pipx install --force /tmp/dist/loopx-1.1.0-py3-none-any.whl\n"
    )
    assert "python -m pip" not in str(wheel_freshness["upgrade_command"])


def test_unknown_distribution_installer_gets_no_index_command(tmp_path: Path) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "0.4.8",
            "installer": "custom-manager",
        },
    )

    assert freshness["python_distribution_installer"] == "custom-manager"
    command = str(freshness["upgrade_command"])
    assert "custom-manager" not in command
    assert "pip install --upgrade loopx" not in command
    assert "editable checkout" in command


def test_editable_checkout_never_recommends_release_channels(tmp_path: Path) -> None:
    """A git checkout develops in place; install-local.sh would take over `loopx`."""

    (tmp_path / ".git").mkdir()

    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
    )

    assert freshness["status"] == "live_checkout"
    for field in ("upgrade_command", "contributor_upgrade_command"):
        command = str(freshness[field])
        assert "pip install -e . --no-deps" in command, command
        if importlib.util.find_spec("setuptools") is not None:
            # Only asked for when the running interpreter can satisfy it.
            assert "--no-build-isolation" in command, command
        assert command.endswith("loopx doctor"), command
        for forbidden in (
            "scripts/install-local.sh",
            "huangruiteng.github.io/loopx/install.sh",
            "pip install --upgrade loopx",
        ):
            assert forbidden not in command, (field, forbidden, command)


def test_editable_refresh_keeps_working_without_a_build_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fresh 3.12 virtualenv has no setuptools; --no-build-isolation would fail there."""

    from loopx import python_install_owner

    class _NoBuildBackend:
        @staticmethod
        def find_spec(name: str) -> None:
            return None

    monkeypatch.setattr(python_install_owner.importlib, "util", _NoBuildBackend)

    assert python_install_owner._editable_install_arguments() == (
        "install",
        "-e",
        ".",
        "--no-deps",
    )
    command = python_install_owner.editable_dev_refresh_command(Path("/tmp/checkout"))
    assert "-m pip install -e . --no-deps" in command, command
    assert "--no-build-isolation" not in command, command


def test_release_snapshot_no_longer_advertises_a_channel(tmp_path: Path) -> None:
    """Release snapshots and their channels were removed (operation log 036)."""

    release_root = tmp_path / "releases" / "20260101T000000Z"
    release_root.mkdir(parents=True)

    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=release_root,
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
    )

    for field in ("upgrade_command", "contributor_upgrade_command"):
        command = str(freshness[field])
        assert "scripts/install-local.sh" not in command, command
        assert "huangruiteng" not in command, command
        assert "install.sh" not in command, command


def test_source_tree_egg_info_is_not_a_managed_distribution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A stale `.egg-info` in a checkout must not pass as an installed distribution.

    ``importlib.metadata`` finds it whenever the checkout is on ``sys.path``
    (running ``python3 -m loopx.cli`` from the repo root), which used to make an
    editable checkout report ``install_kind: python_distribution``.
    """

    checkout = tmp_path / "nano-loopx"
    module_path = checkout / "loopx" / "doctor.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text("# fixture\n", encoding="utf-8")
    (checkout / "pyproject.toml").write_text(
        "[project]\nname = \"loopx\"\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        "loopx.doctor.distribution",
        lambda _name: _FakeDistribution(module_path, checkout),
    )

    assert python_distribution_install(module_path) == {"available": False}


def test_python_distribution_detects_pipx_metadata_owner(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    venv = tmp_path / "venvs" / "loopx-preview"
    module_path = venv / "lib" / "python" / "site-packages" / "loopx" / "doctor.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text("# fixture\n", encoding="utf-8")
    (venv / "pipx_metadata.json").write_text(
        '{"pipx_metadata_version":"0.12","environment":"loopx-preview"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "loopx.doctor.distribution",
        lambda _name: _FakeDistribution(module_path, module_path.parents[2]),
    )
    monkeypatch.setattr("loopx.doctor.sys.prefix", str(venv))

    installed = python_distribution_install(module_path)

    assert installed["available"] is True
    assert installed["installer"] == "pipx"
    assert installed["installer_environment"] == "loopx-preview"


def test_python_distribution_ignores_archive_manifest_version(tmp_path: Path) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "bin" / "loopx",
        release_root=tmp_path / "releases" / "20260713T030000Z",
        repo_root=tmp_path,
        skills={"loopx-project": {"exists": True, "required_phrases": True}},
        release_manifest={
            "available": True,
            "manifest": {
                "package": {"version": "0.4.7"},
                "source": {"git_commit": "a" * 40},
            },
        },
        freshness_source={
            "label": "loopx/loopx@main",
            "git_commit": "b" * 40,
            "revision_relation": "installed_behind",
        },
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "0.4.8",
            "installer": "pip",
        },
        now=datetime(2026, 7, 13, 4, tzinfo=timezone.utc),
    )

    assert freshness["status"] == "python_distribution"
    assert freshness["requires_upgrade"] is False
    assert freshness["manifest_package_version_matches_runtime"] is False


@pytest.mark.parametrize("filename", ["loopx", "loopx.exe"])
def test_current_python_console_script_is_recognized(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
) -> None:
    console_script = tmp_path / "venv" / "bin" / filename
    console_script.parent.mkdir(parents=True)
    console_script.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr("loopx.doctor.sys.argv", [str(console_script), "doctor"])

    assert current_script_invocation_path() == console_script.resolve()


def test_python_distribution_missing_skills_recommends_repair(tmp_path: Path) -> None:
    freshness = build_install_freshness(
        command_path=tmp_path / "loopx",
        release_root=None,
        repo_root=tmp_path,
        skills={
            "loopx-project": {
                "exists": False,
                "required_phrases": False,
            }
        },
        python_distribution={
            "available": True,
            "kind": "python_distribution",
            "version": "0.4.8",
            "installer": "pip",
        },
    )

    assert freshness["status"] == "repair_recommended"
    assert freshness["requires_upgrade"] is True
    repair = str(freshness["upgrade_command"])
    assert "editable checkout" in repair, repair
    assert "wheel" in repair, repair
    assert "pip install --upgrade loopx" not in repair, repair


def test_trusted_release_ref_matches_manifest_repository(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "loopx@example.invalid")
    _git(tmp_path, "config", "user.name", "LoopX Test")
    commit = _commit(tmp_path, "main")
    _git(tmp_path, "remote", "add", "origin", "git@github.com:loopx/loopx.git")
    _git(tmp_path, "update-ref", "refs/remotes/origin/main", commit)

    trusted = trusted_release_ref_for_root(
        tmp_path,
        repository="loopx/loopx",
        ref="main",
    )

    assert trusted is not None
    assert trusted["git_commit"] == commit
    assert trusted["git_ref"] == "origin/main"
    assert (
        trusted_release_ref_for_root(
            tmp_path,
            repository="someone-else/loopx",
            ref="main",
        )
        is None
    )
