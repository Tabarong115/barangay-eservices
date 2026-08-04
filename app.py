"""Entry point for the Barangay e-Services Portal."""

import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4
import json
from io import BytesIO

from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, send_file, send_from_directory, session, url_for
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from config import Config
from database import (
    is_supabase_connected,
    get_supabase_debug_status,
    create_service_request,
    get_service_request_by_reference,
    get_all_service_requests,
    update_service_request_status,
    update_payment_info,
    update_certificate_info,
    get_barangay_settings,
    update_barangay_settings,
    get_service_requests_by_status,
    upload_file_to_supabase_storage,
    upload_base64_image_to_supabase,
    delete_file_from_supabase_storage,
    get_public_url_from_supabase_storage,
    upload_certificate_to_supabase_storage,
    download_certificate_from_supabase_storage,
)
from certificate_generator import (
    generate_barangay_clearance,
    generate_barangay_certification,
    generate_certificate_of_residency,
    generate_certificate_of_indigency,
    generate_business_closure_certification,
    generate_first_time_job_seeker_certification,
)

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config())

print("[DEBUG] Supabase init status:", get_supabase_debug_status())

if app.config["REQUIRE_SUPABASE"] and not is_supabase_connected():
    raise RuntimeError("Supabase is required in this environment but could not be initialized.")

UPLOAD_DIRECTORY = Path(app.root_path) / "uploads"
UPLOAD_DIRECTORY.mkdir(exist_ok=True)
CERTIFICATE_DIRECTORY = Path(app.root_path) / "pdf" / "generated"
CERTIFICATE_DIRECTORY.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE = Path(app.root_path) / "pilot_settings.json"
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_ID_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB


@app.context_processor
def inject_settings():
    """Make pilot settings available in all templates."""
    if is_supabase_connected():
        settings = get_barangay_settings()
    else:
        settings = load_pilot_settings()
    return dict(
        barangay_logo_filename=settings.get("barangay_logo_filename", ""),
        punong_barangay_signature_filename=settings.get("punong_barangay_signature_filename", ""),
        secretary_signature_filename=settings.get("secretary_signature_filename", ""),
    )


SERVICES = [
    {"name": "Barangay Clearance", "fee": "₱50.00", "status": "Available", "available": True},
    {"name": "Barangay Certification", "fee": "₱50.00", "status": "Available", "available": True},
    {"name": "Certificate of Residency", "fee": "₱50.00", "status": "Available", "available": True},
    {"name": "Certificate of Indigency", "fee": "Free", "status": "Available", "available": True},
    {"name": "Business Closure Certification", "fee": "₱50.00", "status": "Available", "available": True},
    {"name": "Barangay Permit", "fee": "₱50.00", "status": "Coming soon"},
    {"name": "First Time Job Seeker Certification", "fee": "Free", "status": "Available", "available": True},
]

# Temporary pilot-only storage. It is intentionally replaced by Supabase before
# the portal is used for real transactions, and clears each time Flask restarts.
CLEARANCE_REQUESTS = []
CERTIFICATION_REQUESTS = []
RESIDENCY_REQUESTS = []
INDIGENCY_REQUESTS = []
BUSINESS_CLOSURE_REQUESTS = []
JOB_SEEKER_REQUESTS = []


def pilot_users():
    """Return the three approved local-pilot staff accounts."""
    return {
        app.config["PILOT_SECRETARY_USERNAME"]: {"password": app.config["PILOT_SECRETARY_PASSWORD"], "role": "Secretary"},
        app.config["PILOT_TREASURER_USERNAME"]: {"password": app.config["PILOT_TREASURER_PASSWORD"], "role": "Treasurer"},
        app.config["PILOT_CHAIRMAN_USERNAME"]: {"password": app.config["PILOT_CHAIRMAN_PASSWORD"], "role": "Punong Barangay"},
    }


def is_service_free(service_type: str) -> bool:
    """Check if a service requires payment or is free."""
    free_services = {
        "certificate_of_indigency",
        "first_time_job_seeker",
    }
    return service_type in free_services


def get_display_status(request_data: dict) -> str:
    """Translate stored status into the correct citizen and staff workflow status."""
    status = request_data.get("status", "")
    is_free = is_service_free(request_data.get("service_type", ""))
    status_map = {
        "pending": "Pending Secretary Review",
        "secretary_reviewed": "Pending Punong Barangay Approval" if is_free else "Awaiting Applicant GCash Payment",
        "payment_submitted": "Pending Treasurer Payment Verification",
        "treasurer_verified": "Pending Punong Barangay Approval",
        "approved": "Approved",
    }
    return status_map.get(status, status)


def all_local_requests():
    """Return every in-memory request for local development mode."""
    return (
        CLEARANCE_REQUESTS + CERTIFICATION_REQUESTS + RESIDENCY_REQUESTS
        + INDIGENCY_REQUESTS + BUSINESS_CLOSURE_REQUESTS + JOB_SEEKER_REQUESTS
    )


def dashboard_login_required(view):
    """Keep the local dashboard inaccessible until a pilot staff member signs in."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "staff_role" not in session:
            flash("Please sign in to access the Dashboard.", "error")
            return redirect(url_for("dashboard_login"))
        return view(*args, **kwargs)
    return wrapped_view


def save_pilot_image(image_file, prefix, bucket_name=None):
    """Validate and save an uploaded image for the local pilot or Supabase Storage."""
    if not image_file or not image_file.filename:
        return ""
    if image_file.filename.split(".")[-1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError("Only JPG and PNG images are allowed.")
    
    # Read file data once for validation and storage
    file_data = image_file.read()
    if len(file_data) > MAX_ID_PHOTO_SIZE:
        raise ValueError("Image size exceeds the 5 MB limit.")
    image_file.seek(0)
    
    # Use Supabase Storage if connected and bucket is specified
    if is_supabase_connected() and bucket_name:
        file_extension = image_file.filename.split('.')[-1].lower()
        content_type = "image/jpeg" if file_extension in ["jpg", "jpeg"] else "image/png"
        file_path = f"{prefix}/{uuid4()}.{file_extension}"
        public_url = upload_file_to_supabase_storage(file_data, bucket_name, file_path, content_type)
        if public_url:
            return public_url  # Return the public URL instead of filename
    
    # Fallback to local storage
    filename = f"{prefix}-{uuid4()}.{image_file.filename.split('.')[-1]}"
    with open(UPLOAD_DIRECTORY / filename, "wb") as f:
        f.write(file_data)
    return filename


def save_base64_image(base64_string, prefix, bucket_name=None):
    """Convert base64 image string to file and save it for the local pilot or Supabase Storage."""
    if not base64_string or not base64_string.startswith("data:image"):
        return ""
    
    import base64
    from io import BytesIO
    
    # Extract the base64 data
    header, encoded = base64_string.split(",", 1)
    image_data = base64.b64decode(encoded)
    
    # Check size
    if len(image_data) > MAX_ID_PHOTO_SIZE:
        raise ValueError("Selfie image size exceeds the 5 MB limit.")
    
    # Use Supabase Storage if connected and bucket is specified
    if is_supabase_connected() and bucket_name:
        file_extension = "jpg" if "jpeg" in header or "jpg" in header else "png"
        file_path = f"{prefix}/{uuid4()}.{file_extension}"
        public_url = upload_base64_image_to_supabase(base64_string, bucket_name, file_path)
        if public_url:
            return public_url  # Return the public URL instead of filename
    
    # Fallback to local storage
    # Determine file extension from header
    if "jpeg" in header or "jpg" in header:
        ext = "jpg"
    elif "png" in header:
        ext = "png"
    else:
        ext = "jpg"  # default
    
    # Save the file
    filename = f"{prefix}-{uuid4()}.{ext}"
    with open(UPLOAD_DIRECTORY / filename, "wb") as f:
        f.write(image_data)
    
    return filename


def delete_pilot_file(filename):
    """Remove a previously saved pilot asset file if it exists."""
    if not filename:
        return
    path = UPLOAD_DIRECTORY / filename
    if path.exists():
        path.unlink()


def load_pilot_settings():
    """Load the pilot settings used by the dashboard settings page and certificate generator."""
    defaults = {
        "barangay_logo_filename": "",
        "punong_barangay_signature_filename": "",
        "secretary_signature_filename": "",
    }
    
    # Try Supabase first if connected
    if is_supabase_connected():
        supabase_settings = get_barangay_settings()
        # If Supabase has data, return it
        if any(supabase_settings.values()):
            return supabase_settings
        # If Supabase returns empty but local file exists, use local file as fallback
    
    # Fall back to local file
    if SETTINGS_FILE.exists():
        try:
            return {**defaults, **json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))}
        except (json.JSONDecodeError, OSError):
            return defaults
    
    return defaults


def save_pilot_settings(settings):
    """Save pilot settings for logo and signature assets."""
    # Always save to local file as primary store and fallback
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    
    # Also try to sync to Supabase if connected
    if is_supabase_connected():
        success = update_barangay_settings(
            barangay_logo_filename=settings.get("barangay_logo_filename", ""),
            punong_barangay_signature_filename=settings.get("punong_barangay_signature_filename", ""),
            secretary_signature_filename=settings.get("secretary_signature_filename", "")
        )
        if not success:
            print("[WARNING] Failed to sync settings to Supabase, but local file saved")


@app.get("/")
def public_portal():
    """Show the public-facing service directory."""
    return render_template("index.html", services=SERVICES)


@app.route("/services/barangay-clearance", methods=["GET", "POST"])
def barangay_clearance():
    """Receive one pilot Barangay Clearance request for local workflow testing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        purpose = request.form.get("purpose", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        birthday = request.form.get("birthday", "").strip()
        civil_status = request.form.get("civil_status", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([full_name, address, purpose, contact_number, sex_at_birth, gender, birthday, civil_status]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("barangay_clearance_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("barangay_clearance_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("barangay_clearance")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(CLEARANCE_REQUESTS) + 1
        
        reference_number = f"BC-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            print(f"[DEBUG] Attempting to create service request in Supabase: {reference_number}")
            db_request = create_service_request(
                service_type="barangay_clearance",
                reference_number=reference_number,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday=birthday,
                civil_status=civil_status,
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                purpose=purpose
            )
            print(f"[DEBUG] Database insert result: {db_request}")
            
            clearance_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            print(f"[DEBUG] Using in-memory storage (Supabase not connected)")
            clearance_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            CLEARANCE_REQUESTS.append(clearance_request)
            print(f"[DEBUG] Added to in-memory storage. Total requests: {len(CLEARANCE_REQUESTS)}")
        
        return render_template("request_received.html", clearance_request=clearance_request)

    return render_template("barangay_clearance_form.html", form_data={})


@app.route("/services/barangay-certification", methods=["GET", "POST"])
def barangay_certification():
    """Receive one pilot Barangay Certification request for local workflow testing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        purpose = request.form.get("purpose", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        birthday = request.form.get("birthday", "").strip()
        civil_status = request.form.get("civil_status", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([full_name, address, purpose, contact_number, sex_at_birth, gender, birthday, civil_status]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("barangay_certification_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("barangay_certification_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("barangay_certification")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(CERTIFICATION_REQUESTS) + 1
        
        reference_number = f"BCERT-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            db_request = create_service_request(
                service_type="barangay_certification",
                reference_number=reference_number,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday=birthday,
                civil_status=civil_status,
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                purpose=purpose
            )
            
            certification_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            certification_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            CERTIFICATION_REQUESTS.append(certification_request)
        return render_template("request_received.html", clearance_request=certification_request)

    return render_template("barangay_certification_form.html", form_data={})


@app.route("/services/certificate-of-residency", methods=["GET", "POST"])
def certificate_of_residency():
    """Receive one pilot Certificate of Residency request for local workflow testing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        residency_years = request.form.get("residency_years", "").strip()
        residency_months = request.form.get("residency_months", "").strip()
        purpose = request.form.get("purpose", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        birthday = request.form.get("birthday", "").strip()
        civil_status = request.form.get("civil_status", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([full_name, address, residency_years, residency_months, purpose, contact_number, sex_at_birth, gender, birthday, civil_status]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("certificate_of_residency_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("certificate_of_residency_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("certificate_of_residency")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(RESIDENCY_REQUESTS) + 1
        
        reference_number = f"RES-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            db_request = create_service_request(
                service_type="certificate_of_residency",
                reference_number=reference_number,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday=birthday,
                civil_status=civil_status,
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                years_resided=int(residency_years),
                months_resided=int(residency_months),
                purpose=purpose
            )
            
            residency_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "years_resided": residency_years,
                "months_resided": residency_months,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            residency_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "years_resided": residency_years,
                "months_resided": residency_months,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            RESIDENCY_REQUESTS.append(residency_request)
        
        return render_template("request_received.html", clearance_request=residency_request)

    return render_template("certificate_of_residency_form.html", form_data={})


@app.route("/services/certificate-of-indigency", methods=["GET", "POST"])
def certificate_of_indigency():
    """Receive one pilot Certificate of Indigency request for local workflow testing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        purpose = request.form.get("purpose", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        birthday = request.form.get("birthday", "").strip()
        civil_status = request.form.get("civil_status", "").strip()
        family_size = request.form.get("family_size", "").strip()
        monthly_income = request.form.get("monthly_income", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([full_name, address, purpose, contact_number, sex_at_birth, gender, birthday, civil_status, family_size, monthly_income]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("certificate_of_indigency_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("certificate_of_indigency_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("certificate_of_indigency")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(INDIGENCY_REQUESTS) + 1
        
        reference_number = f"IND-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            db_request = create_service_request(
                service_type="certificate_of_indigency",
                reference_number=reference_number,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday=birthday,
                civil_status=civil_status,
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                family_size=int(family_size),
                monthly_income=float(monthly_income),
                purpose=purpose
            )
            
            indigency_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "family_size": family_size,
                "monthly_income": monthly_income,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            indigency_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "purpose": purpose,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "family_size": family_size,
                "monthly_income": monthly_income,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            INDIGENCY_REQUESTS.append(indigency_request)
        
        return render_template("request_received.html", clearance_request=indigency_request)

    return render_template("certificate_of_indigency_form.html", form_data={})


@app.route("/services/business-closure", methods=["GET", "POST"])
def business_closure():
    """Receive one pilot Business Closure Certification request for local workflow testing."""
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        business_address = request.form.get("business_address", "").strip()
        business_type = request.form.get("business_type", "").strip()
        owner_name = request.form.get("owner_name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        closure_date = request.form.get("closure_date", "").strip()
        reason = request.form.get("reason", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([business_name, business_address, business_type, owner_name, contact_number, sex_at_birth, gender, closure_date, reason]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("business_closure_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("business_closure_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("business_closure")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(BUSINESS_CLOSURE_REQUESTS) + 1
        
        reference_number = f"BIZ-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            # Include additional details in closure reason for now
            detailed_reason = f"{reason} (Business Type: {business_type}, Closure Date: {closure_date})"
            
            db_request = create_service_request(
                service_type="business_closure",
                reference_number=reference_number,
                full_name=owner_name,  # Map owner_name to full_name
                address=business_address,  # Use business_address as address
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday="1900-01-01",  # Placeholder for business closure
                civil_status="N/A",  # Placeholder for business closure
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                business_name=business_name,
                business_address=business_address,
                closure_reason=detailed_reason
            )
            
            business_closure_request = {
                "reference_number": reference_number,
                "business_name": business_name,
                "business_address": business_address,
                "business_type": business_type,
                "owner_name": owner_name,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "closure_date": closure_date,
                "reason": reason,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            business_closure_request = {
                "reference_number": reference_number,
                "business_name": business_name,
                "business_address": business_address,
                "business_type": business_type,
                "owner_name": owner_name,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "closure_date": closure_date,
                "reason": reason,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            BUSINESS_CLOSURE_REQUESTS.append(business_closure_request)
        
        return render_template("request_received.html", clearance_request=business_closure_request)

    return render_template("business_closure_form.html", form_data={})


@app.route("/services/first-time-job-seeker", methods=["GET", "POST"])
def first_time_job_seeker():
    """Receive one pilot First Time Job Seeker Certification request for local workflow testing."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        address = request.form.get("address", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        sex_at_birth = request.form.get("sex_at_birth", "").strip()
        gender = request.form.get("gender", "").strip()
        birthday = request.form.get("birthday", "").strip()
        civil_status = request.form.get("civil_status", "").strip()
        oath = request.form.get("oath", "").strip()
        email = request.form.get("email", "").strip()
        id_photo = request.files.get("id_photo")

        if not all([full_name, address, contact_number, sex_at_birth, gender, birthday, civil_status, oath]):
            flash("Please complete all required fields before submitting.", "error")
            return render_template("first_time_job_seeker_form.html", form_data=request.form)

        try:
            id_photo_filename = save_pilot_image(id_photo, "id", "id-photos" if is_supabase_connected() else None)
            selfie_photo = request.form.get("selfie_photo", "")
            selfie_photo_filename = save_base64_image(selfie_photo, "selfie", "selfie-photos" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("first_time_job_seeker_form.html", form_data=request.form)

        # Generate reference number (using database count if connected)
        if is_supabase_connected():
            existing_requests = get_all_service_requests("first_time_job_seeker")
            request_count = len(existing_requests) + 1
        else:
            request_count = len(JOB_SEEKER_REQUESTS) + 1
        
        reference_number = f"JOB-{datetime.now():%Y%m%d}-{request_count:03d}"
        
        # Create database record if connected
        if is_supabase_connected():
            db_request = create_service_request(
                service_type="first_time_job_seeker",
                reference_number=reference_number,
                full_name=full_name,
                address=address,
                contact_number=contact_number,
                sex_at_birth=sex_at_birth,
                gender=gender,
                birthday=birthday,
                civil_status=civil_status,
                email=email,
                id_photo_filename=id_photo_filename,
                selfie_photo_filename=selfie_photo_filename,
                oath_of_undertaking=oath
            )
            
            job_seeker_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "oath": oath,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
        else:
            # Fallback to in-memory storage
            job_seeker_request = {
                "reference_number": reference_number,
                "full_name": full_name,
                "address": address,
                "contact_number": contact_number,
                "sex_at_birth": sex_at_birth,
                "gender": gender,
                "birthday": birthday,
                "civil_status": civil_status,
                "oath": oath,
                "email": email,
                "id_photo_filename": id_photo_filename,
                "selfie_photo_filename": selfie_photo_filename,
                "payment_reference": "",
                "payment_proof_filename": "",
                "certificate_number": "",
                "certificate_filename": "",
                "issued_at": None,
                "submitted_at": datetime.now(),
                "status": "Pending Secretary Review",
            }
            JOB_SEEKER_REQUESTS.append(job_seeker_request)
        
        return render_template("request_received.html", clearance_request=job_seeker_request)

    return render_template("first_time_job_seeker_form.html", form_data={})


@app.route("/requests/<reference_number>", methods=["GET"], endpoint="track_request")
def track_request(reference_number):
    """Show the limited public status of a pilot request."""
    # Try Supabase first if connected
    if is_supabase_connected():
        db_request = get_service_request_by_reference(reference_number)
        if db_request:
            db_request["status"] = get_display_status(db_request)
            return render_template("track_request.html", clearance_request=db_request)
    
    # Fallback to in-memory search
    clearance_request = next((item for item in CLEARANCE_REQUESTS if item["reference_number"] == reference_number), None)
    if clearance_request:
        return render_template("track_request.html", clearance_request=clearance_request)
    
    certification_request = next((item for item in CERTIFICATION_REQUESTS if item["reference_number"] == reference_number), None)
    if certification_request:
        return render_template("track_request.html", clearance_request=certification_request)
    
    residency_request = next((item for item in RESIDENCY_REQUESTS if item["reference_number"] == reference_number), None)
    if residency_request:
        return render_template("track_request.html", clearance_request=residency_request)
    
    indigency_request = next((item for item in INDIGENCY_REQUESTS if item["reference_number"] == reference_number), None)
    if indigency_request:
        return render_template("track_request.html", clearance_request=indigency_request)
    
    business_closure_request = next((item for item in BUSINESS_CLOSURE_REQUESTS if item["reference_number"] == reference_number), None)
    if business_closure_request:
        return render_template("track_request.html", clearance_request=business_closure_request)
    
    job_seeker_request = next((item for item in JOB_SEEKER_REQUESTS if item["reference_number"] == reference_number), None)
    if job_seeker_request:
        return render_template("track_request.html", clearance_request=job_seeker_request)
    
    abort(404)


@app.route("/track", methods=["GET", "POST"])
def track_request_lookup():
    """Accept a reference number and open its tracking page."""
    if request.method == "POST":
        reference_number = request.form.get("reference_number", "").strip().upper()
        if not reference_number:
            flash("Enter your tracking number to continue.", "error")
        else:
            # Check Supabase first if connected
            if is_supabase_connected():
                db_request = get_service_request_by_reference(reference_number)
                if db_request:
                    return redirect(url_for("track_request", reference_number=reference_number))
            
            # Fallback to in-memory search
            if any(item["reference_number"] == reference_number for item in CLEARANCE_REQUESTS + CERTIFICATION_REQUESTS + RESIDENCY_REQUESTS + INDIGENCY_REQUESTS + BUSINESS_CLOSURE_REQUESTS + JOB_SEEKER_REQUESTS):
                return redirect(url_for("track_request", reference_number=reference_number))
            else:
                flash("We could not find that tracking number. Please check and try again.", "error")
    return render_template("track_lookup.html")


@app.route("/requests/<reference_number>/payment", methods=["GET", "POST"])
def submit_payment(reference_number):
    """Accept manual GCash proof after Secretary review."""
    # Try Supabase first if connected
    if is_supabase_connected():
        clearance_request = get_service_request_by_reference(reference_number)
    else:
        # Fallback to in-memory search
        clearance_request = next((item for item in CLEARANCE_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in CERTIFICATION_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in RESIDENCY_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in INDIGENCY_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in BUSINESS_CLOSURE_REQUESTS if item["reference_number"] == reference_number), None)
    
    if not clearance_request:
        abort(404)
    
    # Free services should never require payment
    if is_service_free(clearance_request.get("service_type", "")):
        flash("This is a free service and does not require payment.", "error")
        return redirect(url_for("track_request", reference_number=reference_number))
    
    if get_display_status(clearance_request) != "Awaiting Applicant GCash Payment":
        flash("Payment proof cannot be submitted at the current request stage.", "error")
        return redirect(url_for("track_request", reference_number=reference_number))
    if request.method == "POST":
        payment_reference = request.form.get("payment_reference", "").strip()
        payment_proof = request.files.get("payment_proof")
        if not payment_reference or not payment_proof or not payment_proof.filename:
            flash("Enter the GCash payment reference and upload the payment screenshot.", "error")
            return render_template("payment_form.html", clearance_request=clearance_request)
        try:
            payment_proof_filename = save_pilot_image(payment_proof, "payment", "payment-proofs" if is_supabase_connected() else None)
        except ValueError as error:
            flash(str(error), "error")
            return render_template("payment_form.html", clearance_request=clearance_request)
        
        # Update database if connected
        if is_supabase_connected():
            update_payment_info(reference_number, payment_reference, payment_proof_filename)
            update_service_request_status(reference_number, "payment_submitted")
        else:
            # Fallback to in-memory update
            clearance_request["payment_reference"] = payment_reference
            clearance_request["payment_proof_filename"] = payment_proof_filename
            clearance_request["status"] = "Pending Treasurer Payment Verification"
        
        return redirect(url_for("track_request", reference_number=reference_number))
    return render_template("payment_form.html", clearance_request=clearance_request)


@app.get("/pilot-id-photos/<path:filename>")
@dashboard_login_required
def pilot_id_photo(filename):
    """Serve local pilot asset files; this route is protected for staff only."""
    # If filename is a URL (from Supabase), redirect to it
    if filename.startswith("http://") or filename.startswith("https://"):
        return redirect(filename)
    
    settings = load_pilot_settings()
    all_requests = CLEARANCE_REQUESTS + CERTIFICATION_REQUESTS + RESIDENCY_REQUESTS + INDIGENCY_REQUESTS + BUSINESS_CLOSURE_REQUESTS + JOB_SEEKER_REQUESTS
    uploaded_files = {item["id_photo_filename"] for item in all_requests} | {item["payment_proof_filename"] for item in all_requests} | {item["selfie_photo_filename"] for item in all_requests}
    uploaded_files |= {
        settings.get("barangay_logo_filename", ""),
        settings.get("punong_barangay_signature_filename", ""),
        settings.get("secretary_signature_filename", ""),
    }
    uploaded_files = {item for item in uploaded_files if item}
    if filename not in uploaded_files:
        abort(404)
    return send_from_directory(UPLOAD_DIRECTORY, filename)


@app.get("/public-logo/<path:filename>")
def public_logo(filename):
    """Serve the Barangay logo publicly for display on all pages."""
    # If filename is a URL (from Supabase), redirect to it
    if filename.startswith("http://") or filename.startswith("https://"):
        return redirect(filename)
    
    settings = load_pilot_settings()
    allowed_logos = {settings.get("barangay_logo_filename", "")}
    allowed_logos = {item for item in allowed_logos if item}
    if filename not in allowed_logos:
        abort(404)
    return send_from_directory(UPLOAD_DIRECTORY, filename)


@app.route("/dashboard/settings", methods=["GET", "POST"])
@dashboard_login_required
def dashboard_settings():
    """Allow pilot staff to manage the Barangay logo and signature assets."""
    settings = load_pilot_settings()
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "upload_logo":
                logo = request.files.get("barangay_logo")
                if not logo or not logo.filename:
                    raise ValueError("Select a Barangay logo image to upload.")
                filename = save_pilot_image(logo, "logo", "logos" if is_supabase_connected() else None)
                delete_pilot_file(settings.get("barangay_logo_filename", ""))
                settings["barangay_logo_filename"] = filename
                flash("Barangay logo uploaded successfully.", "success")
            elif action == "delete_logo":
                delete_pilot_file(settings.get("barangay_logo_filename", ""))
                settings["barangay_logo_filename"] = ""
                flash("Barangay logo removed.", "success")
            elif action == "upload_punong_signature":
                signature = request.files.get("punong_barangay_signature")
                if not signature or not signature.filename:
                    raise ValueError("Select the Punong Barangay signature image to upload.")
                filename = save_pilot_image(signature, "signature_punong", "signatures" if is_supabase_connected() else None)
                delete_pilot_file(settings.get("punong_barangay_signature_filename", ""))
                settings["punong_barangay_signature_filename"] = filename
                flash("Punong Barangay signature uploaded successfully.", "success")
            elif action == "delete_punong_signature":
                delete_pilot_file(settings.get("punong_barangay_signature_filename", ""))
                settings["punong_barangay_signature_filename"] = ""
                flash("Punong Barangay signature removed.", "success")
            elif action == "upload_secretary_signature":
                signature = request.files.get("secretary_signature")
                if not signature or not signature.filename:
                    raise ValueError("Select the Barangay Secretary signature image to upload.")
                filename = save_pilot_image(signature, "signature_secretary", "signatures" if is_supabase_connected() else None)
                delete_pilot_file(settings.get("secretary_signature_filename", ""))
                settings["secretary_signature_filename"] = filename
                flash("Barangay Secretary signature uploaded successfully.", "success")
            elif action == "delete_secretary_signature":
                delete_pilot_file(settings.get("secretary_signature_filename", ""))
                settings["secretary_signature_filename"] = ""
                flash("Barangay Secretary signature removed.", "success")
            else:
                flash("Unknown settings action.", "error")
        except ValueError as error:
            flash(str(error), "error")
        save_pilot_settings(settings)
        return redirect(url_for("dashboard_settings"))
    return render_template("dashboard_settings.html", settings=settings)


@app.get("/certificates/<reference_number>")
def download_certificate(reference_number):
    """Download a certificate created after final local-pilot approval."""
    # Try Supabase first if connected
    if is_supabase_connected():
        clearance_request = get_service_request_by_reference(reference_number)
        if not clearance_request or not clearance_request.get("certificate_filename"):
            clearance_request = None
    if not clearance_request:
        # Fallback to in-memory search
        clearance_request = next((item for item in CLEARANCE_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in CERTIFICATION_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in RESIDENCY_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in INDIGENCY_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in BUSINESS_CLOSURE_REQUESTS if item["reference_number"] == reference_number), None)
        if not clearance_request:
            clearance_request = next((item for item in JOB_SEEKER_REQUESTS if item["reference_number"] == reference_number), None)

    if clearance_request and clearance_request.get("certificate_filename"):
        stored_filename = clearance_request["certificate_filename"]
        if is_supabase_connected():
            certificate_pdf = download_certificate_from_supabase_storage(stored_filename)
            if certificate_pdf:
                download_name = f"{clearance_request.get('certificate_number') or reference_number}.pdf"
                return send_file(
                    BytesIO(certificate_pdf),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=download_name,
                )
    
    if not clearance_request or not clearance_request.get("certificate_filename"):
        abort(404)

    stored_filename = clearance_request["certificate_filename"]
    local_filename = Path(stored_filename).name
    local_path = CERTIFICATE_DIRECTORY / local_filename
    if local_path.exists():
        return send_from_directory(CERTIFICATE_DIRECTORY, local_filename, as_attachment=True)

    if (CERTIFICATE_DIRECTORY / stored_filename).exists():
        return send_from_directory(CERTIFICATE_DIRECTORY, stored_filename, as_attachment=True)

    abort(404)


@app.route("/dashboard/login", methods=["GET", "POST"])
def dashboard_login():
    """Sign in one of the three staff roles for the local pilot."""
    if session.get("staff_role"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = pilot_users().get(username)
        if user and password == user["password"]:
            session.clear()
            session["staff_username"] = username
            session["staff_role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("dashboard_login.html")


@app.get("/dashboard/logout")
def dashboard_logout():
    """End the local pilot dashboard session."""
    session.clear()
    flash("You have signed out.", "success")
    return redirect(url_for("dashboard_login"))


@app.get("/dashboard")
@dashboard_login_required
def dashboard():
    """Show each local-pilot staff role its assigned step in the clearance workflow."""
    role = session["staff_role"]
    
    # The service fee controls routing. Free services never appear for Treasurer.
    if is_supabase_connected():
        all_requests = get_all_service_requests()
        if role == "Secretary":
            assigned_requests = all_requests
        elif role == "Treasurer":
            assigned_requests = [item for item in all_requests if item["status"] == "payment_submitted"]
        else:  # Punong Barangay
            assigned_requests = [
                item for item in all_requests
                if (is_service_free(item.get("service_type", "")) and item["status"] == "secretary_reviewed")
                or (not is_service_free(item.get("service_type", "")) and item["status"] == "treasurer_verified")
            ]
        for item in assigned_requests:
            item["status"] = get_display_status(item)
    else:
        all_requests = all_local_requests()
        if role == "Secretary":
            assigned_requests = all_requests
        elif role == "Treasurer":
            assigned_requests = [item for item in all_requests if item["status"] == "Pending Treasurer Payment Verification"]
        else:
            assigned_requests = [item for item in all_requests if item["status"] == "Pending Punong Barangay Approval"]
    
    return render_template("dashboard.html", requests=assigned_requests, role=role, username=session["staff_username"])


@app.post("/dashboard/requests/<reference_number>/advance")
@dashboard_login_required
def advance_request(reference_number):
    """Move one pilot clearance request through the frozen Version 1 approval order."""
    # Try Supabase first if connected
    if is_supabase_connected():
        clearance_request = get_service_request_by_reference(reference_number)
        use_db = True
    else:
        # Fallback to in-memory search
        clearance_request = next((item for item in CLEARANCE_REQUESTS if item["reference_number"] == reference_number), None)
        request_list = CLEARANCE_REQUESTS
        generator_func = generate_barangay_clearance
        use_db = False
        
        if not clearance_request:
            clearance_request = next((item for item in CERTIFICATION_REQUESTS if item["reference_number"] == reference_number), None)
            request_list = CERTIFICATION_REQUESTS
            generator_func = generate_barangay_certification
        
        if not clearance_request:
            clearance_request = next((item for item in RESIDENCY_REQUESTS if item["reference_number"] == reference_number), None)
            request_list = RESIDENCY_REQUESTS
            generator_func = generate_certificate_of_residency
        
        if not clearance_request:
            clearance_request = next((item for item in INDIGENCY_REQUESTS if item["reference_number"] == reference_number), None)
            request_list = INDIGENCY_REQUESTS
            generator_func = generate_certificate_of_indigency
        
        if not clearance_request:
            clearance_request = next((item for item in BUSINESS_CLOSURE_REQUESTS if item["reference_number"] == reference_number), None)
            request_list = BUSINESS_CLOSURE_REQUESTS
            generator_func = generate_business_closure_certification
        
        if not clearance_request:
            clearance_request = next((item for item in JOB_SEEKER_REQUESTS if item["reference_number"] == reference_number), None)
            request_list = JOB_SEEKER_REQUESTS
            generator_func = generate_first_time_job_seeker_certification
    
    if not clearance_request:
        abort(404)
    
    # Get service type to determine workflow (free vs paid)
    service_type = clearance_request.get("service_type")
    is_free = is_service_free(service_type)
    
    # Determine current status based on database vs in-memory
    if use_db:
        current_status = clearance_request["status"]
        # Map database status to legacy status for compatibility
        if is_free:
            status_mapping = {
                "pending": "Pending Secretary Review",
                "secretary_reviewed": "Pending Punong Barangay Approval",
                "approved": "Approved - Certificate ready for download",
            }
        else:
            status_mapping = {
                "pending": "Pending Secretary Review",
                "secretary_reviewed": "Awaiting Applicant GCash Payment",
                "payment_submitted": "Pending Treasurer Payment Verification",
                "treasurer_verified": "Pending Punong Barangay Approval",
                "approved": "Approved - Certificate ready for download",
            }
        display_status = status_mapping.get(current_status, current_status)
    else:
        display_status = clearance_request["status"]
    
    # Define allowed transitions based on service type (free vs paid)
    if is_free:
        allowed_transitions = {
            ("Secretary", "Pending Secretary Review"): "Pending Punong Barangay Approval",
            ("Punong Barangay", "Pending Punong Barangay Approval"): "Approved - Certificate ready for download",
        }
    else:
        allowed_transitions = {
            ("Secretary", "Pending Secretary Review"): "Awaiting Applicant GCash Payment",
            ("Treasurer", "Pending Treasurer Payment Verification"): "Pending Punong Barangay Approval",
            ("Punong Barangay", "Pending Punong Barangay Approval"): "Approved - Certificate ready for download",
        }
    
    next_status = allowed_transitions.get((session["staff_role"], display_status))
    if not next_status:
        abort(403)
    
    # Update status based on storage method
    if use_db:
        # Map to database status
        if is_free:
            db_status_mapping = {
                "Pending Punong Barangay Approval": "secretary_reviewed",
                "Approved - Certificate ready for download": "approved",
            }
        else:
            db_status_mapping = {
                "Awaiting Applicant GCash Payment": "secretary_reviewed",
                "Pending Punong Barangay Approval": "treasurer_verified",
                "Approved - Certificate ready for download": "approved",
            }
        db_next_status = db_status_mapping.get(next_status, next_status)
        
        # Handle certificate generation for Punong Barangay
        if session["staff_role"] == "Punong Barangay":
            all_requests = get_all_service_requests()
            certificate_number = f"B7-{datetime.now():%Y}-{len(all_requests):04d}"
            settings = load_pilot_settings()
            
            # Determine which generator to use based on service type
            service_type = clearance_request["service_type"]
            if service_type == "barangay_clearance":
                generator_func = generate_barangay_clearance
            elif service_type == "barangay_certification":
                generator_func = generate_barangay_certification
            elif service_type == "certificate_of_residency":
                generator_func = generate_certificate_of_residency
            elif service_type == "certificate_of_indigency":
                generator_func = generate_certificate_of_indigency
            elif service_type == "business_closure":
                generator_func = generate_business_closure_certification
            elif service_type == "first_time_job_seeker":
                generator_func = generate_first_time_job_seeker_certification
            else:
                generator_func = generate_barangay_clearance  # default
            
            certificate_filename = f"{certificate_number}.pdf"
            certificate_data = dict(clearance_request)
            certificate_data["certificate_number"] = certificate_number
            certificate_data["issued_at"] = datetime.now()
            
            # Handle image paths - use URLs from Supabase or local paths
            if settings.get("barangay_logo_filename"):
                logo_filename = settings["barangay_logo_filename"]
                if logo_filename.startswith("http://") or logo_filename.startswith("https://"):
                    certificate_data["logo_path"] = logo_filename  # Use Supabase URL
                else:
                    certificate_data["logo_path"] = UPLOAD_DIRECTORY / logo_filename  # Use local path
            if settings.get("punong_barangay_signature_filename"):
                sig_filename = settings["punong_barangay_signature_filename"]
                if sig_filename.startswith("http://") or sig_filename.startswith("https://"):
                    certificate_data["punong_barangay_signature_path"] = sig_filename  # Use Supabase URL
                else:
                    certificate_data["punong_barangay_signature_path"] = UPLOAD_DIRECTORY / sig_filename  # Use local path
            if settings.get("secretary_signature_filename"):
                sig_filename = settings["secretary_signature_filename"]
                if sig_filename.startswith("http://") or sig_filename.startswith("https://"):
                    certificate_data["secretary_signature_path"] = sig_filename  # Use Supabase URL
                else:
                    certificate_data["secretary_signature_path"] = UPLOAD_DIRECTORY / sig_filename  # Use local path
            
            local_certificate_path = CERTIFICATE_DIRECTORY / certificate_filename
            try:
                generator_func(certificate_data, local_certificate_path)
            except Exception as error:
                print(f"[ERROR] Certificate generation failed for {reference_number}: {error}")
                flash("Certificate could not be generated. The request remains awaiting approval; please contact the Barangay Secretary.", "error")
                return redirect(url_for("dashboard"))
            storage_path = f"{datetime.now():%Y}/{certificate_filename}"
            uploaded_certificate_path = upload_certificate_to_supabase_storage(local_certificate_path, storage_path)
            if not uploaded_certificate_path:
                flash("Certificate could not be saved to Supabase Storage. The request remains awaiting approval.", "error")
                return redirect(url_for("dashboard"))
            if not update_certificate_info(reference_number, certificate_number, uploaded_certificate_path):
                flash("Certificate details could not be saved. The request remains awaiting approval.", "error")
                return redirect(url_for("dashboard"))
        if not update_service_request_status(reference_number, db_next_status):
            flash("Request status could not be saved. Please try again.", "error")
            return redirect(url_for("dashboard"))
    else:
        # Legacy in-memory update
        clearance_request["status"] = next_status
        if session["staff_role"] == "Punong Barangay":
            clearance_request["certificate_number"] = f"B7-{datetime.now():%Y}-{len(request_list):04d}"
            clearance_request["issued_at"] = datetime.now()
            clearance_request["certificate_filename"] = f"{clearance_request['certificate_number']}.pdf"
            settings = load_pilot_settings()
            certificate_data = dict(clearance_request)
            # Handle image paths - use URLs from Supabase or local paths
            if settings.get("barangay_logo_filename"):
                logo_filename = settings["barangay_logo_filename"]
                if logo_filename.startswith("http://") or logo_filename.startswith("https://"):
                    certificate_data["logo_path"] = logo_filename  # Use Supabase URL
                else:
                    certificate_data["logo_path"] = UPLOAD_DIRECTORY / logo_filename  # Use local path
            if settings.get("punong_barangay_signature_filename"):
                sig_filename = settings["punong_barangay_signature_filename"]
                if sig_filename.startswith("http://") or sig_filename.startswith("https://"):
                    certificate_data["punong_barangay_signature_path"] = sig_filename  # Use Supabase URL
                else:
                    certificate_data["punong_barangay_signature_path"] = UPLOAD_DIRECTORY / sig_filename  # Use local path
            if settings.get("secretary_signature_filename"):
                sig_filename = settings["secretary_signature_filename"]
                if sig_filename.startswith("http://") or sig_filename.startswith("https://"):
                    certificate_data["secretary_signature_path"] = sig_filename  # Use Supabase URL
                else:
                    certificate_data["secretary_signature_path"] = UPLOAD_DIRECTORY / sig_filename  # Use local path
            generator_func(certificate_data, CERTIFICATE_DIRECTORY / clearance_request["certificate_filename"])
    
    flash(f"{reference_number} was forwarded successfully.", "success")
    return redirect(url_for("dashboard"))


@app.get("/dashboard/reports")
@dashboard_login_required
def dashboard_reports():
    """Show transaction history and statistics. Secretary only."""
    role = session["staff_role"]
    
    # Only Secretary can access this
    if role != "Secretary":
        abort(403)
    
    # Gather all requests
    if is_supabase_connected():
        all_requests = get_all_service_requests()
        for req in all_requests:
            req["status"] = get_display_status(req)
    else:
        all_requests = all_local_requests()
    
    # Calculate statistics by service type
    stats = {}
    for req in all_requests:
        service_type = req.get("service_type", "Unknown")
        if service_type not in stats:
            stats[service_type] = {
                "total": 0,
                "completed": 0,
                "pending": 0,
                "awaiting_payment": 0,
                "awaiting_approval": 0,
            }
        
        stats[service_type]["total"] += 1
        
        status = req.get("status", "")
        if status == "Approved":
            stats[service_type]["completed"] += 1
        elif status == "Pending Secretary Review":
            stats[service_type]["pending"] += 1
        elif status == "Awaiting Applicant GCash Payment":
            stats[service_type]["awaiting_payment"] += 1
        elif status == "Pending Punong Barangay Approval" or status == "Pending Treasurer Payment Verification":
            stats[service_type]["awaiting_approval"] += 1
    
    # Overall statistics
    total_requests = len(all_requests)
    completed_requests = sum(1 for req in all_requests if req.get("status") == "Approved")
    pending_requests = total_requests - completed_requests
    
    # Sort requests by date (newest first)
    sorted_requests = sorted(
        all_requests,
        key=lambda x: x.get("submitted_at", datetime.min),
        reverse=True
    )
    
    return render_template(
        "transaction_report.html",
        all_requests=sorted_requests,
        stats=stats,
        total_requests=total_requests,
        completed_requests=completed_requests,
        pending_requests=pending_requests,
        now=datetime.now,
    )


@app.route("/verify", methods=["GET"])
def verify_certificate():
    """Verify certificate authenticity via QR code scan."""
    certificate_number = request.args.get("cert")
    tracking_number = request.args.get("track")
    
    if not certificate_number:
        return render_template("verify_certificate.html", 
                             valid=False, 
                             error="Certificate number is required")
    
    # Search for the certificate in the database
    if is_supabase_connected():
        all_requests = get_all_service_requests()
    else:
        all_requests = all_local_requests()
    
    # Find the request with matching certificate number
    certificate_data = None
    for req in all_requests:
        if req.get("certificate_number") == certificate_number:
            certificate_data = req
            break
    
    if not certificate_data:
        return render_template("verify_certificate.html",
                             valid=False,
                             error="Certificate not found in records")
    
    # Additional verification with tracking number if provided
    if tracking_number and certificate_data.get("tracking_number") != tracking_number:
        return render_template("verify_certificate.html",
                             valid=False,
                             error="Tracking number does not match certificate")
    
    # Certificate is valid
    return render_template("verify_certificate.html",
                         valid=True,
                         certificate=certificate_data,
                         service_type=certificate_data.get("service_type", "Unknown"),
                         certificate_number=certificate_number,
                         tracking_number=certificate_data.get("tracking_number"),
                         full_name=certificate_data.get("full_name", "N/A"),
                         issued_at=certificate_data.get("issued_at"),
                         status=get_display_status(certificate_data))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
