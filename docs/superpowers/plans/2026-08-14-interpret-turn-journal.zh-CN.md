# Turn Journal 解释实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> [English](2026-08-14-interpret-turn-journal.md)

**目标：** 增加一个只读的 `interpret_turn_journal` Effect Program 视角（lens），返回结构化的
回放合法性、身份不匹配、tombstone 与阶段顺序信息。

**架构：** 把公开 lens 放在 `loopx.control_plane.effect_program` 中，与现有的 quota 和
Turn-result 解释器并列。把 canonical Turn 阶段序列移入该核心 Effect Program 模块，并保留
`turn_driver.transaction.TRANSACTION_PHASES` 作为别名，使解释与执行共享同一个精确的排序规则，
且没有循环导入或重复元组。把类型化的违规投影到 `EffectRequest.context`；绝不调用 executor、
journal I/O、调度或 quota 代码。

**技术栈：** Python 3.12、frozen dataclasses、`StrEnum`、pytest、Markdown 参考文档。

## 全局约束

- API 是 `interpret_turn_journal(journal, *, goal_id=None, agent_id=None, turn_key=None, capabilities=()) -> EffectTurn`。
- 语义不匹配返回带 `decision="replay_blocked"` 的 `EffectTurn`；它们不抛出异常。
- `EffectObservation.should_run` 恒为 `False`；`request.context["replay_legal"]` 是合法性信号。
- 该 lens 不做任何 journal I/O、变更、执行、调度、模型调用或 quota 花费。
- 现有 journal 与 Turn wire schema 保持不变。
- Terminal 回放 tombstones 精确为 `committed`、`stopped` 与 `failed`；带 `retry_failed=True`
  的失败恢复仍归 executor 所有。
- 分类使用类型化字段与精确相等，不使用子串启发式。

---

### 任务 1：建立合法回放 lens 与 canonical 阶段来源

**文件：**
- 创建：`tests/control_plane/test_effect_turn_turn_journal.py`
- 修改：`loopx/control_plane/effect_program.py`
- 修改：`loopx/control_plane/turn_driver/transaction.py`

**接口：**
- 消费：现有 `EffectRequest`、`EffectInterpretation`、`EffectObservation`、`EffectNext` 与
  `EffectTurn` dataclasses。
- 产出：`TurnTransactionPhase`、`TURN_TRANSACTION_PHASES` 与
  `interpret_turn_journal(...) -> EffectTurn`；把 `turn_driver.transaction.TRANSACTION_PHASES`
  保留为同一元组。

- [ ] **步骤 1：编写失败中的合法 journal 测试**

```python
from copy import deepcopy

from loopx.control_plane.effect_program import EffectNext, interpret_turn_journal


def _journal(*, status: str = "committed") -> dict[str, object]:
    turn_key = "sha256:fixture-turn"
    return {
        "schema_version": "loopx_turn_journal_v0",
        "goal_id": "fixture-goal",
        "turn_key": turn_key,
        "status": status,
        "completed_phases": [
            "host_execute",
            "typed_result",
            "validation",
            "durable_writeback",
            "quota_spend",
            "scheduler_apply",
            "scheduler_ack",
        ],
        "plan": {
            "turn_envelope": {
                "goal_id": "fixture-goal",
                "agent_id": "fixture-agent",
            },
            "transaction": {
                "turn_key": turn_key,
                "settlement_plan": {
                    "identity": {
                        "goal_id": "fixture-goal",
                        "agent_id": "fixture-agent",
                    }
                },
            },
        },
        "host_result": {"turn_key": turn_key},
        "receipt": {"turn_key": turn_key},
    }


def test_turn_journal_reports_legal_replay_without_mutating_input() -> None:
    journal = _journal()
    before = deepcopy(journal)

    turn = interpret_turn_journal(
        journal,
        goal_id="fixture-goal",
        agent_id="fixture-agent",
        turn_key="sha256:fixture-turn",
        capabilities=["filesystem_read"],
    )

    assert turn.request.kind == "turn_journal"
    assert turn.request.source == "turn_journal"
    assert turn.request.context == {
        "replay_legal": True,
        "goal_matches": True,
        "owner_matches": True,
        "turn_key_matches": True,
        "phases_form_ordered_prefix": True,
        "journal_status": "committed",
        "tombstone_retained": True,
        "completed_phases": (
            "host_execute",
            "typed_result",
            "validation",
            "durable_writeback",
            "quota_spend",
            "scheduler_apply",
            "scheduler_ack",
        ),
        "violations": (),
    }
    assert turn.observation.decision == "replay_legal"
    assert turn.observation.should_run is False
    assert turn.next_effect == EffectNext()
    assert journal == before
```

- [ ] **步骤 2：运行测试并验证 RED**

运行：`python -m pytest -q tests/control_plane/test_effect_turn_turn_journal.py::test_turn_journal_reports_legal_replay_without_mutating_input`

预期：集合失败，因为 `interpret_turn_journal` 不存在。

- [ ] **步骤 3：添加 canonical 阶段枚举与最小合法 lens**

在 `effect_program.py` 中定义 canonical 阶段并实现公开签名：

```python
class TurnTransactionPhase(StrEnum):
    HOST_EXECUTE = "host_execute"
    TYPED_RESULT = "typed_result"
    VALIDATION = "validation"
    DURABLE_WRITEBACK = "durable_writeback"
    QUOTA_SPEND = "quota_spend"
    SCHEDULER_APPLY = "scheduler_apply"
    SCHEDULER_ACK = "scheduler_ack"


TURN_TRANSACTION_PHASES = tuple(phase.value for phase in TurnTransactionPhase)


def interpret_turn_journal(
    journal: Mapping[str, Any],
    *,
    goal_id: str | None = None,
    agent_id: str | None = None,
    turn_key: str | None = None,
    capabilities: Sequence[str] = (),
) -> EffectTurn:
    plan = _mapping(journal.get("plan"))
    envelope = _mapping(plan.get("turn_envelope"))
    transaction = _mapping(plan.get("transaction"))
    settlement = _mapping(transaction.get("settlement_plan"))
    identity = _mapping(settlement.get("identity"))
    completed = tuple(str(value) for value in journal.get("completed_phases", []))
    context = {
        "replay_legal": True,
        "goal_matches": True,
        "owner_matches": True,
        "turn_key_matches": True,
        "phases_form_ordered_prefix": completed
        == TURN_TRANSACTION_PHASES[: len(completed)],
        "journal_status": str(journal.get("status") or ""),
        "tombstone_retained": journal.get("status")
        in {"committed", "stopped", "failed"},
        "completed_phases": completed,
        "violations": (),
    }
    return EffectTurn(
        request=EffectRequest(
            kind="turn_journal",
            source="turn_journal",
            goal_id=goal_id,
            agent_id=agent_id,
            capabilities=tuple(capabilities),
            context=context,
        ),
        interpretation=EffectInterpretation(
            route="turn_journal_replay",
            obligation="observe_fenced_replay",
            interaction_mode="read_only",
        ),
        observation=EffectObservation(
            decision="replay_legal",
            should_run=False,
            effective_action="observe_replay",
            recommended_action="Retain the terminal Turn journal tombstone.",
            protocol_summary="Turn journal replay is legal and effect-free.",
        ),
        next_effect=EffectNext(),
    )
```

在 `turn_driver/transaction.py` 中导入 `TURN_TRANSACTION_PHASES` 并保持兼容：

```python
TRANSACTION_PHASES = TURN_TRANSACTION_PHASES
```

- [ ] **步骤 4：运行合法 lens 与 transaction 回归测试**

运行：`python -m pytest -q tests/control_plane/test_effect_turn_turn_journal.py tests/test_loopx_turn_transaction.py`

预期：全部测试通过。

- [ ] **步骤 5：提交合法 lens 接缝**

```bash
git add -- tests/control_plane/test_effect_turn_turn_journal.py loopx/control_plane/effect_program.py loopx/control_plane/turn_driver/transaction.py
git commit -m "feat(effect): interpret legal turn journal replay"
```

### 任务 2：为非法与 tombstone 状态返回类型化违规

**文件：**
- 修改：`tests/control_plane/test_effect_turn_turn_journal.py`
- 修改：`loopx/control_plane/effect_program.py`

**接口：**
- 消费：任务 1 中的 `TURN_TRANSACTION_PHASES` 与 `interpret_turn_journal`。
- 产出：`TurnJournalViolation(StrEnum)` 以及 `EffectRequest.context` 中完整的结构化回放结果。

- [ ] **步骤 1：添加失败中的身份、阶段、terminal 与格式错误测试**

添加只改动受控 fixture 字段并断言字面结果的测试：

```python
def test_turn_journal_accumulates_identity_and_phase_violations() -> None:
    journal = _journal()
    journal["goal_id"] = "other-goal"
    journal["turn_key"] = "sha256:other-turn"
    journal["completed_phases"] = ["host_execute", "validation"]
    identity = journal["plan"]["transaction"]["settlement_plan"]["identity"]
    identity["agent_id"] = "other-agent"

    turn = interpret_turn_journal(
        journal,
        goal_id="fixture-goal",
        agent_id="fixture-agent",
        turn_key="sha256:fixture-turn",
    )

    assert turn.request.context["replay_legal"] is False
    assert turn.request.context["goal_matches"] is False
    assert turn.request.context["owner_matches"] is False
    assert turn.request.context["turn_key_matches"] is False
    assert turn.request.context["phases_form_ordered_prefix"] is False
    assert turn.request.context["violations"] == (
        "goal_mismatch",
        "owner_mismatch",
        "turn_key_mismatch",
        "completed_phases_not_ordered_prefix",
    )
    assert turn.observation.decision == "replay_blocked"
    assert turn.observation.should_run is False


@pytest.mark.parametrize("status", ["committed", "stopped", "failed"])
def test_turn_journal_retains_terminal_tombstones(status: str) -> None:
    turn = interpret_turn_journal(
        _journal(status=status),
        goal_id="fixture-goal",
        agent_id="fixture-agent",
        turn_key="sha256:fixture-turn",
    )
    assert turn.request.context["tombstone_retained"] is True
    assert turn.request.context["journal_status"] == status
    assert turn.request.context["replay_legal"] is True


def test_turn_journal_blocks_non_terminal_and_malformed_trace() -> None:
    journal = {"status": "in_progress", "completed_phases": "host_execute"}
    turn = interpret_turn_journal(journal)
    assert turn.request.context["replay_legal"] is False
    assert turn.request.context["tombstone_retained"] is False
    assert turn.request.context["violations"] == (
        "goal_identity_missing",
        "owner_identity_missing",
        "turn_key_identity_missing",
        "completed_phases_invalid",
        "journal_not_terminal",
    )
```

- [ ] **步骤 2：运行新测试并验证 RED**

运行：`python -m pytest -q tests/control_plane/test_effect_turn_turn_journal.py`

预期：测试失败，因为任务 1 尚未比较 trace 身份或对阻止的回放分类。

- [ ] **步骤 3：实现精确身份比较与类型化违规**

在 `effect_program.py` 中添加枚举与辅助函数：

```python
class TurnJournalViolation(StrEnum):
    GOAL_IDENTITY_MISSING = "goal_identity_missing"
    GOAL_MISMATCH = "goal_mismatch"
    OWNER_IDENTITY_MISSING = "owner_identity_missing"
    OWNER_MISMATCH = "owner_mismatch"
    TURN_KEY_IDENTITY_MISSING = "turn_key_identity_missing"
    TURN_KEY_MISMATCH = "turn_key_mismatch"
    COMPLETED_PHASES_INVALID = "completed_phases_invalid"
    COMPLETED_PHASES_NOT_ORDERED_PREFIX = "completed_phases_not_ordered_prefix"
    JOURNAL_NOT_TERMINAL = "journal_not_terminal"
    JOURNAL_STATUS_UNSUPPORTED = "journal_status_unsupported"


def _present_strings(*values: Any) -> tuple[str, ...]:
    return tuple(value for item in values if (value := str(item or "").strip()))


def _values_match(values: tuple[str, ...]) -> bool:
    return bool(values) and len(set(values)) == 1
```

更新 `interpret_turn_journal`：

1. 要求 journal/envelope/settlement 的 goal、envelope/settlement 的 owner 与
   journal/transaction 的 Turn key；
2. 提供显式期望时，对每次比较追加该期望；
3. 只有当可选的 host-result 与 receipt Turn key 存在时才比较它们；
4. 区分非列表阶段与不是 canonical 前缀的列表值；
5. 把 `in_progress` 与 `scheduler_action_required` 分类为已知的非 terminal 状态，未知值分类
   为 unsupported；
6. 以空的违规列表计算合法性；
7. 存在任何违规时输出 `replay_blocked`、`block_replay` 与领域中立 readback。

最终合法性计算为：

```python
replay_legal = not violations
context["violations"] = tuple(violation.value for violation in violations)
```

- [ ] **步骤 4：运行聚焦测试与现有 Effect Program 回归**

运行：`python -m pytest -q tests/control_plane/test_effect_turn_turn_journal.py tests/control_plane/test_effect_interpreter_packet.py tests/control_plane/test_effect_turn_turn_result.py tests/test_loopx_turn_transaction.py tests/test_loopx_turn_executor.py`

预期：全部测试通过。

- [ ] **步骤 5：提交结构化违规行为**

```bash
git add -- tests/control_plane/test_effect_turn_turn_journal.py loopx/control_plane/effect_program.py
git commit -m "feat(effect): report blocked turn journal replay"
```

### 任务 3：记录并验证只读契约

**文件：**
- 修改：`docs/reference/effect-interpreter-packet.md`
- 跟踪：`docs/superpowers/plans/2026-08-14-interpret-turn-journal.md`

**接口：**
- 消费：任务 1 与 2 的最终 `interpret_turn_journal` 行为。
- 产出：描述身份、tombstone、回放与无 authority 语义的公开指南。

- [ ] **步骤 1：更新参考文档**

添加一个 `Turn Journal Lens` 章节，说明如下：

```markdown
## Turn Journal Lens

`interpret_turn_journal` reads an existing fenced Turn journal and returns an
`EffectTurn`. It compares goal, agent owner, and Turn-key identity across the
journal trace; validates that completed phases are an ordered transaction
prefix; and exposes retained terminal tombstones.

`request.context.replay_legal` is the legality signal. `should_run` remains
false and `next_effect` remains empty: interpretation grants no permission to
execute, retry, schedule, write state, or spend quota. Semantic mismatches are
returned as typed violation values instead of exceptions.
```

- [ ] **步骤 2：运行格式检查与聚焦验证**

运行：

```powershell
python -m pytest -q tests/control_plane/test_effect_turn_turn_journal.py tests/control_plane/test_effect_interpreter_packet.py tests/control_plane/test_effect_turn_turn_result.py tests/test_loopx_turn_transaction.py tests/test_loopx_turn_executor.py
python examples/loopx-turn-fake-host-walkthrough-smoke.py
loopx check --scan-path docs/reference/effect-interpreter-packet.md --scan-path docs/development/contributor-tasks.md
loopx canary premerge --from-git-diff --git-diff-base upstream/main
git diff --check upstream/main...HEAD
```

预期：每条命令退出码为零。如果 canary 报告显式跳过，记录跳过及其原因，而不是声称该表面已测试。

- [ ] **步骤 3：运行公开/私有边界扫描**

运行：

```powershell
git diff --name-only upstream/main...HEAD
git diff upstream/main...HEAD | Select-String -Pattern 'credential|secret|private state|raw log|trajectory|verifier output|[A-Z]:\\|file://|localhost' -CaseSensitive:$false
```

预期：只出现范围内的 product、test、reference、spec 与 plan 文件；没有 credential、
private-state、raw-evidence、local-path 或 internal-link 内容。

- [ ] **步骤 4：提交文档与计划**

```bash
git add -- docs/reference/effect-interpreter-packet.md docs/superpowers/plans/2026-08-14-interpret-turn-journal.md
git commit -m "docs(effect): explain turn journal replay lens"
```

- [ ] **步骤 5：验证最终分支状态**

运行：

```powershell
git status --short --branch
git log --oneline upstream/main..HEAD
```

预期：工作树干净且列出了范围内提交。
