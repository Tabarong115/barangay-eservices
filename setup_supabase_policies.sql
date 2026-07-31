-- Comprehensive RLS Policies for Barangay e-Services Portal
-- Run this in your Supabase SQL Editor

-- ============================================
-- SERVICE_REQUESTS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "service_requests_insert_policy" ON service_requests;
DROP POLICY IF EXISTS "service_requests_select_policy" ON service_requests;
DROP POLICY IF EXISTS "service_requests_update_policy" ON service_requests;

CREATE POLICY "service_requests_insert_policy" 
ON service_requests FOR INSERT 
WITH CHECK (true);

CREATE POLICY "service_requests_select_policy" 
ON service_requests FOR SELECT 
USING (true);

CREATE POLICY "service_requests_update_policy" 
ON service_requests FOR UPDATE 
USING (true);

-- ============================================
-- BARANGAY_CLEARANCE_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "barangay_clearance_details_insert_policy" ON barangay_clearance_details;
DROP POLICY IF EXISTS "barangay_clearance_details_select_policy" ON barangay_clearance_details;

CREATE POLICY "barangay_clearance_details_insert_policy" 
ON barangay_clearance_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "barangay_clearance_details_select_policy" 
ON barangay_clearance_details FOR SELECT 
USING (true);

-- ============================================
-- BARANGAY_CERTIFICATION_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "barangay_certification_details_insert_policy" ON barangay_certification_details;
DROP POLICY IF EXISTS "barangay_certification_details_select_policy" ON barangay_certification_details;

CREATE POLICY "barangay_certification_details_insert_policy" 
ON barangay_certification_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "barangay_certification_details_select_policy" 
ON barangay_certification_details FOR SELECT 
USING (true);

-- ============================================
-- RESIDENCY_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "residency_details_insert_policy" ON residency_details;
DROP POLICY IF EXISTS "residency_details_select_policy" ON residency_details;

CREATE POLICY "residency_details_insert_policy" 
ON residency_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "residency_details_select_policy" 
ON residency_details FOR SELECT 
USING (true);

-- ============================================
-- INDIGENCY_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "indigency_details_insert_policy" ON indigency_details;
DROP POLICY IF EXISTS "indigency_details_select_policy" ON indigency_details;

CREATE POLICY "indigency_details_insert_policy" 
ON indigency_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "indigency_details_select_policy" 
ON indigency_details FOR SELECT 
USING (true);

-- ============================================
-- BUSINESS_CLOSURE_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "business_closure_details_insert_policy" ON business_closure_details;
DROP POLICY IF EXISTS "business_closure_details_select_policy" ON business_closure_details;

CREATE POLICY "business_closure_details_insert_policy" 
ON business_closure_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "business_closure_details_select_policy" 
ON business_closure_details FOR SELECT 
USING (true);

-- ============================================
-- JOB_SEEKER_DETAILS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "job_seeker_details_insert_policy" ON job_seeker_details;
DROP POLICY IF EXISTS "job_seeker_details_select_policy" ON job_seeker_details;

CREATE POLICY "job_seeker_details_insert_policy" 
ON job_seeker_details FOR INSERT 
WITH CHECK (true);

CREATE POLICY "job_seeker_details_select_policy" 
ON job_seeker_details FOR SELECT 
USING (true);

-- ============================================
-- BARANGAY_SETTINGS TABLE POLICIES
-- ============================================
DROP POLICY IF EXISTS "barangay_settings_insert_policy" ON barangay_settings;
DROP POLICY IF EXISTS "barangay_settings_select_policy" ON barangay_settings;
DROP POLICY IF EXISTS "barangay_settings_update_policy" ON barangay_settings;

CREATE POLICY "barangay_settings_insert_policy" 
ON barangay_settings FOR INSERT 
WITH CHECK (true);

CREATE POLICY "barangay_settings_select_policy" 
ON barangay_settings FOR SELECT 
USING (true);

CREATE POLICY "barangay_settings_update_policy" 
ON barangay_settings FOR UPDATE 
USING (true);

-- ============================================
-- STORAGE BUCKETS SETUP
-- ============================================
-- Create storage buckets if they don't exist
INSERT INTO storage.buckets (id, name, public) 
VALUES 
  ('id-photos', 'id-photos', true),
  ('selfie-photos', 'selfie-photos', true),
  ('payment-proofs', 'payment-proofs', true),
  ('logos', 'logos', true),
  ('signatures', 'signatures', true)
ON CONFLICT (id) DO NOTHING;

-- Allow public access to storage buckets
DROP POLICY IF EXISTS "public_storage_policy" ON storage.objects;
CREATE POLICY "public_storage_policy" 
ON storage.objects FOR SELECT 
USING (bucket_id IN ('id-photos', 'selfie-photos', 'payment-proofs', 'logos', 'signatures'));

DROP POLICY IF EXISTS "public_storage_upload_policy" ON storage.objects;
CREATE POLICY "public_storage_upload_policy" 
ON storage.objects FOR INSERT 
WITH CHECK (bucket_id IN ('id-photos', 'selfie-photos', 'payment-proofs', 'logos', 'signatures'));

DROP POLICY IF EXISTS "public_storage_update_policy" ON storage.objects;
CREATE POLICY "public_storage_update_policy" 
ON storage.objects FOR UPDATE 
USING (bucket_id IN ('id-photos', 'selfie-photos', 'payment-proofs', 'logos', 'signatures'));

-- ============================================
-- INITIAL BARANGAY SETTINGS
-- ============================================
-- Insert default settings if they don't exist
INSERT INTO barangay_settings (id, barangay_logo_filename, punong_barangay_signature_filename, secretary_signature_filename)
VALUES (1, '', '', '')
ON CONFLICT (id) DO NOTHING;
