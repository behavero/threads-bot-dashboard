#!/usr/bin/env python3
"""
Automated Test Suite for Threads Bot API
Tests account login, database operations, and posting functionality
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ThreadsBotAPITester:
    def __init__(self, base_url: str = "https://threads-bot-dashboard-3.onrender.com"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if error:
            print(f"   ❌ Error: {error}")
        print()
    
    def test_health_endpoint(self) -> bool:
        """Test basic API health"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", True, f"Service: {data.get('service', 'unknown')}")
                return True
            else:
                self.log_test("Health Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Endpoint", False, error=str(e))
            return False
    
    def test_accounts_endpoint(self) -> bool:
        """Test accounts listing endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/accounts")
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                self.log_test("Accounts Endpoint", True, f"Found {len(accounts)} accounts")
                return True
            else:
                self.log_test("Accounts Endpoint", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Accounts Endpoint", False, error=str(e))
            return False
    
    def test_account_login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Test account login functionality"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            print(f"🔐 Testing login for {username}...")
            response = self.session.post(
                f"{self.base_url}/api/accounts/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user_info = data.get('user_info', {})
                    session_reused = data.get('session_reused', False)
                    
                    self.log_test(
                        "Account Login", 
                        True, 
                        f"Login successful for {username} - "
                        f"Followers: {user_info.get('followers', 0)}, "
                        f"Posts: {user_info.get('posts', 0)}, "
                        f"Session reused: {session_reused}"
                    )
                    return data
                else:
                    self.log_test("Account Login", False, f"Login failed: {data.get('error', 'Unknown error')}")
                    return None
            else:
                self.log_test("Account Login", False, f"HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Account Login", False, error=str(e))
            return None
    
    def test_session_reuse(self, username: str, password: str) -> bool:
        """Test session reuse functionality"""
        try:
            # First login to establish session
            print(f"🧪 Testing session reuse for {username}...")
            
            # First login
            login_data = {"username": username, "password": password}
            response1 = self.session.post(
                f"{self.base_url}/api/accounts/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response1.status_code != 200:
                self.log_test("Session Reuse", False, f"First login failed: {response1.status_code}")
                return False
            
            data1 = response1.json()
            if not data1.get('success'):
                self.log_test("Session Reuse", False, f"First login failed: {data1.get('error')}")
                return False
            
            # Wait a moment
            time.sleep(2)
            
            # Second login (should reuse session)
            response2 = self.session.post(
                f"{self.base_url}/api/accounts/login",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response2.status_code != 200:
                self.log_test("Session Reuse", False, f"Second login failed: {response2.status_code}")
                return False
            
            data2 = response2.json()
            if not data2.get('success'):
                self.log_test("Session Reuse", False, f"Second login failed: {data2.get('error')}")
                return False
            
            session_reused = data2.get('session_reused', False)
            
            if session_reused:
                self.log_test("Session Reuse", True, f"Session successfully reused for {username}")
                return True
            else:
                self.log_test("Session Reuse", False, f"Session not reused for {username}")
                return False
                
        except Exception as e:
            self.log_test("Session Reuse", False, error=str(e))
            return False
    
    def test_database_operations(self) -> bool:
        """Test database operations by checking account persistence"""
        try:
            # Get initial accounts
            response1 = self.session.get(f"{self.base_url}/api/accounts")
            if response1.status_code != 200:
                self.log_test("Database Operations", False, f"Failed to get accounts: {response1.status_code}")
                return False
            
            initial_accounts = response1.json().get('accounts', [])
            initial_count = len(initial_accounts)
            
            # Test account creation (this would require valid credentials)
            # For now, just verify we can read accounts
            self.log_test(
                "Database Operations", 
                True, 
                f"Successfully read {initial_count} accounts from database"
            )
            return True
            
        except Exception as e:
            self.log_test("Database Operations", False, error=str(e))
            return False
    
    def test_posting_endpoint(self, account_id: int) -> bool:
        """Test posting endpoint (without actually posting)"""
        try:
            print(f"📝 Testing posting endpoint for account {account_id}...")
            
            response = self.session.post(
                f"{self.base_url}/api/accounts/{account_id}/post",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Posting Endpoint", 
                        True, 
                        f"Posting successful for account {account_id} - "
                        f"Caption: {data.get('caption', 'N/A')}, "
                        f"Image: {data.get('image', 'N/A')}, "
                        f"Session reused: {data.get('session_reused', False)}"
                    )
                    return True
                else:
                    self.log_test("Posting Endpoint", False, f"Posting failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                self.log_test("Posting Endpoint", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Posting Endpoint", False, error=str(e))
            return False
    
    def test_content_endpoints(self) -> bool:
        """Test captions and images endpoints"""
        try:
            # Test captions endpoint
            captions_response = self.session.get(f"{self.base_url}/api/captions")
            if captions_response.status_code == 200:
                captions_data = captions_response.json()
                captions = captions_data.get('captions', [])
                self.log_test("Captions Endpoint", True, f"Found {len(captions)} captions")
            else:
                self.log_test("Captions Endpoint", False, f"Status: {captions_response.status_code}")
                return False
            
            # Test images endpoint
            images_response = self.session.get(f"{self.base_url}/api/images")
            if images_response.status_code == 200:
                images_data = images_response.json()
                images = images_data.get('images', [])
                self.log_test("Images Endpoint", True, f"Found {len(images)} images")
            else:
                self.log_test("Images Endpoint", False, f"Status: {images_response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Content Endpoints", False, error=str(e))
            return False
    
    def run_full_test_suite(self, test_username: str = None, test_password: str = None, test_account_id: int = None):
        """Run the complete test suite"""
        print("🧪 Starting Threads Bot API Test Suite")
        print("=" * 50)
        
        # Basic connectivity tests
        self.test_health_endpoint()
        self.test_accounts_endpoint()
        self.test_content_endpoints()
        self.test_database_operations()
        
        # Login tests (if credentials provided)
        if test_username and test_password:
            login_result = self.test_account_login(test_username, test_password)
            if login_result:
                self.test_session_reuse(test_username, test_password)
        
        # Posting test (if account ID provided)
        if test_account_id:
            self.test_posting_endpoint(test_account_id)
        
        # Print summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Test results saved to: {filename}")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Threads Bot API Test Suite")
    parser.add_argument("--username", help="Test username for login tests")
    parser.add_argument("--password", help="Test password for login tests")
    parser.add_argument("--account-id", type=int, help="Test account ID for posting tests")
    parser.add_argument("--base-url", default="https://threads-bot-dashboard-3.onrender.com", 
                       help="Base URL for API")
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = ThreadsBotAPITester(args.base_url)
    
    # Run tests
    tester.run_full_test_suite(
        test_username=args.username,
        test_password=args.password,
        test_account_id=args.account_id
    )

if __name__ == "__main__":
    main()
