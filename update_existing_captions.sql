-- Update existing captions to have default values for missing columns
-- Run this in your Supabase SQL editor to fix the manually added captions

-- Update captions that have NULL category to 'general'
UPDATE captions 
SET category = 'general' 
WHERE category IS NULL;

-- Update captions that have NULL tags to empty array
UPDATE captions 
SET tags = '{}' 
WHERE tags IS NULL;

-- Update captions that have NULL updated_at to created_at
UPDATE captions 
SET updated_at = created_at 
WHERE updated_at IS NULL;

-- Verify the updates
SELECT 
  id,
  text,
  COALESCE(category, 'general') as category,
  COALESCE(tags, '{}') as tags,
  used,
  created_at,
  COALESCE(updated_at, created_at) as updated_at
FROM captions 
ORDER BY created_at DESC
LIMIT 10; 