// Exact metadata validator from baseline 7b9fcc31; fixtures must also work without Git history.
import { z } from "zod";

const id = z.string().min(1).max(128);
export const answerMetadataSchema = z.strictObject({
  status: z.enum(["answered", "clarification_needed", "source_conflict", "insufficient_evidence", "out_of_scope", "temporarily_unavailable", "greeting", "system_information", "abstained"]),
  reason: z.enum(["dialogue_unresolved", "clarification_pending", "route_interpretation", "capability_unavailable",
    "retrieval_coverage", "source_incomplete", "source_conflict", "unsupported_scope", "validation_failure", "system_error"]).optional(),
  conditional: z.boolean(), language: z.enum(["en", "fil", "taglish", "unknown"]),
  missingFields: z.array(z.enum(["program", "curriculum", "course", "course_status", "transfer_direction"])).max(5),
  notice: z.string().min(1).max(240).optional(),
  clarification: z.strictObject({
    courses: z.array(z.strictObject({ code: z.string().min(1).max(240), kind: z.enum(["completion", "enrollment"]) })).max(32),
    scope: z.strictObject({ programId: id, curriculumId: id }).nullable(),
  }).optional(),
});
