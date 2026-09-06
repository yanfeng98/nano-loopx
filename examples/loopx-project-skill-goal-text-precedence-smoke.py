#!/usr/bin/env python3
"""Guard the loopx-project skill against downgrading goal text to bare /loopx."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "loopx-project" / "SKILL.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    require("可识别的项目本地 goal 启动命令：" in text, "goal-start heading missing")
    require("- `/loopx <goal text>`" in text, "goal-text command missing")
    require("- `/loopx`\n" not in text, "bare /loopx should not be listed as project-local fallback")
    require("否则 `/loopx` 之后每个非空白字符都是 goal 文本" in compact, "goal text precedence missing")
    require("推断产品 capability 路由" in text, "implicit capability route guard missing")
    require("不要降低任一形式为状态或检查轮次" in compact, "downgrade guard missing")
    require("Bare `/loopx` is read/status-first" not in text, "bare /loopx status-first branch should not steer this skill")
    print("loopx-project-skill-goal-text-precedence-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
