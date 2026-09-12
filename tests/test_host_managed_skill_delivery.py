from __future__ import annotations

import json
import shutil
from pathlib import Path

from loopx.agent_onboarding import REQUIRED_HOST_SKILL_IDS
from loopx.skill_install_readback import (
    PACKAGED_HOST_SKILL_IDS,
    SKILL_INSTALL_READBACK_FILENAME,
    inspect_skill_install_readback,
    retire_duplicate_managed_skills,
    write_skill_install_readback,
)
from loopx.slash_command_install import materialize_loopx_entry_skill

REPO_ROOT = Path(__file__).resolve().parents[1]


def _materialize_workflow_skills(skills_dir: Path) -> None:
    for skill_id in PACKAGED_HOST_SKILL_IDS:
        shutil.copytree(REPO_ROOT / "skills" / skill_id, skills_dir / skill_id)
    entry = materialize_loopx_entry_skill(
        skills_dir=skills_dir,
        execute=True,
    )
    assert entry["status"] == "created"
    write_skill_install_readback(
        skills_dir=skills_dir,
        skill_ids=REQUIRED_HOST_SKILL_IDS,
        source_root=REPO_ROOT,
    )


def test_skill_readback_rejects_content_changed_after_install(tmp_path: Path) -> None:
    skills_dir = tmp_path / ".agents" / "skills"
    _materialize_workflow_skills(skills_dir)
    skill_path = skills_dir / REQUIRED_HOST_SKILL_IDS[0] / "SKILL.md"
    skill_path.write_text(
        skill_path.read_text(encoding="utf-8") + "\npost-install mutation\n",
        encoding="utf-8",
    )

    readback = inspect_skill_install_readback(
        skills_dir=skills_dir,
        required_skill_ids=REQUIRED_HOST_SKILL_IDS,
    )

    assert readback["ready"] is False
    assert readback["status"] == "skill_digest_mismatch"
    assert readback["digest_mismatches"] == [REQUIRED_HOST_SKILL_IDS[0]]


def test_skill_readback_rejects_a_different_cli_source_revision(
    tmp_path: Path,
) -> None:
    skills_dir = tmp_path / ".agents" / "skills"
    _materialize_workflow_skills(skills_dir)
    manifest_path = skills_dir / SKILL_INSTALL_READBACK_FILENAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["source"]["revision"] = "0" * 40
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    readback = inspect_skill_install_readback(
        skills_dir=skills_dir,
        required_skill_ids=REQUIRED_HOST_SKILL_IDS,
        source_root=REPO_ROOT,
    )

    assert readback["ready"] is False
    assert readback["status"] == "source_revision_mismatch"
    assert readback["source_revision_matches"] is False


def test_skill_readback_records_the_resolved_archive_revision(
    tmp_path: Path,
    monkeypatch,
) -> None:
    skills_dir = tmp_path / ".agents" / "skills"
    _materialize_workflow_skills(skills_dir)
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    resolved_commit = "a" * 40
    monkeypatch.setenv("LOOPX_RESOLVED_SOURCE_GIT_COMMIT", resolved_commit)
    write_skill_install_readback(
        skills_dir=skills_dir,
        skill_ids=REQUIRED_HOST_SKILL_IDS,
        source_root=archive_root,
    )
    (archive_root / "release.json").write_text(
        json.dumps({"source": {"git_commit": resolved_commit}}) + "\n",
        encoding="utf-8",
    )

    readback = inspect_skill_install_readback(
        skills_dir=skills_dir,
        required_skill_ids=REQUIRED_HOST_SKILL_IDS,
        source_root=archive_root,
    )

    assert readback["ready"] is True
    assert readback["source_revision"] == resolved_commit
    assert readback["source_revision_matches"] is True


def test_retire_duplicate_managed_skills_removes_only_loopx_managed_copies(
    tmp_path: Path,
) -> None:
    codex_skills = tmp_path / ".codex" / "skills"
    agents_skills = tmp_path / ".agents" / "skills"
    _materialize_workflow_skills(codex_skills)
    _materialize_workflow_skills(agents_skills)
    facade = agents_skills / "loopx-global-gates" / "SKILL.md"
    facade.parent.mkdir(parents=True)
    facade.write_text(
        "<!-- loopx-managed-slash-command:v1 command=/loopx-global-gates -->\n",
        encoding="utf-8",
    )
    user_file = agents_skills / "loopx-project" / "SKILL.md"
    user_file.write_text(
        user_file.read_text(encoding="utf-8") + "\nuser-edit\n",
        encoding="utf-8",
    )

    dry = retire_duplicate_managed_skills(
        codex_skills,
        alternate_root=agents_skills,
        execute=False,
    )
    assert dry["ok"] is True
    assert "loopx-global-gates" in dry["would_retire"]
    assert "loopx-project" in dry["skipped"]
    assert agents_skills.is_dir()

    applied = retire_duplicate_managed_skills(
        codex_skills,
        alternate_root=agents_skills,
        execute=True,
    )
    assert applied["ok"] is True
    assert "loopx-global-gates" in applied["retired"]
    assert not (agents_skills / "loopx-global-gates").exists()
    assert (agents_skills / "loopx-project").exists()
    assert (codex_skills / "loopx-project").exists()
