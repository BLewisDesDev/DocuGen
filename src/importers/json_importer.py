# File: src/importers/json_importer.py

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class JsonImporter:
    """Handles importing data from client_map.json files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load client data from JSON file."""
        
        json_file = Path(file_path)
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if 'clients' not in data:
            raise ValueError("JSON file must contain 'clients' array")
        
        self.logger.info(f"Loaded {len(data['clients'])} clients from {file_path}")
        return data['clients']
    
    def get_service_types(self, client: Dict[str, Any]) -> List[str]:
        """Extract service types from client service information."""
        service_types = []
        
        # Check service_information.services for service types
        services = client.get('service_information', {}).get('services', [])
        for service in services:
            service_type = service.get('service_type', '')
            if service_type == 'home_maintenance':
                service_types.append('HM')
            elif service_type == 'domestic_assistance':
                service_types.append('DA')
        
        return service_types
    
    def get_acn(self, client: Dict[str, Any]) -> Optional[str]:
        """Extract ACN from aged_care platform identifier."""
        platform_identifiers = client.get('platform_identifiers', [])
        
        for platform in platform_identifiers:
            if platform.get('platform') == 'aged_care':
                return platform.get('identifiers', {}).get('acn')
        
        return None
    
    def get_first_service_date(self, client: Dict[str, Any]) -> Optional[str]:
        """Get the earliest service date from service information."""
        services = client.get('service_information', {}).get('services', [])
        
        earliest_date = None
        for service in services:
            service_date = service.get('first_service_date')
            if service_date:
                if earliest_date is None or service_date < earliest_date:
                    earliest_date = service_date
        
        return earliest_date
    
    def map_client_data(self, client: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Map client data to template fields based on configuration."""
        
        mapped_data = {}
        personal_info = client.get('personal_info', {})
        location = client.get('location', {})
        
        # Basic field mappings
        field_mappings = {
            'FirstName': personal_info.get('given_name', ''),
            'LastName': personal_info.get('family_name', ''),
            'DOB': personal_info.get('birth_date', ''),
            'Gender': personal_info.get('gender', ''),
            'Phone': personal_info.get('contact_numbers', [''])[0] if personal_info.get('contact_numbers') else '',
            'Address1': location.get('address_1', ''),
            'Address2': location.get('address_2', ''),
            'Suburb': location.get('suburb', ''),
            'PostCode': location.get('postcode', ''),
            'Concerns': personal_info.get('concerns', ''),
            'ACN': self.get_acn(client),
            'ServiceStartDate': self.get_first_service_date(client)
        }
        
        # Add service type information
        service_types = self.get_service_types(client)
        field_mappings['ServiceTypes'] = service_types
        field_mappings['Type'] = service_types[0] if service_types else ''
        
        # Apply configured field mappings
        for template_field, source_value in field_mappings.items():
            if source_value is not None:
                mapped_data[template_field] = source_value
        
        # Add fixed values from config
        fixed_values = config.get('fixed_values', {})
        for field, value in fixed_values.items():
            mapped_data[field] = value
        
        return mapped_data
    
    def filter_clients_by_service(self, clients: List[Dict[str, Any]], 
                                service_type: str, limit: int = 1, random_selection: bool = False) -> List[Dict[str, Any]]:
        """Filter clients by service type and return limited number."""
        
        # First, collect all clients with the service type
        matching_clients = []
        
        for client in clients:
            service_types = self.get_service_types(client)
            if service_type in service_types:
                matching_clients.append(client)
        
        self.logger.info(f"Found {len(matching_clients)} total clients with {service_type} service")
        
        # Return random selection or first N clients
        if random_selection and len(matching_clients) > limit:
            import random
            selected_clients = random.sample(matching_clients, limit)
            self.logger.info(f"Randomly selected {len(selected_clients)} clients with {service_type} service")
            return selected_clients
        else:
            # Return first N clients
            filtered_clients = matching_clients[:limit]
            self.logger.info(f"Selected first {len(filtered_clients)} clients with {service_type} service")
            return filtered_clients