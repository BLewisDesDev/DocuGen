# File: src/exporters/sharepoint_exporter.py

import logging
import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import quote

class SharePointExporter:
    """Export documents to SharePoint using Microsoft Graph API."""
    
    def __init__(self, app_config: Dict[str, Any]):
        self.app_config = app_config
        self.logger = logging.getLogger(__name__)
        self.access_token = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        
        # SharePoint configuration
        self.sharepoint_config = app_config.get('sharepoint', {})
        self.tenant_name = self.sharepoint_config.get('tenant_name')
        self.site_name = self.sharepoint_config.get('site_name')
        self.document_library = self.sharepoint_config.get('document_library', 'Documents')
        
    def authenticate(self, client_id: str, client_secret: str, tenant_id: str) -> bool:
        """Authenticate with Microsoft Graph API using client credentials."""
        
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }
        
        try:
            self.logger.debug(f"Token URL: {token_url}")
            self.logger.debug(f"Client ID: {client_id}")
            self.logger.debug(f"Tenant ID: {tenant_id}")
            
            response = requests.post(token_url, data=token_data)
            
            if response.status_code != 200:
                self.logger.error(f"Authentication failed with status {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False
            
            token_response = response.json()
            self.access_token = token_response.get('access_token')
            
            if self.access_token:
                self.logger.info("Successfully authenticated with Microsoft Graph API")
                return True
            else:
                self.logger.error("No access token received")
                self.logger.error(f"Token response: {token_response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_site_id(self) -> Optional[str]:
        """Get SharePoint site ID."""
        
        if not self.access_token:
            self.logger.error("Not authenticated")
            return None
        
        url = f"{self.base_url}/sites/{self.tenant_name}.sharepoint.com:/sites/{self.site_name}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            site_data = response.json()
            site_id = site_data.get('id')
            
            self.logger.info(f"Found site ID: {site_id}")
            return site_id
            
        except Exception as e:
            self.logger.error(f"Failed to get site ID: {e}")
            return None
    
    def get_drive_id(self, site_id: str) -> Optional[str]:
        """Get document library drive ID."""
        
        if not self.access_token:
            self.logger.error("Not authenticated")
            return None
        
        url = f"{self.base_url}/sites/{site_id}/drives"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            drives_data = response.json()
            drives = drives_data.get('value', [])
            
            # Find the document library
            for drive in drives:
                if drive.get('name') == self.document_library:
                    drive_id = drive.get('id')
                    self.logger.info(f"Found drive ID for {self.document_library}: {drive_id}")
                    return drive_id
            
            # If not found, use default drive
            if drives:
                drive_id = drives[0].get('id')
                self.logger.info(f"Using default drive ID: {drive_id}")
                return drive_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get drive ID: {e}")
            return None
    
    def create_folder_structure(self, drive_id: str, folder_path: str) -> bool:
        """Create folder structure in SharePoint if it doesn't exist."""
        
        if not self.access_token:
            self.logger.error("Not authenticated")
            return False
        
        # Split path into components
        path_parts = [p for p in folder_path.split('/') if p]
        current_path = ""
        
        for folder_name in path_parts:
            current_path = f"{current_path}/{folder_name}" if current_path else folder_name
            
            # Check if folder exists
            encoded_path = quote(current_path)
            check_url = f"{self.base_url}/drives/{drive_id}/root:/{encoded_path}"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            try:
                response = requests.get(check_url, headers=headers)
                
                if response.status_code == 404:
                    # Folder doesn't exist, create it
                    parent_path = "/".join(current_path.split('/')[:-1])
                    parent_url = f"{self.base_url}/drives/{drive_id}/root"
                    
                    if parent_path:
                        parent_url = f"{self.base_url}/drives/{drive_id}/root:/{quote(parent_path)}"
                    
                    create_url = f"{parent_url}/children"
                    
                    create_data = {
                        "name": folder_name,
                        "folder": {},
                        "@microsoft.graph.conflictBehavior": "rename"
                    }
                    
                    create_response = requests.post(create_url, headers=headers, json=create_data)
                    create_response.raise_for_status()
                    
                    self.logger.info(f"Created folder: {current_path}")
                    
            except Exception as e:
                self.logger.error(f"Failed to create folder {current_path}: {e}")
                return False
        
        return True
    
    def upload_file(self, file_path: Path, sharepoint_folder: str = "", 
                   filename_override: str = None) -> Optional[str]:
        """Upload file to SharePoint."""
        
        if not self.access_token:
            self.logger.error("Not authenticated")
            return None
        
        # Get site and drive IDs
        site_id = self.get_site_id()
        if not site_id:
            return None
        
        drive_id = self.get_drive_id(site_id)
        if not drive_id:
            return None
        
        # Create folder structure if needed
        if sharepoint_folder:
            if not self.create_folder_structure(drive_id, sharepoint_folder):
                return None
        
        # Prepare file upload
        filename = filename_override or file_path.name
        
        if sharepoint_folder:
            upload_path = f"{sharepoint_folder}/{filename}"
        else:
            upload_path = filename
        
        encoded_path = quote(upload_path)
        upload_url = f"{self.base_url}/drives/{drive_id}/root:/{encoded_path}:/content"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            response = requests.put(upload_url, headers=headers, data=file_content)
            response.raise_for_status()
            
            upload_response = response.json()
            web_url = upload_response.get('webUrl')
            
            self.logger.info(f"Successfully uploaded {filename} to SharePoint")
            self.logger.info(f"SharePoint URL: {web_url}")
            
            return web_url
            
        except Exception as e:
            self.logger.error(f"Failed to upload file {file_path}: {e}")
            return None
    
    def check_folder_exists(self, drive_id: str, folder_path: str) -> bool:
        """Check if a folder exists in SharePoint."""
        
        if not self.access_token:
            return False
        
        encoded_path = quote(folder_path)
        check_url = f"{self.base_url}/drives/{drive_id}/root:/{encoded_path}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(check_url, headers=headers)
            return response.status_code == 200
        except Exception:
            return False
    
    def rename_folder(self, drive_id: str, old_path: str, new_name: str) -> bool:
        """Rename a folder in SharePoint."""
        
        if not self.access_token:
            return False
        
        encoded_path = quote(old_path)
        rename_url = f"{self.base_url}/drives/{drive_id}/root:/{encoded_path}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        rename_data = {
            "name": new_name
        }
        
        try:
            response = requests.patch(rename_url, headers=headers, json=rename_data)
            response.raise_for_status()
            self.logger.info(f"Successfully renamed folder from {old_path} to {new_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to rename folder {old_path}: {e}")
            return False
    
    def upload_care_plan_with_client_folder(self, file_path: Path, client_data: Dict[str, Any]) -> Optional[str]:
        """Upload care plan using client-specific folder structure."""
        
        # Get site and drive IDs
        site_id = self.get_site_id()
        if not site_id:
            return None
        
        drive_id = self.get_drive_id(site_id)
        if not drive_id:
            return None
        
        # Extract client information
        given_name = client_data.get('FirstName', '').strip()
        family_name = client_data.get('LastName', '').strip()
        acn = client_data.get('ACN', '').strip()
        
        if not given_name or not family_name:
            self.logger.error("Missing client name information")
            return None
        
        # Use configured base folder from SharePoint config
        configured_base = self.sharepoint_config.get('base_folder', 'CarePlans')
        base_folder = f"{configured_base}/CarePlans"
        
        temp_folder_name = f"{given_name}, {family_name}"
        final_folder_name = f"{acn}-{given_name}-{family_name}"
        
        temp_folder_path = f"{base_folder}/{temp_folder_name}"
        final_folder_path = f"{base_folder}/{final_folder_name}"
        
        # Step 1: Check if temp folder exists
        if self.check_folder_exists(drive_id, temp_folder_path):
            self.logger.info(f"Found existing folder: {temp_folder_path}")
            
            # Step 2: Rename to final format
            if self.rename_folder(drive_id, temp_folder_path, final_folder_name):
                target_folder = final_folder_path
            else:
                target_folder = temp_folder_path
                
        # Step 3: Check if final folder exists
        elif self.check_folder_exists(drive_id, final_folder_path):
            self.logger.info(f"Found existing final folder: {final_folder_path}")
            target_folder = final_folder_path
            
        # Step 4: Create new folder with final format
        else:
            self.logger.info(f"Creating new folder: {final_folder_path}")
            if self.create_folder_structure(drive_id, final_folder_path):
                target_folder = final_folder_path
            else:
                self.logger.error("Failed to create client folder")
                return None
        
        # Step 5: Upload file with Caura prefix
        original_filename = file_path.name
        caura_filename = f"Caura_Care_Plan_{original_filename}"
        
        # Extract just the folder name from the path
        folder_name_only = target_folder.split('/')[-1]
        
        return self.upload_file(file_path, target_folder, caura_filename)
    
    def upload_care_plan(self, file_path: Path, client_data: Dict[str, Any]) -> Optional[str]:
        """Upload care plan with client-specific folder structure (wrapper for backward compatibility)."""
        return self.upload_care_plan_with_client_folder(file_path, client_data)
    
    def list_files(self, folder_path: str = "") -> List[Dict[str, Any]]:
        """List files in SharePoint folder."""
        
        if not self.access_token:
            self.logger.error("Not authenticated")
            return []
        
        site_id = self.get_site_id()
        if not site_id:
            return []
        
        drive_id = self.get_drive_id(site_id)
        if not drive_id:
            return []
        
        if folder_path:
            encoded_path = quote(folder_path)
            url = f"{self.base_url}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            url = f"{self.base_url}/drives/{drive_id}/root/children"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            files_data = response.json()
            files = files_data.get('value', [])
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files in {folder_path}: {e}")
            return []