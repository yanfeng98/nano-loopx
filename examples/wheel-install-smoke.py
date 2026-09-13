#!/usr/bin/env python3
"""Verify the local-wheel install path end to end, offline.

Builds the wheel with the shipped ``scripts/build-wheel.sh``, installs it into a
throwaway virtualenv with an isolated HOME/CODEX_HOME, and then checks that the
installed distribution is complete and self-describing:

- the wheel carries the assets a wheel install needs (control-plane ``.ts``,
  canary baseline JSON, claude_goal_mode plugin assets, host skills, and the two
  project-scoped skills with their scope markers);
- pip records the file origin in ``direct_url.json`` (the signal the CLI uses to
  tell a local wheel apart from an index install);
- ``loopx doctor`` reports a managed Python distribution;
- ``loopx workflow-skills --install`` can deliver skills from the install;
- ``release_candidate.collect_python_distribution_checks`` accepts the install.

Side effect: like the shipped script, this rebuilds ``build/`` and writes the
wheel into a temporary directory (the build directory is gitignored).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-wheel.sh"


def read_version() -> str:
    text = (REPO_ROOT / "loopx" / "__init__.py").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("__version__"):
            return line.split("=", 1)[1].strip().strip('"')
    raise AssertionError("loopx/__init__.py has no __version__")


def run(
    args: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd or REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def assert_wheel_payload(wheel: Path) -> None:
    names = zipfile.ZipFile(wheel).namelist()
    required = (
        "loopx/canary/module_metric_baseline.json",
        "loopx/claude_goal_mode/.claude-plugin/plugin.json",
        "loopx/claude_goal_mode/hooks/hooks.json",
        "loopx/web/chat/manifest.webmanifest",
        "share/loopx/skills/loopx-project/SKILL.md",
        "share/loopx/skills/loopx-material/SKILL.md",
        "share/loopx/skills/loopx-material/.loopx-skill-scope",
        "share/loopx/skills/loopx-change-quality/SKILL.md",
        "share/loopx/skills/loopx-change-quality/.loopx-skill-scope",
    )
    for entry in required:
        assert any(name.endswith(entry) for name in names), entry

    repo_typescript = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "loopx").rglob("*.ts")
    }
    wheel_typescript = {name for name in names if name.endswith(".ts")}
    missing = sorted(repo_typescript - wheel_typescript)
    assert not missing, f"wheel is missing control-plane sources: {missing[:5]}"
    print(f"wheel payload ok: {len(names)} entries, {len(wheel_typescript)} .ts files")


def main() -> int:
    version = read_version()
    with tempfile.TemporaryDirectory(prefix="loopx-wheel-smoke-") as tmp:
        root = Path(tmp)
        wheel_dir = root / "wheelhouse"
        env = {**os.environ, "PYTHON": sys.executable}
        run(
            ["bash", str(BUILD_SCRIPT), "--out-dir", str(wheel_dir)],
            env=env,
        )
        wheel = wheel_dir / f"loopx-{version}-py3-none-any.whl"
        assert wheel.is_file(), wheel
        assert_wheel_payload(wheel)

        environment = root / "venv"
        venv.EnvBuilder(with_pip=True, symlinks=True).create(environment)
        bin_dir = environment / "bin"
        python = bin_dir / "python"
        run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)])
        purelib = Path(
            run(
                [
                    str(python),
                    "-c",
                    "import sysconfig; print(sysconfig.get_paths()['purelib'])",
                ]
            ).stdout.strip()
        )

        direct_url = json.loads(
            next(purelib.glob("loopx-*.dist-info/direct_url.json")).read_text(
                encoding="utf-8"
            )
        )
        assert direct_url["url"].endswith(".whl"), direct_url
        assert "archive_info" in direct_url, direct_url
        assert not direct_url.get("dir_info", {}).get("editable"), direct_url
        print(f"direct_url.json ok: {direct_url['url'].rsplit('/', 1)[-1]}")

        home = root / "home"
        (home / ".codex").mkdir(parents=True)
        venv_env = {
            **os.environ,
            "HOME": str(home),
            "CODEX_HOME": str(home / ".codex"),
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
        }
        # A wheel ships .ts sources but never Node itself.
        assert shutil.which("node", path=venv_env["PATH"]), "node is required"

        doctor = run([str(bin_dir / "loopx"), "doctor", "--format", "json"], env=venv_env)
        payload = json.loads(doctor.stdout)
        freshness = payload["install_freshness"]
        assert freshness["install_kind"] == "python_distribution", freshness
        print(f"doctor install_kind ok: {freshness['install_kind']}")

        # The two-path vocabulary: a local wheel is reported as such, and the
        # upgrade advice points back at the wheel file instead of an index.
        assert freshness["install_path"] == "local_wheel", freshness
        assert str(freshness["wheel_path"]).endswith(".whl"), freshness
        upgrade = str(freshness["upgrade_command"])
        assert "--force-reinstall" in upgrade, upgrade
        assert freshness["wheel_path"] in upgrade, upgrade
        for forbidden in ("huangruiteng", "install.sh", "github.io", "pip install --upgrade loopx"):
            assert forbidden not in upgrade, upgrade
        print(f"doctor install_path ok: {freshness['install_path']} -> {freshness['wheel_path']}")

        run([str(bin_dir / "loopx"), "workflow-skills", "--install"], env=venv_env)
        installed_skill = home / ".codex" / "skills" / "loopx-project" / "SKILL.md"
        assert installed_skill.is_file(), installed_skill
        print("workflow-skills --install ok")

        # These run inside the venv, so keep cwd away from the checkout: a cwd holding
        # `loopx/` or `loopx.egg-info` shadows the venv's own package and metadata
        # (see docs/development/editable-dev-loop.md, cwd shadowing).
        baseline = run(
            [
                str(python),
                "-c",
                "from loopx.canary.maintainability_ratchet import "
                "MODULE_METRIC_BASELINE_PATH as p; print(p.is_file())",
            ],
            env=venv_env,
            cwd=root,
        )
        assert baseline.stdout.strip() == "True", baseline.stdout
        print("canary maintainability baseline ok")

        checks = run(
            [
                str(python),
                "-c",
                "import json, pathlib;"
                "from loopx.release_candidate import collect_python_distribution_checks as c;"
                f"print(json.dumps(c(command_path=pathlib.Path({str(bin_dir / 'loopx')!r}),"
                f" package_root=pathlib.Path({str(purelib)!r}))))",
            ],
            env=venv_env,
            cwd=root,
        )
        distribution_checks = json.loads(checks.stdout)
        assert distribution_checks["ok"] is True, distribution_checks
        print("collect_python_distribution_checks ok")

    print("wheel-install-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
