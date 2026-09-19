"""Typed Chat actions for canonical Todo lifecycle transitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .agent_registry import registered_agent_ids_for_goal
from .control_plane.todos.active_state_todo_parser import parse_active_state_todos
from .control_plane.todos.contract import TODO_TASK_CLASS_USER_GATE
from .operator_gate import OPERATOR_GATE_DECISIONS, record_operator_gate
from .todos import complete_goal_todo, supersede_goal_todo, update_goal_todo

# An Owner decision is written straight through the canonical services the CLI
# uses, so the same decision reached from the workspace and from the terminal
# lands in the same state. These are the decisions each canonical service takes.
GATE_TODO_DECISION_OUTCOMES = {"approve", "reject", "cancel"}
# The decision must resolve its target whatever lane budget the Goal's status
# projection uses, so the lookup parses every Todo rather than a bounded page.
_GATE_TODO_SCAN_LIMIT: int | None = None


def _todo_group_items(group: dict[str, Any]) -> list[dict[str, Any]]:
    """Every Todo item a projection group exposes, across its lanes."""

    items: list[dict[str, Any]] = []
    for value in group.values():
        if isinstance(value, list):
            items.extend(item for item in value if isinstance(item, dict))
    return items


class ChatTodoActionMixin:
    """Keep Todo preview/apply parity separate from general orchestration."""

    def _run_todo_update(
        self, parameters: dict[str, Any], *, dry_run: bool
    ) -> dict[str, Any]:
        goal_id = str(parameters["goal_id"])
        operation = str(parameters.get("operation") or "edit")
        if operation == "complete":
            return complete_goal_todo(
                registry_path=self.registry_path,
                goal_id=goal_id,
                todo_id=str(parameters["todo_id"]),
                note=parameters.get("note"),
                no_followup=bool(parameters.get("no_followup", True)),
                successor_todo_ids=parameters.get("successor_todo_ids"),
                agent_id=parameters.get("agent_id"),
                authority_reason="owner-confirmed typed Chat action",
                dry_run=dry_run,
            )
        status = parameters.get("status")
        if operation == "block":
            status = "blocked"
        elif operation == "defer":
            status = "deferred"
        return update_goal_todo(
            registry_path=self.registry_path,
            goal_id=goal_id,
            todo_id=str(parameters["todo_id"]),
            text=parameters.get("text"),
            status=status,
            note=parameters.get("note"),
            claimed_by=(
                parameters.get("agent_id") if operation == "reassign" else None
            ),
            resume_when=parameters.get("resume_when"),
            successor_todo_ids=parameters.get("successor_todo_ids"),
            agent_id=parameters.get("agent_id"),
            authority_reason="owner-confirmed typed Chat action",
            dry_run=dry_run,
        )

    def _apply_todo_update(
        self, proposal_id: str, proposal: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        from .chat_actions import _digest, _opaque

        goal_id = str(parameters["goal_id"])
        current_fingerprint = self._goal_state_fingerprint(goal_id)
        if current_fingerprint != proposal.get("expected_state_fingerprint"):
            stale = self.store.apply(
                proposal_id, current_state_fingerprint=current_fingerprint, receipt={}
            )
            return {"proposal": stale, "turn": None}
        operation = str(parameters.get("operation") or "edit")
        result = self._run_todo_update(parameters, dry_run=False)
        todo_id = _opaque(result.get("todo_id"), field="todo_id")
        receipt = {
            "receipt_id": _digest({"proposal_id": proposal_id, "todo_id": todo_id})[
                :32
            ],
            "outcome": (
                "todo_completed"
                if operation == "complete"
                else "todo_updated" if result.get("changed") else "todo_unchanged"
            ),
            "projection_verified": True,
            "resource_ids": {"goal_id": goal_id, "todo_id": todo_id},
        }
        stored = self.store.apply(
            proposal_id, current_state_fingerprint=current_fingerprint, receipt=receipt
        )
        return {"proposal": stored, "turn": None}

    # --- Gate decisions ------------------------------------------------------
    #
    # ``gate.resolve`` covers two targets: one canonical Todo of the Goal, or a
    # Goal-level operator gate that has no Todo behind it. Both are written
    # through the canonical service the CLI names, so the receipt can print the
    # command that reproduces the decision.

    def _common_runtime_root(self) -> str | None:
        value = self._registry().get("common_runtime_root")
        return str(Path(str(value)).expanduser().resolve()) if value else None

    def _gate_target_todo(self, goal_id: str, todo_id: str | None) -> dict[str, Any] | None:
        """Return the canonical Todo behind an id, or None when there is none."""

        if not todo_id:
            return None
        state_path = self._goal_state_path(goal_id)
        try:
            state_text = state_path.read_text(encoding="utf-8")
        except OSError:
            return None
        try:
            parsed = parse_active_state_todos(
                state_text,
                goal=self._goal(goal_id),
                state_path=state_path,
                item_limit=_GATE_TODO_SCAN_LIMIT,
            )
        except (KeyError, ValueError):
            return None
        for key in ("user_todos", "agent_todos"):
            group = parsed.get(key)
            if not isinstance(group, dict):
                continue
            for item in _todo_group_items(group):
                if str(item.get("todo_id") or "") == todo_id:
                    return item
        return None

    def _gate_actor(
        self, goal_id: str, target: dict[str, Any], requested: Any
    ) -> str | None:
        """The Agent whose lane carries the decision, as the CLI would name it."""

        if requested:
            return str(requested)
        registered = registered_agent_ids_for_goal(self._goal(goal_id))
        bound = str(target.get("bound_agent") or "").strip()
        if bound and bound in registered:
            return bound
        if len(registered) <= 1:
            return None
        from .chat_actions import ProtectedActionGate

        raise ProtectedActionGate(
            "gate.resolve",
            gate={
                "kind": "gate_actor_required",
                "summary": (
                    f"{goal_id} registers several Agents, but this Todo is not bound "
                    "to one of them, so the workspace cannot write on its behalf."
                ),
                "next_action": (
                    "Bind an Agent to this user Todo, or run the matching "
                    "loopx todo command with --agent-id from the terminal."
                ),
            },
        )

    @staticmethod
    def _gate_todo_is_open(target: dict[str, Any] | None) -> bool:
        if target is None:
            return False
        return str(target.get("status") or "open") == "open" and not target.get("done")

    @staticmethod
    def _canonical_todo_command(
        goal_id: str,
        todo_id: str,
        decision: str,
        *,
        is_user_gate: bool,
        agent_id: str | None,
    ) -> str:
        parts = ["loopx todo complete", f"--goal-id {goal_id}", f"--todo-id {todo_id}"]
        if agent_id:
            parts.append(f"--agent-id {agent_id}")
        if is_user_gate:
            parts.append(f"--decision-outcome {decision}")
        parts.append("--no-follow-up")
        return " ".join(parts)

    @staticmethod
    def _canonical_supersede_command(goal_id: str, todo_id: str, reason: str) -> str:
        return (
            f"loopx todo supersede --goal-id {goal_id} --todo-id {todo_id} "
            f'--reason "{reason}"'
        )

    @staticmethod
    def _canonical_operator_gate_command(goal_id: str, gate: str, decision: str, reason: str) -> str:
        return (
            f"loopx project operator-gate --goal-id {goal_id} --gate {gate} "
            f'--decision {decision} --reason-summary "{reason}"'
        )

    def _run_gate_resolve(
        self, parameters: dict[str, Any], target: dict[str, Any] | None, *, dry_run: bool
    ) -> dict[str, Any]:
        """Write one Owner decision through its canonical service."""

        from .chat_actions import ProtectedActionGate

        goal_id = str(parameters["goal_id"])
        decision = str(parameters["decision"])
        note = parameters.get("note")
        if target is None:
            gate = str(parameters.get("gate_id") or "")
            if not gate:
                # Neither a current Todo nor a named operator gate: never write
                # against a guessed target.
                raise ProtectedActionGate(
                    "gate.resolve",
                    gate={
                        "kind": "gate_target_unresolved",
                        "summary": "This decision is not linked to a current Todo or operator gate.",
                        "next_action": "Re-check the Goal status and preview the decision again.",
                    },
                )
            if decision not in OPERATOR_GATE_DECISIONS:
                raise ProtectedActionGate(
                    "gate.resolve",
                    gate={
                        "kind": "gate_decision_unsupported",
                        "summary": (
                            f"The operator gate `{gate}` records "
                            f"{', '.join(sorted(OPERATOR_GATE_DECISIONS))} decisions."
                        ),
                        "next_action": "Record the decision as approve, reject, or defer.",
                    },
                )
            reason = f"Owner {decision} via the LoopX workspace for gate {gate}."
            payload = record_operator_gate(
                registry_path=self.registry_path,
                runtime_root_override=self._common_runtime_root(),
                goal_id=goal_id,
                gate=gate,
                decision=decision,
                operator_question=None,
                reason_summary=reason,
                follow_up=None,
                agent_command=None,
                recommended_action=None,
                recorded_at=None,
                dry_run=dry_run,
                sync_global=True,
            )
            payload["canonical"] = "operator_gate"
            payload["canonical_command"] = self._canonical_operator_gate_command(
                goal_id, gate, decision, reason
            )
            return payload
        todo_id = str(target.get("todo_id") or "")
        role = str(target.get("role") or "") or None
        is_user_gate = role == "user" and str(target.get("task_class") or "") == TODO_TASK_CLASS_USER_GATE
        if decision == "defer":
            raise ProtectedActionGate(
                "gate.resolve",
                gate={
                    "kind": "gate_defer_requires_condition",
                    "summary": "A deferred decision needs an evaluable resume condition.",
                    "next_action": "Use the Later action on the preview, or add a resume condition.",
                },
            )
        if decision == "reject" and not is_user_gate:
            reason = str(note or "").strip() or "Owner rejected this Todo from the LoopX workspace."
            payload = supersede_goal_todo(
                registry_path=self.registry_path,
                goal_id=goal_id,
                runtime_root_arg=self._common_runtime_root(),
                todo_id=todo_id,
                role=role,
                reason=reason,
                agent_id=self._gate_actor(goal_id, target, parameters.get("agent_id")),
                authority_reason="owner-confirmed typed Chat action",
                dry_run=dry_run,
            )
            payload["canonical"] = "todo_supersede"
            payload["canonical_command"] = self._canonical_supersede_command(goal_id, todo_id, reason)
            actor = payload.get("agent_id")
            if actor:
                payload["actor_agent_id"] = str(actor)
            return payload
        actor = self._gate_actor(goal_id, target, parameters.get("agent_id"))
        payload = complete_goal_todo(
            registry_path=self.registry_path,
            goal_id=goal_id,
            runtime_root_arg=self._common_runtime_root(),
            todo_id=todo_id,
            role=role,
            decision_outcome=decision if is_user_gate else None,
            note=note,
            no_followup=True,
            agent_id=actor,
            authority_reason="owner-confirmed typed Chat action",
            dry_run=dry_run,
        )
        payload["canonical"] = "todo_complete"
        payload["canonical_command"] = self._canonical_todo_command(
            goal_id, todo_id, decision, is_user_gate=is_user_gate, agent_id=actor
        )
        if actor:
            payload["actor_agent_id"] = actor
        return payload

    def _apply_gate_resolve(
        self, proposal_id: str, proposal: dict[str, Any], parameters: dict[str, Any]
    ) -> dict[str, Any]:
        from .chat_actions import _digest

        goal_id = str(parameters["goal_id"])
        decision = str(parameters["decision"])
        todo_id = str(parameters.get("todo_id") or "")
        gate_id = str(parameters.get("gate_id") or "")
        target = self._gate_target_todo(goal_id, todo_id)
        current_fingerprint = self._goal_state_fingerprint(goal_id)
        expected = str(proposal.get("expected_state_fingerprint") or "")
        # Previews created before gate decisions were fingerprinted per Goal
        # carry the registry digest. Honour them while their Todo is still open,
        # then store the Goal-scoped fingerprint on the applied proposal.
        legacy_open = (
            expected == self._registry_fingerprint()
            and (target is None or self._gate_todo_is_open(target))
        )
        if expected != current_fingerprint and not legacy_open:
            stale = self.store.apply(
                proposal_id, current_state_fingerprint=current_fingerprint, receipt={}
            )
            return {"proposal": stale, "turn": None}
        result = self._run_gate_resolve(parameters, target, dry_run=False)
        resource_ids: dict[str, Any] = {"goal_id": goal_id, "decision": decision}
        if todo_id:
            resource_ids["todo_id"] = todo_id
        if gate_id:
            resource_ids["gate_id"] = gate_id
        actor = result.get("actor_agent_id")
        if actor:
            resource_ids["actor_agent_id"] = str(actor)
        receipt = {
            "receipt_id": _digest(
                {
                    "proposal_id": proposal_id,
                    "goal_id": goal_id,
                    "todo_id": todo_id,
                    "gate_id": gate_id,
                    "decision": decision,
                }
            )[:32],
            "outcome": "gate_resolved",
            "projection_verified": True,
            "resource_ids": resource_ids,
            "canonical": {
                "service": str(result.get("canonical") or ""),
                "changed": bool(result.get("changed", True)),
            },
            "canonical_command": str(result.get("canonical_command") or ""),
        }
        stored = self.store.apply(
            proposal_id, current_state_fingerprint=current_fingerprint, receipt=receipt
        )
        return {"proposal": stored, "turn": None}
