# Supabase Setup Guide for Barangay e-Services Portal

## Database Setup

1. **Create a Supabase Project**
   - Go to [supabase.com](https://supabase.com) and create a new project
   - Wait for the project to be fully provisioned

2. **Run the Database Schema**
   - In Supabase Dashboard, go to SQL Editor
   - Copy and execute the contents of `database/schema.sql`
   - This will create all necessary tables for the 6 services

3. **Configure Environment Variables**
   - Copy your Supabase project URL and anon key from Project Settings > API
   - Add them to your `.env` file:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-public-anon-key
   ```

## Storage Setup

1. **Create Storage Buckets**
   - In Supabase Dashboard, go to Storage
   - Create the following buckets with public access:
     - `id-photos` - For applicant ID photos
     - `selfie-photos` - For selfie verification photos
     - `payment-proofs` - For GCash payment screenshots
     - `barangay-assets` - For barangay logo and signatures

2. **Configure Bucket Policies**
   - For each bucket, ensure public read access is enabled
   - Set appropriate upload policies for authenticated users

3. **Update Storage Bucket Names in Code**
   - If you use different bucket names, update them in `database.py`

## Testing the Connection

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Test Database Connection**
   - Submit a test request through the web interface
   - Check Supabase Dashboard > Table Editor to verify data was stored
   - Check Storage to verify image uploads

## Migration from Local Storage

The application now supports both local file storage and Supabase Storage:
- When Supabase is configured, it automatically uses Supabase for data and images
- When Supabase is not configured, it falls back to local in-memory storage
- No code changes needed - the transition is automatic based on environment configuration

## Security Notes

- Never commit your `.env` file to version control
- Use Row Level Security (RLS) policies in Supabase for production
- Keep your service_role key private and never use it in client-side code
- Consider implementing Supabase Auth for staff authentication in production