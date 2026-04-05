# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Anfinit** — a Django financial advisor website for the Western Balkans (BiH and Serbia). Four main modules: News & Real Estate, E-Learning, Financial Calculators, and Analysis/Reports. Hosted on Railway with PostgreSQL; local dev uses SQLite.

## Commands

All commands must be run from `C:\Users\Bojan\finadvice\` (the project root where `manage.py` lives).

```bash
# Development server (use port 8080 — port 8000 often has stuck processes on this machine)
python manage.py runserver 8080

# Migrations
python manage.py makemigrations
python manage.py migrate

# Scrape bank interest rates (all banks, or one specific bank)
python manage.py scrape_rates
python manage.py scrape_rates --bank raiffeisen-bh

# Collect static files (required before deploy)
python manage.py collectstatic --noinput

# Django shell
python manage.py shell
```

**Deploy**: `git push` triggers Railway auto-deploy. The `Procfile` release command runs `migrate`, `collectstatic`, and creates the superuser automatically.

## Architecture

### App structure (`apps/`)

Five Django apps under `apps/`, each with standard `models.py / views.py / urls.py / admin.py`:

| App | URL prefix | Purpose |
|-----|-----------|---------|
| `core` | `/` | Homepage, search, about, contact. `SiteSettings` singleton. `context_processors.site_settings` injects settings into every template. |
| `news` | `/vijesti/` | `NewsArticle` + `Property` (real estate). Properties have a `PropertyImage` inline; `cover_image` is a `@property` returning the first image with `is_cover=True`. |
| `elearning` | `/edukacija/` | `Course → Module → Lesson` hierarchy. `Quiz / Question / Answer / QuizAttempt` for assessments. |
| `calculators` | `/kalkulatori/` | Pure math in `calculators.py` (no ORM). Scrapers in `scraper.py`. Daily job in `scheduler.py` via `django-apscheduler`. |
| `analysis` | `/analize/` | `AnalysisReport` with `DataPoint` inlines for Chart.js JSON data. `views_count` incremented on detail view. |
| `politics` | `/statistike/` | Political monitoring: `PoliticalParty`, `PoliticalFigure`, `MediaPortal`, `PoliticalMention`, `MentionScrapeLog`. RSS scraper in `scrapers.py` uses `feedparser`. Sentiment analysis in `sentiment.py` (custom B/C/S lexicon). Daily scrape at 07:00 via scheduler in `apps/calculators/scheduler.py`. Management command: `python manage.py collect_mentions [--portal klix.ba] [--dry-run]`. |

### Key patterns

**Abstract base model**: `apps/core/models.py` — `TimeStampedModel` adds `created_at` / `updated_at` to everything.

**Custom managers**: `PublishedManager` (news), `ActivePropertyManager`, `PublishedCourseManager`, `PublishedAnalysisManager` — filter by `status='published'` or `status='active'`. The default manager is always the custom one; use `Model.objects.all()` carefully vs `Model.published.all()`.

**Calculator math**: `apps/calculators/calculators.py` contains pure Python functions — no Django imports. Functions: `calculate_loan_annuity`, `calculate_mortgage`, `calculate_investment_return`, `calculate_savings_goal`, `calculate_deposit`, `convert_currency`, `compare_loan_offers`. Currency rates for BAM/EUR/USD/RSD/CHF are hardcoded constants (BAM is pegged to EUR at 1.95583).

**Interest rate scraper**: `apps/calculators/scraper.py` — `SCRAPER_MAP` dict maps `bank.short_name` to scraper classes. Each class has a `URLS` list of `(url, loan_type, currency)` tuples and a `scrape()` method. `run_all_scrapers()` iterates all active `Bank` objects. Scrapers use `requests` + `BeautifulSoup`; `verify=False` is required for some BiH bank SSL certs. The scheduler in `apps/calculators/apps.py` starts automatically via `AppConfig.ready()` and fires daily at 06:00 Sarajevo time.

**Loan types**: The `InterestRateOffer.loan_type` field uses Bosnian slugs: `stambeni`, `gotovinski`, `auto`, `penzionerski`, `potrosacki`, `refinansiranje`, `poslovni`. Do not use English values (`housing`, `consumer`) — they were changed in migration `0004`.

**Seed data**: Bank records and sample rates are created via data migrations `0002` and `0003` in `apps/calculators/migrations/`. Do not delete these migrations.

### Templates

Templates live in `templates/` at the project root (not inside apps). Structure mirrors app names: `templates/core/`, `templates/news/`, etc. Partials: `templates/partials/_navbar.html`, `_footer.html`, `_pagination.html`. Each app has a `templates/<app>/partials/` for card components.

`base.html` loads Bootstrap 5.3, Bootstrap Icons, Chart.js (CDN), `main.css`, and `favicon.svg`.

### Static files

- `static/css/main.css` — custom styles
- `static/js/main.js` — global JS
- `static/img/logo.svg` — Anfinit SVG logo (infinity symbol + text)
- `static/img/favicon.svg` — favicon
- WhiteNoise serves static files in production. `STATICFILES_STORAGE` is set to `CompressedManifestStaticFilesStorage`.

### Settings

`config/settings.py` uses `python-decouple` for env vars. `DATABASE_URL` is read via `os.environ.get()` directly (not decouple) to ensure Railway env vars are picked up. `ALLOWED_HOSTS` includes `.up.railway.app` wildcard hardcoded for Railway deployments.

### Database

- Local: SQLite (`db.sqlite3`)
- Production: PostgreSQL on Railway via `DATABASE_URL` env var
- `dj-database-url` parses the URL in both cases

### Deployment (Railway)

- `Procfile` — release + web process
- `railway.json` — overrides start command to run `migrate` before gunicorn starts
- `runtime.txt` — Python 3.11.9
- Required env vars on Railway: `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL` (reference to Postgres service), `DJANGO_SUPERUSER_PASSWORD`
