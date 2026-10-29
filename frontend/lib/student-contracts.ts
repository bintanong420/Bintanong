import { z } from "zod";

const id = z.string().min(1).max(128);
export const answerMetadataSchema = z.strictObject({
  status: z.enum(["answered", "clarification_needed", "source_conflict", "insufficient_evidence", "out_of_scope", "temporarily_unavailable", "greeting", "abstained"]),
  conditional: z.boolean(), language: z.enum(["en", "fil", "taglish", "unknown"]),
  missingFields: z.array(z.enum(["program", "curriculum", "course", "course_status"])).max(4),
  clarification: z.strictObject({
    courses: z.array(z.strictObject({ code: z.string().min(1).max(240), kind: z.enum(["completion", "enrollment"]) })).max(32),
    scope: z.strictObject({ programId: id, curriculumId: id }).nullable(),
  }).optional(),
});
export const sourceIdSchema = z.string().regex(/^ev-[a-f0-9]{64}$/);
export const sourceSchema = z.strictObject({
  sourceId: sourceIdSchema, kind: z.enum(["document", "rule"]), title: z.string().min(1).max(1024),
  page: z.number().int().positive(), printedPageLabel: z.string().max(128).nullable(),
  section: z.string().max(4096).nullable(), excerpt: z.string().min(1).max(65536), hasSourceLimits: z.boolean(),
});
export const curriculaSchema = z.strictObject({ curricula: z.array(z.strictObject({
  programId: id, curriculumId: id, programName: z.string().min(1).max(1024), curriculumName: z.string().min(1).max(1024),
})).max(256) });
export const uploadIdSchema = z.string().regex(/^upl-[a-f0-9]{16}$/);
export const uploadSchema = z.strictObject({
  uploadId: uploadIdSchema, unmatchedLines: z.number().int().nonnegative(),
  rows: z.array(z.strictObject({ rowId: id, printedCode: z.string().min(1).max(2048),
    marks: z.array(z.string().max(64)).max(32), courses: z.array(z.strictObject({ courseId: id, label: z.string().min(1).max(2048) })).min(1).max(256),
  })).max(256),
});
export const choiceSchema = z.strictObject({ rowId: id, courseId: id, state: z.enum(["passed", "failed", "enrolled", "not_enrolled"]) });
export const confirmedSchema = z.strictObject({ facts: z.array(z.strictObject({
  courseId: id, label: z.string().min(1).max(2048), state: choiceSchema.shape.state,
})).max(256) });
export type StudentScope = { programId: string; curriculumId: string };
export type StudentRequest = Partial<StudentScope> & { id: string; text: string };
export type StudentSource = z.infer<typeof sourceSchema>;
export type StudentSourceSummary = { sourceId: string; title: string };
export type StudentAnswer = z.infer<typeof answerMetadataSchema> & { text: string; sources: StudentSourceSummary[] };
export type StudentCurriculum = z.infer<typeof curriculaSchema>["curricula"][number];
export type StudentUpload = z.infer<typeof uploadSchema>;
export type StudentChoice = z.infer<typeof choiceSchema>;
export class StudentTransportError extends Error {
  readonly status: number;
  readonly code: string;
  constructor(code: string, status = 502) { super(code); this.code = code; this.status = status; }
}
