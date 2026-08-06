# Barangay e-Services Portal

A Flask-based public service portal for Barangay 7, Poblacion, Salcedo, Eastern Samar, with a staff dashboard, request workflow, online form submissions, document uploads, and certificate generation.

## Current state of the app

The app is now production-ready and fully operational with the following capabilities:

- Public portal with service selection for six services:
  - Barangay Clearance
  - Barangay Certification
  - Certificate of Residency
  - Certificate of Indigency
  - Business Closure Certification
  - First Time Job Seeker Certification
- Online request submission with required personal details, selfie capture, and optional ID photo upload
- **Enhanced tracking system:**
  - Forced tracking number retention with copy-to-clipboard functionality
  - Downloadable voucher containing tracking number and request details
  - Secretary dashboard with full visibility of all requests to assist citizens who forgot tracking numbers
  - Search functionality for Secretary to quickly find requests by name, tracking number, or contact
- Staff dashboard for Secretary, Treasurer, and Punong Barangay workflow
- Manual payment proof review for the GCash payment flow
- Certificate generation in PDF format after approval with professional design elements
- Barangay logo and signature management from the Settings page (upload functionality fully functional)
- Official names management for Punong Barangay, Secretary, and Treasurer (displayed on certificates with proper signature format)
- Treasurer signature and GCash QR code management for payment processing
- Contact information management (phone, email, Facebook) for public accessibility
- **Citizens' Charter page** compliant with ARTA (Anti-Red Tape Authority) guidelines
- **Enhanced signature format:** Professional signature layout with "Approved by/Attested by" → Signature → Printed Name → Line → Position
- Supabase-backed persistence for requests, settings, and uploaded files
- Production-ready settings management (Supabase-first with local fallback for development)
- Local fallback behavior for development and testing when Supabase is unavailable
- Production-ready templates with professional messaging and consistent styling
- Enhanced certificate content with proper purpose display and residency duration information
- QR code verification for certificate authenticity checking
- **GCash QR code display** in payment form for easier payment processing

The current workflow is:
1. Citizen submits a service request and receives tracking number with download option
2. Secretary reviews and forwards the request (can view all requests for citizen assistance)
3. Paid services: applicant uploads GCash payment proof, then the Treasurer verifies it and forwards the request
4. Free services: the request bypasses GCash and the Treasurer, and goes directly to the Punong Barangay
5. Punong Barangay approves the request
6. PDF certificate is generated and stored

## Tech stack

- Flask - Web framework
- Jinja2 templates - HTML templating
- ReportLab - Professional PDF certificate generation with enhanced design elements
- Python-dotenv - Environment configuration management
- Supabase - Database and file storage backend
- Gunicorn - Production WSGI server
- PIL (Pillow) - Image processing for uploads and certificates
- UUID - Unique file naming and reference numbers
- qrcode - QR code generation for certificate verification
- **Temporary file management** for production deployment on Render

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
SUPABASE_SERVICE_ROLE_KEY=server-only-secret-from-supabase
CERTIFICATE_STORAGE_BUCKET=certificates
REQUIRE_SUPABASE=true

PILOT_SECRETARY_USERNAME=secretary
PILOT_SECRETARY_PASSWORD=secretary-test
PILOT_TREASURER_USERNAME=treasurer
PILOT_TREASURER_PASSWORD=treasurer-test
PILOT_CHAIRMAN_USERNAME=chairman
PILOT_CHAIRMAN_PASSWORD=chairman-test

GCASH_ACCOUNT_NAME=Barangay 7
GCASH_ACCOUNT_NUMBER=09XXXXXXXXX
BASE_URL=http://127.0.0.1:5000
```

### 4) Prepare Supabase

Run the SQL from [setup_supabase_policies.sql](setup_supabase_policies.sql) in your Supabase SQL Editor.

This sets up:
- tables used by the app
- storage buckets for uploads
- row-level security policies
- initial barangay settings row

**Note:** If you have an existing database with requests, run any available migration SQL files to apply certificate content fixes and database improvements. For existing deployments, run:
- `add_official_names_migration.sql` to add official name fields
- `add_contact_info_migration.sql` to add contact information and Treasurer settings (including GCash QR code support)

**Storage Bucket Setup:** The migration includes instructions for creating the "qrcodes" storage bucket in Supabase Storage for GCash QR code functionality. Follow the manual steps in the migration file to set up the bucket with appropriate RLS policies.

### 5) Start the app

```powershell
python app.py
```

Then open:
- http://127.0.0.1:5000 (Public Portal)
- http://127.0.0.1:5000/citizens-charter (Citizens' Charter)
- http://127.0.0.1:5000/dashboard (Staff Dashboard)

## Dashboard access

Use the pilot credentials from the `.env` file:

| Role | Username | Password |
|---|---|---|
| Secretary | `secretary` | `secretary-test` |
| Treasurer | `treasurer` | `treasurer-test` |
| Punong Barangay | `chairman` | `chairman-test` |

Open http://127.0.0.1:5000/dashboard to sign in.

## Current deployment status

The app is production-ready and fully operational on Render with enhanced features for citizen tracking and staff efficiency.

### Recent improvements
- **Enhanced tracking workflow:** Citizens can copy or download their tracking numbers as vouchers to prevent loss
- **Secretary dashboard enhancement:** Secretary can view all requests and search by name/tracking number to assist citizens
- **Request sorting optimization:** Latest requests now appear at the top of the dashboard for improved workflow efficiency
- **Fixed file upload functionality:** Logo and signature uploads now work correctly in both local and production environments
- **Production-ready templates:** All templates updated with professional messaging and consistent styling
- **Improved user experience:** Better error handling, clearer instructions, and more intuitive interface
- **Professional certificate design:** Enhanced PDF certificates with tasteful, professional design elements including double borders, watermarks, improved typography, and better signature placement
- **Optimized certificate layout:** Improved header spacing, body content positioning, signature alignment, and QR code placement for more authentic and professional appearance
- **Authentic signature overlap:** Digital signatures now overlap printed names for realistic in-person signature appearance on certificates
- **Fixed certificate content issues:** Corrected purpose field display for Certificate of Indigency and Certificate of Residency, and fixed residency years/months display in Certificate of Residency
- **Grammar corrections:** Removed redundant "for any lawful purpose it may serve" phrases when users specify actual purposes
- **Official names feature:** Added Punong Barangay, Secretary, and Treasurer name fields in Settings page
- **Professional signature format:** Implemented correct certificate signature layout (Approved by/Attested by → Signature → Printed Name → Line → Position)
- **Enhanced verification security:** Certificate verification page now includes verification timestamp, record ID, and additional security information
- **Certificate spacing fixes:** Adjusted First Time Job Seeker certificate spacing to prevent text overlap with signature areas
- **Signature positioning:** Optimized digital signature positions with proper font hierarchy for professional appearance
- **Citizens' Charter page:** Added ARTA-compliant Citizens' Charter with complete service specifications, procedures, fees, and processing times
- **Contact information management:** Added phone, email, and Facebook contact details management via Settings page
- **Treasurer settings enhancement:** Added Treasurer signature upload and name management for complete staff information
- **GCash QR code integration:** Added GCash QR code upload feature for payment processing, displayed in payment form
- **Production storage optimization:** Implemented Supabase-first storage with temporary file cleanup for Render deployment
- **Navigation improvements:** Simplified navigation text and added Citizens' Charter access
- **Mobile responsiveness fixes:** Fixed dashboard settings page and all grid layouts to properly stack on mobile devices

### Remaining security considerations
While the app is production-ready for public use, the following security enhancements are recommended for long-term production:

1. Replace the current staff login approach with Supabase Auth or another proper authentication system
2. Implement additional security hardening for admin routes
3. Add production monitoring (logs, backups, uptime monitoring)
4. Review and enhance data protection measures

## Key features

### For Citizens
- Easy online service request submission
- Selfie capture for identity verification
- Forced tracking number retention (copy or download voucher)
- Real-time request status tracking
- Downloadable PDF certificates upon approval
- **Citizens' Charter access** with complete service information, fees, and processing times
- **GCash QR code display** for convenient payment processing
- Contact information access (phone, email, Facebook)

### For Staff
- Role-based dashboard (Secretary, Treasurer, Punong Barangay)
- Secretary can view all requests and search to assist citizens
- **Latest-first request sorting** for improved workflow efficiency
- Photo verification for ID and selfie uploads
- Payment proof review and verification
- Professional certificate generation with custom logos and signatures
- **Enhanced signature management** for Punong Barangay, Secretary, and Treasurer
- **GCash QR code management** for payment processing
- Settings management for barangay branding
- Official names management for all staff positions
- Contact information management for public accessibility

## Citizens' Charter

The app includes a comprehensive Citizens' Charter page compliant with Republic Act 11032 (Ease of Doing Business and Efficient Government Service Delivery Act of 2018) and ARTA guidelines.

### Charter features
- **Mandate, Vision, Mission, and Service Pledge** for transparency
- **Complete service specifications** for all 6 certificate types
- **Service procedures** with step-by-step client actions and agency responses
- **Processing times** and fee information for each service
- **Requirements checklist** for each certificate type
- **Contact information** including phone, email, and Facebook
- **Complaints and feedback mechanism** with multiple channels
- **Professional formatting** consistent with ARTA standards

### Service information included
- Classification (Simple transactions)
- Transaction type (G2C - Government to Citizen, G2B - Government to Business)
- Who may avail each service
- Complete requirements list
- Processing workflow with responsible personnel
- Fee structure (Free services: Residency, Indigency, Job Seeker; Paid services: Clearance, Certification, Business Closure)

## Certificate generation

The app generates professional A4-size PDF certificates for all services with enhanced design elements:

### Design features
- **Professional double-border design** with navy outer border and gold inner accent
- **Subtle watermark background** for added depth and professionalism
- **Enhanced typography** with improved font sizes, spacing, and hierarchy
- **Better logo placement** with larger, better positioned logos or enhanced default seal
- **Professional footer** with improved signature sections and spacing
- **Color scheme refinement** using professional grays and navy tones

### Certificate types
- **Barangay Clearance** - General purpose clearance certificate
- **Barangay Certification** - General purpose certification  
- **Certificate of Residency** - Proof of residency for indigency and other purposes
- **Certificate of Indigency** - Financial need certification for government services
- **Business Closure Certification** - Business closure documentation
- **First Time Job Seeker Certification** - Employment assistance for first-time job seekers

### Signature format
Certificates now follow professional signature formatting:
- **Punong Barangay:** "Approved by" → Signature (overlapping printed name) → Printed Name → Line → "Punong Barangay"
- **Secretary:** "Attested by" → Signature (overlapping printed name) → Printed Name → Line → "Barangay Secretary"
- **Authentic signature overlap:** Digital signatures are positioned to overlap printed names for realistic in-person signature appearance
- Proper font hierarchy with printed names most prominent
- Consistent positioning and spacing for professional appearance

### Certificate content fixes
- **Purpose field display:** Fixed missing purpose display in Certificate of Indigency and Certificate of Residency
- **Residency duration:** Fixed years/months display in Certificate of Residency

## Settings Management

The Settings page provides comprehensive management of barangay branding and operational information:

### Available Settings
- **Barangay Logo:** Upload and manage barangay logo displayed on certificates and pages
- **Punong Barangay Signature:** Upload signature and set official name for certificates
- **Secretary Signature:** Upload signature and set official name for certificates
- **Treasurer Information:** Upload signature, set official name, and manage GCash QR code
- **Contact Information:** Set phone number, email address, and Facebook page for public access

### GCash QR Code
- Upload GCash QR code image for payment processing
- Displayed in payment form for citizens to scan and pay
- Supports JPEG and PNG formats
- Stored in Supabase Storage with public access for payment form display

### Storage Strategy
- **Production:** Supabase-first storage with automatic fallback prevention
- **Development:** Local file fallback when Supabase is unavailable
- **Render-compatible:** Temporary file management for ephemeral file systems
- **Automatic cleanup:** Temporary files removed after successful Supabase upload
- **Grammar corrections:** Removed redundant phrases when users specify actual purposes
- **Database integration:** Ensured all form fields are properly stored in Supabase and retrieved for certificate generation

### QR code verification
- **Certificate authenticity:** Each generated certificate includes a unique QR code in the footer
- **Verification system:** Scanning the QR code redirects to a verification page showing certificate details
- **Security features:** Enhanced verification page includes timestamp, record ID, and additional security information to prevent forgery
- **Configuration:** QR code URLs use the BASE_URL environment variable for proper domain configuration

## Production deployment

The app is currently deployed on Render with the following configuration:

- **Build command:** `pip install -r requirements-prod.txt`
- **Start command:** `gunicorn --bind 0.0.0.0:$PORT app:app`

### Required environment variables

Configure these in your hosting provider (Render Dashboard → Environment tab):

- `SECRET_KEY` - Flask secret key for session security
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `PILOT_SECRETARY_USERNAME` - Secretary login username
- `PILOT_SECRETARY_PASSWORD` - Secretary login password
- `PILOT_TREASURER_USERNAME` - Treasurer login username
- `PILOT_TREASURER_PASSWORD` - Treasurer login password
- `PILOT_CHAIRMAN_USERNAME` - Punong Barangay login username
- `PILOT_CHAIRMAN_PASSWORD` - Punong Barangay login password
- `GCASH_ACCOUNT_NAME` - GCash account name for payments
- `GCASH_ACCOUNT_NUMBER` - GCash account number for payments
- `BASE_URL` - Base URL for QR code generation (e.g., https://your-domain.com)

### Environment configuration architecture

The app uses a dual-environment configuration system that works seamlessly for both local development and production:

- **Production (Render):** Uses environment variables configured in the Render Dashboard. The `.env` file is not deployed, so the app relies entirely on Render's environment variables.
- **Development (Local):** Uses the local `.env` file via `python-dotenv`. The `config.py` file loads environment variables from `.env` if present, otherwise falls back to default values.

This architecture allows you to:
- Use different credentials for development vs production (security best practice)
- Test locally with your development database while production uses the live Supabase instance
- Maintain separate configurations without code changes

**Note:** You can safely use different passwords for local development and production. The app will automatically use the appropriate environment's configuration.

## Recent fixes and improvements

### Certificate content fixes (August 2026)
- **Fixed purpose field display:** Certificate of Indigency and Certificate of Residency now properly display the user-specified purpose instead of showing blank or default text
- **Fixed residency duration:** Certificate of Residency now correctly shows the number of years and months of residence as entered by the user
- **Grammar corrections:** Removed redundant "for any lawful purpose it may serve" phrases when users specify actual purposes, making certificates grammatically correct
- **Database integration:** Ensured all form fields (purpose, residency years/months) are properly passed to database functions and stored in Supabase

### Certificate design enhancements (August 2026)
- **Professional double-border design** with navy outer border and gold inner accent
- **Subtle watermark background** for added depth and professionalism  
- **Enhanced typography** with improved font sizes, spacing, and hierarchy
- **Better logo placement** with larger, better positioned logos or enhanced default seal
- **Professional footer** with improved signature sections and spacing
- **Color scheme refinement** using professional grays and navy tones
- **Consistent design** across all six certificate types while maintaining official appearance
- **Optimized layout:** Improved header spacing, body content positioning, signature alignment, and QR code placement
- **Authentic signature overlap:** Digital signatures positioned to overlap printed names for realistic appearance

### Responsive design improvements (August 2026)
- **Mobile grid fixes:** Dashboard settings page now properly stacks cards on mobile devices
- **Comprehensive responsive layout:** All grid layouts (service-grid, dashboard-grid, settings-grid, mvms-grid) now respond correctly to screen sizes
- **Mobile-first approach:** Cards and content sections stack properly on smartphones and tablets
- **Consistent behavior:** All pages follow the same responsive patterns as the Public Portal

## Project structure

```text
barangay-eservices/
├── app.py                          # Main Flask application
├── config.py                       # Environment configuration
├── database.py                     # Supabase database operations
├── certificate_generator.py        # Professional PDF certificate generation with enhanced design
├── requirements.txt                 # Development dependencies
├── requirements-prod.txt           # Production dependencies
├── Procfile                        # Heroku/Render deployment
├── render.yaml                     # Render deployment config
├── .env                            # Environment variables (not in git)
├── .env.example                    # Environment variables template
├── setup_supabase_policies.sql     # Supabase database setup
├── add_official_names_migration.sql # SQL migration for official names feature
├── pilot_settings.json             # Local settings (logo/signature paths/names)
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Public portal
│   ├── dashboard.html              # Staff dashboard
│   ├── dashboard_settings.html      # Settings page
│   ├── dashboard_login.html        # Staff login
│   ├── *_form.html                 # Service request forms
│   ├── track_*.html                # Request tracking pages
│   └── camera_capture.html         # Selfie capture component
├── static/                         # Static assets
│   ├── css/style.css              # Main stylesheet
│   ├── js/main.js                 # JavaScript functionality
│   └── images/                    # Static images
├── uploads/                        # Local file uploads (fallback)
├── pdf/generated/                  # Generated certificates
└── docs/                           # Documentation
```

## Development notes

- **Environment setup:** Create a `.env` file using `.env.example` as a template
- **Supabase setup:** Run `setup_supabase_policies.sql` in Supabase SQL Editor to initialize tables and storage
- **File uploads:** Local files stored in `uploads/` directory; production uses Supabase Storage
- **Certificate generation:** PDFs generated using ReportLab with customizable logos and signatures
- **Security:** Keep `.env` file private and never commit to Git. Use strong secret keys in production.

## Recent updates

### Version 1.3 (Current - August 2026)
- Optimized certificate layout with improved header spacing, body content positioning, and signature alignment
- Implemented authentic signature overlap effect for realistic in-person signature appearance
- Enhanced QR code positioning and label placement in certificate footer
- Fixed responsive design issues in dashboard settings page and all grid layouts
- Ensured all pages properly stack cards on mobile devices for better mobile user experience
- Cleaned up duplicate code in certificate generation functions
- Fixed Business Closure Certification formatting issue with closure_date parameter

### Version 1.2 (August 2026)
- Added official names feature for Punong Barangay and Secretary in Settings page
- Enhanced certificate verification page with security information (timestamp, record ID)
- Fixed First Time Job Seeker certificate spacing to prevent text overlap
- Lowered digital signature positions by 5mm for better alignment
- Added SQL migration support for database schema updates
- Updated database functions to handle official name fields
- Enhanced certificate footer with "Signature over printed name" display

### Version 1.1 (August 2026)
- Enhanced tracking system with forced tracking number retention
- Added downloadable voucher functionality for citizens
- Secretary dashboard now shows all requests with search capability
- Fixed file upload functionality for logos and signatures
- Updated all templates to production-ready state
- Improved error handling and user feedback
- Enhanced mobile responsiveness
- Fixed file saving issue in upload functionality

### Version 1.0 (July 2026)
- Initial production deployment
- Six online services with full workflow
- GCash payment integration
- Certificate generation system
- Staff dashboard with role-based access
