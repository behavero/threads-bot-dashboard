# Row Level Security (RLS) Setup for Threads Bot

This document outlines the complete Row Level Security implementation for the Threads Bot application using Supabase.

## 📋 Overview

Row Level Security (RLS) ensures that users can only access their own data, providing complete data isolation between users. This implementation uses Supabase Auth with user-specific data access.

## 🗄️ Database Schema

### Tables with RLS Enabled

1. **`accounts`** - Threads accounts for each user
2. **`captions`** - User-uploaded captions
3. **`images`** - User-uploaded images
4. **`posting_history`** - Posting history linked to accounts
5. **`daily_engagement`** - Engagement data linked to accounts

### User ID References

All tables include a `user_id` column that references `auth.users(id)`:

```sql
user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE
```

## 🔐 RLS Policies

### Accounts Table Policies

```sql
-- Users can only access their own accounts
CREATE POLICY "Users can view own accounts" ON accounts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own accounts" ON accounts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own accounts" ON accounts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own accounts" ON accounts
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all accounts (for backend operations)
CREATE POLICY "Service role can access all accounts" ON accounts
    FOR ALL USING (auth.role() = 'service_role');
```

### Captions Table Policies

```sql
-- Users can only access their own captions
CREATE POLICY "Users can view own captions" ON captions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own captions" ON captions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own captions" ON captions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own captions" ON captions
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all captions (for backend operations)
CREATE POLICY "Service role can access all captions" ON captions
    FOR ALL USING (auth.role() = 'service_role');
```

### Images Table Policies

```sql
-- Users can only access their own images
CREATE POLICY "Users can view own images" ON images
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own images" ON images
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own images" ON images
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own images" ON images
    FOR DELETE USING (auth.uid() = user_id);

-- Service role can access all images (for backend operations)
CREATE POLICY "Service role can access all images" ON images
    FOR ALL USING (auth.role() = 'service_role');
```

### Posting History Table Policies

```sql
-- Users can only access posting history for their own accounts
CREATE POLICY "Users can view own posting history" ON posting_history
    FOR SELECT USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can insert own posting history" ON posting_history
    FOR INSERT WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can update own posting history" ON posting_history
    FOR UPDATE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

CREATE POLICY "Users can delete own posting history" ON posting_history
    FOR DELETE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = posting_history.account_id
        )
    );

-- Service role can access all posting history (for backend operations)
CREATE POLICY "Service role can access all posting history" ON posting_history
    FOR ALL USING (auth.role() = 'service_role');
```

### Daily Engagement Table Policies

```sql
-- Users can only access engagement data for their own accounts
CREATE POLICY "Users can view own engagement data" ON daily_engagement
    FOR SELECT USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can insert own engagement data" ON daily_engagement
    FOR INSERT WITH CHECK (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can update own engagement data" ON daily_engagement
    FOR UPDATE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

CREATE POLICY "Users can delete own engagement data" ON daily_engagement
    FOR DELETE USING (
        auth.uid() = (
            SELECT user_id FROM accounts 
            WHERE accounts.id = daily_engagement.account_id
        )
    );

-- Service role can access all engagement data (for backend operations)
CREATE POLICY "Service role can access all engagement data" ON daily_engagement
    FOR ALL USING (auth.role() = 'service_role');
```

## 🚀 Deployment Steps

### 1. Run the Schema Migration

Execute the `server/init_schema.sql` file to create tables with proper user references:

```bash
# Connect to your Supabase database and run:
\i server/init_schema.sql
```

### 2. Apply RLS Policies

Execute the `server/rls_policies.sql` file to enable RLS and create policies:

```bash
# Connect to your Supabase database and run:
\i server/rls_policies.sql
```

### 3. Verify Policies

Run the verification query to ensure all policies are created:

```sql
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;
```

## 🔧 Frontend Integration

### API Routes

All API routes now require authentication and automatically include the user_id:

```typescript
// Example: Creating a caption
const user = await requireAuth(request)
const [data] = await sql`
  INSERT INTO captions (user_id, text, created_at)
  VALUES (${user.id}, ${caption.trim()}, ${new Date().toISOString()})
  RETURNING *
`
```

### Automatic Filtering

RLS automatically filters queries by user_id, so you don't need to add WHERE clauses:

```typescript
// This will automatically only return the current user's captions
const captions = await sql`SELECT * FROM captions ORDER BY created_at DESC`
```

## 🛡️ Security Benefits

1. **Data Isolation** - Users can only see their own data
2. **Automatic Filtering** - No need to manually add user_id filters
3. **Service Role Access** - Backend can access all data for operations
4. **Cascade Deletes** - When a user is deleted, all their data is removed
5. **Audit Trail** - All operations are tied to specific users

## 🔍 Testing

### Test User Isolation

1. Create two test users
2. Add data for each user
3. Verify each user only sees their own data
4. Verify service role can see all data

### Test Service Role Access

```typescript
// Backend operations should work with service role
const backendDb = new DatabaseManager() // Uses service role
const allAccounts = backendDb.get_active_accounts() // Should return all accounts
```

## 📊 Performance Considerations

### Indexes

The following indexes are created for optimal performance:

```sql
CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_captions_user_id ON captions(user_id);
CREATE INDEX idx_images_user_id ON images(user_id);
```

### Query Optimization

- RLS policies are automatically optimized by PostgreSQL
- Complex policies (like posting_history) use subqueries efficiently
- Service role bypasses RLS for backend operations

## 🚨 Important Notes

1. **Service Role Required** - Backend operations need service role access
2. **User ID Required** - All inserts must include user_id
3. **Cascade Deletes** - Deleting a user removes all their data
4. **Policy Names** - Policy names must be unique across the database
5. **Testing** - Always test with multiple users to verify isolation

## 🔧 Troubleshooting

### Common Issues

1. **"Row Level Security policy violation"** - Check if user_id is being set correctly
2. **"Policy does not exist"** - Ensure all policies are created
3. **"Service role access denied"** - Verify backend is using service role key

### Debug Queries

```sql
-- Check if RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- Check all policies
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Test user access
SELECT auth.uid() as current_user;
```

## 📝 Migration Notes

When migrating existing data:

1. Add user_id columns to existing tables
2. Update existing records with appropriate user_id values
3. Enable RLS after data migration
4. Test thoroughly with multiple users

This RLS implementation provides complete data security and isolation for the Threads Bot application. 