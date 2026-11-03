import assert from "node:assert/strict";
import { test } from "node:test";
import { collegeOf, groupPrograms, curriculumForStartYear, startYearOptions } from "../lib/programs.ts";

const option = (programId, curriculumId, programName, curriculumName) => ({ programId, curriculumId, programName, curriculumName });
const curricula = [
  option("palsu-bscs", "bscs-2018-2019", "Bachelor of Science in Computer Science", "2018-2019"),
  option("palsu-bscs", "bscs-proposed-2025-2026", "Bachelor of Science in Computer Science", "2025-2026"),
  option("palsu-bsit", "bsit-2018-2019", "Bachelor of Science in Information Technology", "2018-2019"),
  option("palsu-bsn", "bsn-2018-2019", "Bachelor of Science in Nursing", "2018-2019"),
  option("palsu-unlisted", "unlisted-2026", "Unlisted Program", "2026"),
];

test("programs follow the prospectus corpus college folders", () => {
  assert.equal(collegeOf("palsu-bscs").name, "College of Sciences");
  assert.equal(collegeOf("palsu-bsn").name, "College of Nursing and Health Sciences");
  assert.equal(collegeOf("palsu-bspsych-clin").name, "College of Arts and Humanities");
  assert.equal(collegeOf("palsu-bsa").name, "College of Architecture and Design");
  assert.equal(collegeOf("palsu-unknown").name, "Other programs");
});

test("grouping lists each program once under its college, colleges and programs sorted", () => {
  const groups = groupPrograms(curricula, "");
  assert.deepEqual(groups.map(group => group.college.name), ["College of Nursing and Health Sciences", "College of Sciences", "Other programs"]);
  const sciences = groups[1].programs;
  assert.deepEqual(sciences.map(program => program.programId), ["palsu-bscs", "palsu-bsit"]);
  assert.equal(sciences[0].curricula.length, 2);
});

test("search matches program names, short names and college names, ignoring case", () => {
  assert.equal(groupPrograms(curricula, "no such program").length, 0);
  assert.deepEqual(groupPrograms(curricula, "comsci").flatMap(g => g.programs.map(p => p.programId)), ["palsu-bscs"]);
  assert.deepEqual(groupPrograms(curricula, "computer").flatMap(g => g.programs.map(p => p.programId)), ["palsu-bscs"]);
  assert.deepEqual(groupPrograms(curricula, "bsit").flatMap(g => g.programs.map(p => p.programId)), ["palsu-bsit"]);
  assert.deepEqual(groupPrograms(curricula, "  NURSING ").flatMap(g => g.programs.map(p => p.programId)), ["palsu-bsn"]);
  assert.deepEqual(groupPrograms(curricula, "college of sciences").flatMap(g => g.programs.map(p => p.programId)), ["palsu-bscs", "palsu-bsit"]);
});

test("BSCS start year picks the curriculum: 2025 and later use the new one", () => {
  const bscs = curricula.slice(0, 2);
  assert.deepEqual(startYearOptions.map(o => o.value), ["before-2023", "2023", "2024", "2025", "2026"]);
  for (const year of ["before-2023", "2023", "2024"]) assert.equal(curriculumForStartYear(bscs, year).curriculumId, "bscs-2018-2019");
  for (const year of ["2025", "2026"]) assert.equal(curriculumForStartYear(bscs, year).curriculumId, "bscs-proposed-2025-2026");
});
