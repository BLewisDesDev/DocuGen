# File: src/core/config_loader.py

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Handles loading and validation of YAML configuration files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_app_config(self, config_path: str = "config/app_config.yaml") -> Dict[str, Any]:
        """Load application configuration."""
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Application config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['logging', 'processing', 'paths', 'output']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
        
        # Create directories if they don't exist
        for path_key, path_value in config.get('paths', {}).items():
            Path(path_value).mkdir(parents=True, exist_ok=True)
        
        self.logger.debug(f"Loaded app config from: {config_path}")
        return config
    
    def load_mapper_config(self, config_path: str) -> Dict[str, Any]:
        """Load mapper configuration."""
        
        self.logger.debug(f"Loading mapper config: {config_path}")
        
        # Support both old path (config/) and new path (mappers/)
        config_file = Path(config_path)
        
        # If relative path, try mappers/ directory first, then config/
        if not config_file.is_absolute():
            mapper_path = Path('mappers') / config_path
            config_path_fallback = Path('config') / config_path
            
            self.logger.debug(f"Trying mapper path: {mapper_path}")
            self.logger.debug(f"Mapper path exists: {mapper_path.exists()}")
            
            if mapper_path.exists():
                config_file = mapper_path
            elif config_path_fallback.exists():
                # Fallback to config directory for backward compatibility
                config_file = config_path_fallback
                self.logger.debug(f"Using fallback path: {config_file}")
            else:
                # Show what files actually exist
                mappers_dir = Path('mappers')
                if mappers_dir.exists():
                    available_files = list(mappers_dir.glob('*.yaml'))
                    self.logger.error(f"Available mapper files: {available_files}")
                raise FileNotFoundError(f"Mapper config file not found: {config_path}")
        
        if not config_file.exists():
            raise FileNotFoundError(f"Mapper config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['project_name', 'template_file', 'field_mappings']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required mapper config field: {field}")
        
        self.logger.debug(f"Loaded mapper config from: {config_file}")
        return config
    
    def get_setting(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get a nested configuration setting using dot notation."""
        
        keys = path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value