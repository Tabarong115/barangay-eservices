"""Test script for Facebook Messenger notifications."""

import os
from dotenv import load_dotenv
from facebook_notifier import facebook_notifier

load_dotenv()

def test_facebook_configuration():
    """Test if Facebook credentials are properly configured."""
    print("=== Testing Facebook Configuration ===")
    print(f"Page Access Token: {'✓ Configured' if os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN') else '✗ Missing'}")
    print(f"Page ID: {'✓ Configured' if os.getenv('FACEBOOK_PAGE_ID') else '✗ Missing'}")
    print(f"App ID: {'✓ Configured' if os.getenv('FACEBOOK_APP_ID') else '✗ Missing'}")
    print(f"App Secret: {'✓ Configured' if os.getenv('FACEBOOK_APP_SECRET') else '✗ Missing'}")
    print(f"Staff Group ID: {'✓ Configured' if os.getenv('FACEBOOK_STAFF_GROUP_ID') else '✗ Missing'}")
    print(f"Staff User IDs: {'✓ Configured' if os.getenv('FACEBOOK_STAFF_USER_IDS') else '✗ Missing'}")
    print(f"\nFacebook Notifier Ready: {'✓ Yes' if facebook_notifier.is_configured() else '✗ No'}")
    return facebook_notifier.is_configured()

def test_new_request_notification():
    """Test notification for new service request."""
    print("\n=== Testing New Request Notification ===")
    
    test_request = {
        "service_type": "barangay_clearance",
        "reference_number": "TEST-20240806-001",
        "full_name": "Test Citizen",
        "contact_number": "09123456789"
    }
    
    print(f"Sending test notification for request: {test_request['reference_number']}")
    result = facebook_notifier.notify_new_request(test_request)
    print(f"Result: {'✓ Success' if result else '✗ Failed'}")
    return result

def test_status_change_notification():
    """Test notification for status change."""
    print("\n=== Testing Status Change Notification ===")
    
    test_request = {
        "service_type": "barangay_clearance",
        "reference_number": "TEST-20240806-001",
        "full_name": "Test Citizen"
    }
    
    print(f"Sending test status change notification")
    result = facebook_notifier.notify_status_change(test_request, "pending", "secretary_reviewed")
    print(f"Result: {'✓ Success' if result else '✗ Failed'}")
    return result

def test_payment_notification():
    """Test notification for payment submission."""
    print("\n=== Testing Payment Notification ===")
    
    test_request = {
        "service_type": "barangay_clearance",
        "reference_number": "TEST-20240806-001",
        "full_name": "Test Citizen"
    }
    
    print(f"Sending test payment notification")
    result = facebook_notifier.notify_payment_submitted(test_request)
    print(f"Result: {'✓ Success' if result else '✗ Failed'}")
    return result

def test_approval_notification():
    """Test notification for request approval."""
    print("\n=== Testing Approval Notification ===")
    
    test_request = {
        "service_type": "barangay_clearance",
        "reference_number": "TEST-20240806-001",
        "full_name": "Test Citizen"
    }
    
    print(f"Sending test approval notification")
    result = facebook_notifier.notify_approval(test_request)
    print(f"Result: {'✓ Success' if result else '✗ Failed'}")
    return result

if __name__ == "__main__":
    print("Facebook Messenger Notification Test Suite")
    print("=" * 50)
    
    # Test configuration first
    if not test_facebook_configuration():
        print("\n❌ Facebook credentials not configured. Please set up your .env file first.")
        print("See .env.example for required environment variables.")
        exit(1)
    
    # Ask user if they want to proceed with tests
    print("\n⚠️  This will send actual test notifications to your Facebook group/staff.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("Test cancelled.")
        exit(0)
    
    # Run all tests
    results = []
    results.append(("New Request", test_new_request_notification()))
    results.append(("Status Change", test_status_change_notification()))
    results.append(("Payment", test_payment_notification()))
    results.append(("Approval", test_approval_notification()))
    
    # Summary
    print("\n=== Test Summary ===")
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")