# Security notes

## Fixes in this review

- Removed the committed Django signing key from current settings. Production now refuses a missing, short, weak or `django-insecure-` key. Never reuse the historical key.
- DEBUG defaults to false. Production requires an exact host allowlist and explicit HTTPS trusted origins, redirects HTTP to HTTPS, enables HSTS, and uses secure session/CSRF cookies. Trust of forwarded HTTPS headers requires explicit operator configuration.
- Anonymous writes are denied by default. Production requires an authenticated Django session and always rejects demo publishing. Author identity is taken from that session, never from submitted JSON.
- Kept CSRF protection enabled, including for authenticated writes. CSRF token responses cannot be cached. CORS is limited to API paths and explicitly configured origins.
- JSON bodies are limited to 16 KiB; malformed JSON, non-string text, wrong content types and text outside 1–2000 characters are rejected.
- Environment files, private-key files and SQLite files are ignored by Git. `.env.example` contains instructions and non-secret local defaults only.
- Updated python-dotenv from 1.2.1 to 1.2.2 for the advisory reported by pip-audit (PYSEC-2026-2270).

## Required action for any existing deployment

The old signing key is still present in previous Git commits. Removing it from current files does not revoke it. Generate a fresh `DJANGO_SECRET_KEY` in the hosting dashboard, set `DJANGO_DEBUG=false`, configure the exact public host and trusted HTTPS origin, and redeploy. Do not put the old key in a fallback list. Rotating it invalidates sessions and other signed tokens using the old key.

This review does not rewrite Git history or force-push. If any other real credential was ever committed outside the scanned history, revoke it at its provider as well.

## Scope and validation

The review covers tracked application/configuration files and credential-pattern scanning of available Git history. The historical signing key was found in two settings-file blobs; no additional matches were found by that pattern scan. Pattern scanning is not proof that no secrets exist.

Regression tests cover production startup restrictions, security headers, HTTPS redirect, cookie flags, CSRF, untrusted origins, anonymous writes, author spoofing, oversized/invalid input, and repeatable demo seeding. Dependency audits use pip-audit and npm audit; Python static analysis uses Bandit. Audit results describe known advisories at scan time, not all possible vulnerabilities.

## Remaining product and deployment work

- No public registration or frontend login UI yet. Staff can use Django admin login on a same-origin deployment. Do not advertise the fixed demo profile as the signed-in identity.
- No public production web-server/frontend-serving configuration is included yet. Do not expose development servers directly.
- SQLite needs persistent storage; `DATABASE_URL` is not supported yet.
- Public signup/login will need abuse controls, rate limits, and account recovery. Likes, follows and bookmarks remain local demo state.
