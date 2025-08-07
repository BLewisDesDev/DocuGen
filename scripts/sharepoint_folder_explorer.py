#!/usr/bin/env python3
# File: scripts/sharepoint_folder_explorer.py

import os
import requests
import sys
from pathlib import Path

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

def list_folder_contents(token, drive_id, folder_path="", get_all=True):
    """List contents of a specific folder with pagination support."""
    
    headers = {'Authorization': f'Bearer {token}'}
    
    if folder_path:
        # Navigate to specific folder
        from urllib.parse import quote
        encoded_path = quote(folder_path)
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{encoded_path}:/children"
    else:
        # Root of document library
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
    
    all_items = []
    
    try:
        while url:
            print(f"📡 Fetching items... (found {len(all_items)} so far)", end='\r')
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                items = data.get('value', [])
                all_items.extend(items)
                
                # Check for next page
                if get_all and '@odata.nextLink' in data:
                    url = data['@odata.nextLink']
                else:
                    url = None
            else:
                print(f"\n❌ Failed to access folder '{folder_path}': {response.status_code}")
                print(f"   Response: {response.text}")
                return []
        
        print(f"✅ Loaded {len(all_items)} items total" + " " * 20)  # Clear the progress line
        return all_items
        
    except Exception as e:
        print(f"\n❌ Error accessing folder: {e}")
        return []

def main():
    """Explore SharePoint folders."""
    
    print("=== SharePoint Folder Explorer ===\n")
    
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
    
    print(f"✅ Connected to SharePoint")
    print(f"Site ID: {site_id[:20]}...")
    print(f"Drive ID: {drive_id[:20]}...")
    print()
    
    # Interactive folder exploration
    current_path = ""
    
    while True:
        # Show current location
        if current_path:
            print(f"📁 Current location: /{current_path}")
        else:
            print("📁 Current location: /Documents (root)")
        
        # List folder contents
        print("\nFolders and files:")
        items = list_folder_contents(token, drive_id, current_path)
        
        folders = []
        files = []
        
        for item in items:
            if 'folder' in item:
                folders.append(item['name'])
                print(f"  📁 {item['name']}/")
            else:
                files.append(item['name'])
                print(f"  📄 {item['name']}")
        
        print(f"\nFound {len(folders)} folders and {len(files)} files")
        
        # Navigation options
        print("\nOptions:")
        print("- Enter folder name to navigate into it")
        print("- Type '..' to go up one level")
        print("- Type 'search <name>' to search for folders containing name")
        print("- Type 'quit' to exit")
        
        choice = input("\n> ").strip()
        
        if choice.lower() == 'quit':
            break
        elif choice == '..':
            # Go up one level
            if current_path:
                path_parts = current_path.split('/')
                if len(path_parts) > 1:
                    current_path = '/'.join(path_parts[:-1])
                else:
                    current_path = ""
            print()
        elif choice.startswith('search '):
            # Search for folders
            search_term = choice[7:].lower()
            matching_folders = [f for f in folders if search_term in f.lower()]
            
            print(f"\n🔍 Folders containing '{search_term}':")
            for i, folder in enumerate(matching_folders[:20], 1):  # Show first 20 matches
                print(f"  {i:2d}. 📁 {folder}")
            
            if len(matching_folders) > 20:
                print(f"  ... and {len(matching_folders) - 20} more")
            
            if matching_folders:
                folder_choice = input(f"\nEnter folder name to navigate or press Enter to continue: ").strip()
                if folder_choice in folders:
                    if current_path:
                        current_path = f"{current_path}/{folder_choice}"
                    else:
                        current_path = folder_choice
            print()
        elif choice in folders:
            # Navigate into folder
            if current_path:
                current_path = f"{current_path}/{choice}"
            else:
                current_path = choice
            print()
        elif choice:
            print(f"❌ Folder '{choice}' not found")
            print()

if __name__ == "__main__":
    main()