# Security and privacy measures inventory (for thesis Chapter IV)

Date: 24 October 2026. Branch `feat/p11-backend-api` at `05f34d2`. Owner request: list every security measure
built so far, for the manuscript. Mapped to the thesis headings where the controls are promised:
Scope and Limitations (physical pages 17-18), Chapter IV "Ethical Considerations": Data Privacy,
Read-Only System Architecture, Responsible Use of AI, Institutional Document Authorization (physical 64-66),
and the private-file input description (physical 55).

Status words: **built and tested** (code plus automated tests), **verified live** (also observed on the real
model and hosted data), **planned** (owner-decided, not built), **deployment** (belongs to the server setup).
This is a research build. None of this is a penetration test, an institutional security audit or a
deployment claim; the thesis itself limits protection to "the security controls implemented and tested within
the Bintanong system" (physical 18).

## 1. Private uploaded files (thesis: Scope p.17-18, Chapter IV input data p.54, Data Privacy p.64)

| Measure | Where | Evidence | Status |
| --- | --- | --- | --- |
| Uploaded files never enter the institutional knowledge base; the private package has no code path to storage, retrieval, embedding or ingestion | `backend/bintanong_private_context/` | `test_private_context_isolation.py` (import check) | built and tested |
| Another session cannot read a student's file, extracted rows, facts or conversation | `sessions.py` | `test_private_context_sessions.py`, `test_private_context_conversation.py` | built and tested |
| Files are processed in memory only; no temporary files, nothing written to disk or the database | `uploads.py`, `worker.py` | temp-folder check in `test_private_context_isolation.py` | built and tested |
| Text written inside a file cannot steer the AI (prompt injection by upload): only a matched course code, the candidate courses and the printed mark leave the extractor | `grades.py` | `test_instructions_inside_the_file_never_leave_the_extractor` | built and tested |
| Grades are never interpreted automatically; the student confirms passed/failed per row, and a refused confirmation stores nothing | `grades.py`, `sessions.py` | Phase 10 exit gate | built and tested |
| File type is decided from the bytes, not the file name; size cap 15 MiB (streamed), PDF cap 20 pages, image cap 60 megapixels | `uploads.py` | upload tests | built and tested |
| Untrusted files are parsed only in a separate child process with a 30 s timeout; a crash or hang ends only that child | `worker.py` (fix S5 `b0dc62b`) | worker tests | built and tested |
| At most 2 uploads parse at once; more get "busy" before the body is read | `uploads` router (fix S6 `93e795e`) | API tests | built and tested |
| Upload delete, session expiry (30 min idle) and server restart remove everything | `sessions.py`, `DELETE /session` | live smoke: after delete, the same check became "unknown" again | verified live |
| Photos/scans refused (`photo_ocr_unavailable`) because OCR misread rows on tilted photos; a wrong grade is worse than none | `photo_rows.py` | photo probe, 2 strict xfails | built and tested |

## 2. Sessions and the web API (thesis: "access restricted to the authorized user/session", p.17-18)

| Measure | Where | Evidence | Status |
| --- | --- | --- | --- |
| Random session credential (`secrets.token_urlsafe(32)`); the server keeps only its SHA-256 digest | `sessions.py` | session tests | built and tested |
| Cookie hardened: `__Host-` prefix, HttpOnly, Secure, SameSite=Strict; unknown or tampered cookies get a fresh session (no session fixation) | `backend/bintanong_api/` (`d42feac`) | API tests; live `DELETE /session` sent Max-Age=0 | verified live |
| Cross-site request forgery blocked: every state-changing request needs an allowed `Origin`; `Sec-Fetch-Site: cross-site` refused; no CORS opening | API origin guard | live: foreign origin got 403 | verified live |
| Session-table lockout fixed: when 1000 sessions exist, the oldest *empty* session is evicted instead of refusing new students | fix S1 `15934a7` | re-probe: after 1000 cookie-less requests a new student still got 200 | verified live |
| Input limits: a question over 8192 characters or a malformed chat body gets 422 before any processing | fix S4 `8b67b8d` | API tests | built and tested |
| Errors are fixed codes; no stack traces, file text, database host or user names are returned (incl. `/health/ready`) | fixes S2 `e87ed7b`, S7 `72ec6d4` | API tests | built and tested |
| Students never see internal ids, variable names or rule codes | `presentation.py` (owner O4) | API tests | built and tested |
| `/sources/{id}` returns only release evidence cards, never private material | Task 6 `b8f829b` | API tests | built and tested |
| Answer queue limits load on the single GPU model: 1 running + 4 waiting, then 503 `answers_busy` | `d1d416c` | live: 6 students at once, 5 served in order, the 6th got "busy" in 0.5 s, no errors | verified live |
| A client that disconnects mid-answer frees its slot | Task 4 `c2cae2e` | live smoke | verified live |

## 3. Data privacy and data minimization (thesis: Data Privacy, RA 10173, p.64-65)

| Measure | Evidence | Status |
| --- | --- | --- |
| No grades, conversations or student records are stored; session data lives in server memory only and expires | Phase 10 exit gate "no persistent personal records" | built and tested |
| The private package has no logging, printing or file writing; no grades or ids in logs, errors or exports | `test_private_context_isolation.py` (AST check) | built and tested |
| Telemetry events are an allowlist: stage, timing, route, status and evidence ids only; no questions, facts, grades or prompts | `StageEvent` contract | built and tested |
| Each student's facts stay in their own evidence branch, even with concurrent requests | `test_orchestration_sessions.py` | built and tested |
| Planned PSU sign-in will store only the Supabase Auth user row (email); emails and tokens are never logged or sent to the model | master 25.1 | planned (UI integration) |

## 4. Institutional knowledge base and database (thesis: Read-Only Architecture p.65, related study 2.1.11)

| Measure | Where | Evidence | Status |
| --- | --- | --- | --- |
| Row Level Security on every application table; the runtime roles (`anon`, `authenticated`) may only read | migrations `20261012010000`-`010003` | Phase 04 effective-privilege check: 0 write privileges incl. TRUNCATE | verified on hosted DB |
| An independent audit (12 Oct) found leftover write/TRUNCATE privileges and draft data visible; all were fixed and re-verified before Phase 05 | `phase-04-security-review-2026-10-12.md`, `c48f404`, `6e762a5` | audit and repair record | verified on hosted DB |
| Only the approved active release is visible to students; drafts, unreleased and superseded content stay hidden; published content is immutable | release security migration | Phase 04 tests | built and tested |
| Admin actions (loading, release activation, rollback) need the service role | migrations | Phase 04 tests | built and tested |
| Supabase security advisor | hosted project | 0 security findings (re-run 24 Oct 2026) | verified on hosted DB |
| Bintanong cannot change university records: no write access to any university system, no enrollment, COR or grade changes | architecture | read-only boundary in every phase | by design |
| Secrets: database keys live in an untracked `.env`; the only key-like strings in Git are Supabase's public local-demo keys | 24 Oct secret scan | security review | checked |

## 5. Responsible AI and abuse resistance (thesis: Responsible Use of AI, p.65)

| Measure | Evidence | Status |
| --- | --- | --- |
| The model never writes free text to students: answers are validated claims tied to cited release evidence, or fixed host sentences | Phase 09 validator; generation tests | built and tested |
| Router output is forced into a fixed JSON schema and then checked by host code (quotes must exist in the message, courses must match reviewed aliases) | routing validation tests | built and tested |
| Eligibility comes only from reviewed Prolog rules, never from model guessing; missing information stays "unknown" | Phase 06/08 tests | built and tested |
| Off-topic, prompt-injection and secret-extraction requests get the fixed out-of-scope notice | live abuse probe: 13/13 refused, 0 leaks (after fix S8 `5ee7b50`) | verified live |
| Excluded audiences (graduate, Law, Medicine, staff) get a scope notice, not substituted undergraduate rules | routing tests | built and tested |
| Missing topics get an honest "not in reviewed sources, ask the office" reply, not a guess (E1 `7c3786e`, E3 `05f34d2`) | live re-check | verified live |
| Every reply starts with a "Candidate preview only. Not official university guidance." line | renderer | built and tested |
| Source-gap rule: a cut-off or conflicting source is stated, never filled in | `limit_notices` tests | built and tested |

## 6. Evaluation integrity

| Measure | Evidence | Status |
| --- | --- | --- |
| Final evaluation set kept separate from prompt examples (leakage and provenance checks) | `9bfcada` | built and tested |
| Every new security guard was mutation-checked: removing the guard makes a test fail | checkpoint records | done |

## Not done yet (state these as limitations)

- Frontend dependencies: `next` (critical RCE advisories), `sharp`, `source-map-js` (high). Owner decision: upgrade
  at UI integration (S3).
- PSU Google sign-in and the per-account limit: planned (master 25.1).
- Per-client rate limits and a request-body limit: reverse proxy at deployment. The API sees only the frontend server's address.
- Memory limit for the parser child: container setting at deployment (Windows has none).
- No HTTPS/TLS configuration yet (deployment); the `Secure` cookie requires it.
- No external penetration test; no linter or static-analysis tool installed (only manual review and tests).
- Results come from one machine and one attempt per probe. They are not rates.

## Suggested manuscript wording (Chapter IV, after "Data Privacy")

> **Security Measures Implemented.** Bintanong's security controls were implemented and tested in four layers.
> (1) *Private-file isolation:* uploaded grade reports are parsed in memory by a separate, time-limited process,
> never indexed into the institutional knowledge base, and deleted when the session ends; only a matched course
> code and printed mark leave the parser, so text inside a file cannot instruct the AI. (2) *Session security:*
> each user receives a random, HttpOnly, Secure, SameSite=Strict session cookie whose value is stored only as a
> hash; requests from other sites are refused; inputs are size-limited; errors reveal no internal details; and
> a queue limits concurrent questions. (3) *Database access control:* Row Level Security restricts runtime roles
> to reading the approved release only; an independent audit's privilege findings were corrected and verified,
> and the Supabase security advisor reports no findings. (4) *AI safeguards:* the model's output is constrained
> to a schema and validated by host code, eligibility decisions come from reviewed Prolog rules, off-topic and
> prompt-injection requests receive a fixed refusal (13 of 13 refused with no leaks in a live probe), and missing
> information is answered with an office referral rather than a guess. No grades or conversations are stored.
