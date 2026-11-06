# Live language and browser results — 5 November 2026

**Completed 72/72 original PDF variants, plus three separately scored IT 3/L regression turns.**
The proposed overall Taglish >= English > Tagalog ordering is **not established**. On the seven checked
eligibility cases, Taglish and English agreed with the reference in 6/7 cases each, versus 4/7 for Tagalog.
Policy/procedure behavior was inconsistent across languages; answered status is not an accuracy measure.
This is a development/regression run, not a sealed final thesis benchmark or institutional validation.

## Composition and procedure

Followed the [frozen protocol](2026-11-05-language-benchmark-and-browser-protocol.md).
Product code `cedad977`; subsequent changes during execution were documentation/test files only.
Candidate frontend/API used **3217/8022**; gathering checkout and **3216/8021** were not modified or restarted.
Owner explicitly confirmed the model was free for this window. All inference was serial.

Real Gemma routing/generation, cached reviewed 39-curriculum release and sealed documents, CPU encoder,
Prolog, admission/validation, HTTP stream and frontend rendering were used. The candidate used a trusted local
guest API composition; hosted release-currentness/auth-provider/storage probes were excluded. This is not
production-path parity for those services. Question scopes were selected in the real program picker; unspecified
programs used BSCS 2018-2019. Fresh browser context per variant; language order rotated by question.

PDF SHA-256: `be467633c1429dc72b49e473d4633f81045f340859dd86f0d167ff368577a9a3`.
Twenty-four rows / three language variants; meaning-matched exploratory subset and confounds are frozen in
the protocol. Tagalog/Filipino and Taglish inputs both expect Taglish replies under the existing owner decision.

Runtime: existing Gemma `gemma-4-E4B-it-UD-Q4_K_XL.gguf`, server context 8192, transport temperature/seed 0;
default output limit 768 with existing per-call overrides. GGUF byte hash was not remeasured. Backend reused
Python 3.13 venv: Pydantic 2.13.5, Janus-SWI 1.5.3, sentence-transformers 6.1.0, Torch 2.14.0,
Transformers 5.17.0, Uvicorn 0.53.0. Separate offline reference checks used system Python/Pydantic 2.13.4 /
Janus-SWI 1.5.2; references share the reviewed authoring ledger, not an independent source audit.
Existing Playwright 1.65.0-alpha-2026-10-30 / Node 22.22.3 / Edge 157.0.4341.30 were reused;
frontend used existing Node 24.21.0 / Next 16.4.3. No installs, lock changes or weight downloads.

## Quantitative observations

| Input | Eligibility conclusion/reference agreement | Prerequisite listing target/code agreement | Expected reply-language metadata | Median local submit-to-render |
|---|---:|---:|---:|---:|
| Taglish | 6/7 | 1/2 | 23/24 | 13.89 s |
| English | 6/7 | 1/2 | 24/24 | 14.39 s |
| Tagalog | 4/7 | 1/2 | 24/24 | 14.87 s |

All seven eligibility references are ineligible with the supplied premise. Conclusion checks only inspect
that the returned first verdict agrees; they do not certify all explanation text, grade binding or citations.
Listing checks verify target/required code presence and no grade-demand slot; both are complete only for these
two simple reference trees. No aggregate documentary accuracy score is claimed: independent gold/adjudication
for all documentary variants remains pending. Do not generalize this small single pass to all languages/programs.

Answered statuses were Taglish 15/24, English 17/24, Tagalog 17/24; these are **not correctness scores**.
Every original variant returned HTTP 200 and rendered, with no automation errors, browser page errors or
horizontal page overflow. All **156 source-card fetches returned 200**. These checks do not establish source accuracy.
Latency is local automation click-to-final-render, excluding startup/navigation/program selection/source fetches/
screenshot saving. Shared-model warm/cache state was inherited; CPU encoder startup was not timed. No ngrok,
LTE/phone, hosted storage or controlled cold-start measurement, SLA or statistically significant speedup is claimed.
Different answer/abstention work and meaning changes in the original translations confound aggregate timing.

## Per-question status, not correctness

A = answered, C = clarification needed, I = insufficient evidence, B = abstained.

| PDF row | Taglish | English | Tagalog |
|---:|:---:|:---:|:---:|
| 1 | A | A | A |
| 2 | A | A | C |
| 3 | A | A | A |
| 4 | A | A | A |
| 5 | C | C | C |
| 6 | A | A | C |
| 7 | A | A | A |
| 8 | A | A | A |
| 9 | C | C | C |
| 10 | I | C | I |
| 11 | A | A | A |
| 12 | A | A | A |
| 13 | A | I | C |
| 14 | A | A | A |
| 15 | I | I | A |
| 16 | I | I | A |
| 17 | B | A | A |
| 18 | I | A | A |
| 19 | I | A | A |
| 20 | A | A | A |
| 21 | C | C | C |
| 22 | A | A | A |
| 23 | A | A | A |
| 24 | A | A | A |

## Concrete failures and review findings

- Rows 2/6 Tagalog re-ask a prerequisite result explicitly supplied in the question.
- Row 5 Nursing: all three re-ask NCM15-115A instead of returning the checked unmet conclusion.
- Row 8 IT 16/L lists IT 10/L correctly in all three; row 9 Forensic 3/L instead asks a generic subject/topic
  clarification in all three despite the scoped catalog/reference resolving the course.
- Row 10 concurrency: English asks for year/semester; the other two say information unavailable.
  This does not establish a useful consistent response to the general policy question.
- Row 11 dropping includes an unrelated shifting referral in all three. Row 15 Tagalog grade-of-4 query
  incorrectly returns dropping/shifting instructions. These demonstrate why answered status is not success.
- Row 16 Tagalog INC response acknowledges deadline conflicts yet also states an automatic within-term NC
  consequence. That juxtaposition needs source/guard review; this report does not resolve held source deadlines.
- Rows 17/19 Taglish abstain or report missing information while English/Tagalog return probation/cheating
  material. Row 18 Taglish falls back to unknown-language/English metadata. Thus the preferred ordering is not
  consistently observed outside the eligibility slice.
- Row 21 Tagalog/Taglish explicitly say leaving for another school, but still receive the direction question.
- Several documentary replies remain lengthy, with verbatim blocks, raw field/role labels and awkward Taglish;
  row 24 selects a library-specific service for a general facilities request. Scope/completeness review is needed.
  The original printed processing-total discrepancy remains disclosed; no source continuation was invented here.

## Separate dependency regression and visuals

The exact IT 3/L inverse-dependency question and matched English/Tagalog variants all returned **IT 14/L directly**,
without a failure premise, and retained the IT 22 percentage-condition limitation. Three actual live turns,
outside the PDF denominator, verified the shared routing/presentation fix on the candidate. They do not prove
all-program live acceptance; the earlier [39-curriculum offline results](2026-11-04-all-curricula-dependency-results.md)
remain a separate component gate.

Six controlled UI fixtures also passed at 1440x1000 and 390x844: no page errors/overflow; mobile navigation
stayed open on its heading click, dismissed on backdrop click/Escape and restored focus to its opener.
Fixtures are not model-quality evidence.
Live 72+3 screenshots use Edge at a mobile viewport, not a real iPhone/Messenger session. The installed WebKit
binary did not match Playwright's expected version; no browser was downloaded. Actual Safari/Messenger remains unverified.

Raw answers/SSE/source excerpts, setup attempts, metadata and PNGs are ignored under
`C:/Coding-projects/bintanong_workspace/audit-evidence/p12dev-language-20261105/`.
`comparison-gallery.html` contains 72 PDF variants and three separate supplemental cards; its 75-card count,
language filter (25 Taglish cards) and screenshot paths were checked with Playwright. `review-summary.json`
contains the mechanical aggregates. No public copy of these bulk artifacts was staged.

## Reproduction and next action

Curated runner: `node frontend/tests/browser/benchmark-languages.mjs`, with `PLAYWRIGHT_MODULE`,
`BINTANONG_BROWSER_URL` (local only), `BINTANONG_BENCHMARK_INPUT` and ignored `BINTANONG_BENCHMARK_OUT`.
Input: `{pdf_sha256, rows:[{id,curriculumId,questions:{en,fil,taglish},startYear?,matchedLanguageSubset?}]}`.
The runner's three-turn dependency supplement passed with no browser/automation errors; both edited browser
files pass `node --check`. The original 72 used the same local runner before path/profile settings were generalized.
No product behavior was changed during the frozen run. Next: trace lost supplied results/course operations and
unrelated service/referral selection, add focused regressions, then rerun only affected cases with baseline retained.

Temporary candidate services were stopped after testing; gathering web/API and original model health each
returned HTTP 200. Shutdown logged a pending `Queue.get` task and an encoder token-length warning (616 > 512).
These were not browser/HTTP failures in the completed run. The warning alone does not prove truncation or
an overlength encode occurred; token-count/preflight and stream cleanup should be checked before a broader claim.
