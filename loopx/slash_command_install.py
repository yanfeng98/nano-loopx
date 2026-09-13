from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .pi_goal_mode import extension_source as pi_extension_source
from .pi_goal_mode import runtime_source as pi_runtime_source
from .slash_command_files import (
    managed_marker as _managed_marker,
    retire_managed_file as _retire_managed_file,
    retire_status as _retire_status,
    skill_body as _skill_body,
    target_status as _target_status,
)
from .slash_commands import build_slash_command_catalog

SCHEMA_VERSION = "loopx_slash_command_install_v0"


def _openai_skill_metadata(*, command: str, display_name: str, short_description: str) -> str:
    return "\n".join(
        [
            f"# {_managed_marker(command=command, surface='codex-skill-metadata')}",
            "interface:",
            f'  display_name: "{display_name}"',
            f'  short_description: "{short_description}"',
            "policy:",
            "  allow_implicit_invocation: false",
            "",
        ]
    )


def _loopx_start_goal_arguments_instruction(
    *,
    cli_bin: str,
    host_surface: str | None,
) -> str:
    selected_host = host_surface or "<exact-current-host>"
    instruction = (
        "If arguments are present and the current host already has a verified "
        "active LoopX Goal/Agent binding, preserve that exact identity when the "
        "request continues, corrects, or refines the registered objective. Do "
        "not call `start-goal` for an ordinary phase, issue, PR, or Todo inside "
        "that Goal; follow its exact current `interaction_contract` or quota "
        "command first, then record the request through the typed Todo/writeback "
        "path for the bound agent. Start another Goal only for a materially "
        "different objective or an explicit new-Goal request. Otherwise pass "
        "the complete visible command arguments unchanged as one value to "
        f'`{cli_bin} start-goal --guided --project . --slash-command-arguments='
        f'"<complete visible $ARGUMENTS>" --host-surface {selected_host}`. '
        "The CLI, not the model, owns parsing supported leading switches and "
        "preserving the remaining goal text. Never split or recompose the "
        "arguments, and never infer a route from issue/PR wording or URLs."
    )
    if host_surface is None:
        instruction += (
            " If the host is unclear, omit the host flag once and follow the "
            "returned host-surface selection gate."
        )
    return instruction



def _command_prompt_specs(*, cli_bin: str, include_legacy_aliases: bool) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        {
            "command": "/loopx",
            "name": "loopx",
            "description": "Inspect LoopX state, or start concrete project work when arguments are provided.",
            "argument_hint": "[--fine-grained] [--capability-route issue-fix] [task text]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                "Identify the exact current host surface (codex-cli-tui, claude-code, pi, shell, or other-agent).",
                _loopx_start_goal_arguments_instruction(
                    cli_bin=cli_bin,
                    host_surface=None,
                ),
                "Treat the returned `ordered_steps` and `goal_start_contract` as authoritative. Follow their identity, capability-route, Todo, writeback, host-loop, quota, and stop/gate rules before substantive work; do not reconstruct those rules from skill memory.",
                "If the packet exposes a goal-selection gate, rerun one exact choice before any mutation.",
                "When authoring task Todos, treat `--action-kind` as the documented extensible public-safe token: choose a short task-relevant value such as `implement`, `test`, or `review`; do not search the LoopX source for an allowlist.",
                "Consume a turn-start quota JSON packet exactly once: read the complete output directly or save it and query it with `jq`; never pipe a turn-start call through `head` or `tail`, and never rerun a turn-start guard to recover hidden fields. When selection is required, choose the Todo and use `interaction_contract.cli_channel.selection_command` with the returned Turn identity before mutation.",
                f"If arguments are empty and the host already identifies an active LoopX goal, follow its exact CLI `interaction_contract` or quota command first; otherwise inspect `{cli_bin} status` and `{cli_bin} bootstrap-command-pack --project .` before changing files.",
                "If this session cannot mutate the host loop surface, surface the exact pasteable gate instead of claiming autonomous setup.",
            ],
        },
        {
            "command": "/loopx-global-summary",
            "name": "loopx-global-summary",
            "description": "Read the compact global LoopX progress digest.",
            "argument_hint": "[optional focus]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                f"Run `{cli_bin} global-summary` first and summarize visible projects, gates, monitor status, and next safe actions.",
                "This command is read-only unless the user explicitly asks for a state update.",
            ],
        },
        {
            "command": "/loopx-global-gates",
            "name": "loopx-global-gates",
            "description": "List open LoopX user/controller gates and what each blocks.",
            "argument_hint": "[optional focus]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                f"Run `{cli_bin} global-gates` first and summarize formal open gates, "
                "blocked todo or goal scope, owner routing, and exact next questions.",
                "This command is read-only unless the user explicitly asks for a state update.",
            ],
        },
        {
            "command": "/loopx-global-todos",
            "name": "loopx-global-todos",
            "description": "List runnable, blocked, deferred-ready, and review LoopX todos across visible projects.",
            "argument_hint": "[optional focus]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                f"Run `{cli_bin} global-todos` first and summarize prioritized ownership and structured readiness across visible projects without mutating state.",
                "This command is read-only unless the user explicitly asks for a state update.",
            ],
        },
        {
            "command": "/loopx-global-risks",
            "name": "loopx-global-risks",
            "description": "Show stale LoopX runs, boundary risks, failing checks, and rollback candidates.",
            "argument_hint": "[optional focus]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                f"Run `{cli_bin} global-risks` first and summarize structured stale runs, "
                "boundary warnings, failing checks, and whether a formally evidenced "
                "rollback candidate source is available, without mutating state.",
                "This command is read-only unless the user explicitly asks for a state update.",
            ],
        },
        {
            "command": "/loopx-pr-review",
            "name": "loopx-pr-review",
            "description": "Run the LoopX PR-review packet first, then review selected PR groups with evidence.",
            "argument_hint": "[--repo owner/repo] [--state open|merged|all] [--since ISO]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                "Use the installed `loopx-pr-review` skill when available.",
                f"Run `{cli_bin} --format json pr-review $ARGUMENTS` first and keep `agent_response_contract.review_execution_contract`, `review_groups`, `pull_requests[].review_plan`, `pull_requests[].review_template`, and `pull_requests[].evidence_commands` visible.",
                "Do not reconstruct the PR queue manually from ad hoc GitHub calls before reading the LoopX packet.",
                "This command is read-only; do not comment, approve, merge, rerun CI, or spend quota unless separately authorized.",
            ],
        },
        {
            "command": "/loopx-deepresearch",
            "name": "loopx-deepresearch",
            "description": "Run a bounded LoopX deep-research loop: packet-driven expeditions, evidence ledgers, citation-auditable report.",
            "argument_hint": "<research question> [--max-sources N]",
            "instructions": [
                "Visible command arguments: `$ARGUMENTS`.",
                f"Run `{cli_bin} --format json deepresearch status --project .` first; if no research is active, treat `$ARGUMENTS` as the question and run `{cli_bin} --format json deepresearch start --project . --question $ARGUMENTS`.",
                "Keep `research_contract`, `stop_conditions`, `next_expedition`, and `evidence_commands` from the packet visible; the packet owns what to research next and when to stop.",
                "Record every finding through the typed subcommands (`add-source`, `add-subquestion`, `resolve-question`); never edit the state file directly, and never fabricate URLs or claims — a claim exists only if a tool you actually ran produced it.",
                "Resolve a question only with recorded evidence claim ids; an open contradiction blocks resolution until an explicit sides-with claim and rationale are recorded.",
                "Re-run `status` after every expedition; stop when `stop_conditions.stopped` is true, then run `deepresearch report` and present the report path.",
                "One active run per project: to research a new question, run `deepresearch close` (or `start --new-run` once stopped) — close marks the terminal state and the next start archives it, never by editing state files.",
            ],
        },
    ]
    if include_legacy_aliases:
        legacy_specs = []
        for canonical in specs:
            name = canonical["name"]
            if not str(name).startswith("loopx-global-"):
                continue
            legacy_name = str(name).replace("loopx-global-", "loop-global-", 1)
            legacy_specs.append(
                {
                    **canonical,
                    "command": "/" + legacy_name,
                    "name": legacy_name,
                    "description": canonical["description"] + " Legacy alias for the canonical /loopx-global-* command.",
                }
            )
        specs.extend(legacy_specs)
    return specs


def _command_skill_content(spec: dict[str, Any], *, surface: str) -> str:
    instructions = list(spec["instructions"])
    return _skill_body(
        command=str(spec["command"]),
        title=str(spec.get("title") or f"LoopX {spec['command']}"),
        description=str(spec["description"]),
        argument_hint=str(spec["argument_hint"]),
        instructions=instructions,
        surface=surface,
        front_matter_name=str(spec["name"]),
    )


def materialize_loopx_entry_skill(
    *,
    skills_dir: Path,
    execute: bool,
    cli_bin: str = "loopx",
) -> dict[str, Any]:
    """Materialize the generated ``$loopx`` entry skill into a host skill root."""

    spec = next(
        item
        for item in _command_prompt_specs(
            cli_bin=cli_bin,
            include_legacy_aliases=False,
        )
        if item["name"] == "loopx"
    )
    skill_path = skills_dir / "loopx" / "SKILL.md"
    content = _command_skill_content(spec, surface="codex-skills")
    return {
        "skill_id": "loopx",
        "path": str(skill_path),
        "status": _target_status(skill_path, content, execute=execute),
    }


def _codex_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
    return Path(raw).expanduser()


def _claude_home(value: str | None = None) -> Path:
    raw = value or os.environ.get("CLAUDE_HOME") or str(Path.home() / ".claude")
    return Path(raw).expanduser()


def _strip_jsonc_comments(content: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(content):
        char = content[index]
        next_char = content[index + 1] if index + 1 < len(content) else ""
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue
        if char == "/" and next_char == "/":
            output.extend((" ", " "))
            index += 2
            while index < len(content) and content[index] not in "\r\n":
                output.append(" ")
                index += 1
            continue
        if char == "/" and next_char == "*":
            output.extend((" ", " "))
            index += 2
            while index < len(content):
                if index + 1 < len(content) and content[index : index + 2] == "*/":
                    output.extend((" ", " "))
                    index += 2
                    break
                output.append("\n" if content[index] == "\n" else " ")
                index += 1
            continue
        output.append(char)
        index += 1
    return "".join(output)


def _strip_jsonc_trailing_commas(content: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(content):
        char = content[index]
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue
        if char == ",":
            lookahead = index + 1
            while lookahead < len(content) and content[lookahead].isspace():
                lookahead += 1
            if lookahead < len(content) and content[lookahead] in "]}":
                index += 1
                continue
        output.append(char)
        index += 1
    return "".join(output)


def _normalize_surfaces(surfaces: list[str] | None) -> list[str]:
    requested = surfaces or ["all"]
    normalized: list[str] = []
    for surface in requested:
        if surface == "all":
            candidates = ["codex", "claude-code"]
        elif surface == "codex":
            candidates = ["codex"]
        elif surface == "codex-cli":
            candidates = ["codex"]
        else:
            candidates = [surface]
        for candidate in candidates:
            if candidate not in normalized:
                normalized.append(candidate)
    return normalized


def _pi_extension_path(project_root: Path) -> Path:
    return project_root / ".pi" / "extensions" / "loopx-goal.ts"


def _pi_runtime_path(project_root: Path) -> Path:
    return project_root / ".pi" / "extensions" / "pi-goal-loop-runtime.mjs"


def install_slash_commands(
    *,
    execute: bool,
    uninstall: bool = False,
    surfaces: list[str] | None = None,
    cli_bin: str = "loopx",
    include_legacy_aliases: bool = True,
    codex_home: str | None = None,
    claude_home: str | None = None,
    pi_project: str | None = None,
) -> dict[str, Any]:
    specs = _command_prompt_specs(cli_bin=cli_bin, include_legacy_aliases=include_legacy_aliases)
    effective_surfaces = _normalize_surfaces(surfaces)
    codex_root = _codex_home(codex_home)
    claude_root = _claude_home(claude_home)
    pi_project_root = Path(pi_project or ".").expanduser().resolve()
    installed: list[dict[str, Any]] = []

    if "codex" in effective_surfaces:
        prompt_dir = codex_root / "prompts"
        for spec in specs:
            prompt_path = prompt_dir / f"{spec['name']}.md"
            if uninstall:
                retire_status = _retire_status(prompt_path, execute=execute)
                installed.append(
                    {
                        "surface": "codex",
                        "host_surfaces": ["codex-cli"],
                        "mechanism": "retired_codex_custom_prompt",
                        "command": spec["command"],
                        "path": str(prompt_path),
                        "status": retire_status,
                        "invoke_as": [],
                    }
                )
                continue
            retire_status = _retire_managed_file(prompt_path, execute=execute)
            if retire_status:
                installed.append(
                    {
                        "surface": "codex",
                        "host_surfaces": ["codex-cli"],
                        "mechanism": "retired_codex_custom_prompt",
                        "command": spec["command"],
                        "path": str(prompt_path),
                        "status": retire_status,
                        "invoke_as": [],
                    }
                )

        skill_dir = codex_root / "skills"
        for spec in specs:
            skill_path = skill_dir / str(spec["name"]) / "SKILL.md"
            metadata_path = skill_path.parent / "agents" / "openai.yaml"
            if uninstall:
                skill_status = _retire_status(skill_path, execute=execute)
                installed.append(
                    {
                        "surface": "codex",
                        "host_surfaces": ["codex-cli"],
                        "mechanism": "codex_explicit_skills",
                        "command": spec["command"],
                        "path": str(skill_path),
                        "status": skill_status,
                        "invoke_as": [f"${spec['name']}", "/skills"],
                    }
                )
                metadata_status = _retire_status(metadata_path, execute=execute)
                installed.append(
                    {
                        "surface": "codex",
                        "host_surfaces": ["codex-cli"],
                        "mechanism": "codex_skill_openai_metadata",
                        "command": spec["command"],
                        "path": str(metadata_path),
                        "status": metadata_status,
                        "invoke_as": [f"${spec['name']}", "/skills"],
                    }
                )
                continue
            skill_content = _command_skill_content(spec, surface="codex-skills")
            skill_status = _target_status(skill_path, skill_content, execute=execute)
            installed.append(
                {
                    "surface": "codex",
                    "host_surfaces": ["codex-cli"],
                    "mechanism": "codex_explicit_skills",
                    "command": spec["command"],
                    "path": str(skill_path),
                    "status": skill_status,
                    "invoke_as": [f"${spec['name']}", "/skills"],
                }
            )
            if skill_status not in {"skipped_user_file", "preserved_existing_loopx_skill"}:
                display_name = (
                    "LoopX" if spec["command"] == "/loopx" else f"LoopX {spec['command']}"
                )
                metadata = _openai_skill_metadata(
                    command=str(spec["command"]),
                    display_name=display_name,
                    short_description=str(spec["description"]),
                )
                metadata_status = _target_status(metadata_path, metadata, execute=execute)
                installed.append(
                    {
                        "surface": "codex",
                        "host_surfaces": ["codex-cli"],
                        "mechanism": "codex_skill_openai_metadata",
                        "command": spec["command"],
                        "path": str(metadata_path),
                        "status": metadata_status,
                        "invoke_as": [f"${spec['name']}", "/skills"],
                    }
                )
            elif skill_status in {"skipped_user_file", "preserved_existing_loopx_skill"}:
                retire_status = _retire_managed_file(metadata_path, execute=execute)
                if retire_status:
                    installed.append(
                        {
                            "surface": "codex",
                            "host_surfaces": ["codex-cli"],
                            "mechanism": "retired_codex_command_metadata",
                            "command": spec["command"],
                            "path": str(metadata_path),
                            "status": retire_status,
                            "invoke_as": [],
                        }
                    )
        for spec in specs:
            installed.append(
                {
                    "surface": "codex",
                    "host_surfaces": ["codex-cli"],
                    "mechanism": "unsupported_native_slash_registry",
                    "command": spec["command"],
                    "path": None,
                    "status": "unsupported_host_surface",
                    "invoke_as": [],
                    "reason": (
                        "Current Codex does not support user-defined native top-level slash "
                        "commands. Use explicit skills instead."
                    ),
                    "native_registry_supported": False,
                    "failure_policy": "fail_closed_to_explicit_skill",
                    "fallback": (
                        f"Use `${spec['name']}` or `/skills` to explicitly invoke the LoopX "
                        "command skill; for the visible TUI loop, run "
                        "`loopx codex-cli-bootstrap-message --project .`, paste the setup "
                        "message, then set `/goal <thin task_body>`."
                    ),
                }
            )

    if "claude-code" in effective_surfaces:
        skills_dir = claude_root / "skills"
        for spec in specs:
            path = skills_dir / str(spec["name"]) / "SKILL.md"
            if uninstall:
                status = _retire_status(path, execute=execute)
                installed.append(
                    {
                        "surface": "claude-code",
                        "mechanism": "claude_code_skills",
                        "command": spec["command"],
                        "path": str(path),
                        "status": status,
                        "invoke_as": [str(spec["command"])],
                    }
                )
                continue
            content = _skill_body(
                command=str(spec["command"]),
                title=f"LoopX {spec['command']}",
                description=str(spec["description"]),
                argument_hint=str(spec["argument_hint"]),
                instructions=list(spec["instructions"]),
                surface="claude-skills",
                front_matter_name=str(spec["name"]),
            )
            status = _target_status(path, content, execute=execute)
            installed.append(
                {
                    "surface": "claude-code",
                    "mechanism": "claude_code_skills",
                    "command": spec["command"],
                    "path": str(path),
                    "status": status,
                    "invoke_as": [str(spec["command"])],
                }
            )

    if "pi" in effective_surfaces:
        extension_path = _pi_extension_path(pi_project_root)
        runtime_path = _pi_runtime_path(pi_project_root)
        extension_content = pi_extension_source()
        runtime_content = pi_runtime_source()
        if uninstall:
            for mechanism, path in (
                ("pi_goal_extension", extension_path),
                ("pi_goal_extension_runtime", runtime_path),
            ):
                installed.append(
                    {
                        "surface": "pi",
                        "host_surfaces": ["pi"],
                        "mechanism": mechanism,
                        "command": "/loopx",
                        "path": str(path),
                        "status": _retire_status(path, execute=execute),
                        "invoke_as": ["/loopx", "loopx_goal_activate"],
                    }
                )
        else:
            # The adapter and its loop runtime are one atomic delivery unit:
            # preflight both targets and fail closed with zero writes when any
            # target is a user-owned file, so a newly created managed adapter
            # can never import an unmanaged runtime that may lack the exports
            # it needs.
            user_owned_pi_paths = [
                str(path)
                for path, content in (
                    (extension_path, extension_content),
                    (runtime_path, runtime_content),
                )
                if _target_status(path, content, execute=False) == "skipped_user_file"
            ]
            if user_owned_pi_paths:
                installed.append(
                    {
                        "surface": "pi",
                        "host_surfaces": ["pi"],
                        "mechanism": "pi_goal_extension",
                        "command": "/loopx",
                        "path": str(extension_path),
                        "status": "blocked_user_owned_pi_file",
                        "invoke_as": ["/loopx", "loopx_goal_activate"],
                        "reason": (
                            "Move or rename the listed user-owned Pi files before "
                            "installing LoopX so the adapter and its loop runtime "
                            "are installed as one atomic unit; no Pi file was written."
                        ),
                        "conflicts": user_owned_pi_paths,
                    }
                )
            else:
                for mechanism, path, content in (
                    ("pi_goal_extension", extension_path, extension_content),
                    ("pi_goal_extension_runtime", runtime_path, runtime_content),
                ):
                    installed.append(
                        {
                            "surface": "pi",
                            "host_surfaces": ["pi"],
                            "mechanism": mechanism,
                            "command": "/loopx",
                            "path": str(path),
                            "status": _target_status(path, content, execute=execute),
                            "invoke_as": ["/loopx", "loopx_goal_activate"],
                        }
                    )

    status_counts: dict[str, int] = {}
    for item in installed:
        status = str(item["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "ok": not any(status.startswith("blocked_") for status in status_counts),
        "schema_version": SCHEMA_VERSION,
        "operation": "uninstall" if uninstall else "install",
        "execute": execute,
        "requested_surfaces": surfaces or ["all"],
        "effective_surfaces": effective_surfaces,
        "catalog_schema_version": build_slash_command_catalog(
            cli_bin=cli_bin,
            include_legacy_aliases=include_legacy_aliases,
        )["schema_version"],
        "summary": {
            "codex_prompt_dir": None,
            "codex_skill_dir": str(codex_root / "skills") if "codex" in effective_surfaces else None,
            "claude_skill_dir": str(claude_root / "skills") if "claude-code" in effective_surfaces else None,
            "pi_extension_path": str(_pi_extension_path(pi_project_root)) if "pi" in effective_surfaces else None,
            "pi_runtime_path": str(_pi_runtime_path(pi_project_root)) if "pi" in effective_surfaces else None,
            "status_counts": status_counts,
            "skip_policy": (
                "Uninstall removes only LoopX-managed files; user files without a LoopX managed marker are preserved"
                if uninstall
                else "LoopX-managed files are upgraded; same-name user files without a LoopX managed marker or legacy signature are never overwritten"
            ),
        },
        "installed": installed,
        "notes": [
            "Codex does not currently support user-defined native top-level slash commands; use explicit skill invocation through `$loopx` or `/skills`.",
            "Explicit LoopX command-facade skills use agents/openai.yaml policy allow_implicit_invocation=false and remain distinct from richer workflow skills such as loopx-project.",
            "Claude Code discovers user skills from CLAUDE_HOME/skills and exposes each skill name as a slash command.",
            "The Pi surface is opt-in and installs the self-contained goal extension and its loop runtime into the project's .pi/extensions/; it is not part of the default all surface.",
            "Uninstall is fail-closed: it retires only files carrying the LoopX managed marker and leaves user-owned files in place.",
        ],
    }


def render_slash_command_install_markdown(payload: dict[str, Any]) -> str:
    operation = str(payload.get("operation") or "install")
    lines = [
        "# LoopX Slash Command Uninstall" if operation == "uninstall" else "# LoopX Slash Command Install",
        "",
        f"- operation: `{operation}`",
        f"- execute: `{payload.get('execute')}`",
        f"- surfaces: `{','.join(payload.get('effective_surfaces') or [])}`",
        f"- skip policy: `{payload.get('summary', {}).get('skip_policy')}`",
    ]
    codex_prompt_dir = payload.get("summary", {}).get("codex_prompt_dir")
    codex_skill_dir = payload.get("summary", {}).get("codex_skill_dir")
    claude_skill_dir = payload.get("summary", {}).get("claude_skill_dir")
    if codex_prompt_dir:
        lines.append(f"- codex prompts: `{codex_prompt_dir}`")
    if codex_skill_dir:
        lines.append(f"- codex skills: `{codex_skill_dir}`")
    if claude_skill_dir:
        lines.append(f"- claude skills: `{claude_skill_dir}`")
    pi_extension_path = payload.get("summary", {}).get("pi_extension_path")
    if pi_extension_path:
        lines.append(f"- pi extension: `{pi_extension_path}`")
    pi_runtime_path = payload.get("summary", {}).get("pi_runtime_path")
    if pi_runtime_path:
        lines.append(f"- pi loop runtime: `{pi_runtime_path}`")
    counts = payload.get("summary", {}).get("status_counts") or {}
    if isinstance(counts, dict) and counts:
        count_text = ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
        lines.append(f"- statuses: `{count_text}`")
    skipped = [
        item for item in payload.get("installed") or []
        if isinstance(item, dict) and item.get("status") == "skipped_user_file"
    ]
    if skipped:
        lines.append("")
        lines.append("Skipped user-owned files:")
        for item in skipped:
            lines.append(f"- `{item.get('command')}` at `{item.get('path')}`")
    notes = [note for note in payload.get("notes") or [] if isinstance(note, str)]
    if notes:
        lines.append("")
        lines.append("Notes:")
        for note in notes:
            lines.append(f"- {note}")
    lines.append("")
    lines.append("Restart the host if its slash-command menu was already open.")
    return "\n".join(lines)
