from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "phase_state.py"


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--repo", str(cwd), "--json"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def write_artifact(path: Path, metadata: dict[str, object], body: str = "# Artifact\n") -> None:
    lines = ["---"]
    for key, value in metadata.items():
        if value is None:
            rendered = "null"
        elif isinstance(value, bool):
            rendered = str(value).lower()
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    lines.extend(["---", "", body])
    path.write_text("\n".join(lines), encoding="utf-8")


class PhaseStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo = Path(self.tempdir.name)
        (self.repo / "plans").mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "tests@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "Phase Tests"], cwd=self.repo, check=True)
        (self.repo / "plans" / "master.md").write_text("# Master\n", encoding="utf-8")
        write_artifact(
            self.repo / "plans" / "phase-00-plan.md",
            {
                "artifact": "phase-plan",
                "phase": 0,
                "status": "in_progress",
                "master": "plans/master.md",
                "previous_handoff": None,
            },
        )
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=self.repo, check=True)
        self.head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, text=True, capture_output=True, check=True
        ).stdout.strip()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def checkpoint(self, *, status: str = "in_progress", head: str | None = None, phase: int = 0) -> None:
        write_artifact(
            self.repo / "plans" / "phase-00-checkpoint.md",
            {
                "artifact": "phase-checkpoint",
                "phase": phase,
                "status": status,
                "sequence": 1,
                "plan": "plans/phase-00-plan.md",
                "head_commit": head or self.head,
                "working_tree": "clean",
                "updated_at": "2026-09-20T12:00:00Z",
            },
        )

    def handoff(self, status: str) -> None:
        write_artifact(
            self.repo / "plans" / "phase-00-handoff.md",
            {
                "artifact": "phase-handoff",
                "phase": 0,
                "status": status,
                "plan": "plans/phase-00-plan.md",
                "final_commit": self.head,
                "next_phase": 1,
                "completed_at": "2026-09-20T13:00:00Z",
            },
        )

    def test_inspect_reports_active_phase_and_refuses_advance_without_handoff(self) -> None:
        self.checkpoint()
        result = run("inspect", cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["active_phase"], 0)
        self.assertEqual(payload["active_plan"], "plans/phase-00-plan.md")
        self.assertFalse(payload["can_advance"])
        self.assertIn("complete handoff", " ".join(payload["advance_reasons"]).lower())

    def test_validate_rejects_duplicate_phase_plans(self) -> None:
        write_artifact(
            self.repo / "plans" / "phase-00-other.md",
            {"artifact": "phase-plan", "phase": 0, "status": "ready", "master": "plans/master.md"},
        )
        result = run("validate", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate", result.stdout.lower())

    def test_validate_rejects_checkpoint_for_different_phase(self) -> None:
        self.checkpoint(phase=1)
        result = run("validate", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checkpoint phase", result.stdout.lower())

    def test_validate_rejects_checkpoint_without_matching_plan(self) -> None:
        (self.repo / "plans" / "phase-00-plan.md").unlink()
        self.checkpoint()
        result = run("validate", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checkpoint", result.stdout.lower())
        self.assertIn("matching phase plan", result.stdout.lower())

    def test_validate_rejects_phase_sequence_gap(self) -> None:
        write_artifact(
            self.repo / "plans" / "phase-02-plan.md",
            {
                "artifact": "phase-plan",
                "phase": 2,
                "status": "complete",
                "master": "plans/master.md",
            },
        )
        result = run("validate", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sequence has gaps", result.stdout.lower())

    def test_inspect_warns_when_checkpoint_commit_is_stale(self) -> None:
        old_head = self.head
        (self.repo / "newer.txt").write_text("newer commit", encoding="utf-8")
        subprocess.run(["git", "add", "newer.txt"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "newer"], cwd=self.repo, check=True)
        self.checkpoint(head=old_head)
        result = run("inspect", cwd=self.repo)
        payload = json.loads(result.stdout)
        self.assertTrue(any("head_commit" in warning for warning in payload["warnings"]))

    def test_inspect_warns_when_working_tree_is_dirty(self) -> None:
        self.checkpoint()
        (self.repo / "plans" / "master.md").write_text("# changed\n", encoding="utf-8")
        (self.repo / "untracked.txt").write_text("resume me", encoding="utf-8")
        result = run("inspect", cwd=self.repo)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["working_tree_dirty"])
        self.assertTrue(any("working tree" in warning.lower() for warning in payload["warnings"]))
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        self.assertIn(" M plans/master.md", status)
        self.assertIn("?? untracked.txt", status)

    def test_completed_checkpoint_does_not_authorize_advance(self) -> None:
        self.checkpoint(status="superseded")
        result = run("can-advance", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["can_advance"])

    def test_complete_handoff_authorizes_next_phase(self) -> None:
        self.checkpoint(status="superseded")
        self.handoff("complete")
        result = run("can-advance", cwd=self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["can_advance"])
        self.assertEqual(payload["next_phase"], 1)

    def test_blocked_handoff_refuses_advance(self) -> None:
        self.checkpoint(status="blocked")
        self.handoff("blocked")
        result = run("can-advance", cwd=self.repo)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["can_advance"])
        self.assertTrue(any("blocked" in reason.lower() for reason in payload["advance_reasons"]))


if __name__ == "__main__":
    unittest.main()
