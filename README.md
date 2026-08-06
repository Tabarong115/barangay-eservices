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
- **Facebook Messenger notifications** (In Development) - Staff notification system for request workflow updates

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
- **requests** - HTTP library for Facebook Messenger API integration (In Development)
- **Temporary file management** for production deployment on Render

## Facebook Messenger Notifications (In Development)

### Overview
A Facebook Messenger-based staff notification system to alert the 3 staff members (Secretary, Treasurer, Punong Barangay) when:
- Citizens submit new service requests
- Payment proofs are uploaded
- Request statuses change during workflow
- Certificates are approved and generated

### Why Facebook Messenger?
- **Works on free data** (Facebook Free Basics in the Philippines)
- **No app installation needed** (staff already use Facebook)
- **Real-time alerts** for immediate response
- **Familiar interface** for barangay staff
- **Group coordination** through Facebook groups

### Current Implementation Status

#### ✅ Completed Components
1. **Facebook Notification Module** (`facebook_notifier.py`)
   - FacebookNotifier class with API integration
   - Functions for all notification types:
     - `notify_new_request()` - Alerts when citizens submit requests
     - `notify_status_change()` - Alerts at workflow stage changes
     - `notify_payment_submitted()` - Alerts Treasurer when payment proof uploaded
     - `notify_approval()` - Alerts when certificate is generated
   - Support for both group posts and direct messages
   - Automatic fallback from group to individual messaging

2. **App Integration** (Modified `app.py`)
   - Notifications integrated into all 6 service types:
     - Barangay Clearance
     - Barangay Certification
     - Certificate of Residency
     - Certificate of Indigency
     - Business Closure Certification
     - First Time Job Seeker Certification
   - Triggers at key workflow points:
     - New request submission
     - Payment proof upload
     - Status changes (Secretary review, Treasurer verification, etc.)
     - Final approval

3. **Configuration Setup** (Updated `.env.example`)
   - Facebook Page Access Token
   - Facebook Page ID
   - Facebook App ID
   - Facebook App Secret
   - Staff Group ID (for group notifications)
   - Staff User IDs (for direct messaging fallback)

4. **Test Suite** (`test_facebook_notifications.py`)
   - Configuration verification
   - Individual notification testing
   - Comprehensive test validation

5. **Dependencies** (Updated `requirements.txt`)
   - Added `requests>=2.31,<3.0` for Facebook API calls

#### ❌ Pending Setup (Current Blocker)
**Facebook App Creation Issue**: The developer is having difficulty creating the Facebook App required for the Messenger API integration.

### Facebook Page Status
- **Page Created**: ✅ https://www.facebook.com/profile.php?id=61592616314846&sk=about
- **Page Name**: Barangay 7 Services (assumed based on URL)
- **Page ID**: 61592616314846 (extracted from URL)
- **Status**: Ready for app integration

### Complete Setup Workflow for Next AI

#### Phase 1: Facebook App Creation (Current Blocker)
**Objective**: Create and configure Facebook Developer App for Messenger API access

**Steps to Complete**:
1. **Navigate to Facebook Developers Portal**
   - Go to https://developers.facebook.com
   - Log in with the same account that created the Facebook Page

2. **Create a New App**
   - Click "Create App" (top right)
   - Select app type: "Business" (recommended for government services)
   - Fill in app details:
     - **App name**: "Barangay 7 Services Bot"
     - **App contact email**: Developer's email address
   - Complete security verification if prompted

3. **Add Messenger Product**
   - In App Dashboard, find "Add Product" in left sidebar
   - Search for "Messenger" and click "Add"
   - This enables Messenger API capabilities

4. **Configure Messenger Settings**
   - Navigate to Messenger → Settings
   - Scroll to "Access Tokens" section
   - Click "Create New Token" or "Generate Token"
   - Select the Barangay 7 Services page from dropdown
   - **CRITICAL**: Copy the generated Page Access Token immediately
   - Store securely (you won't see it again)

5. **Get App Credentials**
   - Go to App Settings → Basic
   - Copy these credentials:
     - **App ID** (shown in Basic settings)
     - **App Secret** (shown in Basic settings, click "Show" to reveal)

6. **Configure App Permissions**
   - In App Dashboard → App Review
   - Request necessary permissions:
     - `pages_messaging` (for sending messages)
     - `pages_read_engagement` (for reading page content)
   - Submit for review if required (may take 1-2 business days)

7. **Verify Page Access**
   - Ensure the app has access to the Barangay 7 Services page
   - Test connection using Facebook's testing tools

#### Phase 2: Staff Group Setup
**Objective**: Create Facebook group for staff notifications

**Steps to Complete**:
1. **Create Private Facebook Group**
   - Use personal Facebook account
   - Create group: "Barangay 7 Staff Notifications"
   - Set as "Private" (only members can see posts)

2. **Add Staff Members**
   - Add Secretary (personal account)
   - Add Treasurer (personal account)
   - Add Punong Barangay (personal account)

3. **Add Facebook Page to Group**
   - Add "Barangay 7 Services" page as a group member
   - This allows the page bot to post in the group
   - **Extract Group ID**: From URL when viewing group (facebook.com/groups/GROUP_ID)

#### Phase 3: Environment Configuration
**Objective**: Configure Flask app with Facebook credentials

**Steps to Complete**:
1. **Update `.env` file**
   ```env
   # Facebook Messenger Notifications
   FACEBOOK_PAGE_ACCESS_TOKEN=EAABwzLixnjYBAO... (from Phase 1)
   FACEBOOK_PAGE_ID=61592616314846 (known)
   FACEBOOK_APP_ID=123456789 (from Phase 1)
   FACEBOOK_APP_SECRET=abcdef123456 (from Phase 1)
   FACEBOOK_STAFF_GROUP_ID=123456789 (from Phase 2)
   # Alternative: Individual staff user IDs (comma-separated)
   FACEBOOK_STAFF_USER_IDS=staff_id_1,staff_id_2,staff_id_3
   ```

2. **Extract Staff User IDs (Optional)**
   - For direct messaging fallback, get staff Facebook user IDs
   - Use Facebook Graph API Explorer or third-party tools
   - Format: Comma-separated list of numeric IDs

#### Phase 4: Testing and Validation
**Objective**: Verify notification system works correctly

**Steps to Complete**:
1. **Run Configuration Test**
   ```powershell
   python test_facebook_notifications.py
   ```
   - Verify all credentials are recognized
   - Check API connectivity

2. **Test Individual Notifications**
   - Run test suite with user confirmation
   - Verify each notification type arrives in Facebook group
   - Check message formatting and content

3. **Test Integration with App**
   - Submit a test service request through the portal
   - Verify staff receive notification in Facebook group
   - Test workflow progression notifications
   - Verify payment submission notifications
   - Test approval notifications

4. **Production Deployment**
   - Add Facebook credentials to Render environment variables
   - Test in production environment
   - Monitor notification delivery and reliability

### Notification Workflow Design

#### Current Workflow with Notifications
```
Citizen submits request
↓
[Facebook Notification] → Staff Group: "🔔 NEW SERVICE REQUEST SUBMITTED"
↓
Secretary reviews request
↓
[Facebook Notification] → Staff Group: "📋 REQUEST STATUS UPDATE: Secretary Reviewed"
↓
(Paid services) Citizen uploads payment proof
↓
[Facebook Notification] → Staff Group: "💰 PAYMENT PROOF SUBMITTED" (Treasurer alert)
↓
Treasurer verifies payment
↓
[Facebook Notification] → Staff Group: "📋 REQUEST STATUS UPDATE: Treasurer Verified"
↓
Punong Barangay approves request
↓
[Facebook Notification] → Staff Group: "✅ REQUEST APPROVED"
↓
Certificate generated and stored
```

#### Notification Message Format
Each notification includes:
- **Emoji indicators** for quick recognition (🔔📋💰✅)
- **Service type** and reference number
- **Applicant name** and contact information
- **Action required** or status change
- **Professional formatting** with clear sections
- **Branding footer**: "📱 Barangay 7 e-Services Portal"

### Technical Implementation Details

#### API Integration
- **Endpoint**: Facebook Graph API v18.0
- **Authentication**: Page Access Token
- **Rate Limits**: Respect Facebook's API rate limits
- **Error Handling**: Graceful fallback if API fails

#### Notification Logic
```python
# In app.py - Example integration
if facebook_notifier.is_configured():
    request_data["service_type"] = "barangay_clearance"
    facebook_notifier.notify_new_request(request_data)
```

#### Fallback Strategy
1. **Primary**: Post to Facebook staff group
2. **Fallback**: Direct messages to individual staff accounts
3. **Failure**: Log error and continue workflow (notifications are non-blocking)

### Troubleshooting Guide for Next AI

**IMPORTANT**: The developer has successfully created the Facebook Page (https://www.facebook.com/profile.php?id=61592616314846&sk=about) but is experiencing difficulty creating the Facebook Developer App. This is the current blocker preventing the notification system from being activated.

#### Common Facebook App Creation Issues
1. **App Creation Fails**
   - Check account permissions
   - Verify phone number is confirmed on Facebook
   - Try different browser or incognito mode

2. **Permission Errors**
   - Ensure app has `pages_messaging` permission
   - Check app review status
   - Verify page ownership

3. **Token Generation Issues**
   - Ensure page is properly connected to app
   - Check admin privileges on the page
   - Regenerate token if expired

#### API Integration Issues
1. **Authentication Failures**
   - Verify Page Access Token is correct
   - Check token hasn't expired
   - Ensure token has necessary permissions

2. **Group Posting Failures**
   - Verify group ID is correct
   - Check page is member of the group
   - Ensure page has posting permissions

3. **Rate Limiting**
   - Implement exponential backoff
   - Batch notifications when possible
   - Monitor API usage

### Alternative Notification Options (If Facebook Fails)

If Facebook App creation continues to be problematic, consider these alternatives:

1. **Email Notifications** (Simplest)
   - Use Flask-Mail or Python's smtplib
   - Staff receive email alerts
   - No external API setup required

2. **Telegram Bot** (Best Free Alternative)
   - Create Telegram bot (@BotFather)
   - Add staff to group with bot
   - 100% free, unlimited messages
   - Easier setup than Facebook

3. **Discord Webhooks** (Team Coordination)
   - Create Discord server for staff
   - Simple webhook integration
   - Real-time notifications
   - Free for small teams

4. **WhatsApp Business** (Mobile-First)
   - Use WhatsApp Business API
   - Direct to staff phones
   - Higher engagement than email
   - Setup complexity similar to Facebook

### Files Modified/Added for Notifications

**New Files**:
- `facebook_notifier.py` - Core notification module
- `test_facebook_notifications.py` - Testing suite

**Modified Files**:
- `app.py` - Integrated notification calls in workflow
- `requirements.txt` - Added requests library
- `.env.example` - Added Facebook configuration variables

### Next Steps for Next AI

1. **Immediate Priority**: Complete Facebook App creation
   - Guide developer through the exact steps
   - Troubleshoot any creation issues
   - Obtain all required credentials

2. **Configuration**: Set up environment variables
   - Add credentials to `.env` file
   - Test configuration recognition
   - Verify API connectivity

3. **Testing**: Validate notification system
   - Run test suite
   - Test end-to-end workflow
   - Verify message delivery

4. **Deployment**: Configure production environment
   - Add credentials to Render
   - Test in production
   - Monitor reliability

5. **Documentation**: Update user guides
   - Add staff notification setup instructions
   - Create troubleshooting guide
   - Document notification preferences

### Benefits for Barangay Operations

- **Faster Response Times**: Staff immediately notified of new requests
- **Better Coordination**: All staff see same notifications in group
- **Reduced Delays**: No need to manually check dashboard
- **Mobile Access**: Works on staff phones with free data
- **Professional Communication**: Consistent, formatted notifications
- **Workflow Transparency**: Clear visibility of request progress

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

# Facebook Messenger Notifications (Optional - In Development)
# Only configure these if you want to enable staff notifications via Facebook Messenger
# See "Facebook Messenger Notifications" section below for setup instructions
FACEBOOK_PAGE_ACCESS_TOKEN=your-page-access-token-here
FACEBOOK_PAGE_ID=61592616314846
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_STAFF_GROUP_ID=your-staff-group-id-here
FACEBOOK_STAFF_USER_IDS=staff_user_id_1,staff_user_id_2,staff_user_id_3
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
- **Facebook Messenger notifications** (In Development) - Real-time alerts for request workflow updates

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
- `FACEBOOK_PAGE_ACCESS_TOKEN` - Facebook Page Access Token for notifications (optional)
- `FACEBOOK_PAGE_ID` - Facebook Page ID for notifications (optional)
- `FACEBOOK_APP_ID` - Facebook App ID for notifications (optional)
- `FACEBOOK_APP_SECRET` - Facebook App Secret for notifications (optional)
- `FACEBOOK_STAFF_GROUP_ID` - Facebook Group ID for staff notifications (optional)
- `FACEBOOK_STAFF_USER_IDS` - Comma-separated staff Facebook user IDs (optional)

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
├── facebook_notifier.py            # Facebook Messenger notification system (In Development)
├── test_facebook_notifications.py  # Facebook notification testing suite
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

### Version 1.4 (In Development - August 2026)
- **Facebook Messenger Notifications System** (In Progress)
  - Created FacebookNotifier class for API integration
  - Implemented notification functions for all workflow stages
  - Integrated notifications into all 6 service types
  - Added support for group posts and direct messaging
  - Created comprehensive test suite for validation
  - Updated configuration system for Facebook credentials
  - **Current Status**: Implementation complete, awaiting Facebook App creation
  - **Blocker**: Developer experiencing difficulty creating Facebook Developer App
  - **Facebook Page**: Created (https://www.facebook.com/profile.php?id=61592616314846&sk=about)
  - **Next Step**: Complete Facebook App setup and credential configuration

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
