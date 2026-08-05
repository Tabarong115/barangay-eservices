-- Migration: Add Contact Information Fields to Barangay Settings
-- This adds contact number, email, and Facebook fields for Citizens' Charter display
-- Run this in your Supabase SQL Editor

-- Add new columns to barangay_settings table
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS contact_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(100),
ADD COLUMN IF NOT EXISTS contact_facebook VARCHAR(255);

-- Add official names columns if they don't exist (for completeness)
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS punong_barangay_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS secretary_name VARCHAR(100);

-- Update the existing row with empty values if columns were just added
UPDATE barangay_settings 
SET 
    contact_number = COALESCE(contact_number, ''),
    contact_email = COALESCE(contact_email, ''),
    contact_facebook = COALESCE(contact_facebook, ''),
    punong_barangay_name = COALESCE(punong_barangay_name, ''),
    secretary_name = COALESCE(secretary_name, '')
WHERE id IS NOT NULL;