#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from loopx import __version__  # noqa: E402
from loopx.cli import build_parser  # noqa: E402
from loopx.help_surface import (  # noqa: E402
    COMMAND_GROUPS,
    MANPAGE_COMMAND_HELP_ONLY,
    manpage_top_level_commands,
    render_manpage,
)


LONG_TAIL_COMMAND = "codex-cli-visible-first-response-capture-plan"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "loopx.cli", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def assert_concise_default_help(output: str) -> None:
    assert "LoopX keeps long-running agent work moving" in output, output
    assert "Start here:" in output, output
    assert "/loopx <goal text>" in output, output
    assert "slash-commands --install" in output, output
    assert "ready-score --goal-id ID" in output, output
    assert "start-goal --guided" in output, output
    for command in ("loopx dashboard", "loopx chat"):
        assert any(
            line.startswith(f"  {command} ") for line in output.splitlines()
        ), f"missing command entry {command!r}:\n{output}"
    assert "Run the loop:" in output, output
    assert "Claude Code" in output, output
    assert "loopx commands" in output, output
    assert "evidence-log --goal-id ID --agent-id AGENT --thin" in output, output
    assert "man loopx" in output, output
    assert LONG_TAIL_COMMAND not in output, output
    assert len(output.splitlines()) <= 39, output


def assert_default_help_surface() -> None:
    bare = run_cli()
    assert bare.returncode == 0, (bare.returncode, bare.stdout, bare.stderr)
    assert_concise_default_help(bare.stdout)
    assert bare.stderr == "", bare.stderr

    top_help = run_cli("--help")
    assert top_help.returncode == 0, (top_help.returncode, top_help.stdout, top_help.stderr)
    assert_concise_default_help(top_help.stdout)
    assert top_help.stderr == "", top_help.stderr


def assert_command_reference_surface() -> None:
    result = run_cli("commands")
    assert result.returncode == 0, (result.returncode, result.stdout, result.stderr)
    assert "LoopX command reference" in result.stdout, result.stdout
    assert "Daily operator commands" in result.stdout, result.stdout
    assert "required evidence-log reads" in result.stdout, result.stdout
    assert "before replan or handoff" in result.stdout, result.stdout
    assert "Loop driver hints" in result.stdout, result.stdout
    assert "Claude Code /loop" in result.stdout, result.stdout
    assert "Maintainer and adapter commands" in result.stdout, result.stdout
    assert "loopx <command> --help" in result.stdout, result.stdout
    assert "codex-cli-bootstrap-message" in result.stdout, result.stdout
    assert "loopx ready-score --goal-id <goal-id>" in result.stdout, result.stdout
    assert "loopx chat --goal-id <goal-id>" in result.stdout, result.stdout
    assert result.stderr == "", result.stderr


def assert_top_level_commands_are_explicitly_classified() -> None:
    parser = build_parser()
    subparsers = next(
        action
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )
    parser_commands = frozenset(subparsers.choices)
    manual_commands = manpage_top_level_commands()
    assert manual_commands.isdisjoint(MANPAGE_COMMAND_HELP_ONLY)
    assert parser_commands == manual_commands | MANPAGE_COMMAND_HELP_ONLY, {
        "unclassified": sorted(
            parser_commands - manual_commands - MANPAGE_COMMAND_HELP_ONLY
        ),
        "stale_manual": sorted(manual_commands - parser_commands),
        "stale_help_only": sorted(MANPAGE_COMMAND_HELP_ONLY - parser_commands),
    }


def assert_extension_capabilities_stay_out_of_core_manual() -> None:
    manifest_paths = sorted(REPO_ROOT.glob("loopx/extensions/**/extension.toml"))
    manifest_paths.extend(sorted(REPO_ROOT.glob("packages/**/extension.toml")))
    extension_owned_ids: set[str] = set()
    for path in manifest_paths:
        manifest = tomllib.loads(path.read_text(encoding="utf-8"))
        extension_id = manifest.get("id")
        if isinstance(extension_id, str):
            extension_owned_ids.add(extension_id)
        for capability in manifest.get("provides", []):
            capability_id = capability.get("id")
            if isinstance(capability_id, str):
                extension_owned_ids.add(capability_id)

    # `[[implements]]` ids are intentionally excluded: they name core-owned
    # capability contracts whose stable core command may belong in the manual.
    manual_commands = manpage_top_level_commands()
    assert extension_owned_ids.isdisjoint(manual_commands), {
        "extension_owned_manual_commands": sorted(
            extension_owned_ids & manual_commands
        )
    }
    man_text = render_manpage()
    for extension_owned_id in extension_owned_ids:
        escaped_id = extension_owned_id.replace("-", r"\-")
        assert rf"\fBloopx {escaped_id}\fR" not in man_text, extension_owned_id


def assert_checked_in_manpage_surface() -> None:
    manpage = REPO_ROOT / "man" / "loopx.1"
    assert manpage.read_text(encoding="utf-8") == render_manpage()


def assert_catalog_is_present(man_text: str) -> None:
    assert f'"LoopX {__version__}"' in man_text, man_text
    for group in COMMAND_GROUPS:
        for entry in group["commands"]:
            command = str(entry["command"])
            purpose = str(entry["purpose"])
            assert command.replace("-", r"\-") in man_text, command
            assert purpose.replace("-", r"\-") in man_text, purpose



def main() -> int:
    assert_default_help_surface()
    assert_command_reference_surface()
    assert_top_level_commands_are_explicitly_classified()
    assert_extension_capabilities_stay_out_of_core_manual()
    assert_checked_in_manpage_surface()
    print("cli-help-manpage-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
