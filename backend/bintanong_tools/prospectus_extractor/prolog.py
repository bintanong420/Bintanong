"""Candidate Prolog knowledge base."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Sequence

from .common import RICH_AVAILABLE, SCHEMA_VERSION

if RICH_AVAILABLE:
    from .common import track
from .prerequisites import EXECUTABLE_PREREQUISITE_STATES
from .text import clean_str


def pl_atom(value: Any) -> str:
    """Quote a Prolog atom, doubling single quotes per ISO rules."""
    text = clean_str(value)
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def pl_comment(value: Any) -> str:
    """One line of comment text: a newline in metadata must not end the comment and start a clause."""
    return " ".join(str(value).split())


PROLOG_RULES = """
% --------------------------------------------------------------------------
% Query helpers
% --------------------------------------------------------------------------
unlocks(Prereq, Course) :- prerequisite(Course, Prereq).

prereq_closure(Course, Prereq) :- prerequisite(Course, Prereq).
prereq_closure(Course, Prereq) :-
    prerequisite(Course, Middle),
    prereq_closure(Middle, Prereq).

% eligible(+Course, +PassedCodes): the prerequisite rule is complete and every
% prerequisite has been passed. A course without rule_complete/1 never qualifies.
eligible(Course, Passed) :-
    rule_complete(Course),
    course(Course, _, _, _, _, _, _, _),
    \\+ ( prerequisite(Course, Prereq), \\+ memberchk(Prereq, Passed) ).

% offered_in(+Course, -Year, -Semester)
offered_in(Course, Year, Semester) :-
    course(Course, _, _, _, _, Year, Semester, _).

% term_load(+Year, +Semester, -Units)
term_load(Year, Semester, Units) :-
    findall(U, course(_, _, U, _, _, Year, Semester, _), List),
    sum_list(List, Units).

% curriculum_units(-Units): total units in the program of study.
curriculum_units(Units) :-
    findall(U, course(_, _, U, _, _, _, _, _), List),
    sum_list(List, Units).

% remaining(+PassedCodes, -Course): not yet taken.
remaining(Passed, Course) :-
    course(Course, _, _, _, _, _, _, _),
    \\+ memberchk(Course, Passed).

% next_eligible(+PassedCodes, -Course): take-able right now.
next_eligible(Passed, Course) :-
    remaining(Passed, Course),
    eligible(Course, Passed).
""".strip()


def generate_prolog_knowledge(
    metadata: dict[str, Any],
    courses: Sequence[dict[str, Any]],
    elective_tracks: Sequence[dict[str, Any]],
    term_units: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Emit consult-ready Prolog plus a mirrored relational view for other tools."""
    clauses: list[str] = []
    add = clauses.append

    add("% ===========================================================================")
    add(f"% PalSU prospectus knowledge base: {pl_comment(metadata.get('degree') or metadata.get('program_name'))}")
    add(f"% Curriculum SY: {pl_comment(metadata.get('effective_school_year'))}")
    add(f"% Source: {pl_comment(metadata.get('source_file'))}")
    add(f"% Generated: {datetime.now().isoformat(timespec='seconds')} by {SCHEMA_VERSION}")
    add("% STATUS: review candidate. rule_complete/1 lists courses whose prerequisite cell the")
    add("% extractor fully understood; eligible/2 needs it. Nothing here is approved for active use.")
    add("% ===========================================================================")
    add("")
    add(":- discontiguous course/8.")
    add(":- discontiguous prerequisite/2.")
    add(":- discontiguous standing_requirement/2.")
    add(":- discontiguous elective_option/3.")
    add(":- discontiguous elective_slot/2.")
    add(":- discontiguous term_units/3.")
    add(":- discontiguous prerequisite_state/2.")
    add(":- dynamic rule_complete/1.")
    add("")

    total_units = sum(c.get("total_units") or 0 for c in courses)
    add("% program(CollegeCode, Degree, ProgramName, CollegeName, SchoolYear, TotalUnits).")
    add(
        "program({}, {}, {}, {}, {}, {}).".format(
            pl_atom(metadata.get("college_code") or "UNKNOWN"),
            pl_atom(metadata.get("degree") or "UNKNOWN"),
            pl_atom(metadata.get("program_name") or "UNKNOWN"),
            pl_atom(metadata.get("college_name") or "UNKNOWN"),
            pl_atom(metadata.get("effective_school_year") or "UNKNOWN"),
            total_units,
        )
    )
    add("")

    add("% course(Code, Title, TotalUnits, LectureUnits, LabUnits, YearLevel, Semester, TermIndex).")
    relational_courses: list[dict[str, Any]] = []
    for course in courses:
        units = course.get("units", {})
        add(
            "course({}, {}, {}, {}, {}, {}, {}, {}).".format(
                pl_atom(course["course_code"]),
                pl_atom(course["course_title"]),
                units.get("total") or 0,
                units.get("lecture") or 0,
                units.get("lab") or 0,
                pl_atom(course["year_level"]),
                pl_atom(course["semester"]),
                course.get("term_index", 99),
            )
        )
        relational_courses.append(
            {
                "code": course["course_code"],
                "title": course["course_title"],
                "total_units": units.get("total") or 0,
                "lecture_units": units.get("lecture") or 0,
                "lab_units": units.get("lab") or 0,
                "year_level": course["year_level"],
                "semester": course["semester"],
                "term_index": course.get("term_index"),
                "category": course.get("category"),
            }
        )

    add("")
    add("% course_category(Code, Category).")
    for course in courses:
        add(f"course_category({pl_atom(course['course_code'])}, {pl_atom(course.get('category'))}).")

    add("")
    add("% prerequisite(Course, RequiredCourse).")
    relational_prereqs: list[dict[str, str]] = []
    for course in courses:
        for prereq in course.get("prerequisites", []):
            add(f"prerequisite({pl_atom(course['course_code'])}, {pl_atom(prereq)}).")
            relational_prereqs.append({"course": course["course_code"], "requires": prereq})

    add("")
    add("% standing_requirement(Course, PolicyRule).")
    relational_rules: list[dict[str, str]] = []
    for course in courses:
        for rule in course.get("standing_requirements", []):
            add(f"standing_requirement({pl_atom(course['course_code'])}, {pl_atom(rule)}).")
            relational_rules.append({"course": course["course_code"], "rule": rule})

    add("")
    add("% prerequisite_state(Course, State): how fully the extractor understood the prerequisite cell.")
    relational_states: list[dict[str, str]] = []
    complete: list[str] = []
    for course in courses:
        state = course.get("prerequisite_state", "unclassified")
        add(f"prerequisite_state({pl_atom(course['course_code'])}, {pl_atom(state)}).")
        relational_states.append({"course": course["course_code"], "state": state})
        if state in EXECUTABLE_PREREQUISITE_STATES:
            complete.append(course["course_code"])
    add("")
    add("% rule_complete(Course): the prerequisite rule is fully understood; eligible/2 requires it.")
    for code in complete:
        add(f"rule_complete({pl_atom(code)}).")

    add("")
    add("% elective_option(Group, OptionCode, OptionTitle).")
    for track in elective_tracks:
        for option in track["options"]:
            add(
                "elective_option({}, {}, {}).".format(
                    pl_atom(track["group"]), pl_atom(option["course_code"]), pl_atom(option["course_title"])
                )
            )
    add("")
    add("% elective_slot(CurriculumCode, Group).")
    for track in elective_tracks:
        for slot in track.get("curriculum_slots", []):
            add(f"elective_slot({pl_atom(slot)}, {pl_atom(track['group'])}).")

    add("")
    add("% term_units(YearLevel, Semester, Units).")
    for term in term_units:
        add(
            "term_units({}, {}, {}).".format(
                pl_atom(term["year_level"]), pl_atom(term["semester"]), term["computed_units"]
            )
        )

    add("")
    add(PROLOG_RULES)

    return {
        "clauses": clauses,
        "relations": {
            "courses": relational_courses,
            "prerequisites": relational_prereqs,
            "standing_requirements": relational_rules,
            "elective_tracks": list(elective_tracks),
            "prerequisite_states": relational_states,
            "rule_complete": complete,
        },
    }
