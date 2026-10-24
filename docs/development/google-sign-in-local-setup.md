# Local Google sign-in setup

For the owner's manual test of landing concept3 and auth concept2. The frontend
is http://127.0.0.1:3215; chat is `/chat`, login is `/login`. The research API is
http://127.0.0.1:8021. Google authentication remains required for chat and uploads.

## Already prepared locally

The ignored `frontend/.env.local` points to the existing hosted Supabase project
using its public/anon key. It contains no Google client secret. The API uses the
reviewed research composition and existing model services. Its readiness probe
passed Supabase, Janus, embedding, Bintu and student-runtime checks; anonymous
curricula access returned401. These are software observations, not a human login.

Owner update24Oct: Google Cloud and Supabase configuration is complete. Live
settings report Google enabled, and the app's303 redirect sets a PKCE cookie;
Supabase then returns302 to `accounts.google.com` with the correct hosted callback.
Owner subsequently confirmed that PalSU email login works. Non-PSU rejection and
the full authenticated chat/upload flow still need the owner's manual test.
Steps1–2 below are the reproducible setup reference; continue
with step3 for the current preview.

## 1. Create the Google application

Open [Google Auth Platform](https://console.cloud.google.com/auth/overview) and
select or create the Google Cloud project for Bintanong.

1. In **Branding**, enter Bintanong's app name and your support/developer email.
2. In **Audience**, use External if this project is outside the PSU Workspace
   organization. While the application is in Testing, add the PSU Google account
   you will use under Test users. Internal applies only to the selected Workspace
   organization; it is not a substitute for Bintanong's server-side PSU checks.
3. In **Clients**, create an OAuth client with type **Web application**.
4. Add this Authorized JavaScript origin:

   ```text
   http://127.0.0.1:3215
   ```

5. Add this exact Authorized redirect URI:

   ```text
   https://jyrudbiuajahsucsorco.supabase.co/auth/v1/callback
   ```

6. Save the client ID and client secret. Enter the secret only in Supabase's
   provider settings, never in Git, frontend public variables or chat.

## 2. Enable Google in Supabase

Open [the project's Google provider settings](https://supabase.com/dashboard/project/jyrudbiuajahsucsorco/auth/providers?provider=Google).
Enter the Google Web application's client ID and secret, enable Google, and save.

In [Authentication URL Configuration](https://supabase.com/dashboard/project/jyrudbiuajahsucsorco/auth/url-configuration), set:

| Setting | Value |
| --- | --- |
| Site URL | `http://127.0.0.1:3215` |
| Allowed redirect URL | `http://127.0.0.1:3215/auth/callback` |

Keep any already-authorized deployment URLs. Use127.0.0.1 consistently for this
test rather than switching to localhost mid-login. Google redirects to Supabase's
HTTPS callback first; Supabase then redirects to this application's local callback.

## 3. Manual test

1. Open http://127.0.0.1:3215. The landing page is public. Check the theme picker,
   mobile/narrow layout, scope information and privacy link.
2. Choose Ask a question. A visitor should reach `/login`.
3. Continue with PSU Google should be available. If the page was already open
   during setup, reload it first.
4. Use the verified `@psu.palawan.edu.ph` Google account added as a test user.
   Successful authentication should lead to `/chat`.
5. Select the appropriate program/curriculum, ask a supported question, and inspect
   its returned source. Try Stop and New chat. Private files are optional; use
   a synthetic PDF for an initial upload/explicit-review/remove test.
6. A non-PSU account should be refused. Do not count this as verified until an
   actual human login has exercised it. No auth bypass is provided for preview.

If Google says access is blocked, first check the OAuth client's audience/test
users and the exact redirect URI. If login returns but Bintanong refuses it,
verify that the chosen account is a confirmed PSU Google identity. Report the
visible error text; do not share passwords, cookies, tokens or client secrets.

## Local services

The current session started Next.js on3215 and the authenticated research API on
8021. The API uses existing Python3.13/model resources; no new weights or packages
were installed for this UI change. Existing development startup/config details:
[student workspace setup](student-ui-integration.md).

The frontend's current Google button checks the hosted provider setting on every
login request. Enabling the provider does not require a code or lockfile change.

Official references checked24October2026:
[Supabase Google OAuth](https://supabase.com/docs/guides/auth/social-login/auth-google),
[redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls),
[server-side clients](https://supabase.com/docs/guides/auth/server-side/creating-a-client).
