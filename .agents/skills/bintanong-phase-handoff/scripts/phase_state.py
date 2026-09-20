#!/usr/bin/env python3
"""Inspect and validate Bintanong phase plans, checkpoints, and handoffs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACTIVE_PLAN_STATUSES = {"ready", "in_progress"}


@dataclass(frozen=True)
class Artifact:
    path: Path
    metadata: dict[str, Any]

    @property
    def phase(self) -> int:
        return int(self.metadata["phase"])

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", ""))


def scalar(value: str) -> Any:
    value = value.strip()
    if value in {"null", "~"}:
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def frontmatter(path: Path) -> dict[str, Any] | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    metadata: dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line in {path}: {line!r}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = scalar(value)
    raise ValueError(f"unterminated frontmatter in {path}")


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )


def relative(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def inspect(repo: Path) -> dict[str, Any]:
    plans_dir = repo / "plans"
    errors: list[str] = []
    warnings: list[str] = []
    by_kind: dict[str, dict[int, list[Artifact]]] = {
        "phase-plan": {},
        "phase-checkpoint": {},
        "phase-handoff": {},
    }

    if not plans_dir.is_dir():
        errors.append("plans directory is missing")
    else:
        for path in sorted(plans_dir.glob("*.md")):
            try:
                metadata = frontmatter(path)
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
                continue
            if not metadata or metadata.get("artifact") not in by_kind:
                continue
            kind = str(metadata["artifact"])
            if "phase" not in metadata:
                errors.append(f"{relative(path, repo)} is missing phase metadata")
                continue
            try:
                artifact = Artifact(path, metadata)
                phase = artifact.phase
            except (TypeError, ValueError):
                errors.append(f"{relative(path, repo)} has an invalid phase")
                continue
            by_kind[kind].setdefault(phase, []).append(artifact)

    for kind, phases in by_kind.items():
        for phase, artifacts in phases.items():
            if len(artifacts) > 1:
                errors.append(f"duplicate {kind} artifacts for phase {phase}")

    phase_numbers = sorted(by_kind["phase-plan"])
    if phase_numbers:
        expected = list(range(phase_numbers[0], phase_numbers[-1] + 1))
        if phase_numbers[0] != 0 or phase_numbers != expected:
            errors.append(f"phase plan sequence has gaps: {phase_numbers}")

    for phase in by_kind["phase-handoff"]:
        if phase not in by_kind["phase-plan"]:
            errors.append(f"phase {phase} handoff has no matching phase plan")
    for phase in by_kind["phase-checkpoint"]:
        if phase not in by_kind["phase-plan"]:
            errors.append(f"phase {phase} checkpoint has no matching phase plan")

    active_plans = [
        artifacts[0]
        for artifacts in by_kind["phase-plan"].values()
        if len(artifacts) == 1 and artifacts[0].status in ACTIVE_PLAN_STATUSES
    ]
    if len(active_plans) > 1:
        errors.append("multiple active phase plans")
    active_plan = active_plans[0] if len(active_plans) == 1 else None

    active_checkpoint: Artifact | None = None
    if active_plan:
        checkpoints = by_kind["phase-checkpoint"].get(active_plan.phase, [])
        if len(checkpoints) == 1:
            active_checkpoint = checkpoints[0]
        for phase in by_kind["phase-checkpoint"]:
            if phase != active_plan.phase:
                errors.append(
                    f"checkpoint phase {phase} does not match active plan phase {active_plan.phase}"
                )

    head_result = git(repo, "rev-parse", "HEAD")
    head = head_result.stdout.strip() if head_result.returncode == 0 else None
    if head is None:
        errors.append("repository HEAD could not be read")

    status_result = git(repo, "status", "--porcelain")
    dirty = bool(status_result.stdout.strip()) if status_result.returncode == 0 else True
    if status_result.returncode != 0:
        errors.append("working tree status could not be read")
    elif dirty:
        warnings.append("working tree is dirty; inspect and preserve its changes before resuming")

    if active_checkpoint and head:
        recorded = str(active_checkpoint.metadata.get("head_commit", ""))
        if not recorded or not head.startswith(recorded):
            warnings.append(
                f"checkpoint head_commit {recorded or '<missing>'} differs from repository HEAD {head}"
            )
        recorded_tree = str(active_checkpoint.metadata.get("working_tree", ""))
        if recorded_tree == "clean" and dirty:
            warnings.append("checkpoint records a clean working tree but the working tree is dirty")

    latest_phase = max(phase_numbers) if phase_numbers else None
    latest_handoff: Artifact | None = None
    if latest_phase is not None:
        handoffs = by_kind["phase-handoff"].get(latest_phase, [])
        if len(handoffs) == 1:
            latest_handoff = handoffs[0]

    advance_reasons: list[str] = []
    can_advance = False
    next_phase: int | None = None
    if latest_phase is None:
        advance_reasons.append("no phase plan exists")
    elif latest_handoff is None:
        advance_reasons.append(f"phase {latest_phase} has no complete handoff")
    elif latest_handoff.status == "complete":
        can_advance = True
        next_phase = int(latest_handoff.metadata.get("next_phase", latest_phase + 1))
    elif latest_handoff.status == "blocked":
        advance_reasons.append(f"phase {latest_phase} handoff is blocked")
    else:
        advance_reasons.append(
            f"phase {latest_phase} handoff status is {latest_handoff.status or '<missing>'}, not complete"
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "active_phase": active_plan.phase if active_plan else None,
        "active_plan": relative(active_plan.path, repo) if active_plan else None,
        "active_checkpoint": relative(active_checkpoint.path, repo) if active_checkpoint else None,
        "latest_handoff": relative(latest_handoff.path, repo) if latest_handoff else None,
        "head_commit": head,
        "working_tree_dirty": dirty,
        "can_advance": can_advance and not errors,
        "next_phase": next_phase if can_advance and not errors else None,
        "advance_reasons": advance_reasons if not can_advance else [],
    }


def human(payload: dict[str, Any]) -> str:
    lines = [
        f"State: {'valid' if payload['valid'] else 'invalid'}",
        f"Active phase: {payload['active_phase']}",
        f"Active plan: {payload['active_plan']}",
        f"Checkpoint: {payload['active_checkpoint']}",
        f"Latest handoff: {payload['latest_handoff']}",
        f"Working tree: {'dirty' if payload['working_tree_dirty'] else 'clean'}",
        f"Can advance: {'yes' if payload['can_advance'] else 'no'}",
    ]
    lines.extend(f"ERROR: {item}" for item in payload["errors"])
    lines.extend(f"WARNING: {item}" for item in payload["warnings"])
    lines.extend(f"ADVANCE: {item}" for item in payload["advance_reasons"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "validate", "can-advance"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    payload = inspect(repo)
    print(json.dumps(payload, indent=2) if args.json else human(payload))

    if args.command == "inspect":
        return 0 if payload["valid"] else 1
    if args.command == "validate":
        return 0 if payload["valid"] else 1
    return 0 if payload["can_advance"] else 1


if __name__ == "__main__":
    sys.exit(main())
