#!/usr/bin/env python3
# File: scripts/sharepoint_folder_metadata_test.py

import os
import requests
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.env_loader import EnvLoader

def get_access_token():
    """Get access token for Microsoft Graph API."""
    
    client_id = os.getenv('AZURE_CLIENT_ID')
    client_secret = os.getenv('AZURE_CLIENT_SECRET')
    tenant_id = os.getenv('AZURE_TENANT_ID')
    
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_site_and_drive_id(token):
    """Get SharePoint site and drive IDs."""
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get site ID
    site_url = "https://graph.microsoft.com/v1.0/sites/nationalabilitycare.sharepoint.com:/sites/Caura2"
    response = requests.get(site_url, headers=headers)
    if response.status_code != 200:
        return None, None
        
    site_id = response.json().get('id')
    
    # Get drive ID (Documents library)
    drives_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    response = requests.get(drives_url, headers=headers)
    if response.status_code != 200:
        return site_id, None
        
    drives = response.json().get('value', [])
    for drive in drives:
        if drive.get('name') == 'Documents':
            return site_id, drive.get('id')
    
    return site_id, drives[0].get('id') if drives else None

def get_folder_contents_with_metadata(token, drive_id, folder_path=""):
    """Get folder contents with full metadata."""
    
    headers = {'Authorization': f'Bearer {token}'}
    
    if folder_path:
        from urllib.parse import quote
        encoded_path = quote(folder_path)
        # Request expanded metadata
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{encoded_path}:/children?$expand=thumbnails&$select=id,name,size,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,file,folder,webUrl"
    else:
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children?$expand=thumbnails&$select=id,name,size,createdDateTime,lastModifiedDateTime,createdBy,lastModifiedBy,file,folder,webUrl"
    
    all_items = []
    
    try:
        while url:
            print(f"📡 Fetching metadata... (found {len(all_items)} items)", end='\r')
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get('value', [])
                all_items.extend(items)
                
                # Check for next page
                if '@odata.nextLink' in data:
                    url = data['@odata.nextLink']
                else:
                    url = None
            else:
                print(f"\n❌ Failed to get metadata: {response.status_code}")
                return []
        
        print(f"✅ Loaded metadata for {len(all_items)} items" + " " * 20)
        return all_items
        
    except Exception as e:
        print(f"\n❌ Error getting metadata: {e}")
        return []

def format_datetime(dt_string):
    """Format datetime string for display."""
    if not dt_string:
        return "Unknown"
    
    try:
        # Parse ISO datetime
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return dt_string

def show_folder_details(item):
    """Show detailed metadata for a folder."""
    
    print(f"\n{'='*60}")
    print(f"📁 {item['name']}")
    print(f"{'='*60}")
    
    # Basic info
    print(f"ID: {item.get('id', 'N/A')}")
    print(f"Type: Folder")
    
    # Folder specific info
    if 'folder' in item:
        folder_info = item['folder']
        if 'childCount' in folder_info:
            print(f"Child Count: {folder_info['childCount']} items")
    
    # Dates
    print(f"\nDates:")
    print(f"Created: {format_datetime(item.get('createdDateTime'))}")
    print(f"Modified: {format_datetime(item.get('lastModifiedDateTime'))}")
    
    # Created by / Modified by
    created_by = item.get('createdBy', {}).get('user', {})
    if created_by:
        print(f"\nCreated by: {created_by.get('displayName', 'Unknown')} ({created_by.get('email', 'No email')})")
    
    modified_by = item.get('lastModifiedBy', {}).get('user', {})
    if modified_by:
        print(f"Modified by: {modified_by.get('displayName', 'Unknown')} ({modified_by.get('email', 'No email')})")
    
    # Web URL
    if 'webUrl' in item:
        print(f"\nSharePoint URL: {item['webUrl']}")
    
    print(f"{'='*60}")

def main():
    """Test folder metadata from Client Records."""
    
    print("=== SharePoint Folder Metadata Test ===\n")
    
    # Load environment variables
    env_loader = EnvLoader()
    env_loader.load_env_file()
    
    # Get authentication
    print("Getting access token...")
    token = get_access_token()
    if not token:
        print("❌ Authentication failed")
        return
    
    print("Getting site and drive information...")
    site_id, drive_id = get_site_and_drive_id(token)
    if not drive_id:
        print("❌ Could not access document library")
        return
    
    print(f"✅ Connected to SharePoint\n")
    
    # Hard-coded folder path for testing
    folder_path = "CHSP/Clients/Client Records"
    
    print(f"📁 Getting folder metadata from: /{folder_path}")
    
    # Get items with metadata
    items = get_folder_contents_with_metadata(token, drive_id, folder_path)
    
    if not items:
        print("No items found or access denied")
        return
    
    # Sort items by type and name
    folders = [item for item in items if 'folder' in item]
    files = [item for item in items if 'file' in item]
    
    folders.sort(key=lambda x: x['name'].lower())
    files.sort(key=lambda x: x['name'].lower())
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"Folders: {len(folders)}")
    print(f"Files: {len(files)}")
    print(f"Total: {len(items)}")
    
    # Show first 2 folders with detailed metadata
    print(f"\n{'='*60}")
    print("FIRST 2 FOLDERS WITH METADATA:")
    print(f"{'='*60}")
    
    first_two_folders = folders[:2]
    for i, item in enumerate(first_two_folders, 1):
        print(f"\n--- FOLDER {i} ---")
        show_folder_details(item)
    
    if len(folders) == 0:
        print("❌ No folders found in this location")
    elif len(folders) < 2:
        print(f"ℹ️ Only {len(folders)} folder(s) found")

if __name__ == "__main__":
    main()