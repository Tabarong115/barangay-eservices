-- Migration: Add staff_users table for secure authentication
-- This migration replaces the pilot-only in-memory authentication with proper database-backed authentication
-- with password hashing using bcrypt

-- Create staff_users table
CREATE TABLE IF NOT EXISTS staff_users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- bcrypt hash
    role VARCHAR(50) NOT NULL, -- 'Secretary', 'Treasurer', 'Punong Barangay'
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT valid_role CHECK (role IN ('Secretary', 'Treasurer', 'Punong Barangay'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_staff_users_username ON staff_users(username);
CREATE INDEX IF NOT EXISTS idx_staff_users_role ON staff_users(role);

-- Insert default staff accounts (passwords will be hashed by the application)
-- These are placeholder records - the actual hashed passwords will be set by the app
-- Passwords should be changed immediately after first login
INSERT INTO staff_users (username, password_hash, role)
VALUES
    ('secretary', '$2b$12$PLACEHOLDER_HASH_SECRETARY', 'Secretary'),
    ('treasurer', '$2b$12$PLACEHOLDER_HASH_TREASURER', 'Treasurer'),
    ('chairman', '$2b$12$PLACEHOLDER_HASH_CHAIRMAN', 'Punong Barangay')
ON CONFLICT (username) DO NOTHING;

-- Create trigger for updated_at
CREATE TRIGGER update_staff_users_updated_at BEFORE UPDATE ON staff_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Note: The placeholder hashes above will be replaced with actual bcrypt hashes
-- by the application when it first runs with the new authentication system.
-- Default passwords (to be changed immediately):
-- - Secretary: secretary-test
-- - Treasurer: treasurer-test
-- - Punong Barangay: chairman-test
