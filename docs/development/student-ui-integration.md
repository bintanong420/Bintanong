# Running the integrated student workspace

The owner's local preview runs from `C:/Users/Hawksprey/source/repos/Bintanong`, branch `frontend`.
It includes the committed integration and backend synchronization through4a134bf. The implementation
worktree `C:/Coding-projects/bintanong_workspace/worktrees/Bintanong/p11-frontend-integration` retains
separate unfinished lifecycle work; those edits are not part of this preview.

The public landing page is `/`; the authenticated student workspace is `/chat`. `/login` uses auth
concept2; successful PSU sign-in leads to `/chat`. `/dev/health` retains the developer dashboard.
No simulated answer/upload/clear adapter is imported by the student workspace.

## Required configuration

Before building or starting Next.js, provide these in its ignored `.env.local` or process environment:

```dotenv
NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLIC_KEY
SITE_ORIGIN=http://127.0.0.1:3215
API_INTERNAL_URL=http://127.0.0.1:8021
```

The publishable/anon key is public by design; never substitute a service-role/secret key. Authentication
tokens remain in the Supabase session cookie and server-to-server authorization header. Next forwards only
the backend's `__Host-bintanong_session` credential; FastAPI verifies the PSU Google identity independently
on every protected request. All unsafe requests require an allowed Origin. Use HTTPS for deployment.

API process environment additionally needs `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
`BINTANONG_RESEARCH_CONFIG` (absolute trusted JSON path) and `STUDENT_ALLOWED_ORIGINS` (comma-separated,
matching SITE_ORIGIN). Model/embedding/DB health URLs use the existing BINTU_URL/EMBEDDING_URL/SUPABASE_DB_URL.

The runtime JSON contains schema_version=`bintanong-student-runtime-v1`, authorization_ref,
hosted_release_id, document_policy (reviewed metadata JSON path), model_url, embedding_url, and optional
approved program_names/curriculum_names dictionaries. Credentials and artifacts stay ignored outside Git.
It validates the hosted release, reviewed ledgers, document snapshot, metadata bindings and encoder identity.
It refuses privileged keys and missing configuration; there is no synthetic or anonymous fallback.

```powershell
# From worktree root, with the existing Python 3.13 API environment:
python -B -m uvicorn backend.bintanong_api.research:load_research_app --factory --host 127.0.0.1 --port 8021 --no-access-log
# In frontend/, using the declared Node 24.21 environment:
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3215
```

`backend.bintanong_api.main:app` is health-only. The student factory above composes Lawrence's
ResearchPipeline/create_app and requires authentication. `/health/ready` includes student_runtime and
validates the release pin; liveness alone is insufficient. API restarts discard temporary sessions.

The resident embedding service needs the strict `/query/configuration`, `/query`, `/query/token-count`
port, `EMBEDDING_ASSET_MANIFEST` and existing read-only model assets. Its source mount must point at this
worktree for reproducible restarts. No second host encoder or model download is needed.

## Google sign-in and manual testing

Master25.1 requires Supabase Auth with PSU Google accounts. The owner configured Google Cloud and
Supabase on24Oct. Hosted settings now report Google enabled. The actual app redirects to Google's
authorization endpoint through Supabase, with the expected callbacks and PKCE cookie. The owner
confirmed actual PalSU email login works. Non-PSU rejection and the complete authenticated manual flow
remain unverified. See the [local setup and manual checklist](google-sign-in-local-setup.md).

1. Create/reuse a Google Cloud **Web application** OAuth client and configure its consent screen. Its
   authorized redirect URI is `https://YOUR_PROJECT.supabase.co/auth/v1/callback`.
2. In Supabase Authentication/Providers/Google, enter that client ID/secret and enable Google. Enter the
   secret in the dashboard, never in a tracked file or chat. Configure any required Google test users.
3. In Supabase redirect settings, allow exactly the application's `/auth/callback` URL for the configured
   SITE_ORIGIN, plus its eventual approved HTTPS deployment URL. Use the same origin when building Next.
4. A human verifies an actual PSU account login and rejects a non-PSU account. The Google `hd` hint is only
   a convenience; FastAPI checks the verified primary email and verified Google identity itself.

If the provider becomes unavailable, `/login` explains the condition and disables its Google button.
The only synthetic auth used in earlier verification runs in a separate loopback fixture instance,
not this research application.

## Current capability and limits

Queue: one running answer/four waiting, then busy; one queued/running answer per verified account across
tabs/devices. The UI exposes waiting and Stop. It does not automatically replay an uncertain completed
request; the backend deliberately rejects an already-answered message ID. Resending is an explicit new check.

Use the checked curriculum picker for course checks/private files. A PDF is parsed in an isolated child;
students choose statuses before confirmation. No printed grade is converted. One pending PDF is reviewed
before adding another; confirmed file references can be removed individually. Existing files remain until
the backend acknowledges changes. No /context endpoint, persistent history or photo/OCR support is invented.

Live clarification now opens a focused dialog with reviewed curriculum choices and course-status questions
derived from canonical backend unknowns. It supports an explicit unknown, alternative/additional explanation,
review and confirmation. Dismissal and unrelated failed operations preserve its draft. Confirmation sends the
original question and stated details through the existing untrusted chat path; it does not create trusted facts.
This self-contained reply does not implement server-side pending-question replay. See the
[workspace verification and current startup blocker](../../plans/2026-10-24-student-workspace-polish.md).

Server-side pending-question continuation, broader natural-language curriculum aliases, actual PalSU grade layouts and
the backend's disclosed Hybrid/model-language gaps remain separate work. E3's office-referral fix is included.
Sign-in stores an auth user/email
in Supabase as recorded in master25.1; chat/grade/file state stays temporary. No university approval or public
release follows from this local integration.
