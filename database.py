"""Supabase database operations for the Barangay e-Services Portal."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from config import Config
import base64
from io import BytesIO
from pathlib import Path
import os

try:
    from supabase import create_client, Client
    supabase: Optional[Client] = None

    config = Config()
    if config.supabase_is_configured:
        try:
            supabase = create_client(config.SUPABASE_URL, config.supabase_server_key)
        except Exception as exc:
            supabase = None
            if os.getenv("FLASK_ENV") != "production":
                print(f"Warning: Supabase client initialization failed: {exc}")
except ImportError:
    supabase = None
    if os.getenv("FLASK_ENV") != "production":
        print("Warning: supabase package not installed. Run: pip install supabase")


def debug_log(*args, **kwargs):
    """Print debug messages only in development mode."""
    if os.getenv("FLASK_ENV") != "production":
        print(*args, **kwargs)


def is_supabase_connected() -> bool:
    """Check if Supabase is properly configured and connected."""
    return supabase is not None


def get_supabase_debug_status() -> Dict[str, Any]:
    """Return a simple debug summary for Supabase initialization."""
    config = Config()
    return {
        "configured": config.supabase_is_configured,
        "url_present": bool(config.SUPABASE_URL),
        "anon_key_present": bool(config.SUPABASE_ANON_KEY),
        "service_role_key_present": bool(config.SUPABASE_SERVICE_ROLE_KEY),
        "client_initialized": supabase is not None,
    }


def create_service_request(
    service_type: str,
    reference_number: str,
    full_name: str,
    address: str,
    contact_number: str,
    sex_at_birth: str,
    gender: str,
    birthday: str,
    civil_status: str,
    email: Optional[str] = None,
    id_photo_filename: Optional[str] = None,
    selfie_photo_filename: Optional[str] = None,
    **service_specific_fields
) -> Optional[Dict[str, Any]]:
    """Create a new service request in the database."""
    if not is_supabase_connected():
        return None
    
    try:
        # Insert common service request data
        request_data = {
            "reference_number": reference_number,
            "service_type": service_type,
            "full_name": full_name,
            "address": address,
            "contact_number": contact_number,
            "sex_at_birth": sex_at_birth,
            "gender": gender,
            "birthday": birthday,
            "civil_status": civil_status,
            "email": email,
            "id_photo_filename": id_photo_filename,
            "selfie_photo_filename": selfie_photo_filename,
            "status": "pending"
        }
        
        result = supabase.table("service_requests").insert(request_data).execute()
        service_request_id = result.data[0]["id"]
        
        # Insert service-specific data based on service type
        if service_type == "barangay_clearance":
            supabase.table("barangay_clearance_details").insert({
                "service_request_id": service_request_id,
                "purpose": service_specific_fields.get("purpose", "")
            }).execute()
        elif service_type == "barangay_certification":
            supabase.table("barangay_certification_details").insert({
                "service_request_id": service_request_id,
                "purpose": service_specific_fields.get("purpose", "")
            }).execute()
        elif service_type == "certificate_of_residency":
            supabase.table("residency_details").insert({
                "service_request_id": service_request_id,
                "years_resided": service_specific_fields.get("years_resided", 0),
                "months_resided": service_specific_fields.get("months_resided", 0),
                "purpose": service_specific_fields.get("purpose", "")
            }).execute()
        elif service_type == "certificate_of_indigency":
            supabase.table("indigency_details").insert({
                "service_request_id": service_request_id,
                "family_size": service_specific_fields.get("family_size", 0),
                "monthly_income": service_specific_fields.get("monthly_income", 0),
                "purpose": service_specific_fields.get("purpose", "")
            }).execute()
        elif service_type == "business_closure":
            supabase.table("business_closure_details").insert({
                "service_request_id": service_request_id,
                "business_name": service_specific_fields.get("business_name", ""),
                "business_address": service_specific_fields.get("business_address", ""),
                "business_type": service_specific_fields.get("business_type", ""),
                "owner_name": service_specific_fields.get("owner_name", ""),
                "closure_date": service_specific_fields.get("closure_date", ""),
                "closure_reason": service_specific_fields.get("closure_reason", "")
            }).execute()
        elif service_type == "first_time_job_seeker":
            supabase.table("job_seeker_details").insert({
                "service_request_id": service_request_id,
                "oath_of_undertaking": service_specific_fields.get("oath_of_undertaking", "")
            }).execute()
        
        return result.data[0]
    except Exception as e:
        debug_log(f"Error creating service request: {e}")
        return None


DETAILS_TABLES = {
    "barangay_clearance": "barangay_clearance_details",
    "barangay_certification": "barangay_certification_details",
    "certificate_of_residency": "residency_details",
    "certificate_of_indigency": "indigency_details",
    "business_closure": "business_closure_details",
    "first_time_job_seeker": "job_seeker_details",
}


def _attach_service_details(service_request: Dict[str, Any]) -> Dict[str, Any]:
    """Merge a request's service-specific record into its common record."""
    if not service_request or not is_supabase_connected():
        return service_request

    enriched_request = dict(service_request)
    details_table = DETAILS_TABLES.get(enriched_request.get("service_type"))
    if details_table:
        try:
            result = (
                supabase.table(details_table)
                .select("*")
                .eq("service_request_id", enriched_request["id"])
                .limit(1)
                .execute()
            )
            if result.data:
                enriched_request.update(result.data[0])
        except Exception as exc:
            debug_log(f"Error loading {details_table}: {exc}")

    # Older Indigency/Residency requests did not yet store their stated purpose.
    # Only set default if purpose field doesn't exist at all (for backward compatibility).
    # Let the certificate generator handle missing/empty purposes.
    if enriched_request.get("service_type") in {"certificate_of_indigency", "certificate_of_residency"}:
        if "purpose" not in enriched_request:
            enriched_request["purpose"] = "any lawful purpose it may serve"

    return enriched_request


def get_service_request_by_reference(reference_number: str) -> Optional[Dict[str, Any]]:
    """Get a service request by its reference number."""
    if not is_supabase_connected():
        return None
    
    try:
        result = supabase.table("service_requests").select("*").eq("reference_number", reference_number).execute()
        if result.data:
            return _attach_service_details(result.data[0])
        return None
    except Exception as e:
        debug_log(f"Error getting service request: {e}")
        return None


def get_all_service_requests(service_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all service requests, optionally filtered by service type."""
    if not is_supabase_connected():
        return []
    
    try:
        query = supabase.table("service_requests").select("*").order("created_at", desc=True)
        if service_type:
            query = query.eq("service_type", service_type)
        result = query.execute()
        return [_attach_service_details(request) for request in result.data]
    except Exception as e:
        debug_log(f"Error getting service requests: {e}")
        return []


def update_service_request_status(
    reference_number: str,
    status: str,
    secretary_notes: Optional[str] = None,
    treasurer_notes: Optional[str] = None,
    chairman_notes: Optional[str] = None,
    decline_reason: Optional[str] = None,
    decline_notes: Optional[str] = None,
    declined_by: Optional[str] = None
) -> bool:
    """Update the status and notes of a service request."""
    if not is_supabase_connected():
        return False
    
    try:
        update_data = {"status": status}
        if secretary_notes is not None:
            update_data["secretary_notes"] = secretary_notes
        if treasurer_notes is not None:
            update_data["treasurer_notes"] = treasurer_notes
        if chairman_notes is not None:
            update_data["chairman_notes"] = chairman_notes
        if decline_reason is not None:
            update_data["decline_reason"] = decline_reason
        if decline_notes is not None:
            update_data["decline_notes"] = decline_notes
        if declined_by is not None:
            update_data["declined_by"] = declined_by
        
        supabase.table("service_requests").update(update_data).eq("reference_number", reference_number).execute()
        return True
    except Exception as e:
        debug_log(f"Error updating service request status: {e}")
        return False





def update_payment_info(reference_number: str, payment_reference: str, payment_proof_filename: str) -> bool:
    """Update payment information for a service request."""
    if not is_supabase_connected():
        return False
    try:
        supabase.table("service_requests").update({
            "payment_reference": payment_reference,
            "payment_proof_filename": payment_proof_filename
        }).eq("reference_number", reference_number).execute()
        return True
    except Exception as e:
        debug_log(f"Error updating payment info: {e}")
        return False


def update_certificate_info(reference_number: str, certificate_number: str, certificate_filename: str) -> bool:
    """Record the durable Supabase Storage path of a generated certificate."""
    if not is_supabase_connected():
        return False

    try:
        supabase.table("service_requests").update({
            "certificate_number": certificate_number,
            "certificate_filename": certificate_filename,
        }).eq("reference_number", reference_number).execute()
        return True
    except Exception as e:
        debug_log(f"Error saving certificate information: {e}")
        return False


def get_barangay_settings() -> Dict[str, str]:
    """Get barangay settings (logo, signature filenames, official names, and contact info)."""
    if not is_supabase_connected():
        return {
            "barangay_logo_filename": "",
            "punong_barangay_signature_filename": "",
            "secretary_signature_filename": "",
            "treasurer_signature_filename": "",
            "gcash_qr_filename": "",
            "punong_barangay_name": "",
            "secretary_name": "",
            "treasurer_name": "",
            "contact_number": "",
            "contact_email": "",
            "contact_facebook": ""
        }
    
    try:
        result = supabase.table("barangay_settings").select("*").limit(1).execute()
        if result.data:
            return {
                "barangay_logo_filename": result.data[0].get("barangay_logo_filename", ""),
                "punong_barangay_signature_filename": result.data[0].get("punong_barangay_signature_filename", ""),
                "secretary_signature_filename": result.data[0].get("secretary_signature_filename", ""),
                "treasurer_signature_filename": result.data[0].get("treasurer_signature_filename", ""),
                "gcash_qr_filename": result.data[0].get("gcash_qr_filename", ""),
                "punong_barangay_name": result.data[0].get("punong_barangay_name", ""),
                "secretary_name": result.data[0].get("secretary_name", ""),
                "treasurer_name": result.data[0].get("treasurer_name", ""),
                "contact_number": result.data[0].get("contact_number", ""),
                "contact_email": result.data[0].get("contact_email", ""),
                "contact_facebook": result.data[0].get("contact_facebook", "")
            }
        return {
            "barangay_logo_filename": "",
            "punong_barangay_signature_filename": "",
            "secretary_signature_filename": "",
            "treasurer_signature_filename": "",
            "gcash_qr_filename": "",
            "punong_barangay_name": "",
            "secretary_name": "",
            "treasurer_name": "",
            "contact_number": "",
            "contact_email": "",
            "contact_facebook": ""
        }
    except Exception as e:
        debug_log(f"Error getting barangay settings: {e}")
        return {
            "barangay_logo_filename": "",
            "punong_barangay_signature_filename": "",
            "secretary_signature_filename": "",
            "treasurer_signature_filename": "",
            "gcash_qr_filename": "",
            "punong_barangay_name": "",
            "secretary_name": "",
            "treasurer_name": "",
            "contact_number": "",
            "contact_email": "",
            "contact_facebook": ""
        }
        return {
            "barangay_logo_filename": "",
            "punong_barangay_signature_filename": "",
            "secretary_signature_filename": "",
            "punong_barangay_name": "",
            "secretary_name": ""
        }


def update_barangay_settings(
    barangay_logo_filename: str = "",
    punong_barangay_signature_filename: str = "",
    secretary_signature_filename: str = "",
    treasurer_signature_filename: str = "",
    gcash_qr_filename: str = "",
    punong_barangay_name: str = "",
    secretary_name: str = "",
    treasurer_name: str = "",
    contact_number: str = "",
    contact_email: str = "",
    contact_facebook: str = ""
) -> bool:
    """Update barangay settings."""
    if not is_supabase_connected():
        return False
    
    try:
        # Get the existing settings row to find its actual UUID
        result = supabase.table("barangay_settings").select("id").limit(1).execute()
        if result.data:
            row_id = result.data[0]["id"]
            # Update the existing row with the correct UUID
            supabase.table("barangay_settings").update({
                "barangay_logo_filename": barangay_logo_filename,
                "punong_barangay_signature_filename": punong_barangay_signature_filename,
                "secretary_signature_filename": secretary_signature_filename,
                "treasurer_signature_filename": treasurer_signature_filename,
                "gcash_qr_filename": gcash_qr_filename,
                "punong_barangay_name": punong_barangay_name,
                "secretary_name": secretary_name,
                "treasurer_name": treasurer_name,
                "contact_number": contact_number,
                "contact_email": contact_email,
                "contact_facebook": contact_facebook
            }).eq("id", row_id).execute()
            return True
        else:
            # No settings row exists, create one
            from uuid import uuid4
            settings_id = str(uuid4())
            supabase.table("barangay_settings").insert({
                "id": settings_id,
                "barangay_logo_filename": barangay_logo_filename,
                "punong_barangay_signature_filename": punong_barangay_signature_filename,
                "secretary_signature_filename": secretary_signature_filename,
                "treasurer_signature_filename": treasurer_signature_filename,
                "gcash_qr_filename": gcash_qr_filename,
                "punong_barangay_name": punong_barangay_name,
                "secretary_name": secretary_name,
                "treasurer_name": treasurer_name,
                "contact_number": contact_number,
                "contact_email": contact_email,
                "contact_facebook": contact_facebook
            }).execute()
            return True
    except Exception as e:
        debug_log(f"Error updating barangay settings: {e}")
        return False


def get_service_requests_by_status(status: str) -> List[Dict[str, Any]]:
    """Get all service requests with a specific status."""
    if not is_supabase_connected():
        return []
    
    try:
        result = supabase.table("service_requests").select("*").eq("status", status).order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        debug_log(f"Error getting service requests by status: {e}")
        return []


def upload_file_to_supabase_storage(file_data: bytes, bucket_name: str, file_path: str, content_type: str = "image/jpeg") -> Optional[str]:
    """Upload a file to Supabase Storage and return the public URL."""
    if not is_supabase_connected():
        return None
    try:
        # Upload file to Supabase Storage
        supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_data,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        return public_url
    except Exception as e:
        debug_log(f"Error uploading file to Supabase Storage: {e}")
        return None


def upload_certificate_to_supabase_storage(local_path: Path, storage_path: str) -> Optional[str]:
    """Upload a generated PDF and return its stable path in the certificates bucket."""
    if not is_supabase_connected():
        return None

    try:
        # Try to create the bucket if it is missing. Some deployments forget to create it.
        try:
            supabase.storage.create_bucket("certificates", public=False)
        except Exception:
            pass

        supabase.storage.from_(config.CERTIFICATE_STORAGE_BUCKET).upload(
            path=storage_path,
            file=local_path.read_bytes(),
            file_options={"content-type": "application/pdf", "upsert": "true"},
        )
        return storage_path
    except Exception as e:
        debug_log(f"Error uploading certificate PDF: {e}")
        return None


def download_certificate_from_supabase_storage(storage_path: str) -> Optional[bytes]:
    """Read a certificate PDF from private Supabase Storage for Flask to send."""
    if not is_supabase_connected():
        return None

    try:
        return supabase.storage.from_(config.CERTIFICATE_STORAGE_BUCKET).download(storage_path)
    except Exception as e:
        debug_log(f"Error downloading certificate PDF: {e}")
        return None


def upload_base64_image_to_supabase(base64_string: str, bucket_name: str, file_path: str) -> Optional[str]:
    """Upload a base64 image string to Supabase Storage and return the public URL."""
    if not is_supabase_connected():
        return None
    
    try:
        # Extract the base64 data
        if not base64_string or not base64_string.startswith("data:image"):
            return None
        
        header, encoded = base64_string.split(",", 1)
        image_data = base64.b64decode(encoded)
        
        # Determine content type from header
        if "jpeg" in header or "jpg" in header:
            content_type = "image/jpeg"
        elif "png" in header:
            content_type = "image/png"
        else:
            content_type = "image/jpeg"  # default
        
        return upload_file_to_supabase_storage(image_data, bucket_name, file_path, content_type)
    except Exception as e:
        debug_log(f"Error uploading base64 image to Supabase Storage: {e}")
        return None


def delete_file_from_supabase_storage(bucket_name: str, file_path: str) -> bool:
    """Delete a file from Supabase Storage."""
    if not is_supabase_connected():
        return False
    
    try:
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        debug_log(f"Error deleting file from Supabase Storage: {e}")
        return False


def get_public_url_from_supabase_storage(bucket_name: str, file_path: str) -> Optional[str]:
    """Get the public URL for a file in Supabase Storage."""
    if not is_supabase_connected():
        return None

    try:
        return supabase.storage.from_(bucket_name).get_public_url(file_path)
    except Exception as e:
        debug_log(f"Error getting public URL from Supabase Storage: {e}")
        return None


def get_staff_user(username: str) -> Optional[Dict[str, Any]]:
    """Get a staff user by username."""
    if not is_supabase_connected():
        return None

    try:
        result = supabase.table("staff_users").select("*").eq("username", username).limit(1).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        debug_log(f"Error getting staff user: {e}")
        # Table might not exist yet
        if "does not exist" in str(e) or "relation" in str(e).lower():
            debug_log(f"[WARN] staff_users table does not exist yet")
        return None


def verify_staff_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Verify staff user credentials using bcrypt password verification."""
    import bcrypt

    user = get_staff_user(username)
    if not user:
        return None

    # Check if user is active
    if not user.get("is_active", True):
        return None

    # Verify password hash
    password_hash = user.get("password_hash", "")
    if not password_hash or password_hash.startswith("$2b$12$PLACEHOLDER"):
        # Placeholder hash - return None to force initialization
        return None

    try:
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return user
    except Exception as e:
        debug_log(f"Error verifying password: {e}")

    return None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_staff_user(username: str, password: str, role: str) -> bool:
    """Create a new staff user with hashed password."""
    if not is_supabase_connected():
        return False

    try:
        password_hash = hash_password(password)
        supabase.table("staff_users").insert({
            "username": username,
            "password_hash": password_hash,
            "role": role,
            "is_active": True
        }).execute()
        return True
    except Exception as e:
        debug_log(f"Error creating staff user: {e}")
        return False


def update_staff_user_password(username: str, new_password: str) -> bool:
    """Update a staff user's password with a new hashed password."""
    if not is_supabase_connected():
        return False

    try:
        password_hash = hash_password(new_password)
        supabase.table("staff_users").update({
            "password_hash": password_hash,
            "updated_at": "NOW()"
        }).eq("username", username).execute()
        return True
    except Exception as e:
        debug_log(f"Error updating staff user password: {e}")
        return False


def initialize_default_staff_users() -> bool:
    """Initialize default staff users with hashed passwords if they don't exist or have placeholder hashes."""
    if not is_supabase_connected():
        debug_log("[WARN] Supabase not connected, skipping staff user initialization")
        return False

    try:
        from config import Config
        config = Config()

        # Get default credentials from config
        defaults = [
            {
                "username": config.PILOT_SECRETARY_USERNAME,
                "password": config.PILOT_SECRETARY_PASSWORD,
                "role": "Secretary"
            },
            {
                "username": config.PILOT_TREASURER_USERNAME,
                "password": config.PILOT_TREASURER_PASSWORD,
                "role": "Treasurer"
            },
            {
                "username": config.PILOT_CHAIRMAN_USERNAME,
                "password": config.PILOT_CHAIRMAN_PASSWORD,
                "role": "Punong Barangay"
            }
        ]

        debug_log(f"[INFO] Initializing {len(defaults)} default staff users...")

        for user_data in defaults:
            username = user_data["username"]
            debug_log(f"[INFO] Processing user: {username}")

            existing_user = get_staff_user(username)

            if existing_user:
                # Check if it has a placeholder hash
                password_hash = existing_user.get("password_hash", "")
                debug_log(f"[INFO] User {username} exists with hash: {password_hash[:20] if password_hash else 'empty'}...")
                if password_hash.startswith("$2b$12$PLACEHOLDER"):
                    # Update with real hash
                    success = update_staff_user_password(username, user_data["password"])
                    if success:
                        debug_log(f"[INFO] Updated password hash for {username}")
                    else:
                        debug_log(f"[ERROR] Failed to update password hash for {username}")
                else:
                    debug_log(f"[INFO] User {username} already has valid hash, skipping")
            else:
                # Create new user
                debug_log(f"[INFO] Creating new staff user: {username}")
                success = create_staff_user(username, user_data["password"], user_data["role"])
                if success:
                    debug_log(f"[INFO] Created staff user {username}")
                else:
                    debug_log(f"[ERROR] Failed to create staff user {username}")

        print("[INFO] Staff user initialization complete")
        return True
    except Exception as e:
        debug_log(f"[ERROR] Error initializing default staff users: {e}")
        import traceback
        traceback.print_exc()
        return False
