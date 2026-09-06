from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

def _project_metadata(path: str) -> dict[str, object]:
    data = tomllib.loads((ROOT / path).read_text(encoding="utf-8"))
    project = data.get("project")
    assert isinstance(project, dict)
    return project


def test_root_license_is_canonical_apache_2_with_historical_notices() -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Apache 许可证" in license_text

    historical_mit = (ROOT / "LICENSE-MIT").read_text(encoding="utf-8")
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    assert historical_mit.startswith("MIT 许可证\n\nCopyright (c) 2026 LoopX contributors")
    assert "v0.4.7 的发布版本均按 MIT 许可证分发" in notice


def test_python_distributions_declare_apache_2() -> None:
    root_project = _project_metadata("pyproject.toml")
    assert root_project["license"] == "Apache-2.0"
    assert set(root_project["license-files"]) == {"LICENSE", "NOTICE", "LICENSE-MIT"}

    extension_project = _project_metadata(
        "packages/loopx-finance-value-discovery/pyproject.toml"
    )
    assert extension_project["license"] == "Apache-2.0"


def test_npm_workspace_metadata_declares_apache_2() -> None:
    for package_dir in ("apps/presentation/site", "apps/presentation/dashboard"):
        manifest = json.loads((ROOT / package_dir / "package.json").read_text())
        lock = json.loads((ROOT / package_dir / "package-lock.json").read_text())
        assert manifest["license"] == "Apache-2.0"
        assert lock["packages"][""]["license"] == "Apache-2.0"


def test_public_docs_state_the_versioned_transition() -> None:
    licensing = (ROOT / "docs/project/licensing.md").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "自 `v0.4.8` 起" in licensing
    assert "`v0.4.7`" in licensing
    assert "git commit -s" in contributing
    assert (ROOT / "DCO").read_text(encoding="utf-8").startswith(
        "开发者原创证明（Developer Certificate of Origin）"
    )
