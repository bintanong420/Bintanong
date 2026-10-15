# Natural student questions and source selection — 15 October 2026

Latest owner reply explicitly approves the revised six/18packet and continuation;
see its acceptance record. Older pending-wording text below is history. The
response requirements and independent source prerequisites remain unchanged.

Standing owner response requirements, recorded during Phase 05 after the
confirmed V/E binding increment `60114e8`. This is a requirements record for
provisional thesis development and later implementation, not deployed behavior.

## Owner direction

The owner explained that users will most probably be undergraduate students and
will not normally say “I am an undergraduate.” The website should explain its
undergraduate scope in its guidelines or equivalent student-facing information.
Users also will not normally name a source or its date, such as the August 2023
special-class memo. Bintanong should answer the ordinary question and provide a
small source reference. The owner wants retrieval to use the latest relevant data
available, giving the August 2023 memo rather than a 2021 source as an example.
They mentioned cosine similarity and k-NN as part of finding relevant evidence.

For requests outside the study scope, such as faculty procedures or Medicine/Law
program questions, Bintanong should clearly admit that the question is outside
its coverage and that it cannot provide that answer. The owner called these
points critical to the intended system response and requested persistent storage.

The owner likes the six-scenario presentation but identified these issues with
its wording and assumptions. This is direction to revise the proposal, **not
acceptance of its original 18 exact variants or of new replacement wordings**.

Exact owner message is preserved separately in ignored workspace evidence at
`audit-evidence/p05-natural-query-owner-direction-20261015/owner-message.json`.

## Requirements to carry into design and evaluation

1. **Natural questions.** Ordinary in-scope examples should not require users to
   declare undergraduate status, identify the institutional source, or know the
   memo's date. Supported undergraduate academic affairs is the website context.
   Make that coverage clear in website guidance; exact placement/copy is not
   decided by this record. Do not add a compulsory status/source question to
   every ordinary interaction.
2. **Clarify facts that matter.** Website context does not establish a student's
   degree program, curriculum edition, cohort, grades or eligibility, and does
   not verify an institutional source's applicability. Ask a focused question
   when a missing fact materially changes the supported answer. Preserve the
   settled old/proposed BSCS curriculum rules rather than guessing an edition.
3. **Answer with a short reference.** When verified visible evidence supports an
   answer, state the useful information plainly and provide a concise reference
   identifying the source/date and relevant section or page. Keep fuller source
   locators in the evidence for traceability. Disclose a material gap, conflict
   or dated/cohort limitation; a small citation must not hide it. Missing prices
   and institutional billing rules remain unavailable.
4. **Prefer the latest applicable reviewed source.** Users should not have to
   choose the source before asking. For the same question and applicable audience,
   prefer the latest relevant reviewed material available. Printed dates and
   temporal validity belong in source selection alongside scope/cohort metadata.
   This records the owner's general research-design preference. It is not proof
   of institutional supersession, current-school-year validity, or a new answer
   to a held field or specific conflict. A newer source for a different cohort,
   program or subject does not replace an applicable older one. Preserve original
   sources and relevant conflicts; do not silently overwrite historical evidence.
5. **Keep ranking and source authority distinct.** Cosine similarity and k-NN
   measure semantic relevance; neither establishes recency, authority or
   applicability. This is the agent's technical clarification of the owner's
   retrieval description, consistent with master sections 10.1–10.3. Candidate
   scope/version checks and recorded source decisions must constrain the evidence
   used; a high-scoring older passage must not silently defeat an applicable newer
   source, nor may date alone settle an unresolved policy conflict. No specific
   recency-weighting formula or algorithm change is approved here.
6. **Explain scope limits honestly.** For explicit excluded-audience requests,
   state that Bintanong covers undergraduate academic affairs and cannot answer
   that procedure/program question from its supported knowledge. Do not substitute
   undergraduate rules, acquire excluded records, or use a generic low-similarity
   cutoff as the sole scope decision. Classify the intended service/audience in
   context; a staff role mentioned in an undergraduate service does not exclude it.
   Missing in-scope information should be described as unavailable, with a supported
   office referral where possible, rather than mislabeled outside the study scope.

## Existing decisions preserved

- Undergraduate-only, read-only scope and private-upload isolation remain.
- The memo's 15 km/h is the recorded provisional vehicle-speed choice; preserve
  the handbook's 20 kph and its discrepancy. This requirements record supplies no
  independent institutional supersession evidence.
- The incoming and continuing enrollment cohorts stay distinct. Preserve the PSA
  original/photocopy difference, clinic timing ambiguity and appointment-slip
  alternative, missing Step 2 label and original Charter cutoff.
- G03 alone is confirmed; original G01/G02 remain unconfirmed. The ASG clause on
  physical page 23 is distinct and excluded. F04's amount remains unresolved.
- The older curriculum may still apply; supplied proposed 2025–2026 BSCS retains
  its proposed label. Unknown student curriculum is not selected by similarity.
- School verification remains pending. These are candidate research requirements,
  not approval to activate sources, deploy a new response policy or advance Phase 06.

Thesis physical pages 17–18 and the routing diagram were reviewed in this session;
these requirements agree with undergraduate-only advice, honest unsupported
responses and separation of private inputs. Master section 10 preserves the
distinction between similarity ranking and policy authority. No scope expansion.

## Concrete next review

The [revised six-scenario packet](2026-10-15-natural-query-review-proposal.md)
removes unnecessary audience/source declarations from ordinary positive and
ambiguous queries. Negative scope examples retain explicit excluded context so
they can exercise the intended notice. The bounded BSIT version-selection test
separates the natural utterance from verified prior request context.

The original proposal remains historical and untested. Present the revised 18
wordings and expected behavior for actual acceptance before testing. This record
does not accept either wording set. No query vectors, scores, thresholds, website,
runtime or product behavior changed to implement these requirements.

## Verification and recovery

Verification for this documentation-only direction:468docs/ledger tests and11subtests
pass11.63s, exit0; phase-state valid and advancement still blocked. Six revised
scenarios/18variants/local links checked; earlier new G5/V/E27file seals unchanged.
No new TDD cycle/product changes or benchmark runs. Owner-direction evidence seal
(3root files) SHA256:647c285405d2372e3899b0f5799bdb282b635dbcd2e4f0c5a93da0fb0bb588a9, read-only verification passes. Preserve raw history;
future writing goes to a new ignored root. Eight explicit curated paths only.
Checkpoint records parent60114e8; following docs commit is discoverable in Git.
