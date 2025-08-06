-- Fix RLS policies for images table
-- Run this in your Supabase SQL editor

-- First, drop any existing policies on the images table
DROP POLICY IF EXISTS "Enable read access for all users" ON images;
DROP POLICY IF EXISTS "Enable insert for all users" ON images;
DROP POLICY IF EXISTS "Enable update for all users" ON images;
DROP POLICY IF EXISTS "Enable delete for all users" ON images;

-- Create new policies with proper syntax
CREATE POLICY "Enable read access for all users" ON images
FOR SELECT TO public USING (true);

CREATE POLICY "Enable insert for all users" ON images
FOR INSERT TO public WITH CHECK (true);

CREATE POLICY "Enable update for all users" ON images
FOR UPDATE TO public USING (true) WITH CHECK (true);

CREATE POLICY "Enable delete for all users" ON images
FOR DELETE TO public USING (true);

-- Verify the policies were created
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename = 'images'; 