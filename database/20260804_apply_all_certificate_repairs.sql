-- Barangay e-Services Portal - Apply all certificate repairs
-- Supabase SQL Editor: New query > paste this entire file > Run.

-- 1. Keep certificate-specific request details needed by PDF generators.
ALTER TABLE indigency_details
ADD COLUMN IF NOT EXISTS purpose TEXT;

ALTER TABLE residency_details
ADD COLUMN IF NOT EXISTS purpose TEXT;

UPDATE indigency_details
SET purpose = 'any lawful purpose'
WHERE purpose IS NULL OR btrim(purpose) = '';

UPDATE residency_details
SET purpose = 'any lawful purpose'
WHERE purpose IS NULL OR btrim(purpose) = '';

-- 2. Allow all workflow statuses used by the current app.
ALTER TABLE service_requests
DROP CONSTRAINT IF EXISTS valid_status;

ALTER TABLE service_requests
ADD CONSTRAINT valid_status CHECK (status IN (
    'pending',
    'secretary_reviewed',
    'payment_submitted',
    'treasurer_verified',
    'approved',
    'rejected'
));

-- 3. Persist generated certificate metadata for reliable downloads.
ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS certificate_number VARCHAR(50);

ALTER TABLE service_requests
ADD COLUMN IF NOT EXISTS certificate_filename VARCHAR(255);

-- 4. Store PDFs in Supabase rather than temporary Render storage.
INSERT INTO storage.buckets (id, name, public)
VALUES ('certificates', 'certificates', false)
ON CONFLICT (id) DO NOTHING;

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
