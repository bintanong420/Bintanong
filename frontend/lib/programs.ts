import type { StudentCurriculum } from "./student-contracts";

export type College = { code: string; name: string };
const colleges = {
  CAD: { code: "CAD", name: "College of Architecture and Design" },
  CAH: { code: "CAH", name: "College of Arts and Humanities" },
  CBA: { code: "CBA", name: "College of Business and Accountancy" },
  CCJE: { code: "CCJE", name: "College of Criminal Justice Education" },
  CHTM: { code: "CHTM", name: "College of Hospitality Management and Tourism" },
  CNHS: { code: "CNHS", name: "College of Nursing and Health Sciences" },
  CoE: { code: "CoE", name: "College of Engineering" },
  CS: { code: "CS", name: "College of Sciences" },
  CTE: { code: "CTE", name: "College of Teacher Education" },
} satisfies Record<string, College>;
const otherPrograms: College = { code: "", name: "Other programs" };

// Grouping follows the college folders of the prospectus corpus (Tiniguiban - Main). It is UI navigation only.
const programs: Record<string, { college: keyof typeof colleges; aliases: string[] }> = {
  "palsu-bsa": { college: "CAD", aliases: ["BS Archi", "Architecture"] },
  "palsu-abcomm": { college: "CAH", aliases: ["AB Comm", "ABComm"] },
  "palsu-abphilstud": { college: "CAH", aliases: ["AB PhilStud"] },
  "palsu-abpolsci": { college: "CAH", aliases: ["AB PolSci"] },
  "palsu-bspsych-clin": { college: "CAH", aliases: ["BS Psych", "Psychology"] },
  "palsu-bspsych-io": { college: "CAH", aliases: ["BS Psych", "Psychology"] },
  "palsu-bssw": { college: "CAH", aliases: ["BSSW"] },
  "palsu-bsacct": { college: "CBA", aliases: ["BSAc", "Accountancy"] },
  "palsu-bsma": { college: "CBA", aliases: ["BSMA"] },
  "palsu-bsba-buseco": { college: "CBA", aliases: ["BSBA", "BusEco"] },
  "palsu-bsba-fm": { college: "CBA", aliases: ["BSBA", "FM"] },
  "palsu-bsba-hrm": { college: "CBA", aliases: ["BSBA", "HRM"] },
  "palsu-bsba-mm": { college: "CBA", aliases: ["BSBA", "MM"] },
  "palsu-bse-agri": { college: "CBA", aliases: ["BS Entrep", "Entrep"] },
  "palsu-bse-franchise": { college: "CBA", aliases: ["BS Entrep", "Entrep"] },
  "palsu-bse-innotech": { college: "CBA", aliases: ["BS Entrep", "Entrep"] },
  "palsu-bscrim": { college: "CCJE", aliases: ["BS Crim", "Crim"] },
  "palsu-bshm-culinary": { college: "CHTM", aliases: ["BSHM"] },
  "palsu-bshm-hotel": { college: "CHTM", aliases: ["BSHM"] },
  "palsu-bstm": { college: "CHTM", aliases: ["BSTM"] },
  "palsu-bsmid": { college: "CNHS", aliases: ["BS Mid"] },
  "palsu-bsn": { college: "CNHS", aliases: ["BSN"] },
  "palsu-bsce": { college: "CoE", aliases: ["BSCE"] },
  "palsu-bsee": { college: "CoE", aliases: ["BSEE"] },
  "palsu-bsme": { college: "CoE", aliases: ["BSME"] },
  "palsu-bspe": { college: "CoE", aliases: ["BSPE", "PetE"] },
  "palsu-bsbio-medbio": { college: "CS", aliases: ["BS Bio", "Med Bio"] },
  "palsu-bsmb": { college: "CS", aliases: ["Marine Bio"] },
  "palsu-bscs": { college: "CS", aliases: ["BSCS", "CompSci", "ComSci"] },
  "palsu-bses": { college: "CS", aliases: ["BSES", "EnviSci"] },
  "palsu-bsit": { college: "CS", aliases: ["BSIT"] },
  "palsu-beed": { college: "CTE", aliases: ["BEEd", "Elem Ed"] },
  "palsu-bsed-eng": { college: "CTE", aliases: ["BSEd"] },
  "palsu-bsed-fil": { college: "CTE", aliases: ["BSEd"] },
  "palsu-bsed-math": { college: "CTE", aliases: ["BSEd"] },
  "palsu-bsed-sci": { college: "CTE", aliases: ["BSEd"] },
  "palsu-bsed-ss": { college: "CTE", aliases: ["BSEd"] },
  "palsu-bsed-valed": { college: "CTE", aliases: ["BSEd", "ValEd"] },
};

export function collegeOf(programId: string): College {
  const entry = programs[programId];
  return entry ? colleges[entry.college] : otherPrograms;
}

export type ProgramChoice = { programId: string; programName: string; college: College; curricula: StudentCurriculum[] };
export type CollegeGroup = { college: College; programs: ProgramChoice[] };

const normalize = (text: string) => text.toLowerCase().replace(/\s+/g, " ").trim();

/** One entry per program, grouped by college and filtered by name, short name or college. */
export function groupPrograms(curricula: StudentCurriculum[], query: string): CollegeGroup[] {
  const byProgram = new Map<string, ProgramChoice>();
  for (const curriculum of curricula) {
    const existing = byProgram.get(curriculum.programId);
    if (existing) existing.curricula.push(curriculum);
    else byProgram.set(curriculum.programId, { programId: curriculum.programId, programName: curriculum.programName, college: collegeOf(curriculum.programId), curricula: [curriculum] });
  }
  const needle = normalize(query);
  const matches = (program: ProgramChoice) => !needle
    || [program.programName, program.college.name, program.college.code, ...(programs[program.programId]?.aliases ?? [])].some(text => normalize(text).includes(needle));
  const groups = new Map<string, CollegeGroup>();
  for (const program of byProgram.values()) {
    if (!matches(program)) continue;
    const group = groups.get(program.college.name) ?? { college: program.college, programs: [] };
    group.programs.push(program);
    groups.set(program.college.name, group);
  }
  const collator = new Intl.Collator("en");
  return [...groups.values()]
    .map(group => ({ ...group, programs: group.programs.sort((a, b) => collator.compare(a.programName, b.programName)) }))
    .sort((a, b) => a.college === otherPrograms ? 1 : b.college === otherPrograms ? -1 : collator.compare(a.college.name, b.college.name));
}

// Owner direction, 3 Nov 2026: BSCS students who started in S.Y. 2025-2026 or later follow the new curriculum.
export const startYearOptions = [
  { value: "before-2023", label: "Before 2023" },
  { value: "2023", label: "2023" },
  { value: "2024", label: "2024" },
  { value: "2025", label: "2025" },
  { value: "2026", label: "2026" },
] as const;
export type StartYear = (typeof startYearOptions)[number]["value"];

const firstYear = (curriculum: StudentCurriculum) => Number(/\d{4}/.exec(curriculum.curriculumName)?.[0] ?? /\d{4}/.exec(curriculum.curriculumId)?.[0] ?? 0);

/** The latest curriculum already in effect in the school year the student started. */
export function curriculumForStartYear(curricula: StudentCurriculum[], startYear: StartYear): StudentCurriculum | null {
  const year = startYear === "before-2023" ? 2022 : Number(startYear);
  const ordered = [...curricula].sort((a, b) => firstYear(a) - firstYear(b));
  return ordered.filter(curriculum => firstYear(curriculum) <= year).at(-1) ?? ordered[0] ?? null;
}
