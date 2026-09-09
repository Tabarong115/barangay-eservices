-- Migration to add decline-related fields to service_requests table
-- This allows staff to decline requests with specific reasons and notes

-- Add decline-related columns to service_requests table
ALTER TABLE service_requests 
ADD COLUMN IF NOT EXISTS decline_reason TEXT,
ADD COLUMN IF NOT EXISTS decline_notes TEXT,
ADD COLUMN IF NOT EXISTS declined_by TEXT;

-- Add comments to explain the new fields
COMMENT ON COLUMN service_requests.decline_reason IS 'Primary reason for declining the request (e.g., not a resident, insufficient documentation)';
COMMENT ON COLUMN service_requests.decline_notes IS 'Additional notes or details about the decline decision';
COMMENT ON COLUMN service_requests.declined_by IS 'Staff role that declined the request (Secretary, Treasurer, or Punong Barangay)';

-- Note: RLS policies from setup_supabase_policies.sql should already allow staff to update service_requests
-- No additional policy changes needed as the existing policies grant update access to authenticated users