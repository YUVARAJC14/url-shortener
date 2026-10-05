# shrt: URL shortener with click analytics

Shorten long URLs and see when, where and on what device each link is opened.

**Live demo:** YOUR-RENDER-URL (the free host sleeps when idle, so the first load can take about a minute)
**Demo login:** demo@example.com / YOUR-DEMO-PASSWORD

![Dashboard](docs/dashboard.png)

## Features
- Register and log in (hashed passwords, Flask-Login sessions)
- Create short links with six-character codes, with optional expiry
- Redirects that log each click: device, browser and source
- Dashboard with clicks per day (7 or 30 days), device split and top links
- Per-link stats page
- Rate limiting on link creation, CSRF protection, URL validation

## Tech stack
Python, Flask, SQLAlchemy, PostgreSQL (SQLite locally), Flask-Login, Flask-WTF,
Flask-Limiter, Chart.js, pytest, gunicorn

## Run locally
```bash
git clone YOUR-REPO-URL && cd url-shortener
python -m venv venv && venv\Scripts\activate    # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python run.py
```
Run the tests with `pytest`.

## Design decisions
- **302 redirects, not 301**, so browsers don't cache them and every click reaches the server to be counted.
- **`secrets` for short codes**, with a uniqueness check and retry. 62^6 is about 56 billion combinations.
- **Ownership checks** on delete and stats routes, so users can only touch their own links.
- **Redirect safety:** only http and https URLs are accepted, which blocks `javascript:` links.
- **Analytics in raw parameterised SQL** (JOIN, GROUP BY, LEFT JOIN), with missing days filled in Python.
- **410 Gone** for expired links, and expiry is checked before a click is logged.

## What I'd add next
Custom aliases, QR codes, click geolocation, Redis for rate limiting, and database migrations with Alembic.