# Barangay e-Services Portal

A Flask-based public service portal for Barangay 7, Poblacion, Salcedo, Eastern Samar, with a staff dashboard, request workflow, online form submissions, document uploads, and certificate generation.

## Current state of the app

The app is now working online and is ready for real pilot use with the following capabilities:

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
- Local fallback behavior for development and testing when Supabase is unavailable

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
- Gunicorn for production hosting

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

## Current deployment status

The app is already online and working through Render.

### Important note about security
The app is now live and functional, but one important production security step was not completed yet:

- Step 5 (secure production setup and hardening) has not been fully implemented.

That means the app is usable for pilot testing, but it still has security risks that should be addressed before wider public use.

## What should be done next

The next priorities for the project are:

1. Secure the production environment
   - set strong secret keys
   - protect admin routes better
   - restrict dashboard access properly

2. Replace the current pilot staff login approach with a more secure authentication system
   - ideally using Supabase Auth or another proper login system

3. Improve data protection
   - review storage and database access permissions
   - ensure only authorized users can view or modify sensitive records

4. Add stronger production monitoring
   - logs
   - backups
   - uptime monitoring

5. Test the live app with real users
   - public forms
   - dashboard workflow
   - uploads and certificate generation
   - tracking and payment proof flow

## Recommended production hosting setup

For deployment, use:

- Build command: `pip install -r requirements-prod.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT app:app`

Add these environment variables in your hosting provider:

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
├── requirements-prod.txt
├── Procfile
├── render.yaml
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
- The app is suitable for pilot use and public testing, but production hardening should still be completed before broader public rollout.
