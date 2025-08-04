#!/usr/bin/env python3
# File: scripts/test_client_folder_logic.py

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.exporters.sharepoint_exporter import SharePointExporter
from src.core.config_loader import ConfigLoader

def test_folder_logic_scenarios():
    """Test different client folder scenarios."""
    
    # Test scenarios
    scenarios = [
        {
            'name': 'New Client (no existing folder)',
            'existing_folders': [],
            'client_data': {'FirstName': 'John', 'LastName': 'Smith', 'ACN': 'AC00111111'},
            'expected_folder': 'CarePlans/AC00111111-John-Smith',
            'expected_filename': 'Caura_Care_Plan_test.docx'
        },
        {
            'name': 'Existing temp folder (needs rename)',
            'existing_folders': ['CarePlans/John, Smith'],
            'client_data': {'FirstName': 'John', 'LastName': 'Smith', 'ACN': 'AC00111111'},
            'expected_folder': 'CarePlans/AC00111111-John-Smith',
            'expected_filename': 'Caura_Care_Plan_test.docx'
        },
        {
            'name': 'Existing final folder',
            'existing_folders': ['CarePlans/AC00111111-John-Smith'],
            'client_data': {'FirstName': 'John', 'LastName': 'Smith', 'ACN': 'AC00111111'},
            'expected_folder': 'CarePlans/AC00111111-John-Smith',
            'expected_filename': 'Caura_Care_Plan_test.docx'
        },
        {
            'name': 'Both temp and final exist (use final)',
            'existing_folders': ['CarePlans/John, Smith', 'CarePlans/AC00111111-John-Smith'],
            'client_data': {'FirstName': 'John', 'LastName': 'Smith', 'ACN': 'AC00111111'},
            'expected_folder': 'CarePlans/AC00111111-John-Smith',
            'expected_filename': 'Caura_Care_Plan_test.docx'
        }
    ]
    
    print("=== SharePoint Client Folder Logic Test ===\n")
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print(f"  Existing folders: {scenario['existing_folders']}")
        print(f"  Client: {scenario['client_data']['FirstName']} {scenario['client_data']['LastName']} ({scenario['client_data']['ACN']})")
        print(f"  Expected folder: {scenario['expected_folder']}")
        print(f"  Expected filename: {scenario['expected_filename']}")
        print()
    
    print("This logic will:")
    print("1. Check if '{FirstName}, {LastName}' folder exists")
    print("2. If found, rename to '{ACN}-{FirstName}-{LastName}'")
    print("3. If not found, check if '{ACN}-{FirstName}-{LastName}' exists")
    print("4. If neither exists, create '{ACN}-{FirstName}-{LastName}'")
    print("5. Upload file with 'Caura_Care_Plan_' prefix")

def main():
    """Test SharePoint client folder logic."""
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Show test scenarios
    test_folder_logic_scenarios()
    
    # Check if we can test with actual SharePoint
    client_id = os.getenv('GRAPH_CLIENT_ID')
    client_secret = os.getenv('GRAPH_CLIENT_SECRET')
    tenant_id = os.getenv('GRAPH_TENANT_ID')
    
    if not all([client_id, client_secret, tenant_id]):
        print("\n" + "="*50)
        print("To test with real SharePoint, set environment variables:")
        print("export GRAPH_CLIENT_ID='your-app-client-id'")
        print("export GRAPH_CLIENT_SECRET='your-app-client-secret'")
        print("export GRAPH_TENANT_ID='your-tenant-id'")
        return
    
    try:
        # Load config and test with real SharePoint
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        exporter = SharePointExporter(app_config)
        
        print("\n" + "="*50)
        print("Testing with actual SharePoint...")
        
        if exporter.authenticate(client_id, client_secret, tenant_id):
            print("✅ Authentication successful")
            
            # Test with a real file if available
            test_files = list(Path("output/test_client_map").glob("*.docx"))
            if test_files:
                test_file = test_files[0]
                print(f"\nTesting upload with: {test_file.name}")
                
                # Test client data
                client_data = {
                    'FirstName': 'Maria',
                    'LastName': 'TestClient',
                    'ACN': 'AC00999999'
                }
                
                web_url = exporter.upload_care_plan(test_file, client_data)
                
                if web_url:
                    print(f"✅ Successfully uploaded to: {web_url}")
                else:
                    print("❌ Upload failed")
            else:
                print("No test files found - run client map generation first")
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        logger.error(f"Error testing SharePoint: {e}")

if __name__ == "__main__":
    main()