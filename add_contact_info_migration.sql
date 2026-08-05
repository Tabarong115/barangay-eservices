-- Migration: Add Contact Information and Treasurer Fields to Barangay Settings
-- This adds contact number, email, Facebook fields, and Treasurer information
-- Run this in your Supabase SQL Editor

-- ============================================
-- STEP 1: Add new columns to barangay_settings table
-- ============================================

-- Contact information columns
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS contact_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(100),
ADD COLUMN IF NOT EXISTS contact_facebook VARCHAR(255);

-- Official names columns
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS punong_barangay_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS secretary_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS treasurer_name VARCHAR(100);

-- Treasurer signature and GCash QR code columns
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS treasurer_signature_filename VARCHAR(255),
ADD COLUMN IF NOT EXISTS gcash_qr_filename VARCHAR(255);

-- ============================================
-- STEP 2: Update existing row with empty values
-- ============================================

UPDATE barangay_settings 
SET 
    contact_number = COALESCE(contact_number, ''),
    contact_email = COALESCE(contact_email, ''),
    contact_facebook = COALESCE(contact_facebook, ''),
    punong_barangay_name = COALESCE(punong_barangay_name, ''),
    secretary_name = COALESCE(secretary_name, ''),
    treasurer_name = COALESCE(treasurer_name, ''),
    treasurer_signature_filename = COALESCE(treasurer_signature_filename, ''),
    gcash_qr_filename = COALESCE(gcash_qr_filename, '')
WHERE id IS NOT NULL;

-- ============================================
-- STEP 3: Create storage bucket for GCash QR codes
-- ============================================
-- NOTE: Storage buckets must be created manually in Supabase Storage dashboard
-- 
-- MANUAL STEPS:
-- 1. Go to Supabase Dashboard → Storage
-- 2. Click "Create a new bucket"
-- 3. Bucket name: "qrcodes" (must be exactly this)
-- 4. Make bucket Public: YES (enable public access)
-- 5. File size limit: 5MB (or as needed)
-- 6. Allowed MIME types: image/jpeg, image/png
-- 7. Click "Create bucket"
-- 
-- After creating the bucket, set up RLS policies:
-- insert into storage.buckets (id, name, public) values ('qrcodes', 'qrcodes', true);

-- ============================================
-- STEP 4: Create RLS policies for qrcodes bucket
-- ============================================

-- Allow public read access to QR codes (needed for payment form display)
CREATE POLICY "Allow public read access to qrcodes"
ON storage.objects FOR SELECT
TO public
USING ( bucket_id = 'qrcodes' );

-- Allow authenticated users to upload QR codes
CREATE POLICY "Allow authenticated upload to qrcodes"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK ( bucket_id = 'qrcodes' );

-- Allow authenticated users to delete QR codes
CREATE POLICY "Allow authenticated delete from qrcodes"
ON storage.objects FOR DELETE
TO authenticated
USING ( bucket_id = 'qrcodes' );

-- ============================================
-- VERIFICATION QUERY
-- ============================================
-- Run this to verify the migration was successful:
-- SELECT * FROM barangay_settings;