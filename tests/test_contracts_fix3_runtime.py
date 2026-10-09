"""Phase 1 Task 3, fix pass 3, M1: a bound value is DATA; the fixed renderer quotes it.

The shapes below are synthetic. They copy the SHAPES of the real course codes found in the cached
BSBA-HRM and IT prospectuses (bare capitals, letter+digits, colon forms with spaces) without carrying any
institutional data.
"""

from __future__ import annotations

import random
import string

import pytest
from pydantic import ValidationError

from backend.bintanong_contracts import runtime
from backend.bintanong_contracts.base import ContractError

SHAPES = ["HBO", "TQM", "P2101", "P2108", "E2101", "E2104", "Practicum", "GE- Elect: EM", "GE-Elect: PES",
          "CS 101", "GE-ET", "ITEC 101", "FICTIONAL-101", "CS101", "X", "Y1", "_foo", "A_B", "is", "mod", "-", "..",
          "a'b", "a\\b", ":- foo", "x), halt(", "a;b", "50% (lab)", "\u00d1and\u00fa 1"]


def value(v):
    return {"name": "course", "value": v, "fact_ref": None}


def unquote(atom: str) -> str:
    """An independent reader of a single-quoted Prolog atom: the whole text must be ONE quoted atom."""
    assert len(atom) >= 2 and atom[0] == "'" and atom[-1] == "'", atom
    out, i, body = [], 0, atom[1:-1]
    while i < len(body):
        ch = body[i]
        assert ch != "'", f"unescaped quote inside {atom!r}"
        if ch == "\\":
            i += 1
            assert i < len(body) and body[i] in "\\'", f"bad escape in {atom!r}"
            ch = body[i]
        out.append(ch)
        i += 1
    return "".join(out)


@pytest.mark.parametrize("v", SHAPES)
def test_every_real_shape_parses_and_renders_as_one_quoted_atom(v):
    assert runtime.BoundInput.parse(value(v)).value == v
    atom = runtime.prolog_quote(v)
    assert unquote(atom) == v


def test_quoting_is_exact_for_the_dangerous_values():
    assert runtime.prolog_quote("X") == "'X'"
    assert runtime.prolog_quote("HBO") == "'HBO'"
    assert runtime.prolog_quote("a'b") == "'a\\'b'"
    assert runtime.prolog_quote("a\\b") == "'a\\\\b'"
    assert runtime.prolog_quote(":- foo") == "':- foo'"


def test_quoting_round_trips_over_random_printable_text():
    rng = random.Random(20261007)
    alphabet = string.printable[:-5] + "'\\'\\\u00e9\u03a9"
    for _ in range(500):
        v = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 20))).strip()
        if not v or "  " in v:
            continue
        assert unquote(runtime.prolog_quote(v)) == v


@pytest.mark.parametrize("v", ["a\x00b", "a\nb", "a\rb", "a\tb", "a\x1fb", "a\x7fb", "a\x85b", "a\u202eb", "a\u200bb", "a\u00adb", "a\ue000b", "a\u0378b",
                               "a\u00a0b", "a\u2028b", "a\ud800b", ""])
def test_the_renderer_refuses_control_and_format_characters(v):
    with pytest.raises(ContractError, match="control|format|empty|printable"):
        runtime.prolog_quote(v)


@pytest.mark.parametrize("v", ["a\x00b", "a\nb", "a\rb", "a\tb", "a\x1fb", "a\x7fb", "a\u202eb", "a\u200bb", "a\u00a0b", "",
                               " CS 101", "CS 101 ", "CS  101", "x" * (runtime.BOUND_VALUE_MAX + 1)])
def test_a_bound_value_still_refuses_control_padding_empty_and_over_long(v):
    with pytest.raises(ValidationError, match='printable text|padding|at least 1 character|at most'):
        runtime.BoundInput.parse(value(v))


@pytest.mark.parametrize("v", [None, 5, b"abc", ["a"]])
def test_the_renderer_quotes_text_only(v):
    with pytest.raises(ContractError, match="cannot quote a"):
        runtime.prolog_quote(v)


def test_the_value_cap_is_the_documented_default():
    assert runtime.BOUND_VALUE_MAX == 128


def test_the_longest_allowed_value_parses_and_renders():
    v = "x" * runtime.BOUND_VALUE_MAX
    assert runtime.BoundInput.parse(value(v)).value == v
    assert unquote(runtime.prolog_quote(v)) == v


def test_the_predicate_name_rule_is_unchanged():
    for name in ("can_enroll", "a", "p2_check"):
        runtime.PredicateRequest.parse({"predicate": name, "inputs": []})
    for name in ("Can", "a b", "a-b", "a(", "_a", "1a", "a:-b", "a.", ""):
        with pytest.raises(ValidationError, match="String should match pattern '\\^\\[a\\-z\\]\\[a\\-z0\\-9_\\]\\*\\$"):
            runtime.PredicateRequest.parse({"predicate": name, "inputs": []})


def test_the_docs_say_data_not_cannot_carry_syntax():
    text = runtime.__doc__ + open(runtime.__file__, encoding="utf-8").read()
    assert "cannot carry Prolog" not in text
    assert "rendering must quote" in text
