# Barangay e-Services Portal

A Flask-based public service portal for Barangay 7, Poblacion, Salcedo, Eastern Samar, with a staff dashboard, request workflow, online form submissions, document uploads, and certificate generation.

## Current state of the app

The app is now functional for pilot and early production use with the following capabilities:

- Public portal with service selection for six services:
  - Barangay Clearance
  - Barangay Certification
  - Certificate of Residency
  - Certificate of Indigency
  - Business Closure Certification
  - First Time Job Seeker Certification
- Online request submission with required personal details, selfie capture, and optional ID photo upload
- Request tracking with a reference number and lookup page
- Staff dashboard for Secretary, Treasurer, and Punong Barangay workflow
- Manual payment proof review for the GCash pilot flow
- Certificate generation in PDF format after approval
- Barangay logo and signature management from the Settings page
- Supabase-backed persistence for requests, settings, and uploaded files
- Local fallback behavior for development/testing when Supabase is unavailable

The current workflow is:
1. Citizen submits a service request
2. Secretary reviews and forwards the request
3. Applicant uploads GCash payment proof
4. Treasurer verifies payment and forwards the request
5. Punong Barangay approves the request
6. PDF certificate is generated and stored

## Tech stack

- Flask
- Jinja2 templates
- ReportLab for PDF certificate generation
- Python-dotenv for environment settings
- Supabase for database and storage

## Local setup

Requirements:
- Python 3.11 or newer
- Access to a Supabase project

### 1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root with the following values:

```env
SECRET_KEY=replace-with-a-long-random-value
FLASK_ENV=development

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

PILOT_SECRETARY_USERNAME=secretary
PILOT_SECRETARY_PASSWORD=secretary-test
PILOT_TREASURER_USERNAME=treasurer
PILOT_TREASURER_PASSWORD=treasurer-test
PILOT_CHAIRMAN_USERNAME=chairman
PILOT_CHAIRMAN_PASSWORD=chairman-test

GCASH_ACCOUNT_NAME=Barangay 7
GCASH_ACCOUNT_NUMBER=09XXXXXXXXX
```

### 4) Prepare Supabase

Run the SQL from [setup_supabase_policies.sql](setup_supabase_policies.sql) in your Supabase SQL Editor.

This sets up:
- tables used by the app
- storage buckets for uploads
- row-level security policies
- initial barangay settings row

### 5) Start the app

```powershell
python app.py
```

Then open:
- http://127.0.0.1:5000

## Dashboard access

Use the pilot credentials from the `.env` file:

| Role | Username | Password |
|---|---|---|
| Secretary | `secretary` | `secretary-test` |
| Treasurer | `treasurer` | `treasurer-test` |
| Punong Barangay | `chairman` | `chairman-test` |

Open http://127.0.0.1:5000/dashboard to sign in.

## Production rollout plan

The app is ready for a first production-style deployment. Recommended next steps:

1. Deploy to a hosting platform such as Render, Railway, Fly.io, or PythonAnywhere.
2. Set the environment variables securely in the hosting dashboard.
3. Use a production WSGI server such as Gunicorn.
4. Enable HTTPS and a custom domain.
5. Test the public portal, dashboard workflow, file uploads, certificate generation, and tracking pages from real devices.
6. Collect feedback from staff and residents before expanding the system.

### Recommended production hosting setup

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add these environment variables in hosting:
  - `SECRET_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `PILOT_*` credentials
  - `GCASH_ACCOUNT_NAME`
  - `GCASH_ACCOUNT_NUMBER`

## Project structure

```text
barangay-eservices/
├── app.py
├── config.py
├── database.py
├── certificate_generator.py
├── requirements.txt
├── .env
├── setup_supabase_policies.sql
├── pilot_settings.json
├── templates/
├── static/
├── uploads/
├── pdf/generated/
└── docs/
```

## Notes

- Do not commit `.env` to Git.
- Keep the Supabase service-role key private and never expose it in the frontend.
- The current app is already suitable for pilot use and early public testing, but production hardening should still include security review, backups, and monitoring.
