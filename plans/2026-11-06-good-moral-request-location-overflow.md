# Good-moral request/location context overflow

Owner exact question: “Paano mag-request ng Good Moral? Saan po ito kinukuha?”
Student saw temporarily unavailable. Services remained healthy; saved API errors
show `context_overflow` at topic selection, before evidence retrieval/generation.
Latest failure `api-error-1793960696253933900.json` is ignored execution evidence.

## Cause and correction

The generic word “request” matches many reviewed service labels, adding too many
optional client-step examples to the full145-topic selector. Measured system content
7749tokens plus request/template and reserved output exceeds the existing8192 context.

Retain every topic and original labels. Use corpus-label frequency to omit common
words from optional example matching (terms shared by more than three service topics),
then cap client-step examples at three across the full selector. This changes display
hints only; original question, claim vocabulary, reviewed content, selected-topic step
metadata, semantic routing and all support/scope/privacy guards remain unchanged.
No model context increase, dependency change, new source claim or source override.

## Verification

- Synthetic RED: common request expanded12 service examples; global bound allowed12.
  Both regressions failed before the correction. New tests in `test_routing_source_fit.py`.
- Focused151 passed3.42s; final routing/orchestration/generation338 passed6.66s using
  existing Python3.13, cache-off, ignored external basetemp `goodmoral-location-regression-final`.
- Exact question selector system content now7240tokens. Isolated live router succeeds:
  English/Taglish policy selects Taglish; both request and location parts select Charter
  good-moral evidence. No claim of generated-answer acceptance yet.
- Ignored probe/evidence: `good_moral_request_location_probe.py`,
  `good-moral-request-location-router.json` under benchmark-fixes-20261106.
- Dev-only8022 reload and exact3217 HTTP check are the remaining verification.
  Main/frontend/model stay running, keepalive preserves zero dev rate window/grade5120.

## Live acceptance

Code `c20c1d1a` loaded into dev API61132/server18844. Exact owner question through
`3217/api/chat` returned HTTP200, status answered, Taglish, Charterpp52–53, OSAS service
and complete reviewed seven-step process with checklist/printed fee/total. No duplicate
process rendered for the two requested parts. HTTP9.92s excludes rendered-browser time.
Evidence: ignored `good-moral-request-location-r4-chat.json` and `.sse`.
Allfive endpoints HTTP200, keepalive36880 active; automated queries stopped.
No full72 rerun or universal natural-wording claim. New commits remain local, not pushed.
