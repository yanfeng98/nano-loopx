from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime, timezone
import platform
import sys

from .. import __version__


PrintPayload = Callable[
    [dict[str, object], str, Callable[[dict[str, object]], str]],
    None,
]

LOCAL_FEEDBACK_HINT = (
    "Local only - nothing is sent. This build has no online feedback channel; "
    "copy the receipt yourself if you want to share it."
)


def collect_first_run_report() -> dict[str, object]:
    os_label = f"{platform.system()} {platform.release()}".strip()
    return {
        "schema_version": "first_run_report_v0",
        "loopx_version": __version__,
        "os": os_label,
        "arch": platform.machine(),
        "python": sys.version.split()[0],
        "reported_at": datetime.now(timezone.utc).isoformat(),
        "feedback_hint": LOCAL_FEEDBACK_HINT,
        "sent": False,
    }


def render_first_run_report_markdown(payload: dict[str, object]) -> str:
    lines = [
        "LoopX first-run report (local only, nothing was sent)",
        "",
        f"- LoopX: {payload['loopx_version']}",
        f"- OS: {payload['os']}",
        f"- Arch: {payload['arch']}",
        f"- Python: {payload['python']}",
        f"- Generated: {payload['reported_at']}",
        "",
        str(payload["feedback_hint"]),
    ]
    return "\n".join(lines)


def register_first_run_report_command(
    subparsers: argparse._SubParsersAction,
) -> argparse.ArgumentParser:
    return subparsers.add_parser(
        "first-run-report",
        help="Print a local first-run receipt. Nothing is sent and there is no feedback link.",
    )


def handle_first_run_report_command(
    args: argparse.Namespace,
    print_payload: PrintPayload,
) -> int:
    payload = collect_first_run_report()
    print_payload(payload, args.format, render_first_run_report_markdown)
    return 0
