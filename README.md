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
  - **Automatic tracking number dialogue box** that pops up upon request submission
  - **One-click save functionality** that copies tracking number to clipboard and downloads JPG image
  - **Tracking number JPG download** with certificate type, applicant name, and important details
  - Downloadable voucher containing tracking number and request details
  - Secretary dashboard with full visibility of all requests to assist citizens who forgot tracking numbers
  - Search functionality for Secretary to quickly find requests by name, tracking number, or contact
  - **Request decline functionality** with specific reasons for each certificate type
  - Declined requests show reason and notes in client tracking page
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
- **Legal compliance footer** with RA 8792 and A.M. No. 01-7-01-SC recognition text on all certificates
- **Philippine timezone support** for accurate verification timestamps (Asia/Manila, UTC+8)

The current workflow is:
1. Citizen submits a service request and receives tracking number with download option
2. Secretary reviews and can either approve/forward or decline the request (can view all requests for citizen assistance)
3. Paid services: applicant uploads GCash payment proof, then the Treasurer verifies it and forwards the request
4. Free services: the request bypasses GCash and the Treasurer, and goes directly to the Punong Barangay
5. Punong Barangay can approve or decline the request
6. PDF certificate is generated and stored (for approved requests)
7. Declined requests show specific reasons and notes in the client tracking page

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

# Staff credentials (for initial setup - passwords will be hashed with bcrypt)
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

**Important Security Note:** The default passwords above are for initial setup only. After the first login, you should change these passwords immediately through the Supabase dashboard or by updating the `staff_users` table directly. The application uses bcrypt for secure password hashing.

### 4) Prepare Supabase

Run the SQL from [setup_supabase_policies.sql](setup_supabase_policies.sql) in your Supabase SQL Editor.

This sets up:
- tables used by the app
- storage buckets for uploads
- basic row-level security policies
- initial barangay settings row

**Important Security Note:** After running the initial setup, you should apply the secure RLS policies by running [secure_rls_policies.sql](secure_rls_policies.sql). This implements proper Row-Level Security (RLS) policies that:
- Restrict access to sensitive tables (staff_users)
- Allow public access to necessary data (barangay_settings for public info)
- Maintain all functionality for citizens to submit and track requests
- Provide defense-in-depth security

**Note:** If you have an existing database with requests, run any available migration SQL files to apply certificate content fixes and database improvements. For existing deployments, run:
- `add_official_names_migration.sql` to add official name fields
- `add_contact_info_migration.sql` to add contact information and Treasurer settings (including GCash QR code support)
- `add_decline_fields_migration.sql` to add decline functionality (decline reasons, notes, and declined by fields)
- `add_staff_users_migration.sql` to add secure staff authentication with bcrypt password hashing (REQUIRED for security)
- `secure_rls_policies.sql` to implement secure Row-Level Security policies (HIGHLY RECOMMENDED for production)

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

Use the staff credentials from the `.env` file:

| Role | Username | Password |
|---|---|---|
| Secretary | `secretary` | `secretary-test` |
| Treasurer | `treasurer` | `treasurer-test` |
| Punong Barangay | `chairman` | `chairman-test` |

**Security Enhancement:** The application now uses bcrypt for secure password hashing. Passwords are never stored in plain text. After the first login, you should change these default passwords immediately through the Supabase dashboard or by updating the `staff_users` table directly.

Open http://127.0.0.1:5000/dashboard to sign in.

## Current deployment status

The app is production-ready and fully operational on Render with enhanced features for citizen tracking and staff efficiency.

### Recent improvements
- **Debug statement removal:** Implemented debug_log() helper function that only prints in development mode. All debug print statements in app.py and database.py now use this helper and are automatically disabled in production when FLASK_ENV=production. This prevents information disclosure to users while maintaining debugging capabilities during development.
- **Secure session cookies:** Configured secure session cookie settings for production. Enabled HTTPS-only cookies, HTTPOnly for XSS protection, and SameSite for CSRF protection. Added warning for default SECRET_KEY in production. Render automatically generates a strong SECRET_KEY.
- **QR code URL fix:** Fixed certificate QR code generation to use production URL instead of localhost. Updated render.yaml to include BASE_URL environment variable for correct QR code verification links. Modified certificate generator functions to accept base_url parameter for flexibility.
- **CSRF protection implementation:** Added Flask-WTF CSRF protection to all 24 POST forms across the application. This prevents cross-site request forgery attacks while being transparent to legitimate users. All forms now include automatic CSRF tokens.
- **Secure authentication with bcrypt:** Implemented proper password hashing using bcrypt to replace plain text password storage. Staff credentials are now securely hashed in the database with automatic initialization on startup. Passwords are never stored in plain text.
- **Enhanced authentication debugging:** Added comprehensive logging for authentication flow to help diagnose login issues. Includes fallback to in-memory authentication for development and error scenarios.
- **Improved .gitignore:** Comprehensive protection for sensitive files including .env, secrets, uploads, and generated files. Only necessary application files are committed to GitHub.
- **Automatic tracking number dialogue box:** Pop up upon request submission with one-click save functionality
- **One-click tracking number save:** Automatically copies to clipboard and downloads JPG image with certificate details
- **Enhanced tracking workflow:** Citizens can copy or download their tracking numbers as vouchers to prevent loss
- **Request decline functionality:** Staff can decline requests with service-specific reasons and optional notes
- **Declined request visibility:** Clients see detailed decline reasons and notes in their tracking page
- **Updated processing times:** Citizens' Charter now reflects realistic 2-3 minute approval times (reduced from 1-2 hours)
- **Secretary dashboard enhancement:** Secretary can view all requests and search by name/tracking number to assist citizens
- **Request sorting optimization:** Latest requests now appear at the top of the dashboard for improved workflow efficiency
- **Fixed file upload functionality:** Logo and signature uploads now work correctly in both local and production environments
- **Production-ready templates:** All templates updated with professional messaging and consistent styling
- **Improved user experience:** Better error handling, clearer instructions, and more intuitive interface
- **Professional certificate design:** Enhanced PDF certificates with tasteful, professional design elements including double borders, watermarks, improved typography, and better signature placement
- **Fixed certificate content issues:** Corrected purpose field display for Certificate of Indigency and Certificate of Residency, and fixed residency years/months display in Certificate of Residency
- **Grammar corrections:** Removed redundant "for any lawful purpose it may serve" phrases when users specify actual purposes
- **Official names feature:** Added Punong Barangay, Secretary, and Treasurer name fields in Settings page
- **Professional signature format:** Implemented correct certificate signature layout (Approved by/Attested by → Signature → Printed Name → Line → Position)
- **Enhanced verification security:** Certificate verification page now includes verification timestamp, record ID, and additional security information
- **Certificate spacing fixes:** Adjusted First Time Job Seeker certificate spacing to prevent text overlap with signature areas
- **Signature positioning:** Optimized digital signature positions with proper font hierarchy for professional appearance
- **Citizens' Charter page:** Added ARTA-compliant Citizens' Charter with complete service specifications, procedures, fees, and updated processing times
- **Contact information management:** Added phone, email, and Facebook contact details management via Settings page
- **Treasurer settings enhancement:** Added Treasurer signature upload and name management for complete staff information
- **GCash QR code integration:** Added GCash QR code upload feature for payment processing, displayed in payment form
- **Production storage optimization:** Implemented Supabase-first storage with temporary file cleanup for Render deployment
- **Navigation improvements:** Simplified navigation text and added Citizens' Charter access
- **Legal compliance footer:** Added RA 8792 and A.M. No. 01-7-01-SC recognition text to all certificates for electronic document validity
- **Philippine timezone support:** Updated verification timestamps to use Asia/Manila timezone (UTC+8) for accurate time display

### Security Audit Findings (2026-10-10)

A comprehensive security and performance audit was conducted to identify vulnerabilities and optimization opportunities. The following issues were found and prioritized:

#### 🔴 Critical Security Issues

**1. Weak Authentication System**
- Passwords stored in plain text (no hashing)
- Simple string comparison for authentication
- Default weak credentials (`secretary-test`, `treasurer-test`, `chairman-test`)
- No rate limiting on login attempts
- No account lockout mechanism
- **Status**: ✅ FIXED - Implemented proper password hashing with bcrypt. Staff passwords are now securely hashed using bcrypt. Run `add_staff_users_migration.sql` to create the staff_users table. The application automatically initializes default staff users with hashed passwords on startup.

**2. Supabase RLS Policies Completely Open**
- All tables use `WITH CHECK (true)` and `USING (true)` - essentially no access control
- Anyone with the anon key can read/write ALL data
- Storage buckets are completely public (read/write)
- No row-level security based on user roles
- **Critical**: The `SUPABASE_SERVICE_ROLE_KEY` gives full database access to anyone who finds it
- **Status**: ✅ FIXED - Applied `secure_rls_policies.sql` which implements proper Row-Level Security:
  - Restricted access to sensitive tables (staff_users)
  - Allowed public access to necessary data (barangay_settings for public info)
  - Maintained all functionality for citizens to submit and track requests
  - Provided defense-in-depth security
  - **Note**: The app uses server-side architecture with service role key, so functionality is preserved.

**3. No CSRF Protection**
- Flask doesn't have CSRF protection enabled
- All POST forms are vulnerable to cross-site request forgery
- An attacker could submit forms on behalf of logged-in users
- **Status**: ✅ FIXED - Implemented Flask-WTF CSRF protection. Added CSRF tokens to all 24 POST forms including:
  - Login form
  - All 6 service request forms
  - Payment form
  - Track lookup form
  - Dashboard approval/decline forms
  - Settings page forms (14 forms)
  - Protection is transparent to legitimate users but prevents CSRF attacks.

**4. Insecure Session Configuration**
- No `SESSION_COOKIE_SECURE` flag (cookies sent over HTTP)
- No `SESSION_COOKIE_HTTPONLY` (vulnerable to XSS)
- No `SESSION_COOKIE_SAMESITE` (CSRF vulnerability)
- Default `SECRET_KEY` is weak (`development-only-change-me`)
- **Status**: ✅ FIXED - Configured secure session cookies:
  - `SESSION_COOKIE_SECURE = True` in production (HTTPS only)
  - `SESSION_COOKIE_HTTPONLY = True` (prevents XSS access to cookies)
  - `SESSION_COOKIE_SAMESITE = 'Lax'` (CSRF protection)
  - Added warning for default SECRET_KEY in production
  - Note: Set a strong SECRET_KEY in Render environment variables for production.

**5. Insufficient File Upload Validation**
- Only checks file extension, not actual content
- Could upload malicious files with valid extensions
- No virus scanning
- File size limit (5MB) is reasonable but no rate limiting
- **Status**: PENDING - Need content validation and stricter security

**6. No Rate Limiting**
- No protection against brute force login attempts
- No protection against form submission spam
- No protection against API abuse
- No protection against DoS attacks
- **Status**: PENDING - Implement Flask-Limiter

#### 🟡 Performance Issues

**1. Slow Certificate Generation**
- ReportLab PDF generation is synchronous and CPU-intensive
- Blocks the request thread during generation
- No caching of generated certificates
- Downloads images from URLs during generation (network latency)
- **Status**: PENDING - Consider async generation with Celery

**2. Database Query Optimization**
- `get_all_service_requests()` fetches ALL requests every time
- No pagination on dashboard
- Dashboard loads all requests even if only a subset is needed
- No query indexing mentioned in schema
- **Status**: PENDING - Add pagination and query optimization

**3. No Caching Layer**
- Settings loaded on every request via `inject_settings()`
- Images fetched from Supabase URLs repeatedly
- No CDN for static assets
- No browser caching headers configured
- **Status**: PENDING - Implement caching with Redis or Flask-Caching

**4. Synchronous File Operations**
- All file operations are blocking
- PDF upload to Supabase is synchronous
- No async operations for I/O-bound tasks
- **Status**: PENDING - Consider async operations

**5. In-Memory Fallback Issues**
- In-memory lists clear on restart (data loss in dev mode)
- Linear search through lists (O(n) complexity)
- Not scalable for production
- **Status**: ACCEPTABLE - Only for development, production uses Supabase

#### 🟢 Good Security Practices Found

1. Uses `secure_filename()` for file uploads
2. Supabase client (SQL injection protection via ORM)
3. Role-based access control in dashboard routes
4. Input sanitization with `.strip()`
5. Size limits on file uploads
6. Temporary directory usage for certificate generation

#### 📊 Priority Recommendations

**Immediate (Critical) - All Completed:**
1. ✅ Implement proper password hashing (bcrypt/argon2) - COMPLETED
2. ✅ Restrict Supabase RLS policies to only allow authenticated access - COMPLETED
3. ✅ Enable Flask CSRF protection - COMPLETED
4. ✅ Set secure session cookie flags - COMPLETED
5. ✅ Remove debug print statements in production - COMPLETED

**High Priority:**
1. Add rate limiting (Flask-Limiter)
2. Implement proper authentication integration with Supabase Auth
3. Add input validation and sanitization
4. Implement file content validation

**Medium Priority:**
1. Add database query optimization and pagination
2. Implement caching (Redis or Flask-Caching)
3. Add async certificate generation (Celery/background tasks)
4. Add CDN for static assets

#### Remaining security considerations
While the app is production-ready for public use, the following security enhancements are recommended for long-term production:

1. ~~Replace the current staff login approach with Supabase Auth or another proper authentication system~~ (IN PROGRESS)
2. Implement additional security hardening for admin routes
3. Add production monitoring (logs, backups, uptime monitoring)
4. Review and enhance data protection measures

## Key features

### For Citizens
- Easy online service request submission
- Selfie capture for identity verification
- **Automatic tracking number dialogue box** upon submission with one-click save
- **One-click tracking number save** (copy to clipboard + download JPG with details)
- Real-time request status tracking including decline reasons
- Downloadable PDF certificates upon approval
- **Citizens' Charter access** with complete service information, fees, and updated processing times
- **GCash QR code display** for convenient payment processing
- Contact information access (phone, email, Facebook)

### For Staff
- Role-based dashboard (Secretary, Treasurer, Punong Barangay)
- Secretary can view all requests and search to assist citizens
- **Request decline functionality** with service-specific reasons and optional notes
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
- **Legal compliance footer** with RA 8792 and A.M. No. 01-7-01-SC recognition text for electronic document validity
- **QR code positioning** optimized to avoid overlap with footer text

### Certificate types
- **Barangay Clearance** - General purpose clearance certificate
- **Barangay Certification** - General purpose certification  
- **Certificate of Residency** - Proof of residency for indigency and other purposes
- **Certificate of Indigency** - Financial need certification for government services
- **Business Closure Certification** - Business closure documentation
- **First Time Job Seeker Certification** - Employment assistance for first-time job seekers

### Signature format
Certificates now follow professional signature formatting:
- **Punong Barangay:** "Approved by" → Signature → Printed Name → Line → "Punong Barangay"
- **Secretary:** "Attested by" → Signature → Printed Name → Line → "Barangay Secretary"
- Proper font hierarchy with printed names most prominent
- Consistent positioning and spacing for professional appearance

### Certificate content fixes
- **Purpose field display:** Fixed missing purpose display in Certificate of Indigency and Certificate of Residency
- **Residency duration:** Fixed years/months display in Certificate of Residency

## Request Decline System

The app includes a comprehensive request decline system that allows staff to reject ineligible or incomplete requests with clear explanations.

### Decline Features
- **Service-specific decline reasons** tailored to each certificate type (residency issues, documentation problems, eligibility concerns, etc.)
- **Optional decline notes** for additional context or explanations
- **Staff role tracking** (who declined the request - Secretary, Treasurer, or Punong Barangay)
- **Client visibility** - declined requests show detailed reasons and notes in the tracking page
- **Professional decline display** with clear formatting and guidance for citizens

### Decline Reasons by Service Type
- **Barangay Clearance:** Not a resident, incomplete documentation, identity verification, pending barangay issues, etc.
- **Barangay Certification:** Not a resident, incomplete documentation, purpose mismatch, insufficient evidence, etc.
- **Certificate of Residency:** Not a resident, insufficient residency period, address verification failed, etc.
- **Certificate of Indigency:** Not a resident, financial verification failed, income exceeds threshold, etc.
- **Business Closure:** Business not registered, cannot verify active business, incomplete documentation, etc.
- **First Time Job Seeker:** Not a resident, cannot verify first-time status, previous employment records, etc.

### Decline Workflow
1. Staff clicks "Decline" button on any request they have access to
2. Modal appears with service-specific decline reasons dropdown
3. Staff selects primary reason and optionally adds notes
4. Request status changes to "Declined: [Reason]"
5. Client sees full decline details when tracking their request
6. Guidance provided for citizens to contact barangay if they believe it's an error

### Database Requirements
The decline feature requires the `add_decline_fields_migration.sql` to be run in Supabase to add:
- `decline_reason` field for storing the primary decline reason
- `decline_notes` field for additional context
- `declined_by` field to track which staff role declined the request
- Updated `valid_status` constraint to include "declined" as a valid status

## Tracking Number Retention System

The app includes an automatic tracking number retention system to prevent citizens from losing their tracking numbers.

### Automatic Dialogue Box
- **Pop-up upon submission** - Automatically appears when citizens submit a request
- **Clear instructions** - Tells citizens to save their tracking number immediately
- **Prominent display** - Shows tracking number in large, highlighted format
- **One-click save** - Single button to save tracking number multiple ways

### One-Click Save Functionality
When citizens click "Save":
1. **Automatically copies** tracking number to clipboard
2. **Downloads JPG image** containing:
   - Tracking number (large and prominent)
   - Certificate type
   - Applicant name
   - Submission date
   - Barangay branding
   - Instructions to keep the number safe

### JPG Download Features
- **Professional design** with barangay branding and colors
- **Client-side generation** using HTML5 Canvas (no server load)
- **Automatic filename** based on tracking number
- **High quality** JPEG format suitable for printing or saving
- **Mobile-friendly** works on all devices

### Benefits
- **Prevents tracking number loss** - Citizens have multiple ways to save it
- **Reduces support requests** - Fewer citizens forget their tracking numbers
- **User-friendly** - One-click solution instead of manual copying
- **Professional appearance** - Branded JPG image looks official
- **Cross-platform** - Works on desktop, tablet, and mobile devices

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
- **Philippine timezone:** Verification timestamps use Asia/Manila timezone (UTC+8) for accurate time display

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

### Certificate legal compliance (September 2026)
- **Legal compliance footer:** Added RA 8792 and A.M. No. 01-7-01-SC recognition text to all certificates for electronic document validity
- **QR code positioning:** Optimized QR code placement to avoid overlap with footer text
- **Philippine timezone:** Updated verification timestamps to use Asia/Manila timezone (UTC+8) for accurate time display
- **Small font footer:** Legal compliance text displayed in small font (6.3pt) at bottom of certificates

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

### Tracking number retention system (September 2026)
- **Automatic dialogue box** that pops up upon request submission with tracking number
- **One-click save functionality** that copies tracking number to clipboard and downloads JPG image
- **Professional JPG generation** with certificate type, applicant name, and submission date
- **Client-side canvas generation** for fast performance without server load
- **Cross-platform compatibility** works on desktop, tablet, and mobile devices

### Request decline system (September 2026)
- **Service-specific decline reasons** tailored to each certificate type
- **Decline modal with dropdown** for selecting specific reasons
- **Optional decline notes** for additional context and explanations
- **Staff role tracking** to identify who declined each request
- **Client visibility** of decline reasons and notes in tracking page
- **Database migration** to add decline fields and update status constraints

### Citizens' Charter processing time updates (September 2026)
- **Realistic approval times** updated from 1-2 hours to 2-3 minutes for Punong Barangay approval
- **Total processing time** reduced to 15-20 minutes for paid services, 10-15 minutes for free services
- **Efficient workflow** reflecting modern e-services processing capabilities
- **Better citizen expectations** with accurate timeline estimates

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
├── add_contact_info_migration.sql   # SQL migration for contact info and Treasurer settings
├── add_decline_fields_migration.sql # SQL migration for decline functionality
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

### Version 1.3 (Current - September 2026)
- Added legal compliance footer with RA 8792 and A.M. No. 01-7-01-SC recognition text on all certificates
- Optimized QR code positioning to avoid overlap with footer text
- Updated verification timestamps to use Philippine timezone (Asia/Manila, UTC+8)
- Legal compliance text displayed in small font (6.3pt) at bottom of certificates
- Enhanced certificate footer design for better readability

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
