# Cosmix ✧

A small social universe: Django 5.2 + React 19 + TypeScript + Vite, with SQLite.

## Run locally

Python 3.12+ and Node 22.12+ (or 24+) are recommended. From the repository root:

```bash
cp .env.example .env
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
npm --prefix frontend ci
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
```

Start in two terminals:

```bash
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

```bash
npm --prefix frontend run dev
```

Open the Vite address shown in the terminal. Vite proxies `/api` to Django; use this single origin so CSRF cookies work. In the prepared cloud machine, `/workspace/cosmix-venv/bin/python` can be used instead of `.venv/bin/python`.

## MVP scope

- Responsive dark feed with cosmic dust, creator suggestions and image posts.
- Text posts stored in SQLite, validated by Django, protected with CSRF.
- Search across loaded posts, demo profile, following feed and bookmarks.
- Likes, follows and bookmarks are local React state and reset on refresh.
- Demo stories filter the feed; replies and notifications are placeholders.
- `seed_demo` populates an empty database and never overwrites posts.
- External demo photos: Unsplash and Pravatar. Fonts: Google Fonts, with system fallbacks.

Anonymous publishing is available only in explicit local demo mode (`DJANGO_DEBUG=true` and `DJANGO_ALLOW_DEMO_POSTS=true`). Otherwise posting requires a Django session and the author comes from the authenticated user. The existing Django admin login can be used for staff accounts (`manage.py createsuperuser`); public signup and a frontend login screen are not implemented yet. The visible frontend profile is still a demo placeholder.

Production configuration now defaults to HTTPS, secure cookies, no debug output, and exact host/origin allowlists. This does not complete deployment: a production WSGI server, built frontend serving, persistent database, and public user authentication flows still need to be configured. See [SECURITY.md](SECURITY.md).

## Validate

```bash
.venv/bin/python backend/manage.py test feed
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Hosting environment variables

Set these in your hosting dashboard; never commit real values:

| Variable | Production value |
| --- | --- |
| `DJANGO_SECRET_KEY` | Generate a **new** random key of at least 50 characters; do not reuse the old key from Git history. |
| `DJANGO_DEBUG` | `false` (default) |
| `DJANGO_ALLOWED_HOSTS` | Exact hostname(s), comma-separated, without scheme; no wildcards. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Explicit `https://` frontend origin(s), comma-separated. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Empty for same-origin deployments; exact HTTPS frontend origins only when needed. |
| `DJANGO_ALLOW_DEMO_POSTS` | `false` (default); production refuses `true`. |
| `DJANGO_TRUST_PROXY_SSL_HEADER` | `true` **only** behind a trusted proxy (such as Render's HTTPS ingress) that strips/replaces client-supplied `X-Forwarded-Proto`. Otherwise leave `false`. |
| `DJANGO_SQLITE_PATH` | Optional path on a persistent disk; default is `backend/db.sqlite3`. |

`DATABASE_URL` is not wired up yet; setting it alone does not switch this app to PostgreSQL. A public deployment needs persistent database storage. Never use `runserver` or the Vite dev server as the public production server.

Local `.env` files are loaded from the repository root and `backend/`; process environment values take precedence. The example is for local development only. When DEBUG is enabled without a key, a random signing key is generated per process, so sessions reset when it restarts.
