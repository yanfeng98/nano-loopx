"""Retired host routes fail without mutating an existing goal."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from loopx.host_loop_activation import (
    AgentTypeError,
    agent_type_for_host_surface,
    build_host_loop_activation_packet,
    normalize_agent_type,
)
from loopx.registry import find_registry_goal, read_json


@pytest.mark.parametrize(
    "alias",
    ["traex-cli", "traex_cli", "TraeX CLI", "traex", "traex-cli-tui",
     "traex tui", "trae-cli", "trae_cli", "trae cli"],
)
def test_retired_host_alias_cannot_activate(alias: str) -> None:
    for resolve in (normalize_agent_type, agent_type_for_host_surface):
        with pytest.raises(AgentTypeError, match="unsupported"):
            resolve(alias)
    with pytest.raises(AgentTypeError, match="unsupported"):
        build_host_loop_activation_packet(agent_type=alias, goal_id="historical-goal")


@pytest.mark.parametrize(
    "args",
    [
        ["agent-onboard", "--agent-type", "traex-cli", "--project", "."],
        ["heartbeat-prompt", "--goal-id", "historical-goal",
         "--runtime-profile", "generic_cli", "--visible-goal-host", "traex-cli"],
        ["benchmark", "traex-evidence", "--source-jsonl", "evidence.jsonl",
         "--atif-output", "trajectory.json", "--route-receipt-output", "route.json",
         "--requested-model", "fixture-model", "--execute"],
    ],
)
def test_retired_cli_rejects_without_changing_historical_state(
    tmp_path: Path, args: list[str],
) -> None:
    root = Path(__file__).resolve().parents[1]
    registry_path = tmp_path / "registry.json"
    goal = {
        "id": "historical-goal", "status": "active", "repo": str(tmp_path),
        "host_surface": "traex-cli", "state_file": "ACTIVE_GOAL_STATE.md",
        "coordination": {"agent_model": "peer_v1", "registered_agents": ["traex-worker"]},
    }
    registry_path.write_text(json.dumps({"goals": [goal]}), encoding="utf-8")
    (tmp_path / "ACTIVE_GOAL_STATE.md").write_text("# Historical goal\n", encoding="utf-8")
    (tmp_path / "evidence.jsonl").write_text('{}\n', encoding="utf-8")
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    completed = subprocess.run(
        [sys.executable, "-m", "loopx.cli", "--registry", str(registry_path), *args],
        cwd=tmp_path,
        env={**os.environ, "HOME": str(tmp_path), "PYTHONPATH": str(root),
             "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=30, check=False,
    )
    assert completed.returncode != 0
    assert "unsupported" in completed.stdout + completed.stderr or (
        "unrecognized arguments" in completed.stderr or "invalid choice" in completed.stderr
    )
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    assert find_registry_goal(read_json(registry_path), "historical-goal") == goal
