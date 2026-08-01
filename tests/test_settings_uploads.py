import io
import unittest
from pathlib import Path
from unittest.mock import patch

import app as app_module
import database


class SettingsUploadTests(unittest.TestCase):
    def test_dashboard_settings_upload_logo_uses_logos_bucket(self):
        client = app_module.app.test_client()

        with client.session_transaction() as session:
            session["staff_role"] = "Secretary"

        def fake_save_pilot_image(image_file, prefix, bucket_name=None):
            self.assertEqual(bucket_name, "logos")
            return "logo.png"

        with patch.object(app_module, "is_supabase_connected", return_value=True), \
             patch.object(app_module, "save_pilot_image", side_effect=fake_save_pilot_image), \
             patch.object(app_module, "delete_pilot_file"), \
             patch.object(app_module, "save_pilot_settings"):
            response = client.post(
                "/dashboard/settings",
                data={
                    "action": "upload_logo",
                    "barangay_logo": (io.BytesIO(b"fake-image-data"), "logo.png"),
                },
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 302)

    def test_update_barangay_settings_uses_existing_row_id(self):
        class FakeQuery:
            def __init__(self, payload=None):
                self.payload = payload
                self.eq_column = None
                self.eq_value = None

            def limit(self, n):
                return self

            def eq(self, column, value):
                self.eq_column = column
                self.eq_value = value
                return self

            def execute(self):
                # For the select query (finding existing row), return a row with a UUID
                if self.payload is None:
                    return type("Result", (), {"data": [{"id": "550e8400-e29b-41d4-a716-446655440000"}]})()
                # For the update query, just return success
                if self.eq_column == "id":
                    return type("Result", (), {"data": [{"id": "550e8400-e29b-41d4-a716-446655440000"}]})()
                return type("Result", (), {"data": []})()

        class FakeTable:
            def __init__(self):
                self.payload = None

            def select(self, *args):
                return FakeQuery()

            def update(self, payload):
                self.payload = payload
                return FakeQuery(payload)

        class FakeSupabaseClient:
            def __init__(self):
                self.table_name = None
                self.table_instance = FakeTable()

            def table(self, name):
                self.table_name = name
                return self.table_instance

        fake_client = FakeSupabaseClient()

        with patch.object(database, "supabase", fake_client), \
             patch.object(database, "is_supabase_connected", return_value=True):
            result = database.update_barangay_settings("logo.png", "sig.png", "sec.png")

        self.assertTrue(result)
        self.assertEqual(fake_client.table_instance.payload["barangay_logo_filename"], "logo.png")


if __name__ == "__main__":
    unittest.main()
