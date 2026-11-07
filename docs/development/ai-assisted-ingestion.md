# Local AI-assisted ingestion

This is the researcher preparation workflow for undergraduate-applicable Handbook
and Citizens' Charter content. It uses the existing PDF reviewer and review journal.
AI suggestions never save a review or approve a source. The student application,
hosted database, release pin and symbolic rules are outside these commands.

Run PowerShell from the repository root with the approved existing dependencies.
Python 3.13 is required. The researcher app targets Node 24.21.0; this machine's
Node 22.22.3 passed the recorded checks but differs from that target. No command
below installs packages or downloads models.

## Choose a preparation method

| Method | What it does | External data transfer |
| --- | --- | --- |
| Native | Existing deterministic extraction, then manual review | No AI service |
| Native + vision | Existing extraction, then compares each selected field against original page images | Whole selected page images, candidate wording, source digest, item/field/page identifiers and related item IDs go to the configured endpoint |
| LlamaParse | Alternate parser, then the same manual reviewer | **The complete original PDF is uploaded for each new batch**, even though only selected physical pages are requested |

Use public institutional documents for these experiments. Private student files
belong to the separate private-file workflow. Provider retention and billing are
external account matters; selecting fewer pages does not prove fewer upload bytes
or lower charges. A loopback vision endpoint can keep image inference local.

Use an ignored output directory under
`C:/Coding-projects/bintanong_workspace/audit-evidence/`. Keep originals and outputs
in separate sibling directories. Never change the frozen 78-chunk baseline.

```powershell
$work = 'C:/Coding-projects/bintanong_workspace/audit-evidence/my-ingestion-run'
# Place the source manifest in $work/inputs/manifest.json, separate from outputs.
py -3.13 -m backend.bintanong_tools.knowledge_update prepare "$work/inputs/manifest.json" --out "$work/native"
```

Native extraction is currently blocked in this machine's installed environment:
Transformers 5.10.2 requires huggingface-hub >=1.5,<2, but 2.2.0 is installed.
The extension's mocked tests do not resolve that conflict. Use an approved compatible
environment before relying on fresh native conversion; do not bypass the check.

## Native extraction with vision suggestions

Set a compatible image-capable chat-completions endpoint and model explicitly.
The URL is its API base, including `/v1` if that server requires it. The adapter
appends `/chat/completions`. HTTPS and loopback HTTP are supported; redirects and
environment proxies are disabled. Use the existing secure environment mechanism
for a key, if required; never put one in manifests, commands committed to Git or UI.

```powershell
$env:BINTANONG_ASSIST_URL = 'http://127.0.0.1:8080/v1'
$env:BINTANONG_ASSIST_MODEL = 'gemma-4-E4B'
# Optional credential environment name: BINTANONG_ASSIST_API_KEY
py -3.13 -m backend.bintanong_tools.knowledge_update prepare "$work/inputs/manifest.json" --out "$work/vision" --assist-mode selected --assist-pages 46
```

The example URL is configuration, not proof that a server is running there.
Gemma 4 E4B supports images according to Google's
[model card](https://ai.google.dev/gemma/docs/core/model_card_4). Owner30Oct:
**do not use the LM Studio projector**,including copying it to another location.
Use the shared GGUF with a separately approved compatible projector. The30Oct
shared-MODELS inventory found no projector;live local image inference therefore
needs that asset resolved first. No download or substitute asset is authorized here.
The [27Oct live check](../../plans/2026-10-27-local-vision-readiness.md) used the
now-excluded projector and remains historical only. It processed image input but
missed a corrupt grade range and violated the advisory format;manual review remained.
That evidence does not authorize reusing the excluded asset. The probe was stopped.

Modes are `none` (default; no AI), `flagged` (existing findings/source gaps), `all`
(every eligible field), and `selected` (explicit pages or `--assist-items` IDs).
Page numbers are **physical PDF pages starting at 1**, not printed page labels.
`selected` needs pages or IDs. Literal source-blank fields are not filled by AI.
Full original pages are used; no unverified crop or coordinates are invented.
Each field call includes all physical pages recorded on that field. Unrecorded
adjacent-page context is not automatically inferred.

Suggestions are generated before packet hashing. Repeating an identical prepare
rechecks the packet without calling the model again. Changing the model, mode or
selection requires a new output directory. Existing frozen reviewed snapshots
cannot receive assistance in place; prepare fresh candidates instead.

A timeout, malformed response or rendering failure leaves a manual-review notice.
It never means the candidate is correct. There is no automatic retry of vision
inference; use a new packet for a deliberate new experiment.

## LlamaParse selected-page batches

Supply `LLAMA_CLOUD_API_KEY` through the secure environment. The adapter uses the
[official REST v2 API](https://developers.llamaindex.ai/llamaparse/parse/guides/api-reference/)
with the already-installed HTTP client; no SDK installation is needed.

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update parse-llama "$work/originals/source.pdf" --out "$work/llama" --pages 11 12 13 --batch-size 3 --tier agentic --version latest
```

Exit 0 means all selected pages returned, **not** that their content is accurate.
Exit 2 means some pages failed; `result.json` and batch receipts preserve the good
pages. Exit 1 means a command/configuration error. Rerun the same command to resume
recorded jobs and reuse successful pages. Add `--retry-failed` to explicitly replace
a failed job. Only missing pages are requested again. Changes to source bytes,
page selection, batch size, tier or version need a new output directory.

Receipts save a job ID before polling, so a polling timeout can resume. An upload
accepted remotely whose response is lost before its ID is saved cannot be proven
deduplicated; review provider jobs before another upload. Automatic paid retry or
credit-savings claims are intentionally absent. `latest` is provider-selected and
can change; record an explicit supported version for a repeatable live experiment.

To prepare the parser result, use a normal manifest with this additional document
input. Fill hashes using `Get-FileHash -Algorithm SHA256`, in lowercase:

```json
{
  "schema_version": "bintanong-knowledge-update-v1",
  "documents": [{
    "id": "charter", "kind": "charter", "title": "Citizens' Charter",
    "edition": "2025 fourth edition",
    "source": "../originals/source.pdf", "sha256": "<original PDF SHA256>",
    "locator": "<recorded source reference>",
    "parser_result": {"path": "../llama/result.json", "sha256": "<result JSON SHA256>"}
  }]
}
```

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update prepare "$work/inputs/llama-manifest.json" --out "$work/llama-review"
```

`parser_result` cannot be combined with a candidate bundle, review template,
reviewed snapshot or prospectus document. Prospectuses retain their existing
reviewed structured-data and symbolic-authoring path.

Tables, merged-cell HTML and continuation metadata remain grouped as escaped JSON
in a review field. Headings retain their hierarchy; headers/footers remain visible
for review. TOC wording does not replace body wording. These are parser candidates,
not automatically authored service steps. Review complete client/agency action,
fee, time, office, requirements and applicability relationships together. Charter
items initially link the selected document's other items as context; that broad
grouping is not proof that every item belongs to the same service.

Missing geometry, rotated pages or boxes that cannot be checked against the
original page dimensions stay build-withheld. The GUI's omission-area feedback
does not create verified source spans. Resolve geometry through the existing
source-bound preparation/review process in a fresh packet. Do not approve a
table merely because every word is present.

## Review, build and verify

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update review "$work/vision" --reviewer 'Your name' --api-port 8770 --ui-port 3010
```

Use free loopback ports. Save existing browser drafts before stopping a reviewer;
new launches use new local credentials. Keep launch links private and outside Git.

1. Compare the extracted wording with the original PDF beside it.
2. **Use suggestion** copies it into your editable draft. **Ignore suggestion**
   dismisses it for that draft. Neither action saves a decision.
3. Correct the text yourself if needed, or leave it unresolved when evidence is
   missing. A confidence score is never a reason to approve.
4. Record applicability and a review note, check related context, then explicitly
   **Save my review**. Context links do not approve linked fields.
5. Use **Report missing content** for an extraction omission; use the source-gap
   controls for defects in the original. Feedback remains independent of approval.

Stale or mismatched source/candidate proposals cannot be applied. Normal manual
review controls remain available when assistance fails or returns uncertainty.

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update build "$work/vision" --out "$work/package" --model-dir 'C:/Coding-projects/bintanong_workspace/MODELS/SEA-LION-E5-Embedding-600M'
py -3.13 -m backend.bintanong_tools.knowledge_update verify "$work/package" --packet "$work/vision"
```

Use the existing build selection, subject assignments, claim-review metadata and
baseline membership requirements. An extraction-only manifest is not a complete
authoring specification. `--cache` can reuse an existing package only when its
configuration and exact bindings match. Pending, unresolved, out-of-scope or
unlocated required evidence prevents a usable reviewed package. A verified local
package remains inactive; these commands do not publish it or create trusted Prolog.
Local lifecycle T4 and operator-rehearsal T5 remain separate unfinished work.

## Compare the strategies

The ignored prepared sample is under
`audit-evidence/p11-ai-ingestion-20261027/matched-sample/` in the workspace.
It contains 28 matched physical pages: 16 Handbook and 12 Charter. Each has a
sampling rationale. There are 84 measurement rows across `native`, `native_vision`
and `llamaparse`; **all measurements initially remain blank**.

To create another sample, supply source paths/hashes and physical pages/reasons:

```json
{"documents":[{"source":"C:/path/original.pdf","sha256":"<SHA256>",
"pages":[{"page":46,"reason":"Undergraduate numeric grading table"}]}]}
```

```powershell
py -3.13 -m backend.bintanong_tools.knowledge_update evaluation-sample "$work/inputs/sample.json" --out "$work/sample"
# Fill measurements.csv after independently reviewing/timing each strategy.
py -3.13 -m backend.bintanong_tools.knowledge_update evaluate "$work/sample/measurements.csv" --out "$work/summary"
```

Keep the same source/page set for every strategy. Count human corrections,
omissions, hierarchy/table/order/number/citation errors, unresolved items,
suggestion outcomes, calls, failures and retries; record reviewer minutes and
latency separately. Enter zero only when actually measured as zero. Cost columns
must use one documented currency/unit; observed and estimated values stay separate.
Missing observations remain null, including aggregate totals. Provider usage
receipts are not automatically converted into money or accuracy.

The summary writes JSON, CSV and Markdown. Relational comparison checks field
paths, so swapped fees/times fail even with 100% word recall. The harness does not
create a human gold standard or decide which provider is better. Reviewer timing,
correctness adjudication and matched live runs are still required.

## Offline checks

Create a fresh external test directory; do not put test temporaries in the corpus.

```powershell
py -3.13 -m pytest -q -p no:cacheprovider tests/test_ingestion_assistance.py tests/test_llamaparse_ingestion.py tests/test_ingestion_evaluation.py tests/test_knowledge_update_cli.py --basetemp "$work/test-tmp"
Set-Location researcher
npm test
node node_modules/typescript/bin/tsc --noEmit
```

Normal tests use fake providers and synthetic source evidence. The browser save
rehearsal additionally requires an isolated synthetic packet, dedicated ports,
`BINTANONG_REVIEW_TEST_LAUNCH` and
`BINTANONG_REVIEW_TEST_WRITE=isolated-rehearsal`; never target owner review packets.
Live provider smoke tests and real human A/B measurements are separate checks.
