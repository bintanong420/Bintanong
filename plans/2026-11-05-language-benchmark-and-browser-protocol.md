# Language comparison and browser verification

Owner requested the fourth benchmark PDF, comparison of Taglish >= English > Tagalog, and Playwright inspection.
Treat that ordering as an empirical hypothesis; never weaken a language to manufacture the ranking.
This is a development/regression evaluation: reported query families informed earlier fixes, so it is not
an untouched final thesis benchmark. No new phase or institutional approval is inferred.

## Frozen inputs and composition

- Product code `cedad977`, branch `p12-post-gathering-fixes`; only browser-test selector correction during setup.
- PDF `E:/Hawksprey/Downloads/The_Bintanong_Benchmark_Queries (4).pdf`, 3 pages, 24 rows / 72 variants.
  SHA-256 `be467633c1429dc72b49e473d4633f81045f340859dd86f0d167ff368577a9a3`.
  Extracted by original span positions; removed repeated column headings from rows 14/17, reviewed page 1 image.
- English questions expect English; Filipino/Tagalog and Taglish inputs expect Taglish replies under the
  existing owner language decision. This compares input handling, not generation of pure Tagalog answers.
- Owner explicitly confirmed model free / live testing window on 5 November. Serial calls only.
- Candidate frontend 3217, API 8022. Existing gathering frontend 3216/API 8021 untouched.
  API uses cached 39 reviewed ledgers and sealed documents, existing local CPU encoder and shared Gemma service.
  The existing research pipeline, admission, validators and Prolog execute. No hosted-currentness check,
  database writes, activation, new model/dependency downloads, auth-provider or remote-storage measurement.

## Comparison contract

Run all original 72 variants descriptively. Some translations change requested information: rows 12/13/14
add program/student/enrollment context; 15/20 add a separate form/location question; 18 changes the ID cases;
21 clarifies transfer direction; 22/23/24 add incident/vehicle/event context. These differences can change
legitimate answer slots, clarification and retrieval work and confound an overall language ranking.

Use rows 1-11,16,17,19 as an exploratory meaning-matched subset (14 triplets), and disclose residual register
differences. Freeze these inclusion criteria before scoring. Do not treat answered status as correctness.
Report separately: operational completion/status, intent/target/negation, checked symbolic conclusion,
source-supported completeness/limitations, unsupported claims, reply-language compliance and latency.
Documentary correctness requires review against applicable cited excerpts; automatic validation alone is insufficient.
Do not assert Taglish >= English > Tagalog from screenshot appearance, status counts or this small sample alone.

## Execution and visual evidence

- Fresh isolated browser context per item/language, explicit program/curriculum selected through the real picker.
  Unspecified-program questions use BSCS 2018-2019 as the fixed UI profile; this is not inference from a code.
- Rotate language order by row: Taglish/English/Filipino, English/Filipino/Taglish, Filipino/Taglish/English.
  One pass is descriptive; repeats/uncertainty analysis are needed for reliable differences.
- Capture raw SSE, response metadata, answer text, actual source excerpts, browser errors, page overflow and screenshots.
  Submit-to-render time includes local frontend/API/model/retrieval work; excludes startup, initial navigation,
  program selection, subsequent source-card fetches and screenshot saving. CPU encoder startup is separate;
  shared-model warm/prefix-cache state is inherited, not a controlled cold-start measurement.
- Controlled UI fixtures separately inspect 1440x1000 and 390x844. Six fixture cases passed: no page overflow
  or page errors; inside heading clicks preserve mobile navigation and outside clicks dismiss it.
  Fixtures prove UI behavior, not model accuracy. The original navigation test clicked the history button
  via the navigation container's center, legitimately closing it; target the Chats heading for its inside-click check.
- Live benchmark viewport is 390x844; screenshot/file metadata distinguishes it from controlled UI fixtures.
  Browser contexts isolate state ([Playwright isolation](https://playwright.dev/docs/browser-contexts));
  viewport/touch emulation cannot reproduce real iPhone Messenger injection
  ([Playwright emulation](https://playwright.dev/docs/emulation)). Actual device retest remains separate.

## Evidence and next action

Raw evidence stays ignored under `C:/Coding-projects/bintanong_workspace/audit-evidence/p12dev-language-20261105/`.
`benchmark72.json` contains source-bound queries; `live-results.json` is incrementally written after each turn;
`live/*.sse` and PNG files preserve output; `visual-results.json` marks controlled fixtures explicitly.
`live-setup-attempts.json` preserves the initial privacy-dialog race and one successful preliminary live turn;
exclude these from the restarted run rather than counting them as language failures.
Next: complete live 72, review output/evidence per language and publish an honest result with failures and limits.
