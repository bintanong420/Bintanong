# Landing concept3 and auth concept2

Owner requested the Figma landing/auth pages and Google/backend setup, then chose
landing concept3, auth concept2 and antislop during implementation. No phase
advancement or new authentication provider is authorized by this task.

## Design evidence and decisions

- [Landing concept3, node26:5730](https://www.figma.com/design/tYH9AcExjq0UyIXpKJVgGa/Bintanong-AI---Frontend-Design?node-id=26-5730): broad photo band, centered introduction and paired actions.
- [Auth concept2, node27:9426](https://www.figma.com/design/tYH9AcExjq0UyIXpKJVgGa/Bintanong-AI---Frontend-Design?node-id=27-9426): split image/form composition.
- The Figma MCP tools were not exposed; connector search found it unconnected.
  Read-only browser/prototype inspection supplied actual reference screenshots.
  No claim of Figma MCP access or exported design assets.
- Existing approved campus photograph replaces mock artwork/photo; the literal
  university seal was not fabricated. Bintanong uses its existing wordmark.
- Concept2's template email/GitHub controls become the already-required PSU Google
  flow. No email/password, GitHub login or separate account-registration system.
- Unsupported4200+ user/social-proof placeholder omitted. About/scope and privacy
  destinations are actual page sections; no invented developer biographies/terms.
- Design read: PalSU research landing and student sign-in, neutral light/dark
  typography with campus imagery; ENERGY1/RHYTHM2/MOTION1. Photo establishes place,
  centered hero follows concept3; split auth follows concept2. Existing fonts,
  control primitives, themes and spacing serve consistency and reading comfort.

## Boundaries and implementation

Public `/` is the landing page. `/chat` holds the existing workspace and remains
protected by the existing verified PSU Google policy. Successful OAuth and an
already-signed-in login request lead to `/chat`. API authorization is unchanged.
No academic routing/retrieval/generation/Prolog changes or lifecycle WIP copied.

The ignored frontend env now uses the existing hosted public settings. The owner
configured Google Cloud and Supabase; live settings now report Google enabled.
[One-document setup/manual checklist](../docs/development/google-sign-in-local-setup.md).
The real API runs8021 with all readiness probes passing and anonymous access401.
Real PSU/non-PSU OAuth remains an owner/external verification step.

## Verification

- Existing public auth-policy seam: new page-access regression observed RED
  (missing export), then GREEN2. Combined auth tests4 pass; complete UI suite45.
- Installed Node24.21/npm11.19, `next typegen` and `tsc --noEmit`:pass.
- Live route check:root200,login200,chat307 ->login,anonymous API401.
- Next16.4.3 production build:pass, including final contrast/accessibility fixes.
- Actual Edge browser31 checks pass: both pages,320/390/768/1440px, light/dark/system,
  keyboard skip link, scope/privacy destinations, protected chat ->login, enabled
  Google action, wrong-account error,200% auth text reflow and no runtime errors.
- Initial button contrast RED1.108:1 exposed an anchor color overriding the shared
  button foreground. Scoped the inherited link color to non-button links; final
  measured control contrast14.05:1 minimum across both themes. Appearance control's
  accessible name was also made explicit after the browser locator exposed it.
- All rendered page text and the wrong-account alert measured above4.5:1 in both
  themes; lowest5.58:1 in the light error state. Caption calculation used white
  behind its dark translucent panel as the conservative photograph backing.
- Hosted Google enabled; app303 ->Supabase sets PKCE verifier cookie, then302
  ->accounts.google.com. Local callback127.0.0.1:3215/auth/callback and hosted
  jyrudbiuajahsucsorco.supabase.co/auth/v1/callback verified. No human exchange claimed.
- Scripts: pinned Node24.21 `--experimental-strip-types --test tests/*.test.mjs`,
  `node_modules/next/dist/bin/next typegen`, `node_modules/typescript/bin/tsc --noEmit`,
  `node_modules/next/dist/bin/next build`; external `check-pages.mjs`, `check-contrast.mjs`
  and `check-text-contrast.mjs`.
  Screenshots/scripts and `oauth-readiness.json` stay ignored under workspace
  `audit-evidence/p11-20261024/landing-auth-setup/`.
- No new dependencies, model downloads, schema changes, deployment or source activation.

## Review and remaining work

The owner can now test an actual PSU login, curriculum selection, supported chat,
synthetic PDF review/removal, clearing and sign-out using the linked checklist.
Phase11 remains active with its inherited evaluation gates. This UI increment
does not resolve the recorded Docling environment failures or model-quality gaps.

## Antislop delivery gate

Scope: the two changed public pages; existing chat behavior retains its separate
integration evidence and unresolved phase exits. Static source review, the actual
browser run and measured contrast support the following gate.

- R-02 PASS: no em dash in either page's copy.
- R-03 PASS:24 page/theme/width reflow checks;200% auth text reflow.
- R-17 PASS: no user counts, uptime or performance statistics.
- R-18 PASS: no testimonials or invented people.
- R-23 PASS: owner-selected Figma compositions and existing approved campus asset.
- R-24 PASS: home, scope, privacy, login and chat destinations exist and were exercised.
- R-25 PASS: measured text contrast minimum5.58:1 including error state; controls14.05:1 minimum; conservative caption backing checked.
- R-26 PASS: theme, links, anchors and actual OAuth form have working behavior.
- R-27 PASS: unavailable provider disables Google with retry guidance; wrong-account and failed-login alerts remain explicit.
- R-28 PASS: no filler FAQ.
- R-32 PASS: keyboard skip/navigation and existing visible focus outlines checked.
- R-33 PASS: implementation is in tracked TSX/CSS; external scripts only verify.
- R-34 PASS: light/dark/system checked for both pages at four widths.
- R-35 PASS: app run and production build pass; Google submit reaches real authorization.
- R-36 PASS: research/currentness/advisory limitations shown; no compliance or speed claims.
- R-37 PASS: owner selected landing3/auth2; design read and dials recorded above.
- R-38 PASS: no fabricated metrics, team, features or ghost links.
- R-01 PASS: no gradient/glow; campus photograph supplies place and identity.
- R-04 PASS: back arrow signifies navigation; existing theme icons identify appearance.
- R-06 PASS: existing Geist/Inter retained for familiar heading/body hierarchy.
- R-07 PASS: no background grid or decorative pattern.
- R-08 PASS: only a back-navigation arrow, no decorative CTA arrows.
- R-09 PASS: research status is plain text, no decorative capsules.
- R-10 PASS: no glass panels or blur.
- R-12 PASS: no page-wide floating shadows; existing control treatment retained.
- R-13 PASS: no glow.
- R-14 PASS: no generic feature-card grid.
- R-19 PASS: motion1; existing control feedback only, reduced-motion support retained.
- R-22 PASS: campus photograph replaces unrelated template artwork.
- Dials PASS: ENERGY1/RHYTHM2/MOTION1 documented and reflected by quiet type/photo composition.
- Focal point PASS: centered landing heading/action and centered auth action.
- Whitespace PASS: separates campus, invitation, scope and privacy; form stays readable.
- Accent PASS: the campus image is the repeated chromatic accent against neutral controls.
- Identity PASS: PalSU entrance, Bintanong heading voice and university-specific scope recur.
- Design read PASS: recorded before generation with owner-selected references.
- C-1 PASS: composition, asset, font and control purposes documented above.
- C-2 PASS: real destinations and actual OAuth submission; no dead controls.
- C-3 PASS: introduction, scope and privacy each address a student decision.
- C-4 PASS:31 browser checks cover themes, reflow, keyboard, errors and destinations.
- C-5 PASS: content follows thesis scope, master25.1 and existing session architecture.
- R-05 PASS: photo band, centered introduction and asymmetric scope block follow rhythm2.
- R-11 PASS: existing compact button radius; no pill/card decoration.
- R-15 PASS: actions name sign-in, asking a question or viewing scope.
- R-16 PASS: no marketing superlatives or generic technology slogans.
- R-20 PASS: actual PalSU photograph and undergraduate research limits carry identity.
- R-21 PASS: system/light/dark controls work; no forced dark default.
- R-29 PASS: existing neutral palette with campus photo accent.
- R-30 PASS: composition follows the owner's Figma concepts, not another product clone.
- R-31 PASS: purpose of image, layout, type, spacing and controls is written above.
