# Graduation application source diagnosis — 4 November 2026

Bounded A11 / stabilization Phase 6 source check at `9cc236c8` in an isolated
worktree. The pinned package **contains undergraduate graduation application
procedure fields**, separately from general graduation requirements. This does
not establish why the observed runtime reply missed them; no live trace ran.

## Pinned evidence

- Config: `C:/Coding-projects/bintanong_workspace/audit-evidence/p12-hosted-560-activation-20261030/hosted-research-api-config.json`.
- Pin: same directory, `hosted-research-pin.json`; SHA-256
  `8ba58463233bb51e67c1d42a4b218cd3c98d446edbebb08def20dd196d220a96`.
- Release `p12-research-faqsplit-20261030`; embedding set
  `f7a7f1b01770834c71838eccd6347ab1db798f0fe37917c9426fb79d93592218`.
- Package: `C:/Coding-projects/bintanong_workspace/audit-evidence/p11-local-documents-20261029/runtime-package`.
- Runtime seal SHA-256 `954d376e3c47e55856f2e7c959f4dd9b98f5195a2fb25242807e6081e4cabb8e`;
  all seven member digests verified against their local bytes.
- `draft-chunks.json` SHA-256 `480a0ff621991e6b06f89b2042a6c5c603c68eeb6672d65111f32e96f07c9fbf`;
  catalogue `cf500ded7b5d64872df5fef80df2091f9567a35d47a88d7e6e7db09ba14ba0b0`;
  source-review register `dc0ef7822a37cb4fcd344039dc1e6fc3659b7e28ce76317076e969aab464fb0e`.
- Original `PSU Student Handbook.pdf` bytes/version suffix:
  `4c9a95bf6895ddba75a997a37fa069644ac081dd7ab4a43f882496db834351c8`;
  version ID is `ver-` plus that digest. These are local source identities,
  not a claim of institutional currentness or approval.

## Different source subjects

| Subject / reviewed claim | Coverage in pinned package |
| --- | --- |
| `handbook_graduation` / `printed graduation fields` | Physical 50, two chunks: compliance, candidate lists, deficiencies, residence; not the application flow |
| `handbook_graduation_approval` / `printed graduation approval fields` | Physical 51, one chunk: date, graduation fee, council/Board approval |
| `handbook_image_flow_64` / `printed graduation process fields` | Physical 64, ten chunks, 27 review-bound fields: application through visible commencement steps |

Physical 64 readings `H-image-flow-64-geometry-v1-001` through `-010`
are all assigned to `handbook_image_flow_64`; none are unassigned. Review basis:
`audit-evidence/p11-expanded-topic-binding-20261027/binding-basis.json`, digest
`923761bdf5520097770f1bb11f873c1c291edbd96760ec913b071cd938315310`.
The source-review register records `visible_fields`. Top-level chunk verification
and review states remain `pending`; a field-bound research review does not
convert those states or authorize institutional activation.

| Reading suffix | Chunk ID | Visible process |
| --- | --- | --- |
| 001 | `4e0d8018e68eeefb1c4da6b338f772eba44ee7d560655c6012f7197f36984b1c` | Secure an application form for graduation; Student |
| 002 | `4ea1dc352acc36f9d6651e42aef89a434900c46aae5ac1ad601f48149c0cb9e3` | Student obtains form/complies with form requirements; Registrar staff receives application |
| 003 | `f336de00e73fd7ea79ad1cc168009acf4c3c5a88a61ff649625ac008b1f6621d` | Registrar staff evaluates completeness of records/grades |
| 004 | `5a1c460082d51c0cc0e82da6788fe3589e9e87c40c2ba8a4a29458b3abcc544c` | List of deficiencies |
| 005 | `481ca274acd23eb6e1c2eb94837ba73f0df4356910af6f776f87d3030054a4d8` | Encode list of candidates |
| 006 | `dda24ab7890abb4b43e0b3931f716ace4c76c7cd46cfca6b28ac78a2a44cd029` | Update Student Records |
| 007 | `883baa4ad3547dd1e2ed36c9545b1c411ae202aea8928eca62456df2f257db52` | Prepare final list of graduates |
| 008 | `eeca11b8a7b5657c26e2eeebbed6135953a7fa302ba977a4ae184dcb59247788` | Prepare diploma cover/certificates |
| 009 | `f502e8d677e6c4fc9b1dbb61b68c87420b1899ae47779002c614d2ccb28d6b6d` | Distribute diploma cover/certificates; University Registrar |
| 010 | `1925a5e44f273d7993c17ce973930b0f3be07ee29a2b47e36e2f4d2c624d5d0a` | Last detail cuts off at “during” |

The flow manifest has `source_complete=false` and unresolved outgoing geometry
after step 9. Last-detail limit `limit-1`, `source_cutoff`, explicitly affects
“remaining graduation process and endpoint unavailable”. Preserve this original
cutoff and refer to the University Registrar where the unknown continuation
matters. Do not infer form-specific requirements, a continuation, or an endpoint.
This agrees with `plans/source-gap-policy.md`'s physical-64 example and the
owner's 26 October fidelity instruction in the decisions ledger.

## Static authoring/selection trace and remaining live question

`research_app._package` reads the hash-bound pin and seal. The catalogue binds
readings to subjects; the review register binds exact claims/fields. Runtime
`research.topic_menu` builds a topic for every reviewed subject and carries
unresolved cutoff claims in `not_stated`. `SourceAwareEvidencePolicy._chunk_ids`
selects assigned chunks and their required neighbors for the requested claim.

A local Python 3.13 probe instantiated that policy from these package bytes,
without an encoder/model or HTTP, and supplied **all selected IDs** to `_assess`:
general requirements selected 2 chunks, procedure selected 10, both returned
`reviewed_fields_available`. Procedure assessment retained the emitted cutoff.
This proves static availability only. It did not retrieve/rank chunks, assemble
live context, or measure live `record_coverage`; that field was not present in
this static claim report. No answer completeness or retrieval success follows.

Next bounded probe on the current C04 runtime baseline: submit exactly
`how to apply for graduation?` once fresh, then once after one prerequisite
question in the same conversation. Capture pin/release identity, selected
subjects/claims, router parts, search scores and source IDs, emitted chunk IDs,
`record_coverage`, source-limit propagation and terminal disposition. Contrast
with `what are the graduation requirements?`. Locate the first stage losing
the physical-64 subject/fields before choosing a correction. Do not patch an
application phrase or acquire/activate sources based on this source-only check.

Consulted scope: thesis physical 17–18 and runtime routing architecture PNG;
this check stays within undergraduate academic affairs and document retrieval.
Original PDFs/package/configs were read only. Verification: seal-member hashes,
catalogue/review membership and static policy assessment; no live/browser/model,
HTTP, service or database checks and no source edits.
