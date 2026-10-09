"""Phase 1 Task 3, fix pass 3: the decision record states the limits that tests pin."""

from __future__ import annotations

from pathlib import Path

import pytest

RECORD = (Path(__file__).resolve().parents[1] / "docs" / "decisions" / "phase-01-contracts.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("text", ["Fact-Sheet-2024.pdf", "BS-Fact-1", "doc-to-doc", "Conflict-free-zone"])
def test_the_known_false_positives_of_the_scan_are_listed(text):
    assert text in RECORD


def test_the_raw_text_limit_of_the_table_serialization_hash_is_listed():
    assert "raw text" in RECORD and "content_hash_mismatch" in RECORD


@pytest.mark.parametrize("text", ["prolog_quote", "rendering must quote", "FrozenDict", "model_copy", "owner decision 22"])
def test_the_new_owner_decisions_and_design_change_are_recorded(text):
    assert text.lower() in RECORD.lower()


def test_the_authorization_date_wording_covers_all_relied_evidence():
    assert "ANY evidence the approved or revoked state relies on" in RECORD
    assert "must not be dated before the acquisition or scope evidence it relies on" not in RECORD


def test_the_record_no_longer_claims_a_value_cannot_carry_prolog():
    assert "cannot carry Prolog syntax" not in RECORD
