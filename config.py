"""Environment-based configuration for the Barangay e-Services Portal."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Config:
    """Configuration values are kept outside source code for safer deployment."""

    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    CERTIFICATE_STORAGE_BUCKET = os.getenv("CERTIFICATE_STORAGE_BUCKET", "certificates")
    REQUIRE_SUPABASE = os.getenv("REQUIRE_SUPABASE", "false").lower() == "true"

    # Local pilot accounts only. Replace these with Supabase Authentication
    # before the portal is used with real citizen records.
    PILOT_SECRETARY_USERNAME = os.getenv("PILOT_SECRETARY_USERNAME", "secretary")
    PILOT_SECRETARY_PASSWORD = os.getenv("PILOT_SECRETARY_PASSWORD", "secretary-test")
    PILOT_TREASURER_USERNAME = os.getenv("PILOT_TREASURER_USERNAME", "treasurer")
    PILOT_TREASURER_PASSWORD = os.getenv("PILOT_TREASURER_PASSWORD", "treasurer-test")
    PILOT_CHAIRMAN_USERNAME = os.getenv("PILOT_CHAIRMAN_USERNAME", "chairman")
    PILOT_CHAIRMAN_PASSWORD = os.getenv("PILOT_CHAIRMAN_PASSWORD", "chairman-test")
    GCASH_ACCOUNT_NAME = os.getenv("GCASH_ACCOUNT_NAME", "Barangay 7 — To be provided")
    GCASH_ACCOUNT_NUMBER = os.getenv("GCASH_ACCOUNT_NUMBER", "To be provided")
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  # Base URL for QR code generation

    @property
    def supabase_is_configured(self):
        """True when the server has a Supabase URL and a usable server key."""
        return bool(self.SUPABASE_URL and (self.SUPABASE_SERVICE_ROLE_KEY or self.SUPABASE_ANON_KEY))

    @property
    def supabase_server_key(self):
        """Prefer the server-only key; retain anon-key support for local development."""
        return self.SUPABASE_SERVICE_ROLE_KEY or self.SUPABASE_ANON_KEY
