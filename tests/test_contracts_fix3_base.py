"""Phase 1 Task 3, fix pass 3, L-a: the namespace scan reads text the way a person does.

Invisible format characters, percent escapes and look-alike letters from other scripts must not hide a
foreign id. The known false positives of the scan (institutional file names, ordinary hyphenated words) are
pinned here on purpose: they are an owner decision, recorded in the decision record, not a silent quirk."""

from __future__ import annotations

import pytest

from backend.bintanong_contracts import base

PRIVATE = "institutional"      # scanning an institutional record for private ids
SESSION = "private_session"    # scanning a private record for institutional ids


@pytest.mark.parametrize("text", [
    "\u0455ess-synth-0001",              # Cyrillic dze, which prints as s
    "fa\u0441t-synth-0001",              # Cyrillic es inside
    "fact\u200b-synth-0001",             # zero-width space
    "fact\u200d-synth-0001",             # zero-width joiner
    "fa\u00adct-synth-0001",             # soft hyphen
    "fact-\u2060synth-0001",             # word joiner
    "\ufefffact-synth-0001",             # byte order mark
    "fact%2dsynth-0001", "fact%2Dsynth-0001", "fact%252dsynth-0001", "see%20fact-synth-0001",
    "%66act-synth-0001",                 # %66 is f
    "s\u0435ss-synth-0001",              # Cyrillic ie
    "sess-synth-0001\u200b",
])
def test_a_private_id_cannot_hide_from_the_scan(text):
    assert base.foreign_ids({"v": text}, PRIVATE), text


@pytest.mark.parametrize("text", [
    "d\u03bfc-synth-handbook",           # Greek omicron
    "\u03bdersion-synth-1".replace("\u03bdersion", "\u03bder"),      # Greek nu: 'ver'
    "\u0435dition-synth-1",              # Cyrillic ie
    "\u0441\u043enflict-synth-0001",     # Cyrillic es and o
    "doc\u200d-synth-handbook", "ver-\u2060synth-1", "ver%2dsynth-1", "edition%2Dsynth-1", "conflict\u00ad-synth-1",
])
def test_an_institutional_id_cannot_hide_inside_a_private_record(text):
    assert base.foreign_ids({"v": text}, SESSION), text


@pytest.mark.parametrize("text", [
    "Fact-checking Office of Records", "edition-specific wording", "50% off", "100%", "Fact%20sheet", "%zz-fact",
    "\u041f\u0440\u0438\u0432\u0435\u0442 \u043c\u0438\u0440", "\u03a0\u03b1\u03c1\u03ac\u03b4\u03b5\u03b9\u03b3\u03bc\u03b1", "caf\u00e9 society",
    "xfact-synth-0001", "verification", "sess", "zero\u200bwidth words", "doc",
])
def test_ordinary_text_is_still_not_an_id(text):
    assert base.foreign_ids({"v": text}, PRIVATE) == []
    assert base.foreign_ids({"v": text}, SESSION) == []


def test_a_cyrillic_es_prints_as_c_not_s():
    # "\u0441ess" reads "cess", which is not a private prefix; only the look-alike of the real prefix letter counts
    assert base.foreign_ids({"v": "\u0441ess-synth-0001"}, PRIVATE) == []


def test_the_keys_of_a_mapping_are_scanned_too():
    assert base.foreign_ids({"fact-synth-0001": "x"}, PRIVATE)
    assert base.foreign_ids({"a": {"sess-synth-0001": [1]}}, PRIVATE)
    assert base.foreign_ids({"ver-synth-1": "x"}, SESSION)


def test_strip_format_removes_only_format_characters():
    assert base.strip_format("a\u200bb\u00adc\u200dd\ufeffe") == "abcde"
    assert base.strip_format("caf\u00e9 \u0441") == "caf\u00e9 \u0441"
    assert base.strip_format("") == ""


# ---------------------------------------------------------------- known false positives (owner decision)
def test_known_false_positives_are_pinned_not_hidden():
    # An institutional file name or hyphenated phrase that reads like an id of the other namespace is flagged.
    # A safe tightening does not exist (see the decision record), so the scan stays strict.
    assert base.foreign_ids({"v": "Fact-Sheet-2024.pdf"}, PRIVATE) == ["fact-sheet-2024"]
    assert base.foreign_ids({"v": "BS-Fact-1"}, PRIVATE) == ["fact-1"]
    assert base.foreign_ids({"v": "doc-to-doc review"}, SESSION) == ["doc-to-doc"]
    assert base.foreign_ids({"v": "Conflict-free-zone"}, SESSION) == ["conflict-free-zone"]


# the closed look-alike map, written out by hand so that a removed or changed entry is noticed
CONFUSABLES = {
    "\u0430": "a", "\u0441": "c", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0455": "s", "\u0456": "i",
    "\u0501": "d", "\u0445": "x", "\u0475": "v", "\u0442": "t", "\u0433": "r", "\u043f": "n",
    "\u03b1": "a", "\u03b5": "e", "\u03bf": "o", "\u03c1": "p", "\u03b9": "i", "\u03bd": "v", "\u03c4": "t",
    "\u03c7": "x", "\u03b7": "n", "\u0131": "i", "\u0251": "a", "\u0192": "f"}


def test_the_look_alike_map_is_exactly_the_reviewed_one():
    assert {chr(k): v for k, v in base._CONFUSABLES.items()} == CONFUSABLES
    assert set(CONFUSABLES.values()) == set("acepsidxvtrnfo")


@pytest.mark.parametrize("char,letter", list(CONFUSABLES.items()))
def test_each_look_alike_reads_as_its_latin_letter(char, letter):
    assert base.scan_form(char) == letter


def test_scan_form_decodes_up_to_three_layers_and_no_more():
    assert base.scan_form("%2566") == "f"                    # %25 -> % -> %66 -> f
    assert base.scan_form("%252566") == "f"
    assert base.scan_form("%25252566") == "%66"             # a fourth layer is left alone
    assert base.scan_form("100%") == "100%"


def test_every_look_alike_survives_folding_so_it_can_fire():
    # the map is applied after NFKC and casefold; a key those would change (final sigma) could never match
    assert all(base.folded(chr(k)) == chr(k) for k in base._CONFUSABLES)
