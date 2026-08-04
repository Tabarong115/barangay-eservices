import unittest
from pathlib import Path
from unittest import mock

from app import app, CERTIFICATE_DIRECTORY


class CertificateDownloadTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_download_falls_back_to_local_pdf_when_supabase_download_fails(self):
        certificate_filename = "fallback-test.pdf"
        certificate_path = CERTIFICATE_DIRECTORY / certificate_filename
        certificate_path.write_bytes(b"%PDF-1.4\n%test")

        with mock.patch("app.is_supabase_connected", return_value=True), \
             mock.patch("app.get_service_request_by_reference", return_value={
                 "reference_number": "TEST123",
                 "certificate_filename": certificate_filename,
                 "certificate_number": "CERT-001",
             }), \
             mock.patch("app.download_certificate_from_supabase_storage", return_value=None):
            response = self.client.get("/certificates/TEST123")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertIn(b"%PDF", response.data)

        certificate_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
