#!/usr/bin/env python3
"""
AEGIS OS — Workspace Identity Probe
Diagnostic script to test administrative API access to the aijesusbro.com Workspace.

Requirements:
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

import os
import sys

try:
    import google.auth
    from googleapiclient.discovery import build
    from google.auth.exceptions import DefaultCredentialsError
except ImportError:
    print("CRITICAL PAUSE: Missing dependencies. Please run:")
    print("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

def run_probe():
    print("--- AEGIS OS WORKSPACE PROBE ---")
    
    # 1. Attempt to grab default environment credentials
    try:
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/admin.directory.user.readonly']
        )
        print(f"Auth Success: Using active machine credentials.")
        print(f"GCP Project: {project if project else 'Unspecified (using gcloud auth)'}")
    except DefaultCredentialsError as e:
        print("\nRAIL DETECTED: Authentication Failed.")
        print(f"Details: {e}")
        print("Required Action: Run 'gcloud auth application-default login' to grant the CLI access to your account.")
        return

    # 2. Build the Admin Directory Service
    try:
        service = build('admin', 'directory_v1', credentials=credentials)
    except Exception as e:
        print("\nRAIL DETECTED: Failed to build Admin Directory API client.")
        print(f"Details: {e}")
        return

    # 3. Request User List
    print("Executing Directory API request (list users in customer domain)...")
    try:
        results = service.users().list(customer='my_customer', maxResults=10, orderBy='email').execute()
        users = results.get('users', [])

        if not users:
            print("Response: No users found in the domain.")
        else:
            print(f"\nSUCCESS. Admin Directory access confirmed. Found {len(users)} users:")
            for user in users:
                print(f" - {user['primaryEmail']} (Admin: {user.get('isAdmin', False)})")
                
        print("\nAll rails cleared for Admin Directory access.")

    except Exception as e:
        # We expect a 403 or similar scope error if the UI handshake hasn't happened
        print("\nRAIL DETECTED: API Request Failed.")
        print(f"Error Details: {e}")
        
        err_str = str(e).lower()
        if "not authorized" in err_str or "403" in err_str:
            print("\nDIAGNOSIS: Workspace Admin privileges are locked for this credential scope.")
            print("Action Required in Google Admin Console:")
            print("1. We need an authorized Service Account or OAuth Client.")
            print("2. Navigate to Security -> Access and data control -> API controls.")
            print("3. Ensure Directory API is enabled and granted Domain-Wide Delegation (if using Service Account).")
        elif "admin sdk api has not been used" in err_str:
            print("\nDIAGNOSIS: Admin SDK API is disabled in the GCP Project.")
            print("Action Required in Google Cloud Console:")
            print("1. Go to console.cloud.google.com -> APIs & Services.")
            print("2. Enable the 'Admin SDK API'.")

if __name__ == '__main__':
    run_probe()
