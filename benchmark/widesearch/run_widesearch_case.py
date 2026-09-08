"""Run one WideSearch case under baseline (native Codex Goal) or treatment
(LoopX-guided) arm, producing a fresh final_answer.md in an isolated workspace.

Verifier is intentionally NOT part of this repo: it runs as the official
WideSearch evaluator inside a pier task (sandboxed, gold hidden from the agent)
for the local real-sandbox path, matching the deepswe infrastructure. This file
reuses the shipped native Goal runtime (no second implementation):
  from loopx.capabilities.benchmark_toolkit.native_codex_goal import ...
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from tasks import answer_is_fresh, fresh_workspace, prepare_case, stamp_run_start

REPO_ROOT = Path(__file__).resolve().parents[2]
_PROVIDER_CREDENTIAL_ENV_KEY = "ARK_OPENAI_API_KEY"
_PROVIDER_BASE_URL_ENV_KEY = "ARK_OPENAI_BASE_URL"
_PROVIDER_SENTINEL_ENV_KEY = "LOOPX_MODEL_PROVIDER_SENTINEL"
_PROVIDER_SENTINEL_VALUE = "runner-owned-gateway-no-upstream-secret"
_PROVIDER_ID = "loopx_runner_gateway"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from loopx.capabilities.benchmark_toolkit.native_codex_goal import (  # noqa: E402
    NativeGoalConfig,
    compact_native_goal_receipt,
    run_native_goal_process_until_terminal,
)
from loopx.capabilities.benchmark_toolkit.native_codex_isolation import (  # noqa: E402
    NativeCodexIsolationError,
    build_native_codex_isolation_envelope,
    rebase_native_codex_loopx_workspace_state,
)
from loopx.capabilities.benchmark_toolkit.provider_gateway import (  # noqa: E402
    serve_runner_owned_provider_gateway,
)

# 隔离 profile 的安装实现共享 swe-marathon 的 runtime/modes/profile_install.py
# （原 benchmark_toolkit 里的宿主专用 profile 模块已随其宿主退役）；按文件路径
# 加载，因为各 benchmark 目录不是同一个可导入包。
_PROFILE_INSTALLER_PATH = (
    Path(__file__).resolve().parent.parent
    / "swe-marathon" / "runtime" / "modes" / "profile_install.py"
)
_PROFILE_INSTALLER_SPEC = importlib.util.spec_from_file_location(
    "swe_marathon_profile_install", _PROFILE_INSTALLER_PATH
)
if _PROFILE_INSTALLER_SPEC is None or _PROFILE_INSTALLER_SPEC.loader is None:  # pragma: no cover
    raise ImportError(f"profile installer 不可加载: {_PROFILE_INSTALLER_PATH}")
_profile_installer = importlib.util.module_from_spec(_PROFILE_INSTALLER_SPEC)
sys.modules["swe_marathon_profile_install"] = _profile_installer  # dataclass 需要 module 注册
_PROFILE_INSTALLER_SPEC.loader.exec_module(_profile_installer)

# app-server 模型创建 shell 的 env 白名单 + 排除项，作为凭据隔离的纵深防御。
# 真正的凭据边界是 native_codex_isolation 的 OS authority boundary。
_ENV_PASSTHROUGH = (
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "PATH",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TERM",
    "TZ",
)
_AGENT_SHELL_ENV_INCLUDE_ONLY = (
    "HOME",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "LOGNAME",
    "PATH",
    "SHELL",
    "SSL_CERT_DIR",
    "SSL_CERT_FILE",
    "TERM",
    "TMPDIR",
    "TZ",
    "USER",
)
_SAFE_ENV_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def _profile_environment(
    profile: _profile_installer.InstalledProfile,
    base_env: dict[str, str],
) -> dict[str, str]:
    """profile 的最小运行环境：HOME/CODEX_HOME/PATH + 非 secret 直通项。"""

    env = {key: str(base_env[key]) for key in _ENV_PASSTHROUGH if base_env.get(key)}
    inherited_path = env.get("PATH", os.defpath)
    env.update(
        {
            "HOME": str(profile.home),
            "CODEX_HOME": str(profile.codex_home),
            "PATH": f"{profile.bin_dir}{os.pathsep}{inherited_path}",
        }
    )
    return env


def _shell_environment_policy_args(
    *,
    excluded_env_keys: tuple[str, ...],
) -> tuple[str, ...]:
    """Codex shell 环境的纵深防御：只继承最小非 secret 变量集。"""

    normalized = tuple(
        sorted({str(value).strip() for value in excluded_env_keys if str(value).strip()})
    )
    invalid = [key for key in normalized if not _SAFE_ENV_KEY.fullmatch(key)]
    if invalid:
        raise ValueError(
            "excluded_env_keys must contain safe environment variable names"
        )
    return (
        "-c",
        'shell_environment_policy.inherit="core"',
        "-c",
        "shell_environment_policy.ignore_default_excludes=false",
        "-c",
        f"shell_environment_policy.include_only={json.dumps(_AGENT_SHELL_ENV_INCLUDE_ONLY)}",
        "-c",
        f"shell_environment_policy.exclude={json.dumps(normalized)}",
    )


def _objective(case_id: str, workspace: Path, instruction: str, treatment: bool) -> str:
    common = (
        f"Write the final markdown table to {workspace}/final_answer.md and stop. "
        "Use web_search / web_fetch to gather facts from the web."
    )
    if treatment:
        return (
            "Use the installed LoopX skill (/loopx) to start a goal for the benchmark "
            "task in this workspace, then complete the task through LoopX's guided "
            "control (follow its todos and state writebacks). "
            f"Task instruction is in instruction.md: {instruction} {common}"
        )
    return (
        "Complete the benchmark task described in instruction.md inside this "
        f"workspace. {common}"
    )


def _app_server_command(
    *,
    codex_bin: str,
    enable_web_search: bool,
    gateway_base_url: str,
    shell_policy_args: tuple[str, ...],
) -> list[str]:
    """Build the app-server Goal command with hosted Responses API compatibility.

    The codex app-server emits a ``multi_agent_v1`` dynamic-tool namespace by
    default; some hosted Responses endpoints reject ``namespace`` tool types.
    Disabling the multi-agent feature keeps the Goal tool surface minimal and
    provider-neutral while preserving the goal tools (get/create/update_goal)
    that the benchmark needs. Web search is toggled independently because some
    hosted endpoints also reject the ``external_web_access`` web_search field.
    """

    command = [
        codex_bin,
        "app-server",
        "--listen",
        "stdio://",
        "--enable",
        "goals",
        "-c",
        "features.multi_agent=false",
        "-c",
        f'model_provider="{_PROVIDER_ID}"',
        "-c",
        f'model_providers.{_PROVIDER_ID}.name="runner-owned-gateway"',
        "-c",
        f"model_providers.{_PROVIDER_ID}.base_url={json.dumps(gateway_base_url)}",
        "-c",
        (
            f"model_providers.{_PROVIDER_ID}.env_key="
            f"{json.dumps(_PROVIDER_SENTINEL_ENV_KEY)}"
        ),
        "-c",
        f'model_providers.{_PROVIDER_ID}.wire_api="responses"',
        *shell_policy_args,
    ]
    command += [
        "-c",
        "tools.web_search=true" if enable_web_search else "tools.web_search=false",
    ]
    return command


def _app_server_environment(
    profile: _profile_installer.InstalledProfile,
    environ: dict[str, str],
) -> dict[str, str]:
    """Build the credential-free environment visible inside native isolation."""

    profile_environment = _profile_environment(profile, environ)
    forbidden = {
        _PROVIDER_BASE_URL_ENV_KEY,
        _PROVIDER_CREDENTIAL_ENV_KEY,
    }.intersection(profile_environment)
    if forbidden:
        raise ValueError("provider credential authority must stay outside app-server")
    return {
        **profile_environment,
        _PROVIDER_SENTINEL_ENV_KEY: _PROVIDER_SENTINEL_VALUE,
    }


def _runner_provider_authority(environ: dict[str, str]) -> tuple[str, str]:
    base_url = str(environ.get(_PROVIDER_BASE_URL_ENV_KEY) or "").strip()
    credential = str(environ.get(_PROVIDER_CREDENTIAL_ENV_KEY) or "")
    if not base_url or not credential.strip():
        raise RuntimeError("widesearch_runner_provider_authority_missing")
    return base_url, credential


def run_case(
    *,
    case_id: str,
    arm: str,
    data_root: Path,
    timeout_sec: int,
    enable_web_search: bool = True,
) -> dict[str, Any]:
    if sys.platform != "linux":
        raise RuntimeError("widesearch_native_isolation_unavailable_use_pier")
    raw = data_root / "widesearch.jsonl"
    gold_dir = data_root / "gold"
    cases_root = data_root / "cases"
    run_id = f"{case_id}-{arm}-{time.strftime('%Y%m%d-%H%M%S')}"

    prepare_case(raw=raw, gold_dir=gold_dir, cases_root=cases_root, case_id=case_id)
    workspace = fresh_workspace(cases_root=cases_root, case_id=case_id, run_id=run_id)
    started_at = stamp_run_start(workspace)
    instruction = (workspace / "instruction.md").read_text(encoding="utf-8")

    model = os.environ.get("ARK_OPENAI_MODEL", "deepseek-v4-flash-ga-260731")
    provider_base_url, provider_credential = _runner_provider_authority(
        dict(os.environ)
    )
    codex_bin = os.environ.get("CODEX_BIN", "codex")

    with (
        tempfile.TemporaryDirectory(prefix="loopx-widesearch-profile-") as profile_dir,
        tempfile.TemporaryDirectory(prefix="loopx-widesearch-worker-") as worker_dir,
    ):
        profile = _profile_installer.install(
            REPO_ROOT,
            Path(profile_dir),
            require_clean_source=True,
        )
        with serve_runner_owned_provider_gateway(
            upstream_base_url=provider_base_url,
            upstream_bearer_token=provider_credential,
        ) as gateway:
            shell_policy_args = _shell_environment_policy_args(
                excluded_env_keys=(_PROVIDER_SENTINEL_ENV_KEY,)
            )
            app_server_command = _app_server_command(
                codex_bin=codex_bin,
                enable_web_search=enable_web_search,
                gateway_base_url=gateway.base_url,
                shell_policy_args=shell_policy_args,
            )
            try:
                envelope = build_native_codex_isolation_envelope(
                    executable=codex_bin,
                    process_args=app_server_command[1:],
                    work_dir=Path(worker_dir),
                    private_root=gold_dir,
                    workspace_source=workspace,
                    profile_root=profile.root,
                )
            except NativeCodexIsolationError as exc:
                raise RuntimeError(
                    "widesearch_native_isolation_unavailable_use_pier"
                ) from exc
            if envelope.workspace_alias is None:
                raise RuntimeError("widesearch_native_workspace_alias_missing")
            runtime_workspace = envelope.workspace_alias
            rebase_native_codex_loopx_workspace_state(
                workspace,
                source_root=runtime_workspace,
                target_root=workspace,
            )
            restore_required = False
            try:
                rebase_native_codex_loopx_workspace_state(
                    workspace,
                    source_root=workspace,
                    target_root=runtime_workspace,
                )
                restore_required = True
                config = NativeGoalConfig(
                    cwd=str(runtime_workspace),
                    objective=_objective(
                        case_id,
                        runtime_workspace,
                        instruction,
                        treatment=(arm == "treatment"),
                    ),
                    task_instruction=instruction,
                    model=model,
                    effort=os.environ.get("CODEX_GOAL_EFFORT", "xhigh"),
                    approval_policy="never",
                    sandbox="danger-full-access",
                    required_skill_ids=profile.required_skill_ids,
                )
                turn = run_native_goal_process_until_terminal(
                    config,
                    codex_bin=codex_bin,
                    process_command=envelope.process_command,
                    process_env=_app_server_environment(profile, dict(os.environ)),
                    process_cwd=str(envelope.work_dir),
                    goal_timeout_sec=timeout_sec,
                )
            finally:
                if restore_required:
                    rebase_native_codex_loopx_workspace_state(
                        workspace,
                        source_root=runtime_workspace,
                        target_root=workspace,
                    )
            receipt = compact_native_goal_receipt(turn)
            receipt["provider_credential_boundary"] = {
                "schema_version": "runner_owned_provider_gateway_boundary_v0",
                "gateway_owner": "runner",
                "gateway_loopback_only": True,
                "upstream_credential_in_app_server": False,
                "ambient_home_exposed": False,
                "linux_user_mount_pid_namespace": True,
            }

    fresh, reason = answer_is_fresh(workspace, started_at)
    if not fresh:
        return {"status": "runner_invalid", "reason": reason, "receipt": receipt}
    return {
        "status": "completed",
        "final_answer": str(workspace / "final_answer.md"),
        "receipt": receipt,
        "arm": arm,
        "run_id": run_id,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=["baseline", "treatment"], required=True)
    p.add_argument("--case", default="ws_en_001")
    p.add_argument("--data-root", type=Path, required=True)
    p.add_argument("--timeout-sec", type=int, default=7200)
    p.add_argument(
        "--disable-web-search",
        action="store_true",
        help=(
            "Disable the native web_search tool in the app-server Goal config "
            "(some hosted Responses endpoints reject its external_web_access field)."
        ),
    )
    args = p.parse_args()
    outcome = run_case(
        case_id=args.case,
        arm=args.arm,
        data_root=args.data_root,
        timeout_sec=args.timeout_sec,
        enable_web_search=not args.disable_web_search,
    )
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    return 0 if outcome["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
