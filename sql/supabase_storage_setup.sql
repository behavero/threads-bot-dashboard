-- Supabase Storage Setup for Threads Bot
-- This script sets up the storage bucket and policies for image uploads

-- 1. Create the images bucket (if it doesn't exist)
-- Note: This needs to be done via Supabase Dashboard or API
-- Bucket name: 'images'
-- Public bucket: true
-- File size limit: 50MB
-- Allowed MIME types: image/*

-- 2. Create storage policies for the images bucket

-- Policy: Allow authenticated users to upload images
CREATE POLICY "Allow authenticated users to upload images" ON storage.objects
FOR INSERT WITH CHECK (
  bucket_id = 'images' AND
  auth.role() = 'authenticated'
);

-- Policy: Allow users to view their own uploaded images
CREATE POLICY "Allow users to view their own images" ON storage.objects
FOR SELECT USING (
  bucket_id = 'images' AND
  auth.role() = 'authenticated'
);

-- Policy: Allow users to update their own uploaded images
CREATE POLICY "Allow users to update their own images" ON storage.objects
FOR UPDATE USING (
  bucket_id = 'images' AND
  auth.role() = 'authenticated'
);

-- Policy: Allow users to delete their own uploaded images
CREATE POLICY "Allow users to delete their own images" ON storage.objects
FOR DELETE USING (
  bucket_id = 'images' AND
  auth.role() = 'authenticated'
);

-- 3. Enable RLS on storage.objects (if not already enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 4. Create a function to get user's images
CREATE OR REPLACE FUNCTION get_user_images(user_uuid UUID)
RETURNS TABLE (
  id UUID,
  name TEXT,
  bucket_id TEXT,
  owner UUID,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ,
  last_accessed_at TIMESTAMPTZ,
  metadata JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    o.id,
    o.name,
    o.bucket_id,
    o.owner,
    o.created_at,
    o.updated_at,
    o.last_accessed_at,
    o.metadata
  FROM storage.objects o
  WHERE o.bucket_id = 'images' 
    AND o.owner = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Grant necessary permissions
GRANT USAGE ON SCHEMA storage TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON storage.objects TO authenticated;

-- 6. Create a trigger to automatically set owner on insert
CREATE OR REPLACE FUNCTION set_storage_object_owner()
RETURNS TRIGGER AS $$
BEGIN
  NEW.owner = auth.uid();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger (only if it doesn't exist)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger 
    WHERE tgname = 'set_storage_object_owner_trigger'
  ) THEN
    CREATE TRIGGER set_storage_object_owner_trigger
      BEFORE INSERT ON storage.objects
      FOR EACH ROW
      EXECUTE FUNCTION set_storage_object_owner();
  END IF;
END $$; 