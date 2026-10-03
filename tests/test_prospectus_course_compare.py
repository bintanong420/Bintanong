import copy
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prospectus_course_compare", Path(__file__).resolve().parents[1] / "scripts" / "prospectus_course_compare.py"
)
compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare)


def payload():
    return {
        "courses": [{"course_code": "CS 101", "course_title": "Intro", "total_units": 3}],
        "audit": {"status": "ok", "total_courses": 1},
    }


def test_identical_payloads_have_no_differences_and_timestamps_are_ignored():
    new = payload()
    new["generated_at"] = "later"
    assert compare.compare_payloads(payload(), new) == []


def test_one_changed_course_field_is_reported():
    new = copy.deepcopy(payload())
    new["courses"][0]["course_title"] = "Changed"
    assert compare.compare_payloads(payload(), new) == ["course 0 differs: ['course_title']"]


def test_audit_and_count_changes_are_reported():
    new = payload()
    new["audit"]["status"] = "error"
    new["courses"].append(dict(new["courses"][0]))
    issues = compare.compare_payloads(payload(), new)
    assert any(i.startswith("audit differs") for i in issues) and any("course count" in i for i in issues)


# --- the gate must fail on missing outputs and cell mismatches ---

import subprocess  # noqa: E402

import pytest  # noqa: E402


def _run_folder(root, name, exit_code, candidate=None):
    folder = root / name / "01"
    folder.mkdir(parents=True)
    (folder / "source.txt").write_text("x_docling.json", encoding="utf-8")
    (folder / "exit.txt").write_text(str(exit_code), encoding="utf-8")
    if candidate is not None:
        (folder / "candidate.json").write_text(__import__("json").dumps(candidate), encoding="utf-8")
    return folder


@pytest.mark.parametrize("code", [0, 1])
def test_neither_side_writing_candidate_json_is_a_failure(tmp_path, code):
    _run_folder(tmp_path, "old", code)
    _run_folder(tmp_path, "new", code)
    assert compare.compare_runs(tmp_path / "old", tmp_path / "new", check_markup=False) == 1


def test_both_sides_exiting_nonzero_is_a_failure_even_with_candidates(tmp_path):
    _run_folder(tmp_path, "old", 1, payload())
    _run_folder(tmp_path, "new", 1, payload())
    assert compare.compare_runs(tmp_path / "old", tmp_path / "new", check_markup=False) == 1


def test_matching_successful_runs_still_pass(tmp_path):
    _run_folder(tmp_path, "old", 0, payload())
    _run_folder(tmp_path, "new", 0, payload())
    assert compare.compare_runs(tmp_path / "old", tmp_path / "new", check_markup=False) == 0


def _twin(tmp_path, ids):
    cells = "".join(f'<td data-cell="{i}">x</td>' for i in ids)
    (tmp_path / "candidate_prospectus.md").write_text(
        f"<!-- extraction_audit: ok | x -->\n<table><tr>{cells}</tr></table>\n", encoding="utf-8"
    )
    return {"audit": {"status": "ok"}, "evidence": {"canonical_cell_count": len(ids)}}


def test_markup_cell_ids_must_equal_the_evidence_ids_not_just_their_count(tmp_path):
    result = _twin(tmp_path, ["t0-c0", "t0-c0"])  # right count, one id duplicated, one missing
    problems = compare.markup_problems(tmp_path, result, expected_ids=["t0-c0", "t0-c1"])
    assert problems and any("t0-c1" in p for p in problems)
    assert compare.markup_problems(tmp_path, result, expected_ids=["t0-c0", "t0-c0"]) == []


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout.strip()


def test_existing_worktree_must_be_at_the_requested_ref(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "one")
    first = _git(repo, "rev-parse", "HEAD")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "two")
    tree = tmp_path / "wt"
    assert compare.ensure_worktree(first, tree, repo=repo) == tree
    assert compare.ensure_worktree(first, tree, repo=repo) == tree  # reused at the right commit
    with pytest.raises(SystemExit):
        compare.ensure_worktree("HEAD", tree, repo=repo)  # worktree sits at the first commit, HEAD is the second


def test_run_one_launches_with_absolute_paths(tmp_path, monkeypatch):
    seen = {}

    def fake_run(cmd, **kwargs):
        seen["cmd"], seen["cwd"] = cmd, kwargs["cwd"]
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(compare.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    compare.run_one(Path("tree"), Path("in/x_docling.json"), Path("out/01"), Path("map.md"))
    cmd = seen["cmd"]
    for flag in ("-i", "-o", "--semantic-doc"):
        assert Path(cmd[cmd.index(flag) + 1]).is_absolute()
    assert Path(seen["cwd"]).is_absolute()