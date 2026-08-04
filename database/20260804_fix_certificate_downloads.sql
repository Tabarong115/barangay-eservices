-- Barangay e-Services Portal - Durable certificate downloads
-- Run this entire file once in Supabase: SQL Editor > New query > Run.

-- Save the official certificate number and its Supabase Storage path.
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS certificate_number VARCHAR(50);

ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS certificate_filename VARCHAR(255);

-- PDFs must survive Render restarts, so they are stored in Supabase Storage.
INSERT INTO storage.buckets (id, name, public)
VALUES ('certificates', 'certificates', false)
ON CONFLICT (id) DO NOTHING;

-- The Flask app currently connects using the configured Supabase anon key.
-- These policies allow it to upload and retrieve PDFs through the app's
-- controlled download endpoint. Do not expose direct public certificate URLs.
DROP POLICY IF EXISTS "certificate_storage_read_policy" ON storage.objects;
DROP POLICY IF EXISTS "certificate_storage_insert_policy" ON storage.objects;
DROP POLICY IF EXISTS "certificate_storage_update_policy" ON storage.objects;

CREATE POLICY "certificate_storage_read_policy"
ON storage.objects FOR SELECT
USING (bucket_id = 'certificates');

CREATE POLICY "certificate_storage_insert_policy"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'certificates');

CREATE POLICY "certificate_storage_update_policy"
ON storage.objects FOR UPDATE
USING (bucket_id = 'certificates')
WITH CHECK (bucket_id = 'certificates');
