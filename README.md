# Cosmix ✧

A small social universe: Django 5.2 + React 19 + TypeScript + Vite, with SQLite.

## Run locally

Python 3.12+ and Node 22.12+ (or 24+) are recommended. From the repository root:

```bash
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

This is a local prototype using one shared demo author, without authentication or photo uploads. Do not deploy publicly as a multi-user service yet. Production needs authentication/authorization, per-user interactions, media storage, pagination, environment-based Django settings, and a production web server.

## Validate

```bash
.venv/bin/python backend/manage.py test feed
npm --prefix frontend run lint
npm --prefix frontend run build
```
