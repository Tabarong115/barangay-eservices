"""Supabase database operations for the Barangay e-Services Portal."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from config import Config
import base64
from io import BytesIO
from pathlib import Path

try:
    from supabase import create_client, Client
    supabase: Optional[Client] = None

    config = Config()
    if config.supabase_is_configured:
        try:
            supabase = create_client(config.SUPABASE_URL, config.supabase_server_key)
        except Exception as exc:
            supabase = None
            print(f"Warning: Supabase client initialization failed: {exc}")
except ImportError:
    supabase = None
    print("Warning: supabase package not installed. Run: pip install supabase")


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
                "closure_reason": service_specific_fields.get("closure_reason", "")
            }).execute()
        elif service_type == "first_time_job_seeker":
            supabase.table("job_seeker_details").insert({
                "service_request_id": service_request_id,
                "oath_of_undertaking": service_specific_fields.get("oath_of_undertaking", "")
            }).execute()
        
        return result.data[0]
    except Exception as e:
        print(f"Error creating service request: {e}")
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
            print(f"Error loading {details_table}: {exc}")

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
        print(f"Error getting service request: {e}")
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
        print(f"Error getting service requests: {e}")
        return []


def update_service_request_status(
    reference_number: str,
    status: str,
    secretary_notes: Optional[str] = None,
    treasurer_notes: Optional[str] = None,
    chairman_notes: Optional[str] = None
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
        
        supabase.table("service_requests").update(update_data).eq("reference_number", reference_number).execute()
        return True
    except Exception as e:
        print(f"Error updating service request status: {e}")
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
        print(f"Error updating payment info: {e}")
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
        print(f"Error saving certificate information: {e}")
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
        print(f"Error getting barangay settings: {e}")
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
        print(f"Error updating barangay settings: {e}")
        return False


def get_service_requests_by_status(status: str) -> List[Dict[str, Any]]:
    """Get all service requests with a specific status."""
    if not is_supabase_connected():
        return []
    
    try:
        result = supabase.table("service_requests").select("*").eq("status", status).order("created_at", desc=True).execute()
        return result.data
    except Exception as e:
        print(f"Error getting service requests by status: {e}")
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
        print(f"Error uploading file to Supabase Storage: {e}")
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
        print(f"Error uploading certificate PDF: {e}")
        return None


def download_certificate_from_supabase_storage(storage_path: str) -> Optional[bytes]:
    """Read a certificate PDF from private Supabase Storage for Flask to send."""
    if not is_supabase_connected():
        return None

    try:
        return supabase.storage.from_(config.CERTIFICATE_STORAGE_BUCKET).download(storage_path)
    except Exception as e:
        print(f"Error downloading certificate PDF: {e}")
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
        print(f"Error uploading base64 image to Supabase Storage: {e}")
        return None


def delete_file_from_supabase_storage(bucket_name: str, file_path: str) -> bool:
    """Delete a file from Supabase Storage."""
    if not is_supabase_connected():
        return False
    
    try:
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
    except Exception as e:
        print(f"Error deleting file from Supabase Storage: {e}")
        return False


def get_public_url_from_supabase_storage(bucket_name: str, file_path: str) -> Optional[str]:
    """Get the public URL for a file in Supabase Storage."""
    if not is_supabase_connected():
        return None
    
    try:
        return supabase.storage.from_(bucket_name).get_public_url(file_path)
    except Exception as e:
        print(f"Error getting public URL from Supabase Storage: {e}")
        return None
