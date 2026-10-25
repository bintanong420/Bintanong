# Thesis context: useful recovery guidance and private conversations

25 October 2026; owner requested direct PDF reading after review of earlier notes.
Source: Context/bintanong_thesis_for_context.pdf,88 physical pages, SHA256
729653540c7991496aceea1f728382d2e2262ca096e4342ce956d072e603c81c.
Original PDF unchanged. Page references below use physical PDF page first, printed
body page in parentheses; the contents list does not consistently locate body sections.

## Reading scope

Inspected title/contents, scanned all88 pages for relevant topics, and read targeted
introduction/problem/objective/scope pages7–15/17–20, symbolic reasoning39–44,
LLM/framework/methodology50–60, privacy/evaluation64–73. Visually checked full
pages9,54,65, plus the separate runtime routing architecture PNG. This is targeted
context review, not an exhaustive editorial or external-reference verification.
Ignored extraction/render evidence: workspace audit-evidence/p11-20261025/
thesis-context-review/pages.json and page-{9,54,65}.png.

## Thesis requirements relevant to the reported question

-7(6): natural-language, context-sensitive conversational interaction is part of
  the rationale; policy answers must remain grounded in institutional evidence.
-9(8): the motivating student problem explicitly includes failing a major subject,
  planning a retake and navigating the relevant university processes.
-13/15(12/14): messy/vague language, appropriate clarification/refusal and usability
  are evaluation targets. Merely returning a safe status does not establish usability.
-17–20(16–19): undergraduate academic affairs, advisory/read-only behavior, no
  autonomous acquisition of unavailable institutional knowledge, and private-input
  separation remain mandatory. Missing policy needs honest limits or referral.
-40(39): recovering after failing CC4/L is an explicit example: conversational
  explanation uses neural/retrieval components; symbolic reasoning verifies affected
  courses. This is an architectural illustration, not approved retake policy.
-50(49): LLM translates retrieved information and symbolic results into clear,
  student-friendly guidance. Unchecked model knowledge cannot supply university rules.
-54(53): genuine vague intent should produce questions that clarify what the student
  means, to avoid answers that sound valid but do not apply.
-55/65(54/64): private inputs/conversations are isolated to the owning user's chat
  context and cannot enter institutional knowledge or influence another session.
-65–66(64–65): data minimization and no stored personal academic records, including
  grades/enrollment/identification. The PDF does not specify a memory representation,
  transcript window, TTL, IDs-only contract or precise transient-record boundary.
-71–73(70–72): evaluation includes user-facing relevance/usability and UAT under
  realistic usage conditions, alongside factual correctness measures.

## Reconciliation with implementation notes

The earlier statement that the thesis required very little memory was too broad.
IDs-only context and omitted inline chat facts are the later Phase10/master23
implementation choices. The PDF supports conversation isolation and data minimization;
it does not prescribe forgetting a student's conversational goal after one answer.
Its simultaneous isolated-conversation and no-academic-record-storage wording needs
a precise technical boundary. This review does not authorize persistent grades,
full-transcript transmission or changing the current owner-approved context contract.

The current options question fits the study's recovery-guidance purpose. If its
antecedent or intent is ambiguous, the system should ask a specific clarifying question.
Once understood, institutional options need reviewed documentary support; structured
eligibility/dependency conclusions need reviewed symbolic checks. A bare generic
clarification is a usability/capability gap, even though it avoids an invented answer.
The current failed trace does not prove that omitted grades alone caused the failure.

Some older thesis prose describes universal retrieval and closed-world illustrations.
Preserve the owner's later structured-course routing and unknown-versus-unmet rules;
this reading does not reopen settled source decisions or turn examples into policy.

No application edits, model calls, server restarts, DB writes or activation. Only
documentation updated. Options follow-up remains unresolved under frontend-focused
scope. No claim that any specific retake/alternative procedure is covered by sources.
