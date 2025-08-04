#!/usr/bin/env python3
# File: scripts/test_sharepoint_upload.py

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.exporters.sharepoint_exporter import SharePointExporter
from src.core.config_loader import ConfigLoader

def main():
    """Test SharePoint upload functionality."""
    
    # Setup logging with debug level to see more details
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        
        # Initialize SharePoint exporter
        exporter = SharePointExporter(app_config)
        
        # Get credentials from environment variables (try both naming conventions)
        client_id = os.getenv('AZURE_CLIENT_ID') or os.getenv('GRAPH_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET') or os.getenv('GRAPH_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID') or os.getenv('GRAPH_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            print("❌ Missing Microsoft Graph API credentials")
            print(f"Found: CLIENT_ID={bool(client_id)}, CLIENT_SECRET={bool(client_secret)}, TENANT_ID={bool(tenant_id)}")
            print("\nYour .env should contain:")
            print("AZURE_CLIENT_ID='your-app-client-id'")
            print("AZURE_CLIENT_SECRET='your-app-client-secret'")
            print("AZURE_TENANT_ID='your-tenant-id'")
            print("\nTo get these credentials:")
            print("1. Go to Azure Portal > App registrations")
            print("2. Create new registration or use existing")
            print("3. Add API permissions: Sites.ReadWrite.All")
            print("4. Create client secret")
            return
        
        # Test authentication
        print("=== Testing SharePoint Authentication ===")
        if exporter.authenticate(client_id, client_secret, tenant_id):
            print("✅ Successfully authenticated with Microsoft Graph API")
        else:
            print("❌ Authentication failed")
            return
        
        # Test site access
        print("\n=== Testing Site Access ===")
        site_id = exporter.get_site_id()
        if site_id:
            print(f"✅ Successfully accessed SharePoint site: {site_id}")
        else:
            print("❌ Failed to access SharePoint site")
            print("Check your tenant_name and site_name in config/app_config.yaml")
            return
        
        # Test drive access
        print("\n=== Testing Document Library Access ===")
        drive_id = exporter.get_drive_id(site_id)
        if drive_id:
            print(f"✅ Successfully accessed document library: {drive_id}")
        else:
            print("❌ Failed to access document library")
            return
        
        # Test folder creation
        print("\n=== Testing Folder Creation ===")
        test_folder = "CarePlans/Test/2025/01"
        if exporter.create_folder_structure(drive_id, test_folder):
            print(f"✅ Successfully created folder structure: {test_folder}")
        else:
            print("❌ Failed to create folder structure")
        
        # Test file upload if we have test files
        print("\n=== Testing File Upload ===")
        test_files = list(Path("output/test_client_map").glob("*.docx"))
        
        if test_files:
            test_file = test_files[0]
            print(f"Uploading test file: {test_file.name}")
            
            # Create mock client data for organized upload
            client_data = {
                'ServiceStartDate': '2025-01-15',
                'Type': 'DA',
                'FirstName': 'Test',
                'LastName': 'Client',
                'ACN': 'AC00123456'
            }
            
            web_url = exporter.upload_care_plan(test_file, client_data)
            
            if web_url:
                print(f"✅ Successfully uploaded file")
                print(f"SharePoint URL: {web_url}")
            else:
                print("❌ File upload failed")
        else:
            print("No test files found. Run the client map generation script first.")
        
        # Test file listing
        print("\n=== Testing File Listing ===")
        files = exporter.list_files("CarePlans")
        if files:
            print(f"✅ Found {len(files)} items in CarePlans folder")
            for file in files[:3]:  # Show first 3 files
                print(f"  - {file.get('name')} ({file.get('size', 0)} bytes)")
        else:
            print("No files found in CarePlans folder")
            
    except Exception as e:
        logger.error(f"Error in SharePoint upload test: {e}")
        raise

if __name__ == "__main__":
    main()