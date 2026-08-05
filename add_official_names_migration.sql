-- Migration: Add official names to barangay_settings table
-- Run this in your Supabase SQL Editor to add Punong Barangay and Secretary name fields

-- Add columns for official names
ALTER TABLE barangay_settings 
ADD COLUMN IF NOT EXISTS punong_barangay_name TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS secretary_name TEXT DEFAULT '';

-- Update existing settings row with default values if needed
UPDATE barangay_settings 
SET punong_barangay_name = COALESCE(punong_barangay_name, ''),
    secretary_name = COALESCE(secretary_name, '');
