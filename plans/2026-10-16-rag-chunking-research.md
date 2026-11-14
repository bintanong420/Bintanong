# RAG chunking research: interpreting the selected 19 chunks

Owner requested this research on16October2026 after asking whether the reviewed
material becoming19chunks is normal. Baseline21ceea5; no product/source changes.

## Accepted justification

On 16 October 2026, the owner accepted the research explanation with
"ok that's good enough. Just document that somewhere so we have good justification".
This records acceptance of the chunking rationale for the selected development
package; it introduces no source-content or release approval.

The selected development corpus groups 52 reviewed field associations and
54 source spans into 19 coherent retrieval chunks. Chunk boundaries follow
related policy records and preserve source citations, limitations and required
neighboring context. This is consistent with documented RAG practices that
separate fine-grained retrieval from the wider context needed to interpret it.
The chunk count reflects this bounded selection. Its adequacy is judged through
coverage of the intended questions, recovery of relevant evidence and retention
of material conditions, rather than a predetermined minimum number of chunks.
These 19 chunks support bounded development testing; they do not establish
complete coverage of the original documents or the finished system. The primary
sources supporting this justification are linked below.

## Findings from primary sources

Multiple reviewed fields becoming one coherent chunk is consistent with RAG.
Chunk boundaries can follow sentences, sections, semantic units or structured
records; they need not match PDF pages, source-review decisions or questions.
Microsoft documents these alternatives and demonstrates that different splitting
settings produce substantially different counts from the same document. Its
512-token/25%-overlap suggestion is a starting configuration, not a universal
size or corpus-count requirement. [Microsoft chunking guidance](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents).

Retrieving a small unit while restoring surrounding context is an established
pattern. LlamaIndex's sentence-window example embeds individual sentences and
passes their surrounding window after retrieval. This supports the general
design of small retrieval units plus necessary context; it does not validate our
specific neighbor links or model performance. Current official documentation
was fetched through Context7. [LlamaIndex sentence-window example](https://developers.llamaindex.ai/python/examples/node_postprocessor/metadatareplacementdemo/).

Very short fragments can lose their subject, time period or other meaning.
Anthropic illustrates this with an isolated financial statement and adds document
context to improve retrieval. This is evidence for preserving context, not a
requirement to adopt its models or generate additional institutional wording.
[Anthropic contextual retrieval](https://www.anthropic.com/engineering/contextual-retrieval).

Evaluate relevant evidence recovered and irrelevant/redundant material returned.
Chroma's technical report measures these at token level using precision, recall
and intersection-over-union. Its findings concern its own datasets and cannot be
transferred as a performance guarantee for Bintanong.
[Chroma chunking evaluation](https://www.trychroma.com/research/evaluating-chunking).

A multi-dataset study likewise reports different suitable chunk sizes for concise
fact retrieval and tasks needing wider context, with embedding-model differences.
This supports testing the intended capability instead of treating a size/count
as universally correct. [Bhat et al.,2025](https://arxiv.org/abs/2505.21700).

## Application to this repository

The19chunks are an intentionally selected development corpus:52field associations,
54source spans and five original source files, not the entire handbook/Charter
or everything the owner has reviewed. The scope packet lists the selection.
A grade-table row, for example, holds its grade, percentage and rating together.

Read-only inspection of the unchanged draft shows2,309characters in source_text
across19chunks, with minimum/median/maximum6/119/261characters. These are source
fragment lengths, not embedding-token counts or total serialized context size.
The adapter embeds chunk.text, which includes serialized field labels and limits;
it does not simply embed the bare source_text fragment. Existing chunk token
estimates are also not fresh tokenizer measurements. No model/tokenizer was run.

F08's bare source fragment is370.37; the arrows fragment is Yes/No/END. Their
field labels and required context matter. Required-neighbor assembly addresses
context preservation after retrieval, but does not by itself prove that isolated
embedding representations retrieve every intended question correctly.

Inference: this is a reasonable small pilot selection. Its count cannot establish
broad undergraduate coverage, robust retrieval against a larger corpus, or final
answer quality. Existing39document observations remain18field-available but
uncalibrated/21insufficient, with36/39related contexts; answer sufficiency is
unassessed. Do not relabel that result as a full-corpus RAG validation.

RAG does not impose a fixed conversion ratio from review decisions to chunks or
a requirement to have a human approve each chunk. Bintanong's source-review,
undergraduate-scope and release gates are project/thesis governance requirements.
Repackaging confirmed fields does not invalidate their existing confirmations.
The separate selected-review completion question remains unanswered; this
research request is not recorded as an approval or new source-content decision.

Retain the existing package and completed evaluations. Do not split/merge solely
to change the count, create a new sweep, expand into unsupported audiences, or
reroute curriculum eligibility away from structured facts/Prolog. Further corpus
work must serve a concrete supported capability and applicable phase requirement.

## Verification and limits

This is an owner-requested literature review and read-only package inspection,
not a new retrieval experiment or chunking implementation. Sources are primary
documentation, first-party research and the study authors' paper. Research does
not supply institutional authenticity/currentness, release authority or Phase06
eligibility. Product, database, dependencies, model assets and existing sealed
evidence are unchanged; owner artifact changes remain unstaged.

Documentation/phase-ledger checks:518tests and11subtests pass in11.44s, exit0.
Existing Python3.13 environment, pytest cache disabled and workspace basetemp;
no dependency change or unchanged product-suite rerun. Phase validation is valid
and remains blocked; whitespace checks pass. Four documentation files form this
research/continuity commit. No owner decision or source status was changed.
