"""Test script to verify Supabase connection and configuration."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Supabase Connection Test ===")
print()

# Check if .env file exists
if os.path.exists('.env'):
    print("[OK] .env file exists")
else:
    print("[ERROR] .env file does NOT exist")

print()

# Check environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY: {supabase_key[:20]}...{supabase_key[-10:] if supabase_key else 'None'}")
print()

# Check if they're configured
if supabase_url and supabase_key:
    print("[OK] Environment variables are set")
else:
    print("[ERROR] Environment variables are NOT set")
    if not supabase_url:
        print("   - SUPABASE_URL is missing")
    if not supabase_key:
        print("   - SUPABASE_ANON_KEY is missing")

print()

# Try to create Supabase client
try:
    from supabase import create_client
    print("[OK] supabase package is installed")
    
    if supabase_url and supabase_key:
        print("Attempting to create Supabase client...")
        client = create_client(supabase_url, supabase_key)
        print("[OK] Supabase client created successfully")
        
        # Test a simple query
        print("Testing database connection...")
        try:
            result = client.table('service_requests').select('count').execute()
            print(f"[OK] Database connection successful! Found {result.count} service requests")
        except Exception as e:
            print(f"[ERROR] Database query failed: {e}")
    else:
        print("[ERROR] Cannot create client - missing credentials")
        
except ImportError as e:
    print(f"[ERROR] supabase package not installed: {e}")
except Exception as e:
    print(f"[ERROR] Error creating Supabase client: {e}")

print()
print("=== Test Complete ===")