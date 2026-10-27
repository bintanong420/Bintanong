# Expanded corpus hosted staging results

Owner-authorized import completed27October2026 through unchanged administrative
loaders. New release `p11-research-combined-20261027` remains **draft/inactive**.
[Plan](2026-10-27-hosted-corpus-staging-plan.md). No activation was requested or performed.

| Item | Verified result |
| --- | ---: |
| Combined release members | 465 |
| New expansion chunks uploaded | 388 |
| Existing members reused | 77 |
| Embeddings in new set | 465 |
| Source-version links | 5 |
| Curriculum links | 39 |
| Selected source-span rows | 2283 |
| Total stored chunks, including historical records | 479 |
| Total stored source spans | 2332 |
| Total stored embedding rows | 642 |
| Runtime-visible chunks | 78, unchanged |

The corrected78 package and388 expansion produce465members after omitting one
exact same-source/span penalty alias from the new membership. Both historical
records remain stored. Cash/check wording at different service locations remains;
four partial narrative overlaps retain their distinct fields/limits for later
canonical packaging. No source wording or source-register state was promoted.

## Verification and execution

- Existing storage suites:19tests/39subtests passed in106.69s; sharedPython3.13,
  `pytest -q -p no:cacheprovider tests/test_storage_client.py
  tests/test_storage_loader_idempotency.py tests/test_storage_release_isolation.py`,
  with external evidence-root basetemp. No production behavior changed;full
  application suite was not repeated for this data-only import.
- Exact local E5 encoding:388new vectors,77identical text/config vectors reused;
  1024dimensions,L2,exact tokenizer parity,max477<=480tokens,no truncation.
  CPU encoding610.83s;existing model only,no download/dependency change.
- Actual-data disposable-DB rehearsal passed in92.37s:388new chunks,91old rows
  preserved,exact chunk/span replay,465vectors,39links,draft invisible to anon and
  authenticated users,and unreviewed activation rejected. Fixture did not recreate
  old releases/vectors/active pointer;hosted pre/post comparison covers those.
- Initial rehearsal helper compared unordered SQL results positionally. Full-row
  multiset comparison proved unchanged content;helper corrected,then rehearsal
  rerun successfully. No production correction was necessary.
- First hosted465vector RPC hit server statement timeout. Independent SQL read
  confirmed zero vectors committed and no new release. Existing388new chunks and
  manifest remained. Sent25vector batches through the same transactional loader;
  all465committed,then draft and39links created. No timeout/schema/RLS setting changed.
- Final full16-table admin readback preserved every preexisting row,including
  timestamps,source states,receipts,old releases and vectors. All465chunk records
  and2283spans match prepared fields;all465vectors match within1e-7.
- Independent Supabase MCP SQL confirmed new465draft/465vectors/39curricula/5versions,
  corrected78active,old80draft and19superseded. Active pointer/timestamp unchanged;
  runtime anon selection still exactly the original78IDs. MCP works in resumed session.
- Fresh-context reviewer found no staging blocker;local-fixture limitation above
  retained. Security advisor reports Auth leaked-password protection disabled;
  [existing configuration guidance](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
  No auth configuration changed by this import.

## Evidence and recovery

Ignored evidence root:
`C:/Coding-projects/bintanong_workspace/audit-evidence/p11-hosted-expanded-staging-20261027`.
Preparation:`prepare_package.py`;encoding:`encode_package.py`;rehearsal:
`rehearse_package.py`;hosted import:`stage_hosted.py stage`,all run with the
existing sharedPython environment. `operation-state.json` records completion;
`hosted-before.json`,`hosted-after.json`,`hosted-staging-result.json`,independent
SQL receipt,and `artifact-seal.json` preserve readback and identities.

- Before snapshot SHA256:`58f25df1b1310afb2654810110d2dae9c59ea9167eb519998d33d24ae2c978d5`.
- Expansion388input SHA256:`589530958bc5ca0745012b0c2c0ee44f1b55883eadd215506b03081c8f38c7b6`.
- Embedding-set ID:`d846afc365c812e318b6193f8c16b41b2395af752ae87e47711a33bcbd9579b4`.
- Existing active release:`p11-research-corrected-20261026`;local runtime pin and
  active package unchanged. No rollback switch is needed because activation never changed.

## Remaining gates

Hosted storage is complete;activation is pending. Final service/image structural
bindings,label/native-hyphen/URL normalization,canonical packaging,context-budget
and answer regressions,and applicable selected-release review remain outstanding.
Known source gaps and undergraduate restrictions accompany the data;no university
approval,source completeness guarantee,frontend integration,executable-rule change,
public deployment or Phase11exit is implied. Preserve prior approvals without re-asking.
