-- Supabase Storage Setup for Threads Bot
-- Run this in your Supabase SQL Editor

-- =============================================================================
-- STEP 1: CREATE STORAGE BUCKET FOR IMAGES
-- =============================================================================

-- Create the images bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('images', 'images', true)
ON CONFLICT (id) DO NOTHING;

-- =============================================================================
-- STEP 2: CREATE STORAGE POLICIES
-- =============================================================================

-- Allow authenticated users to upload images
CREATE POLICY "Allow authenticated users to upload images" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'images' 
        AND auth.role() = 'authenticated'
    );

-- Allow authenticated users to view their own images
CREATE POLICY "Allow authenticated users to view own images" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'images' 
        AND auth.role() = 'authenticated'
    );

-- Allow authenticated users to update their own images
CREATE POLICY "Allow authenticated users to update own images" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'images' 
        AND auth.role() = 'authenticated'
    );

-- Allow authenticated users to delete their own images
CREATE POLICY "Allow authenticated users to delete own images" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'images' 
        AND auth.role() = 'authenticated'
    );

-- Allow service role to access all images
CREATE POLICY "Allow service role to access all images" ON storage.objects
    FOR ALL USING (
        bucket_id = 'images' 
        AND auth.role() = 'service_role'
    );

-- =============================================================================
-- STEP 3: VERIFICATION
-- =============================================================================

-- Check if bucket was created
SELECT * FROM storage.buckets WHERE id = 'images'; 