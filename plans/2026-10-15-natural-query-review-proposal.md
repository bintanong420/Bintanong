# Revised natural student-query proposal — 15 October 2026

**Draft for owner wording and expected-behavior review. Not accepted or tested.**
This revises the six scenarios / 18 variants in the
[earlier proposal](2026-10-15-unavailable-query-review-proposal.md) in response to
the owner's [natural-query requirements](2026-10-15-natural-query-response-requirements.md).
Preserve the accepted 12 scenarios / 36 variants and all saved vectors unchanged.

Normal questions use the website's supported undergraduate academic-affairs
context without making users say “undergraduate” or name a memo. That context
does not invent student-specific facts or approve source applicability. Answer
evidence should carry a concise source/date reference and any material limitation.
Phase 05 evaluates evidence and response requirements without LLM answer generation.

## U1. Lost vehicle sticker: unavailable replacement price

- **English:** I lost my vehicle pass sticker. How much does a replacement cost?
- **Filipino:** Nawala ang sticker ng aking vehicle pass. Magkano ang bayad sa kapalit?
- **Taglish:** Nawala ang vehicle pass sticker ko. Magkano ang replacement fee?

Expected: recover the reviewed owner-expense clause, explain that it does not
state the replacement price, and avoid substituting the P50 application/sticker
payment. Provide a small guideline section/source reference. A Security Services
Unit referral requires the separately reviewed office/context evidence. The user
does not need to identify the guideline. Do not claim that the amount is absent
from every university source, that replacement is free, or that it is automatic.

Prerequisite retained: complete necessary II/III context and supported office
association must be reviewed/bound before this case is tested. Confirmed V01–V06
bindings alone do not approve the whole vehicle application procedure.

## U2. Special class: unavailable per-student billing rule

- **English:** There are ten students in our special class with three lecture units. How much does each student need to pay?
- **Filipino:** Sampu kami sa special class na may tatlong lecture unit. Magkano ang kailangang bayaran ng bawat isa?
- **Taglish:** Ten students kami sa special class na 3 lecture units. Magkano ang babayaran per student?

Expected: retrieve the applicable reviewed three-lecture-unit example and its
rate/hours and effectivity. Preserve the printed P20,000; explain that the visible
memo does not establish how it becomes an individual student's assessment. Do not
silently divide it into an official P2,000 bill or infer FHE coverage. Give a short
August 2023 memo reference; the student need not know that source/date in advance.
Do not label the printed amount an established class-total or per-student charge.

Source prerequisite: complete F01/F08/F09 selected bindings are available. This
does not resolve held F04 or establish school/current-year verification. Any
comparison with an older source must compare the same applicable subject/cohort;
cosine similarity alone does not select the governing version.

## S1. Explicit professional Law context

- **English:** I am a law student. What are my graduation requirements?
- **Filipino:** Estudyante ako ng Law. Ano ang mga kailangan ko para makapagtapos?
- **Taglish:** Law student ako. Ano ang graduation requirements ko?

Expected: a clear notice that Bintanong covers undergraduate academic affairs and
cannot answer professional Law graduation requirements from its supported knowledge.
Do not borrow undergraduate requirements or add Law sources to the positive corpus.
The explicit Law context is intentional in this negative scope test; ordinary
undergraduate users do not have to supply an audience declaration. No particular
office referral is invented.

## S2. Faculty employment procedure

- **English:** I am a faculty member requesting a certificate of employment. What documents must I submit?
- **Filipino:** Miyembro ako ng faculty at humihingi ng certificate of employment. Anong mga dokumento ang kailangan kong isumite?
- **Taglish:** Faculty member ako and I need a certificate of employment. Ano ang documents na kailangan kong i-submit?

Expected: a notice that the employment procedure is outside Bintanong's undergraduate
academic-affairs coverage. Do not substitute student academic-record procedures or
acquire/index faculty records. The explicit faculty/employment context is necessary
for this negative test; a staff role merely mentioned in a student service does
not make that service unsupported.

## A1. Ambiguous acronym

- **English:** How do I get TC?
- **Filipino:** Paano ako makakakuha ng TC?
- **Taglish:** Paano kumuha ng TC?

Expected: ask what “TC” means or which document/service the student wants. Website
undergraduate context is available; no canonical acronym expansion is supplied.
Do not select an expansion from similarity scores or assert an official local use.
If the owner considers this wording unambiguous in context, revise/omit the case
before testing.

## P1. Prevent borrowing BSCS evidence for BSIT

- **English:** What are the prerequisites for CC5 in BSIT?
- **Filipino:** Ano ang mga prerequisite ng CC5 sa BSIT?
- **Taglish:** Sa BSIT, ano ang prerequisites ng CC5?

Scenario context, separate from the natural utterance: the student's BSIT
2018–2019 curriculum has already been explicitly established in prior conversation
or verified request metadata for this offline fixture. No semantic inference,
default curriculum choice or user-source/date declaration is invented.

Expected in the bounded eight-row selection: preserve that verified BSIT scope
and requested-course role; no matching BSIT CC5 row is in the selected set, so return
insufficient matching evidence rather than borrowing either BSCS CC5 row. This is
not a claim that CC5 is absent from the complete BSIT curriculum or from PalSU.
If the actual student's curriculum is unknown and materially affects the answer,
clarify it; do not use this fixture's prior context as a general runtime default.

## Review state and execution limits

- The owner accepted the design direction, not these newly drafted wordings.
- All 18 exact variants and six expected behaviors require actual acceptance.
- The earlier async acceptance request refers to the old packet and is superseded;
  no acceptance is inferred from the owner's critique.
- U1 source prerequisites remain separate from wording acceptance; U2 needs no
  F04 decision. Record prerequisites and scope context per case.
- No new queries encoded/scored; no new benchmark fixtures, thresholds, website
  changes, response generation, source activation or Phase 06 advancement.

Owner review: accept these six scenarios in all three languages and their stated
expected behavior, or identify the IDs/wordings to change. This is the separate
benchmark wording review required by the standing AGENTS instruction.
