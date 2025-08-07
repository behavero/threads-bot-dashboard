# Threads Bot API Testing Guide

This guide explains how to run automated tests to verify the Threads Bot API functionality.

## 🧪 Test Scripts Overview

### 1. `quick_test.py` - Basic API Verification
Quick tests for basic endpoint functionality without requiring real credentials.

### 2. `test_database.py` - Database Operations Testing
Tests Supabase database operations and connectivity.

### 3. `test_api.py` - Comprehensive API Testing
Full test suite with login and posting verification (requires real credentials).

## 🚀 Quick Start

### Basic API Tests (No Credentials Required)
```bash
cd server
python quick_test.py
```

### Database Tests
```bash
cd server
python test_database.py
```

### Full API Tests (Requires Real Credentials)
```bash
cd server
python test_api.py --username your_username --password your_password --account-id 1
```

## 📋 Test Coverage

### ✅ Quick Tests (`quick_test.py`)
- Health endpoint connectivity
- Accounts listing
- Captions retrieval
- Images retrieval
- Login endpoint (with test credentials)

### ✅ Database Tests (`test_database.py`)
- Database connection
- Account operations (CRUD)
- Content operations (captions/images)
- Session data operations
- Posting history

### ✅ Full API Tests (`test_api.py`)
- All quick tests
- Real account login verification
- Session reuse testing
- Posting endpoint testing
- Comprehensive error handling

## 🎯 What Each Test Verifies

### Account Login Tests
```python
# Tests login functionality
test_account_login(username, password)

# Tests session reuse
test_session_reuse(username, password)
```

**Verifies:**
- ✅ Account credentials work with Threads API
- ✅ Session data is saved to Supabase
- ✅ Session reuse works correctly
- ✅ Last login timestamps are updated

### Database Operations Tests
```python
# Tests account persistence
test_database_operations()

# Tests session storage
test_session_operations()
```

**Verifies:**
- ✅ Accounts are saved to Supabase
- ✅ Session data is stored and retrieved
- ✅ Database connection is stable
- ✅ CRUD operations work correctly

### Posting Tests
```python
# Tests posting functionality
test_posting_endpoint(account_id)
```

**Verifies:**
- ✅ Posting endpoint triggers Threads posts
- ✅ Content selection works (captions/images)
- ✅ Session reuse during posting
- ✅ Posting history is recorded

## 📊 Test Results

All tests generate detailed reports:

### Console Output
```
🧪 Starting Threads Bot API Test Suite
==================================================
✅ PASS Health Endpoint
   📝 Service: threads-bot

✅ PASS Accounts Endpoint
   📝 Found 3 accounts

✅ PASS Account Login
   📝 Login successful for testuser - Followers: 150, Posts: 25, Session reused: False

✅ PASS Session Reuse
   📝 Session successfully reused for testuser
```

### JSON Report
Tests save detailed results to `test_results_YYYYMMDD_HHMMSS.json`:

```json
{
  "test": "Account Login",
  "success": true,
  "details": "Login successful for testuser - Followers: 150, Posts: 25",
  "error": "",
  "timestamp": "2025-08-07T10:30:00"
}
```

## 🔧 Test Configuration

### Environment Variables
Tests use the same environment variables as the main application:
- `SUPABASE_URL`
- `SUPABASE_KEY`

### Test Credentials
For full testing, you need:
- Real Threads username/password
- Account ID from your database

### Command Line Options
```bash
# Test with specific credentials
python test_api.py --username myuser --password mypass --account-id 1

# Test against different API URL
python test_api.py --base-url http://localhost:5000

# Quick tests only
python quick_test.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `SUPABASE_URL` and `SUPABASE_KEY`
   - Verify Supabase project is active

2. **Login Tests Fail**
   - Verify Threads credentials are correct
   - Check if account has 2FA enabled
   - Ensure account is not locked

3. **Posting Tests Fail**
   - Verify account has posting permissions
   - Check if captions/images exist in database
   - Ensure account is not rate-limited

### Debug Mode
Add debug logging to any test:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Continuous Testing

### Automated Testing
Run tests in CI/CD pipeline:
```bash
# Install dependencies
pip install requests

# Run tests
python test_api.py --username $TEST_USERNAME --password $TEST_PASSWORD
```

### Scheduled Testing
Set up cron job for regular testing:
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/server && python quick_test.py >> test_logs.txt
```

## 🎯 Test Scenarios

### Scenario 1: New Account Setup
1. Add account via API
2. Verify account saved to database
3. Test login functionality
4. Verify session data saved
5. Test posting capability

### Scenario 2: Session Management
1. Login with existing account
2. Verify session reuse
3. Test posting with reused session
4. Verify last_login updated

### Scenario 3: Content Management
1. Add captions/images
2. Test content retrieval
3. Test unused content selection
4. Verify content marking as used

## 📝 Adding New Tests

To add a new test:

1. **Create test function:**
```python
def test_new_feature(self) -> bool:
    """Test new feature functionality"""
    try:
        # Test implementation
        return True
    except Exception as e:
        self.log_test("New Feature", False, error=str(e))
        return False
```

2. **Add to test suite:**
```python
def run_full_test_suite(self):
    # ... existing tests ...
    self.test_new_feature()
```

3. **Update documentation:**
- Add test description to this guide
- Update test coverage list
- Add troubleshooting steps if needed

## 🏆 Success Criteria

Tests are considered successful when:
- ✅ All endpoints respond correctly
- ✅ Database operations complete successfully
- ✅ Login functionality works with real credentials
- ✅ Session reuse works as expected
- ✅ Posting triggers actual Threads posts
- ✅ Error handling works correctly

## 📞 Support

If tests fail:
1. Check the error messages in console output
2. Review the JSON test report
3. Verify environment variables
4. Check Supabase dashboard for errors
5. Test with different credentials if needed
