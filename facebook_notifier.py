"""Facebook Messenger notification module for Barangay e-Services Portal."""

import os
import requests
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class FacebookNotifier:
    """Handle Facebook Messenger notifications for staff."""
    
    def __init__(self):
        """Initialize Facebook Messenger API credentials."""
        self.page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.staff_group_id = os.getenv("FACEBOOK_STAFF_GROUP_ID")
        
        # Facebook Graph API base URL
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        
        # Staff Facebook user IDs (for direct messaging)
        self.staff_user_ids = self._parse_staff_ids()
    
    def _parse_staff_ids(self) -> List[str]:
        """Parse staff Facebook user IDs from environment variable."""
        staff_ids_str = os.getenv("FACEBOOK_STAFF_USER_IDS", "")
        if staff_ids_str:
            return [id.strip() for id in staff_ids_str.split(",")]
        return []
    
    def is_configured(self) -> bool:
        """Check if Facebook credentials are properly configured."""
        return bool(self.page_access_token and self.page_id)
    
    def send_message_to_user(self, user_id: str, message: str) -> bool:
        """Send a message to a specific Facebook user."""
        if not self.is_configured():
            print("Facebook credentials not configured")
            return False
        
        try:
            url = f"{self.graph_api_url}/{self.page_id}/messages"
            headers = {
                "Content-Type": "application/json"
            }
            params = {
                "access_token": self.page_access_token
            }
            data = {
                "recipient": {"id": user_id},
                "message": {"text": message}
            }
            
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"Message sent successfully to user {user_id}")
                return True
            else:
                print(f"Failed to send message: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending Facebook message: {e}")
            return False
    
    def send_message_to_all_staff(self, message: str) -> bool:
        """Send a message to all staff members."""
        if not self.staff_user_ids:
            print("No staff user IDs configured")
            return False
        
        success_count = 0
        for user_id in self.staff_user_ids:
            if self.send_message_to_user(user_id, message):
                success_count += 1
        
        print(f"Sent message to {success_count}/{len(self.staff_user_ids)} staff members")
        return success_count > 0
    
    def post_to_group(self, group_id: str, message: str) -> bool:
        """Post a message to a Facebook group."""
        if not self.is_configured():
            print("Facebook credentials not configured")
            return False
        
        try:
            url = f"{self.graph_api_url}/{group_id}/feed"
            headers = {
                "Content-Type": "application/json"
            }
            params = {
                "access_token": self.page_access_token
            }
            data = {
                "message": message
            }
            
            response = requests.post(url, headers=headers, params=params, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"Message posted successfully to group {group_id}")
                return True
            else:
                print(f"Failed to post to group: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error posting to Facebook group: {e}")
            return False
    
    def notify_new_request(self, request_data: Dict[str, Any]) -> bool:
        """Send notification when a new service request is submitted."""
        service_type = request_data.get("service_type", "Unknown").replace("_", " ").title()
        reference_number = request_data.get("reference_number", "N/A")
        full_name = request_data.get("full_name", "Unknown")
        contact_number = request_data.get("contact_number", "N/A")
        
        message = f"""🔔 NEW SERVICE REQUEST SUBMITTED

Service Type: {service_type}
Reference Number: {reference_number}
Applicant Name: {full_name}
Contact Number: {contact_number}

Please review this request in the dashboard.

📱 Barangay 7 e-Services Portal"""
        
        # Try group notification first, fallback to direct messages
        if self.staff_group_id:
            if self.post_to_group(self.staff_group_id, message):
                return True
        
        # Fallback to direct messages
        return self.send_message_to_all_staff(message)
    
    def notify_status_change(self, request_data: Dict[str, Any], old_status: str, new_status: str) -> bool:
        """Send notification when a request status changes."""
        service_type = request_data.get("service_type", "Unknown").replace("_", " ").title()
        reference_number = request_data.get("reference_number", "N/A")
        full_name = request_data.get("full_name", "Unknown")
        
        # Use the status directly if they're already readable, otherwise map them
        message = f"""📋 REQUEST STATUS UPDATE

Service Type: {service_type}
Reference Number: {reference_number}
Applicant Name: {full_name}

Status: {old_status} → {new_status}

Please take appropriate action in the dashboard.

📱 Barangay 7 e-Services Portal"""
        
        # Try group notification first, fallback to direct messages
        if self.staff_group_id:
            if self.post_to_group(self.staff_group_id, message):
                return True
        
        # Fallback to direct messages
        return self.send_message_to_all_staff(message)
    
    def notify_payment_submitted(self, request_data: Dict[str, Any]) -> bool:
        """Send notification when payment proof is submitted."""
        service_type = request_data.get("service_type", "Unknown").replace("_", " ").title()
        reference_number = request_data.get("reference_number", "N/A")
        full_name = request_data.get("full_name", "Unknown")
        
        message = f"""💰 PAYMENT PROOF SUBMITTED

Service Type: {service_type}
Reference Number: {reference_number}
Applicant Name: {full_name}

The applicant has uploaded GCash payment proof.
Please verify the payment in the dashboard.

📱 Barangay 7 e-Services Portal"""
        
        # Target Treasurer specifically if possible
        if self.staff_user_ids:
            # Send to all staff (can be refined to target treasurer only)
            return self.send_message_to_all_staff(message)
        
        return False
    
    def notify_approval(self, request_data: Dict[str, Any]) -> bool:
        """Send notification when a request is approved."""
        service_type = request_data.get("service_type", "Unknown").replace("_", " ").title()
        reference_number = request_data.get("reference_number", "N/A")
        full_name = request_data.get("full_name", "Unknown")
        
        message = f"""✅ REQUEST APPROVED

Service Type: {service_type}
Reference Number: {reference_number}
Applicant Name: {full_name}

The certificate has been generated and is ready for release.

📱 Barangay 7 e-Services Portal"""
        
        # Try group notification first, fallback to direct messages
        if self.staff_group_id:
            if self.post_to_group(self.staff_group_id, message):
                return True
        
        # Fallback to direct messages
        return self.send_message_to_all_staff(message)


# Singleton instance
facebook_notifier = FacebookNotifier()