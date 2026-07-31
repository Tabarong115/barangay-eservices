-- Supabase Database Schema for Barangay e-Services Portal
-- This schema supports all 6 Version 1 services with proper normalization

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Common table for all service requests with shared fields
CREATE TABLE service_requests (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    reference_number VARCHAR(20) UNIQUE NOT NULL,
    service_type VARCHAR(50) NOT NULL, -- 'barangay_clearance', 'barangay_certification', etc.
    
    -- Common applicant information
    full_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    sex_at_birth VARCHAR(20) NOT NULL,
    gender VARCHAR(50) NOT NULL,
    birthday DATE NOT NULL,
    civil_status VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    
    -- File references
    id_photo_filename VARCHAR(255),
    selfie_photo_filename VARCHAR(255),
    payment_proof_filename VARCHAR(255),
    
    -- Payment information
    payment_reference VARCHAR(100),
    
    -- Workflow status
    status VARCHAR(30) DEFAULT 'pending', -- 'pending', 'secretary_reviewed', 'treasurer_verified', 'chairman_approved', 'completed', 'rejected'
    secretary_notes TEXT,
    treasurer_notes TEXT,
    chairman_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for common queries
    CONSTRAINT valid_service_type CHECK (service_type IN (
        'barangay_clearance', 
        'barangay_certification', 
        'certificate_of_residency', 
        'certificate_of_indigency', 
        'business_closure', 
        'first_time_job_seeker'
    )),
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 
        'secretary_reviewed', 
        'treasurer_verified', 
        'chairman_approved', 
        'completed', 
        'rejected'
    ))
);

-- Service-specific tables for unique fields

-- Barangay Clearance specific fields
CREATE TABLE barangay_clearance_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
    UNIQUE(service_request_id)
);

-- Barangay Certification specific fields
CREATE TABLE barangay_certification_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    purpose TEXT NOT NULL,
    UNIQUE(service_request_id)
);

-- Certificate of Residency specific fields
CREATE TABLE residency_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    years_resided INTEGER NOT NULL,
    months_resided INTEGER NOT NULL,
    UNIQUE(service_request_id)
);

-- Certificate of Indigency specific fields
CREATE TABLE indigency_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    family_size INTEGER NOT NULL,
    monthly_income DECIMAL(10,2) NOT NULL,
    UNIQUE(service_request_id)
);

-- Business Closure specific fields
CREATE TABLE business_closure_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    business_name VARCHAR(100) NOT NULL,
    business_address TEXT NOT NULL,
    closure_reason TEXT NOT NULL,
    UNIQUE(service_request_id)
);

-- First Time Job Seeker specific fields
CREATE TABLE job_seeker_details (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_request_id UUID REFERENCES service_requests(id) ON DELETE CASCADE,
    oath_of_undertaking TEXT NOT NULL,
    UNIQUE(service_request_id)
);

-- Settings table for barangay logo and signatures
CREATE TABLE barangay_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    barangay_logo_filename VARCHAR(255),
    punong_barangay_signature_filename VARCHAR(255),
    secretary_signature_filename VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_service_requests_reference ON service_requests(reference_number);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_service_type ON service_requests(service_type);
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at DESC);

-- Insert default settings row
INSERT INTO barangay_settings (barangay_logo_filename, punong_barangay_signature_filename, secretary_signature_filename)
VALUES ('', '', '');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_service_requests_updated_at BEFORE UPDATE ON service_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_barangay_settings_updated_at BEFORE UPDATE ON barangay_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();