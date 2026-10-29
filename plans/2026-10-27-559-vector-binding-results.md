# Current 559-chunk vectors and bounded topic maps

The current source selection now has a complete **inactive local package**:559
chunks/vectors,145subjects,and240claim records (208existing reviews plus32technical
field facets). This removes the missing-vector and oversized-field-map preparation
blockers. It does not establish answer quality or authorize activation. The corrected
78-chunk research release remains active;no hosted data or default settings changed.

## Exact vector binding

Used the existing pinned SEA-LION-E5-Embedding-600M,1024dimensions/L2,local CPU,
batch4/four threads,empty document prompt,and offline model loading. The257new
serialized texts took402.39seconds including loading/validation/finalization;
302old vectors were reused only after exact text/source/content/configuration
matches. All559current records pass their existing chunk/embedding contracts,
exact token counts (maximum477,480bound),finite dimensions and normalization.
Maximum independently measured L2 norm error:1.34e-7. No truncation or download.

Independent verification checked all559token-ID sequences against the model's
tokenizer and re-encoded the shortest/longest new texts (163/470tokens);both vectors
matched exactly. This is offline preparation cost,not student-visible latency.

Current chunk SHA:
`5e790a240eb79e1d2b9d176d462abb587ac7646ea289018ffcbb882f27ed5bdf`.
Vector JSONL SHA:
`cc41167b32fd19c41fe0a1d1b28ac93a1fa36700cbe3dac76787d8461863291b`.
Fresh complete-corpus embedding set:
`210b51f8850ccb17be7bdc9531c1875915bc7364c17fc83e689aaeb74d3c654c`.
All seven encoder configuration values match the historical465package.

Verification caught the authoring helper retaining the old manifest's explicit
embedding-set ID. The loader intentionally trusts a supplied ID;the helper now
removes it before deriving the current corpus identity. Focused identity RED:
1failed/2passed3.27s;corrected GREEN:3passed3.42s. The initial missing-vector RED
was2failures against465records. Historical artifacts were not changed.

## Complete bounded field coverage

Four parent claims exceed the optional64-name map. Their whole-service claim access
and complete208original review objects remain unchanged. Added source-side facets
partition existing fields into metadata/checklist,complete numbered steps and totals:

| Subject | Original fields | Added facets |
| --- | ---: | ---: |
| Admission test | 85 | 10 |
| Good moral certificate | 71 | 9 |
| Readmission | 65 | 6 |
| Transfer | 76 | 7 |

All297field references appear exactly once in their parent's partition;the largest
facet has30names. Every step retains its associated actions,time,person,office and
fees. Parent flat maps remain intentionally absent above64;their bounded child maps
expose every field. No source reading,wording,condition,approval or bound changed.
These are technical field groupings,not32new institutional conclusions.

Actual-data RED:2failed/2passed2.03s;GREEN:4passed1.15s. Independent checks verified
all32selector/context/render profiles with no missing/unverified fields. Their four
complete companion closures remain required;largest7566E5tokens. Facets solve the
field-name packaging problem;they do not shrink complete source context or prove
an answer. Both intentional negative findings remain unchanged.

## Local rehearsal and remaining gates

Six exact input copies plus explicit candidate-only status form the local package.
Existing PackageStorage,SourceAwareEvidencePolicy and145DocumentTopic contracts
accept it.145filtered self-vector storage probes retain required companion closure.
These are storage checks,not semantic retrieval or student-answer accuracy tests.
No subject budget override was installed. Old465package and active pin hash match.

Current default-capacity,selector semantics,initial/checker/repair English/Taglish/
Hybrid answers,and governed selected-release review remain open.54complete source
closures exceed2048E5tokens. Original cutoffs and held claims remain attached.
No school approval,public deployment,Phase11exit or Phase12advance is implied.

## Recovery evidence

All source-derived artifacts remain ignored under workspace/audit-evidence:

- `p11-559-vectors-20261027`:author/independent verifier,RED/GREEN logs,302reuse
  receipts,257resumable new vectors,manifest and `runtime-package/` with file hashes.
- `p11-559-topic-facets-20261027`:technical basis,derived register,topic export,
  exhaustive partition tests and independent rendered-field/context profiles.

Reproduce with the existing sharedPython3.13.7 venv and `-X utf8 -B`;pytest uses
`-p no:cacheprovider` and ignored external basetemp. Encoder resume validates all
saved batches and encodes only missing texts. Do not rerun frozen historical jobs.
The [preparation plan](2026-10-27-559-vector-capacity-plan.md) records the next gates.

Relevant existing source-review/retrieval/topic/companion regressions:143tests and
156subtests passed in3.13s. Documentation/phase checks:30tests/14subtests passed
in14.39s. Seven stable authoring artifacts repeat byte-identically;both original
PDFs,old/current package seals and active pin hash verify. Raw roots sealed locally.
No production code changed;the fresh f635ccc7025-test full-suite result remains
the applicable production freeze. No redundant full run or dependency installation.
