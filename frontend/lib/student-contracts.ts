import { z } from "zod";

const id = z.string().min(1).max(128);
export const sourceIdSchema = z.string().regex(/^ev-[a-f0-9]{64}$/);
export const answerPresentationSchema = z.strictObject({
  schemaVersion: z.literal("bintanong-answer-presentation-v2"),
  coverageState: z.enum(["complete", "partial", "withheld"]),
  parts: z.array(z.strictObject({
    partId: z.string().regex(/^r[1-8]$/), label: z.string().min(1).max(240),
    evidenceNeed: z.enum(["structured", "document"]),
    conditional: z.boolean().optional(),
    state: z.enum(["answered", "unknown", "clarification_needed", "not_checked", "withheld", "unavailable"]),
    blocks: z.array(z.strictObject({ type: z.enum(["summary", "verdict", "explanation", "limitation", "source_notice", "details"]),
      text: z.string().min(1).max(12000), title: z.string().min(1).max(160).optional(),
    }).refine(block => (block.type === "details") === (block.title !== undefined), "Details require a title")).min(1).max(8),
    sourceIds: z.array(sourceIdSchema).max(64),
  })).min(1).max(8),
}).superRefine((value, ctx) => {
  const answered = value.parts.filter(p => p.state === "answered").length;
  const coverage = answered === value.parts.length ? "complete" : answered ? "partial" : "withheld";
  if (coverage !== value.coverageState || new Set(value.parts.map(p => p.partId)).size !== value.parts.length
    || value.parts.some(p => new Set(p.sourceIds).size !== p.sourceIds.length || (p.state !== "answered" && p.sourceIds.length)))
    ctx.addIssue({ code: "custom", message: "Invalid part coverage or source binding" });
});
export type AnswerPresentation = z.infer<typeof answerPresentationSchema>;
export const clarificationReplySchema = z.strictObject({
  replyToTurnId: id, revision: z.number().int().nonnegative(),
  slots: z.array(z.strictObject({ slot: z.string().min(1).max(128), value: z.string().min(1).max(2048) })).max(32),
});
export const answerMetadataSchema = z.strictObject({
  status: z.enum(["answered", "clarification_needed", "source_conflict", "insufficient_evidence", "out_of_scope", "temporarily_unavailable", "greeting", "system_information", "abstained"]),
  reason: z.enum(["dialogue_unresolved", "clarification_pending", "route_interpretation", "capability_unavailable",
    "retrieval_coverage", "source_incomplete", "source_conflict", "unsupported_scope", "validation_failure", "system_error"]).optional(),
  conditional: z.boolean(), language: z.enum(["en", "fil", "taglish", "unknown"]),
  missingFields: z.array(z.enum(["program", "curriculum", "course", "course_status", "transfer_direction"])).max(5),
  notice: z.string().min(1).max(240).optional(),
  presentation: answerPresentationSchema.optional(),
  clarification: z.strictObject({
    courses: z.array(z.strictObject({ code: z.string().min(1).max(240), kind: z.enum(["completion", "enrollment"]), slot: id.optional() })).max(32),
    scope: z.strictObject({ programId: id, curriculumId: id }).nullable(),
    binding: z.strictObject({ replyToTurnId: id, revision: z.number().int().nonnegative(),
      requestedSlots: z.array(z.string().min(1).max(128)).max(32) }).optional(),
  }).optional(),
});
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
export type StudentRequest = Partial<StudentScope> & { id: string; text: string; clarificationReply?: z.infer<typeof clarificationReplySchema> };
export type StudentSource = z.infer<typeof sourceSchema>;
export type StudentSourceSummary = { sourceId: string; title: string };
export type StudentAnswer = z.infer<typeof answerMetadataSchema> & { text: string; sources: StudentSourceSummary[] };
export type StudentCurriculum = z.infer<typeof curriculaSchema>["curricula"][number];
export type StudentUpload = z.infer<typeof uploadSchema>;
export type StudentChoice = z.infer<typeof choiceSchema>;
export class StudentTransportError extends Error {
  readonly status: number;
  readonly code: string;
  /** Whole seconds until the server will accept another question (rate limit), when it said so. */
  readonly retryAfter: number | null;
  constructor(code: string, status = 502, retryAfter: number | null = null) { super(code); this.code = code; this.status = status; this.retryAfter = retryAfter; }
}
