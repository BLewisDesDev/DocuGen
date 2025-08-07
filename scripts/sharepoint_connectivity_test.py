#!/usr/bin/env python3
# File: scripts/sharepoint_connectivity_test.py

import os
import requests
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.env_loader import EnvLoader

def main():
    """Simple SharePoint connectivity test."""
    
    print("=== SharePoint Connectivity Test ===\n")
    
    # Load environment variables
    env_loader = EnvLoader()
    env_loader.load_env_file()
    
    # Get credentials
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    print(f"Client ID: {client_id[:8]}..." if client_id else "❌ Missing AZURE_CLIENT_ID")
    print(f"Client Secret: {'✅ Found' if client_secret else '❌ Missing AZURE_CLIENT_SECRET'}")
    print(f"Tenant ID: {tenant_id}" if tenant_id else "❌ Missing AZURE_TENANT_ID")
    print()
    
    if not all([client_id, client_secret, tenant_id]):
        print("❌ Missing credentials in .env file")
        return
    
    # Step 1: Test Authentication
    print("1. Testing Authentication...")
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Step 2: Test SharePoint Site Access
    print("\n2. Testing SharePoint Site Access...")
    site_url = "https://graph.microsoft.com/v1.0/sites/nationalabilitycare.sharepoint.com:/sites/Caura2"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(site_url, headers=headers)
        if response.status_code == 200:
            site_data = response.json()
            site_id = site_data.get('id')
            print(f"✅ Site access successful")
            print(f"   Site ID: {site_id[:20]}...")
        else:
            print(f"❌ Site access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Site access error: {e}")
        return
    
    # Step 3: Test Document Library Access
    print("\n3. Testing Document Library Access...")
    drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    
    try:
        response = requests.get(drives_url, headers=headers)
        if response.status_code == 200:
            drives_data = response.json()
            drives = drives_data.get('value', [])
            print(f"✅ Document library access successful")
            print(f"   Found {len(drives)} drives")
            for drive in drives[:2]:  # Show first 2 drives
                print(f"   - {drive.get('name')} ({drive.get('driveType')})")
        else:
            print(f"❌ Document library access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Document library error: {e}")
        return
    
    print("\n🎉 All tests passed! SharePoint connectivity is working.")

if __name__ == "__main__":
    main()