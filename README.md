# Breathe ESG — ESG Data Ingestion Prototype

A prototype ESG Data Ingestion application: Django + Django REST Framework backend with a React (Vite) frontend. The app ingests utility, SAP and travel data, normalizes energy and emissions, provides an analyst review queue, and produces audit exports.

## Purpose

This project demonstrates a production-oriented ingestion pipeline for ESG data with a focus on practical features needed by small teams and analysts: robust parsing, normalization, tenant overrides, human review, and auditability.

## Tech stack

- Backend: Django 5.x, Django REST Framework
- Auth: JSON Web Tokens via SimpleJWT
- Frontend: React 18 + Vite
- Dev DB: SQLite (development); target: PostgreSQL for production
- PDF parsing: pdfplumber (pdfminer beneath)

## Unique / Notable Features

- Auto source detection: uploaded files are auto-detected as `UTILITY`, `SAP`, or `TRAVEL` by inspecting file content (CSV/TXT/PDF supported).
- PDF ingestion: text extraction from PDFs (including mixed-section PDFs containing multiple source blocks) so auditors can drop exported PDFs directly into the system.
- Normalization: all energy values are normalized to kWh and CO2e is computed to kg CO2e using configurable factors.
- Tenant-configurable emission factors and Plant mapping: per-tenant overrides allow accuracy for different regions/fleets.
- Analyst review queue: parsed records land in a queue for approve/flag/reject with edit history stored in `raw_data` and `edit_history`.
- Human-readable `raw_data`: UI renders nested parsed payloads in a readable key/value table so analysts can inspect original fields easily.
- Audit CSV export: flattens `raw_data` into columns and formats numbers/dates to be immediately useful in Excel/auditor reports.
- Tests and samples: parser unit tests and sample files (CSV/TXT/PDF) are included to reproduce parsing scenarios.

## Quickstart (development)

1. Create and activate a Python virtualenv and install backend deps:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r breathe_esg/requirements-dev.txt
```

2. Apply migrations and create a superuser:

```powershell
cd breathe_esg
python manage.py migrate
python manage.py createsuperuser
```

3. Start the Django dev server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

4. Start the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

5. Open the app: the frontend default port is Vite's port (e.g. http://localhost:5174/) and the API is at http://127.0.0.1:8000/api/.

## How to demo

- Register or login using the UI. Registration will return a JWT and auto-login.
- Go to the Ingest page and upload one of the sample files in `samples/` (or drop a PDF). The system will detect type and parse rows.
- Visit the Review queue to approve/flag/reject parsed records.
- Visit the Audit page to view all records and use the CSV export to download a flattened audit report.

## Important backend endpoints

- `POST /api/register/` — create user (returns JWT)
- `POST /api/token/` — obtain access/refresh token
- `POST /api/ingest/upload/` — upload files (auto-detect source)
- `GET /api/records/pending/` — pending review list
- `POST /api/records/{id}/approve/` — approve a record
- `POST /api/records/{id}/flag/` — flag for follow-up
- `POST /api/records/{id}/reject/` — reject and remove from queue
- `GET /api/records/audit/export/?tenant_id=<id>` — download flattened CSV audit export

## Project layout (high level)

- `breathe_esg/` — Django project and apps: `api`, `ingestion`, `records`, `tenants`
- `frontend/` — React + Vite app
- `samples/` — sample CSV/TXT/PDF files used by tests and for manual testing

## Tests

- Run backend tests:

```powershell
cd breathe_esg
python manage.py test
```

## Known limitations & next improvements

- Production packaging: add Dockerfile, Postgres, and Celery for background processing and larger imports.
- Token refresh flow in the frontend is minimal; implement automatic refresh for long sessions.
- XLSX export for richer auditor-friendly exports (typed numbers/dates) could be added with `openpyxl`.
- Parser edge cases: support more locale numeric formats and more PDF layouts.
- Add Google/OAuth login if needed for SSO.

## Files to review for architecture & decisions

- `breathe_esg/ingestion/parsers.py` — parsing and normalization logic
- `breathe_esg/records/views.py` — review and audit APIs
- `frontend/src/pages/ReviewQueue.jsx` — review UI
- `frontend/src/pages/AuditLog.jsx` — audit UI & CSV export

## Contact / Next steps

If you'd like, I can also:

- Add a `MODEL.md` / `DECISIONS.md` / `TRADEOFFS.md` / `SOURCES.md` set summarizing architecture decisions and tradeoffs.
- Create Docker + Postgres + simple deployment instructions.
- Implement Google OAuth or XLSX export.

---

README created to document the prototype and highlight its unique features.
ESG Data Ingestion — prototype

Quick start (dev):

1) Create and activate a Python venv, then install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Run DB migrations and create an admin user:

```powershell
cd breathe_esg
python manage.py migrate
python manage.py createsuperuser
```

3) Start the backend and (separately) the frontend dev server:

```powershell
python manage.py runserver 127.0.0.1:8000
cd ../frontend
npm install
npm run dev
```

Notes:
- Uses SQLite locally by default; set `DATABASE_URL` for Postgres.
- Set `DJANGO_SECRET_KEY` in env for non-dev use (32+ chars recommended).
- Upload endpoint: `/api/ingestion/upload/` (JWT required).

If you want, I can also add a single-command script to run the whole demo.

