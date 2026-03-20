# Clinical Trial Document Workflow System

## Overview

This project is a **full-stack clinical trial document management and workflow system** designed to simulate how regulated industries (such as life sciences, pharma, and healthcare) manage documents, approvals, and patient data.

In real-world environments, platforms like Veeva Vault are used to:

* manage regulatory submissions
* track document versions
* enforce review and approval workflows
* maintain audit logs for compliance

This project recreates a simplified version of that ecosystem.

---

## Live Demo

* Frontend: https://mini-veeva-vault.vercel.app
* Backend API Docs: https://mini-veeva-vault-production.up.railway.app/docs

---

## Features

### Authentication & Security

* JWT-based authentication
* Role-based access control (Researcher / Reviewer)
* Secure login and signup

### Patient Data Management

* Create and track patient records
* Associate treatments and outcomes
* Display structured clinical data

### Document Workflow System

* Upload and manage documents
* Track document versions
* Submit documents for review
* Maintain document lifecycle states:

  * Draft
  * Submitted
  * Approved / Reviewed (extensible)

### Version Control

* Upload multiple versions of a document
* Track changes over time
* Maintain version history

### Audit Logging

* Capture user actions (document creation, submission, updates)
* Provide traceability for compliance workflows

### Dashboard

* View patient records
* View document states
* Manage workflow actions from a central UI

---

## Tech Stack

### Frontend

* React (Vite)
* TypeScript
* Axios (API communication)

### Backend

* FastAPI (Python)
* SQLAlchemy (ORM)
* JWT authentication

### Database

* PostgreSQL (Railway)

### Deployment

* Frontend: Vercel
* Backend: Railway

---

## Architecture

```
Frontend (React)
     ↓
API Layer (Axios)
     ↓
FastAPI Backend
     ↓
PostgreSQL Database
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mini-veeva-vault.git
cd mini-veeva-vault
```

---

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:

```
DATABASE_URL=your_postgres_url
JWT_SECRET=your_secret
```

Run server:

```bash
uvicorn app.main:app --reload
```

---

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create `.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Run:

```bash
npm run dev
```

---

## Production Setup

### Frontend (Vercel)

* Connect GitHub repo
* Set:

```
VITE_API_BASE_URL=https://your-railway-backend-url
```

### Backend (Railway)

* Add PostgreSQL
* Set DATABASE_URL from Railway
* Configure CORS origins

---

## API Usage

Visit:

```
/docs
```

for Swagger UI to:

* create patients
* authenticate users
* manage documents

---

## Example Workflow

1. Create a user account
2. Add patient records
3. Upload a document (Draft)
4. Submit document for review
5. Upload a new version
6. Track document history and audit logs

---

## Why Did I Make This Project 

This project demonstrates how regulated workflows are implemented in software systems:

* data integrity
* auditability
* controlled access
* versioning

It simulates real-world enterprise tools used in clinical and regulatory environments.

---

## Future Improvements

* Reviewer approval UI
* File storage (S3)
* Real-time notifications
* Improved UI/UX
* Analytics dashboard
* Multi-tenant support

---

## License

MIT
