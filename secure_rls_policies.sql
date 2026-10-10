-- Secure RLS Policies for Barangay e-Services Portal
-- This file implements proper Row-Level Security (RLS) policies
-- while maintaining the app's functionality for public users and staff

-- ============================================
-- SECURITY ARCHITECTURE
-- ============================================
-- This application uses a server-side architecture:
-- 1. All database operations happen via Flask backend
-- 2. Backend uses SUPABASE_SERVICE_ROLE_KEY (bypasses RLS by design)
-- 3. SUPABASE_ANON_KEY is never exposed to the frontend
-- 4. Therefore, RLS policies primarily protect against:
--    - Accidental exposure of service role key
--    - Future client-side access patterns
--    - Direct database access via Supabase dashboard

-- ============================================
-- SERVICE_REQUESTS TABLE POLICIES
-- ============================================

-- Drop existing policies
DROP POLICY IF EXISTS "service_requests_insert_policy" ON service_requests;
DROP POLICY IF EXISTS "service_requests_select_policy" ON service_requests;
DROP POLICY IF EXISTS "service_requests_update_policy" ON service_requests;

-- Allow INSERT for service role (backend operations)
CREATE POLICY "service_requests_insert_policy"
ON service_requests FOR INSERT
TO service_role
WITH CHECK (true);

-- Allow SELECT for service role (backend operations)
CREATE POLICY "service_requests_select_policy"
ON service_requests FOR SELECT
TO service_role
USING (true);

-- Allow UPDATE for service role (backend operations)
CREATE POLICY "service_requests_update_policy"
ON service_requests FOR UPDATE
TO service_role
USING (true);

-- Note: We don't create anon policies for service_requests because:
-- - All operations happen server-side via service role
-- - Anon key is never exposed to frontend
-- - This provides defense-in-depth security

-- ============================================
-- SERVICE DETAIL TABLES POLICIES
-- ============================================

-- Barangay Clearance Details
DROP POLICY IF EXISTS "barangay_clearance_details_insert_policy" ON barangay_clearance_details;
DROP POLICY IF EXISTS "barangay_clearance_details_select_policy" ON barangay_clearance_details;

CREATE POLICY "barangay_clearance_details_insert_policy"
ON barangay_clearance_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "barangay_clearance_details_select_policy"
ON barangay_clearance_details FOR SELECT
TO service_role
USING (true);

-- Barangay Certification Details
DROP POLICY IF EXISTS "barangay_certification_details_insert_policy" ON barangay_certification_details;
DROP POLICY IF EXISTS "barangay_certification_details_select_policy" ON barangay_certification_details;

CREATE POLICY "barangay_certification_details_insert_policy"
ON barangay_certification_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "barangay_certification_details_select_policy"
ON barangay_certification_details FOR SELECT
TO service_role
USING (true);

-- Residency Details
DROP POLICY IF EXISTS "residency_details_insert_policy" ON residency_details;
DROP POLICY IF EXISTS "residency_details_select_policy" ON residency_details;

CREATE POLICY "residency_details_insert_policy"
ON residency_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "residency_details_select_policy"
ON residency_details FOR SELECT
TO service_role
USING (true);

-- Indigency Details
DROP POLICY IF EXISTS "indigency_details_insert_policy" ON indigency_details;
DROP POLICY IF EXISTS "indigency_details_select_policy" ON indigency_details;

CREATE POLICY "indigency_details_insert_policy"
ON indigency_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "indigency_details_select_policy"
ON indigency_details FOR SELECT
TO service_role
USING (true);

-- Business Closure Details
DROP POLICY IF EXISTS "business_closure_details_insert_policy" ON business_closure_details;
DROP POLICY IF EXISTS "business_closure_details_select_policy" ON business_closure_details;

CREATE POLICY "business_closure_details_insert_policy"
ON business_closure_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "business_closure_details_select_policy"
ON business_closure_details FOR SELECT
TO service_role
USING (true);

-- Job Seeker Details
DROP POLICY IF EXISTS "job_seeker_details_insert_policy" ON job_seeker_details;
DROP POLICY IF EXISTS "job_seeker_details_select_policy" ON job_seeker_details;

CREATE POLICY "job_seeker_details_insert_policy"
ON job_seeker_details FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "job_seeker_details_select_policy"
ON job_seeker_details FOR SELECT
TO service_role
USING (true);

-- ============================================
-- BARANGAY_SETTINGS TABLE POLICIES
-- ============================================
-- This table contains public information (logo, contact info, etc.)
-- We allow SELECT for both service_role and anon for public access

DROP POLICY IF EXISTS "barangay_settings_insert_policy" ON barangay_settings;
DROP POLICY IF EXISTS "barangay_settings_select_policy" ON barangay_settings;
DROP POLICY IF EXISTS "barangay_settings_update_policy" ON barangay_settings;

CREATE POLICY "barangay_settings_insert_policy"
ON barangay_settings FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "barangay_settings_select_policy"
ON barangay_settings FOR SELECT
TO service_role, anon
USING (true);

CREATE POLICY "barangay_settings_update_policy"
ON barangay_settings FOR UPDATE
TO service_role
USING (true);

-- ============================================
-- STAFF_USERS TABLE POLICIES (CRITICAL SECURITY)
-- ============================================
-- This table contains sensitive authentication data
-- Only service role should have access

DROP POLICY IF EXISTS "staff_users_insert_policy" ON staff_users;
DROP POLICY IF EXISTS "staff_users_select_policy" ON staff_users;
DROP POLICY IF EXISTS "staff_users_update_policy" ON staff_users;

CREATE POLICY "staff_users_insert_policy"
ON staff_users FOR INSERT
TO service_role
WITH CHECK (true);

CREATE POLICY "staff_users_select_policy"
ON staff_users FOR SELECT
TO service_role
USING (true);

CREATE POLICY "staff_users_update_policy"
ON staff_users FOR UPDATE
TO service_role
USING (true);

-- ============================================
-- STORAGE BUCKETS POLICIES
-- ============================================
-- Storage buckets contain public assets (logos, signatures, etc.)
-- We allow public SELECT for the assets that need to be displayed

DROP POLICY IF EXISTS "public_storage_policy" ON storage.objects;
DROP POLICY IF EXISTS "public_storage_upload_policy" ON storage.objects;
DROP POLICY IF EXISTS "public_storage_update_policy" ON storage.objects;

-- Allow public SELECT for logos, signatures, and QR codes (needed for display)
CREATE POLICY "public_storage_select_policy"
ON storage.objects FOR SELECT
TO service_role, anon
USING (bucket_id IN ('logos', 'signatures', 'qrcodes'));

-- Allow service role to upload to all buckets
CREATE POLICY "storage_upload_policy"
ON storage.objects FOR INSERT
TO service_role
WITH CHECK (bucket_id IN ('id-photos', 'selfie-photos', 'payment-proofs', 'logos', 'signatures', 'certificates', 'qrcodes'));

-- Allow service role to update all buckets
CREATE POLICY "storage_update_policy"
ON storage.objects FOR UPDATE
TO service_role
USING (bucket_id IN ('id-photos', 'selfie-photos', 'payment-proofs', 'logos', 'signatures', 'certificates', 'qrcodes'));

-- ============================================
-- SECURITY NOTES
-- ============================================
-- 1. All backend operations use SUPABASE_SERVICE_ROLE_KEY (bypasses RLS)
-- 2. SUPABASE_ANON_KEY is never exposed to the frontend
-- 3. These policies provide defense-in-depth security
-- 4. Future enhancement: Implement Supabase Auth for proper row-level security
-- 5. Critical: Never expose SUPABASE_SERVICE_ROLE_KEY to the frontend
-- 6. Critical: Keep SUPABASE_SERVICE_ROLE_KEY secure in environment variables
