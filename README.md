# Mini Veeva Vault (Demo)

Mini Veeva Vault is a simulated clinical trial + regulatory document management system.

## Tech Stack
- Backend: Python FastAPI (JWT auth, role-based access control)
- Frontend: React + TypeScript
- Database: PostgreSQL

## Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (recommended) or a local PostgreSQL instance

## 1) Start PostgreSQL
From the project root:
```bash
docker compose up -d
```

Postgres runs on `localhost:5432` with database `miniveeva`.

## 2) Backend (FastAPI)
```bash
cd backend
cp .env.example .env
# For local demo data, set SEED_ON_STARTUP=true in backend/.env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the API server
uvicorn app.main:app --reload --port 8000
```

On startup the app:
- Creates the PostgreSQL schema (via SQLAlchemy `create_all`)
- Seeds demo data (users, patients, documents, and a submission/approval workflow)

### Production start
When running in production, use:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
and set `SEED_ON_STARTUP=false` in `backend/.env` (so demo records aren’t inserted on every start).

## 3) Frontend (React)
```bash
cd ../frontend
cp .env.example .env
npm install
npm run dev
```

Frontend dev server runs at `http://localhost:5173`.

## Demo Accounts (seeded)
Email and password (password is `Password123!`):
- `researcher1@miniveeva.local` (Researcher)
- `reviewer1@miniveeva.local` (Reviewer)
- `admin1@miniveeva.local` (Admin)

## Key API Endpoints
- Auth: `POST /api/auth/signup`, `POST /api/auth/login`
- Patients:
  - `POST /api/patients`
  - `GET /api/patients`
- Documents:
  - `POST /api/documents` (multipart upload, metadata only)
  - `GET /api/documents`
  - `POST /api/documents/{document_id}/submit`
  - `POST /api/documents/{document_id}/review`
  - `GET /api/documents/{document_id}/history`
  - `GET /api/documents/approvals/queue` (reviewers)
- Audit Logs (Admin):
  - `GET /api/audit-logs`

