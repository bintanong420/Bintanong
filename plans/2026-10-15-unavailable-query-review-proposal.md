# Proposed unavailable-query and scope-boundary development cases

Date: 15 October 2026. Phase05, baseline `029d031`.
**Draft for owner wording/expected-behavior review. NOT TESTED.**
Latest owner15October retention decision keeps the supplemental sources for review.
U1/U2 source preparation may resume after the necessary field-level human decisions;
the retention decision is not acceptance of these proposed question wordings.
The earlier pause to consider a two-PDF policy baseline is historical and superseded
by the retention decision. U1/U2 still await reviewed evidence and wording acceptance.
These six scenarios / eighteen English, Filipino and Taglish variants are proposed
additions. They do not replace or relabel the accepted12 scenarios /36 variants.
No new query vectors, scores, gold files or thresholds have been generated.

## Purpose and evaluation boundary

Master section10.3 requires unavailable policies, ambiguous acronyms, wrong-program
matches and outdated-edition checks. Current measurements recover complete expected
evidence for30scoped language variants; sixBSCS variants remain curriculum holds.
All scored cases have relevant evidence, including accepted source-gap/conflict
cases. That evidence-positive set cannot measure a globally useful abstention
threshold. The existing Charter cutoff and deadline conflict cases remain accepted
and are reused without reopening their wording or source review.

This proposal exercises different outcomes. Excluded audiences must be stopped by
scope; ambiguous wording must request clarification; a known missing claim must not
be invented even if related source evidence scores well. These outcomes must be
reported separately from empty retrieval and primary ranking Precision@k/Recall@k.
Do not select a global similarity threshold from easy excluded-audience negatives.
No LLM answer generation is required in Phase05: assess returned evidence, scope,
limitations and explicit unsupported fields in an offline evaluation harness.

Two scenarios depend on the new source intake. Owner acceptance of question wording
does not make those sources or field transcriptions approved. Hold those scenarios
until the separately reviewed image-derived evidence is bound and verified. None
of these proposals establishes absence across the entire university's knowledge.

## U1. Vehicle sticker replacement price unavailable

- **en:** I am an undergraduate and lost my vehicle pass sticker. What exact replacement fee do the supplied vehicle guidelines state?
- **tl:** Undergraduate ako at nawala ang sticker ng aking vehicle pass. Anong eksaktong bayad sa kapalit ang nakasaad sa ibinigay na patakaran sa sasakyan?
- **taglish:** Undergraduate ako at nawala ang vehicle pass sticker ko. Magkano ang exact replacement fee ayon sa supplied vehicle guidelines?

Expected: preserve guidelineIII.l, which puts replacement at the owner's expense,
and distinguish its missing price from the P50 application/sticker payment inII.
No inference that replacement is P50, free or automatically granted. Expose the
unavailable amount and the named Security Services Unit as the source-supported
office for clarification. This is partial evidence with a missing consequential
field, not a source with no relevant passage. Prerequisite: intakeV2 review and
verified completeII/III evidence. Current21candidate snapshot has no vehicle chunks.

## U2. Special-class per-student division unavailable

- **en:** Our undergraduate special class has ten students and three lecture units. How much must each student pay under the supplied August 2023 memo?
- **tl:** Sampu kaming mag-aaral sa undergraduate special class na may tatlong lecture unit. Magkano ang dapat bayaran ng bawat isa ayon sa ibinigay na memo noong Agosto 2023?
- **taglish:** Ten students kami sa undergraduate special class na 3 lecture units. Magkano ang payment per student under the supplied August 2023 memo?

Expected: recover the complete reviewed three-lecture-unit example and rate/hours,
preserve the printed P20,000 amount and dated effectivity, and expose that the
visible material does not specify per-student division. Do not output an official
P2,000 student assessment or claim that FHE automatically covers it. The arithmetic
may be mathematically possible; the institutional billing rule is unsupported.
Prerequisite: intakeF1 review and exact source-bound derivative. This proposed
scenario does not label P20,000 an established class-total or per-student charge.

## S1. Explicit professional Law program

- **en:** I am in the Juris Doctor program. What are my graduation requirements under the Law curriculum?
- **tl:** Nasa programang Juris Doctor ako. Ano ang mga kinakailangan ko para makapagtapos ayon sa kurikulum ng Law?
- **taglish:** Juris Doctor student ako. Ano ang graduation requirements ko under the Law curriculum?

Expected: explicit unsupported professional-program scope; no retrieval of
undergraduate requirements as the user's Law requirements. No professional Law
source is added to a supported corpus or positive benchmark. A university office
referral can remain general unless that specific office is verified. This is an
audience rejection, not rejection of undergraduate clauses merely mentioning Law.
Prerequisite: accepted exact wording and explicit scope in the evaluation request.

## S2. Explicit faculty employment transaction

- **en:** I am a faculty member requesting a certificate of employment. What documents must I submit?
- **tl:** Miyembro ako ng faculty at humihingi ng certificate of employment. Anong mga dokumento ang kailangan kong isumite?
- **taglish:** Faculty member ako and I need a certificate of employment. Ano ang documents na kailangan kong i-submit?

Expected: staff/faculty employment procedure outside undergraduate academic affairs;
no substitution of student academic-record procedures. Do not acquire/index staff
records to answer it. This is a valid negative scope case, not supported staff
knowledge. Prerequisite: accepted wording and explicit staff transaction scope.

## A1. Ambiguous acronym without service meaning

- **en:** I am an undergraduate. How do I get TC?
- **tl:** Undergraduate ako. Paano ako makakakuha ng TC?
- **taglish:** Undergraduate ako. Paano kumuha ng TC?

Expected: ask what "TC" means/the document or service intended; do not silently
expand it as Transfer Credential, Transcript of Records or a course code. No
assertion that this acronym is officially used for any particular service. The
evaluation supplies no canonical entity hint. If the owner intends an unambiguous
local use, revise or omit this case before testing; do not set the answer by score.

## P1. Prevent a BSCS passage being borrowed for BSIT

- **en:** Under my BSIT 2018–2019 curriculum, what prerequisites are listed for CC5?
- **tl:** Sa sinusunod kong BSIT curriculum na 2018–2019, ano ang mga nakalistang prerequisite ng CC5?
- **taglish:** BSIT 2018–2019 ang curriculum ko. Ano ang listed prerequisites ng CC5?

Expected in the bounded current eight-row curriculum selection: use verified BSIT
2018–2019 scope and a requested-course role forCC5; never borrow either BSCS CC5
row. No BSIT CC5 row is present in that selected set, so return insufficient matching
evidence rather than presenting BSCS conditions as BSIT conditions. **This does not
claim CC5 is absent from the complete BSIT curriculum or from PalSU.** A full-source
expansion would need a separately reviewed row and a versioned expected-evidence
update, not an invented negative institutional fact. No new original curriculum
conversion is needed to exercise this candidate-selection boundary.

## Review and execution checklist

- [x] State all18exact proposed wordings and expected behavior before testing.
- [x] Preserve the accepted12/36questions, model assets, vectors and original sources.
- [x] Distinguish pending incoming evidence, claim gaps, explicit scope, ambiguity
  and subset-relative missing rows; no whole-corpus accuracy assertion.
- [ ] Owner accepts/corrects the six scenario wordings and expected outcomes.
- [ ] Apply recorded incoming source decisions and verify the necessary derivatives.
- [ ] Create a versioned development packet with source/field/locator labels and
  separate request scope; keep derived JSON, embeddings and raw evidence ignored.
- [ ] Run bounded calibration/evaluation with appropriate positive controls;
  report k3/5/8, language/category and each outcome separately. Additional true
  in-scope unavailable-policy cases may still be needed for global calibration;
  present any new questions for review before testing.
- [ ] Resolve remaining Phase05 exit gates and prepare the formal handoff only
  when their evidence exists. No source activation or Phase06 follows from this draft.

Owner review request: accept the six questions in all three languages and their
expected behavior, or identify the IDs/wordings to change. This is new benchmark
review required by the standing `AGENTS.md` owner decision: "Show proposed new or
changed benchmark questions to the owner before testing them."
