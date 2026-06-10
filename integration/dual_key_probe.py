#!/usr/bin/env python3
"""
AEGIS OS — Dual Key Probe
Tests both Service Account JSON keys to confirm Domain-Wide Delegation access
to the Google Workspace Admin Directory.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user.readonly']
CUSTOMER_DOMAIN = 'aijesusbro.com'  # Replaced 'my_customer' with explicit domain to test delegation
IMPERSONATE_EMAIL = 'kruze@aijesusbro.com'

KEYS = [
    "devmcp-gmail-intelligence-3092613a3922.json", # The new aegis-os-admin
    "devmcp-gmail-intelligence-187ff1e8a588.json"  # The original devmcp-gmail-sa
]

def test_key(key_filename):
    print(f"\n--- Testing Key: {key_filename} ---")
    key_path = os.path.join(os.path.dirname(__file__), "..", key_filename)
    
    if not os.path.exists(key_path):
        print(f"File missing at {key_path}")
        return False
        
    try:
        # 1. Load the credential
        creds = service_account.Credentials.from_service_account_file(
            key_path, scopes=SCOPES
        )
        
        # 2. To control Workspace (users/groups/Voice), a Service Account MUST impersonate an Admin.
        # This tests if Domain-Wide Delegation is active for this client ID.
        delegated_creds = creds.with_subject(IMPERSONATE_EMAIL)
        
        # 3. Build SDK
        service = build('admin', 'directory_v1', credentials=delegated_creds)
        
        # 4. Fire Request
        print(f"Requesting user list impersonating {IMPERSONATE_EMAIL}...")
        results = service.users().list(domain=CUSTOMER_DOMAIN, maxResults=5, orderBy='email').execute()
        users = results.get('users', [])
        
        print("✅ SUCCESS! Domain-Wide Delegation is active.")
        print(f"Found {len(users)} users:")
        for user in users:
            print(f" - {user['primaryEmail']}")
            
        return True

    except Exception as e:
        err_str = str(e).lower()
        if "client is unauthorized to retrieve access tokens" in err_str:
            print("❌ RAIL DETECTED: Missing Domain-Wide Delegation.")
            print("   This Service Account exists in GCP, but Workspace Admin does not trust it yet.")
        else:
            print(f"❌ FAILED: {e}")
        return False

if __name__ == '__main__':
    for k in KEYS:
        test_key(k)
