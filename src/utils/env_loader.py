# File: src/utils/env_loader.py

import os
import logging
from pathlib import Path
from typing import Dict, Any

class EnvLoader:
    """Load environment variables from .env files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_env_file(self, env_path: str = "config/.env") -> Dict[str, str]:
        """Load environment variables from .env file."""
        
        env_file = Path(env_path)
        env_vars = {}
        
        if not env_file.exists():
            self.logger.warning(f".env file not found: {env_path}")
            return env_vars
        
        try:
            with open(env_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY="VALUE" or KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        env_vars[key] = value
                        
                        # Set in os.environ so other parts of the app can use it
                        os.environ[key] = value
                        
                    else:
                        self.logger.warning(f"Invalid line in .env file at line {line_num}: {line}")
            
            self.logger.info(f"Loaded {len(env_vars)} environment variables from {env_path}")
            return env_vars
            
        except Exception as e:
            self.logger.error(f"Error loading .env file {env_path}: {e}")
            return {}
    
    def get_graph_credentials(self) -> Dict[str, str]:
        """Get Microsoft Graph API credentials from environment."""
        
        # Try different environment variable names
        credential_mappings = [
            ('GRAPH_CLIENT_ID', ['CLIENT_ID', 'AZURE_CLIENT_ID']),
            ('GRAPH_CLIENT_SECRET', ['CLIENT_SECRET', 'AZURE_CLIENT_SECRET']),
            ('GRAPH_TENANT_ID', ['TENANT_ID', 'AZURE_TENANT_ID'])
        ]
        
        credentials = {}
        
        for standard_name, alt_names in credential_mappings:
            value = None
            
            # Try standard name first
            value = os.getenv(standard_name)
            
            # Try alternative names
            if not value:
                for alt_name in alt_names:
                    value = os.getenv(alt_name)
                    if value:
                        # Set the standard name for consistency
                        os.environ[standard_name] = value
                        break
            
            if value:
                credentials[standard_name] = value
            else:
                self.logger.warning(f"Missing credential: {standard_name} (also tried: {alt_names})")
        
        return credentials
    
    def get_sharepoint_config(self) -> Dict[str, str]:
        """Get SharePoint configuration from environment."""
        
        sharepoint_config = {}
        
        # Parse SharePoint site URL
        site_url = os.getenv('SHAREPOINT_SITE_URL', '')
        
        if site_url:
            # Extract tenant and site from URL
            # Example: https://nationalabilitycare.sharepoint.com/sites/Caura2
            if 'sharepoint.com' in site_url:
                parts = site_url.split('/')
                
                # Extract tenant (e.g., "nationalabilitycare" from "nationalabilitycare.sharepoint.com")
                if len(parts) >= 3:
                    domain = parts[2]  # "nationalabilitycare.sharepoint.com"
                    tenant_name = domain.split('.')[0]  # "nationalabilitycare"
                    sharepoint_config['tenant_name'] = tenant_name
                
                # Extract site name (e.g., "Caura2" from "/sites/Caura2")
                if '/sites/' in site_url:
                    site_part = site_url.split('/sites/')[-1]
                    site_name = site_part.split('/')[0]  # First part after /sites/
                    sharepoint_config['site_name'] = site_name
                
                # Check for document library path
                if '/Documents/' in site_url:
                    doc_path = site_url.split('/Documents/')[-1]
                    sharepoint_config['base_folder'] = doc_path
        
        self.logger.info(f"Parsed SharePoint config: {sharepoint_config}")
        return sharepoint_config