#!/usr/bin/env python3
"""Guard `loopx update` in the two-path world, without touching the network.

Two shapes are covered in-process (a local wheel install, in both pip and pipx
flavours) and the rest through the real CLI: this checkout must report itself as
an editable install whose update is a manual in-place refresh, `apply` must refuse
that, and the retired release-snapshot/archive flags must no longer exist.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from loopx.self_update import build_update_plan


REPO_ROOT = Path(__file__).resolve().parents[1]
WHEEL = "/tmp/dist/loopx-1.1.0-py3-none-any.whl"
FORBIDDEN_FRAGMENTS = (
    "huangruiteng",
    "install.sh",
    "github.io",
    "codeload",
    "pip install --upgrade loopx",
    "pipx upgrade",
    "install-local.sh",
)


def doctor_payload(
    *,
    install_path: str | None,
    installer: str = "pip",
    wheel: str | None = WHEEL,
) -> dict[str, object]:
    return {
        "path": {"loopx": str(REPO_ROOT / "scripts" / "loopx")},
        "package": {"install_kind": "python_distribution"},
        "install_freshness": {
            "status": "python_distribution",
            "requires_upgrade": False,
            "install_kind": "python_distribution",
            "install_path": install_path,
            "wheel_path": wheel,
            "python_distribution_installer": installer,
            "upgrade_command": (
                f"{sys.executable} -m pip install --force-reinstall --no-deps {WHEEL}"
                "\nloopx workflow-skills --install\nloopx doctor"
            ),
        },
    }


def assert_no_retired_fragments(rendered: str, label: str) -> None:
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in rendered, (label, fragment)


def assert_in_process_plans() -> None:
    wheel_plan = build_update_plan(
        action="plan",
        doctor_payload=doctor_payload(install_path="local_wheel"),
    )
    lifecycle = wheel_plan["install_lifecycle"]
    assert lifecycle["owner"] == "local_wheel_install", lifecycle
    assert lifecycle["execution_driver"] == "python_pip", lifecycle
    assert wheel_plan["plan"]["apply_supported"] is True, wheel_plan
    assert wheel_plan["commands"]["apply"] == "loopx update apply", wheel_plan

    pipx_plan = build_update_plan(
        action="plan",
        doctor_payload=doctor_payload(install_path="local_wheel", installer="pipx"),
    )
    assert pipx_plan["install_lifecycle"]["execution_driver"] == "python_pipx", pipx_plan

    checkout_plan = build_update_plan(
        action="apply",
        doctor_payload=doctor_payload(install_path="editable_checkout", wheel=None),
    )
    assert checkout_plan["ok"] is False, checkout_plan
    assert checkout_plan["install_lifecycle"]["owner"] == "source_checkout", checkout_plan
    assert checkout_plan["commands"]["apply"] is None, checkout_plan

    index_plan = build_update_plan(
        action="apply",
        doctor_payload=doctor_payload(install_path="index_install", wheel=None),
    )
    assert index_plan["install_lifecycle"]["owner"] == "unsupported_index_install", index_plan
    assert "does not publish to a package index" in index_plan["recommended_action"], index_plan

    unknown_plan = build_update_plan(
        action="plan",
        doctor_payload=doctor_payload(install_path=None, wheel=None),
    )
    assert unknown_plan["install_lifecycle"]["owner"] == "unknown_install", unknown_plan

    for label, payload in (
        ("wheel", wheel_plan),
        ("pipx", pipx_plan),
        ("checkout", checkout_plan),
        ("index", index_plan),
        ("unknown", unknown_plan),
    ):
        assert_no_retired_fragments(json.dumps(payload), label)


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "loopx.cli", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_cli_surfaces() -> None:
    plan = run_cli("update", "plan", "--format", "json")
    assert plan.returncode == 0, (plan.stdout, plan.stderr)
    payload = json.loads(plan.stdout)
    lifecycle = payload["install_lifecycle"]
    assert lifecycle["owner"] == "source_checkout", lifecycle
    assert payload["plan"]["apply_supported"] is False, payload
    assert payload["commands"]["apply"] is None, payload
    assert_no_retired_fragments(plan.stdout + plan.stderr, "cli plan")

    check = run_cli("update", "check", "--format", "json")
    assert check.returncode == 0, (check.stdout, check.stderr)
    assert json.loads(check.stdout)["requested_action"] == "check"
    assert_no_retired_fragments(check.stdout + check.stderr, "cli check")

    apply = run_cli("update", "apply", "--format", "json")
    assert apply.returncode == 1, (apply.stdout, apply.stderr)
    applied = json.loads(apply.stdout)
    assert applied["ok"] is False, applied
    assert applied["changes_applied"] is False, applied
    assert "cannot mutate an installation owned by" in applied["error"], applied

    markdown = run_cli("update", "plan")
    assert markdown.returncode == 0, (markdown.stdout, markdown.stderr)
    assert "## Next Action" in markdown.stdout, markdown.stdout
    assert_no_retired_fragments(markdown.stdout, "cli markdown")

    # The release-snapshot/archive channel is gone: neither the flags nor the
    # commands they drove may survive.
    help_text = run_cli("update", "--help")
    assert help_text.returncode == 0, (help_text.stdout, help_text.stderr)
    for retired_flag in (
        "--rollback",
        "--repo",
        "--ref",
        "--archive-url",
        "--installed-doctor-json",
    ):
        assert retired_flag not in help_text.stdout, retired_flag
    retired = run_cli("update", "--rollback", "previous")
    assert retired.returncode != 0, (retired.stdout, retired.stderr)


def main() -> int:
    assert_in_process_plans()
    assert_cli_surfaces()
    print("loopx-update-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
