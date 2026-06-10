#!/usr/bin/env python3
"""
AEGIS OS — Workspace Direct Bridge
Demonstrates exact sovereign capabilities of the Aegis OS Service Account
without requiring Workspace Domain-Wide impersonation.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# We will test Drive API access (which is Native to the Service Account itself)
SCOPES = ['https://www.googleapis.com/auth/drive']

# Use the Aegis OS Admin key
KEY_FILENAME = "devmcp-gmail-intelligence-3092613a3922.json"
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", KEY_FILENAME)

def verify_sovereign_drive():
    print("--- AEGIS OS WORKSPACE BRIDGE ---")
    print(f"Authenticating with: {KEY_FILENAME}")

    if not os.path.exists(KEY_PATH):
        print(f"CRITICAL: Key not found at {KEY_PATH}")
        return

    try:
        # Load the key natively (NO .with_subject() impersonation)
        creds = service_account.Credentials.from_service_account_file(
            KEY_PATH, scopes=SCOPES
        )
        
        # We can extract the service account email directly from the creds
        sa_email = creds.service_account_email
        print(f"Sovereign Identity: {sa_email}")

        # Build the Drive SDK
        print("Engaging Google Drive API...")
        drive_service = build('drive', 'v3', credentials=creds)

        # Execute a native request: List files owned by or shared with this exact SA
        results = drive_service.files().list(
            pageSize=10, 
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])

        print("\n✅ API CLEARANCE VERIFIED.")
        if not items:
            print(f"Sovereign Drive is completely empty.")
            print(f"To give Aegis OS access to your files, you must explicitly Share them with:")
            print(f"  -> {sa_email}")
        else:
            print("Files accessible to this Persona:")
            for item in items:
                print(f" - {item['name']} ({item['mimeType']})")
                
    except Exception as e:
        print(f"\n❌ BRIDGE FAILURE: {e}")

if __name__ == '__main__':
    verify_sovereign_drive()
