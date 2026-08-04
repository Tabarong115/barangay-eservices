-- Barangay e-Services Portal - Certificate data and workflow repair
-- Run this entire file once in Supabase: SQL Editor > New query > Run.

-- Store the stated purpose needed by the PDF generators.
ALTER TABLE indigency_details
ADD COLUMN IF NOT EXISTS purpose TEXT;

ALTER TABLE residency_details
ADD COLUMN IF NOT EXISTS purpose TEXT;

-- The current app uses these workflow states. Replace the old constraint,
-- which rejected payment_submitted and approved updates.
ALTER TABLE service_requests
DROP CONSTRAINT IF EXISTS valid_status;

ALTER TABLE service_requests
ADD CONSTRAINT valid_status CHECK (status IN (
    'pending',
    'secretary_reviewed',
    'payment_submitted',
    'treasurer_verified',
    'approved',
    'chairman_approved',
    'completed',
    'rejected'
));

-- Existing Indigency and Residency requests do not have a recoverable stated
-- purpose. This fallback lets their certificates generate without inventing one.
UPDATE indigency_details
SET purpose = 'any lawful purpose'
WHERE purpose IS NULL OR btrim(purpose) = '';

UPDATE residency_details
SET purpose = 'any lawful purpose'
WHERE purpose IS NULL OR btrim(purpose) = '';
