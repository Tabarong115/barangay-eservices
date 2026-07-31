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

    @property
    def supabase_is_configured(self):
        """True only when both public Supabase settings are supplied."""
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)
