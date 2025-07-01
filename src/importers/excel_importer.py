# File: src/importers/excel_importer.py

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExcelImporter:
    """Handles Excel file reading and data mapping."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_file(self, file_path: str) -> pd.DataFrame:
        """Read Excel file and return DataFrame."""
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        try:
            # Read Excel file
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_path.suffix.lower() == '.xls':
                df = pd.read_excel(file_path, engine='xlrd')
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()
            
            self.logger.info(f"📊 Loaded Excel file: {file_path}")
            self.logger.info(f"   Rows: {len(df)}")
            self.logger.info(f"   Columns: {len(df.columns)}")
            self.logger.debug(f"   Column names: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to read Excel file {file_path}: {str(e)}")
            raise
    
    def map_data(self, df: pd.DataFrame, mapper_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Map DataFrame columns to template variables."""
        
        field_mappings = mapper_config.get('field_mappings', {})
        transformations = mapper_config.get('transformations', {})
        required_fields = mapper_config.get('required_fields', [])
        fixed_values = mapper_config.get('fixed_values', {})
        
        mapped_rows = []
        warnings = []
        
        for idx, row in df.iterrows():
            mapped_row = {}
            row_warnings = []
            
            # Map each field
            for excel_col, template_var in field_mappings.items():
                if excel_col in df.columns:
                    value = row[excel_col]
                    
                    # Handle NaN values
                    if pd.isna(value):
                        value = ""
                        if excel_col in required_fields:
                            row_warnings.append(f"Missing required field: {excel_col}")
                    
                    # Apply transformations
                    if template_var in transformations:
                        value = self._apply_transformation(value, transformations[template_var])
                    
                    mapped_row[template_var] = value
                else:
                    # Column not found
                    mapped_row[template_var] = ""
                    if excel_col in required_fields:
                        row_warnings.append(f"Required column not found: {excel_col}")
            
            # Add fixed values
            for key, value in fixed_values.items():
                mapped_row[key] = value
            
            # Create client_name from FirstName + LastName for file naming
            first_name = mapped_row.get('FirstName', '').strip()
            last_name = mapped_row.get('LastName', '').strip()
            if first_name or last_name:
                mapped_row['client_name'] = f"{first_name} {last_name}".strip()
            else:
                mapped_row['client_name'] = mapped_row.get('ACN', 'Unknown')
            
            # Process service types for checkbox logic
            service_types = mapper_config.get('service_types', {})
            current_service = mapped_row.get('ServiceType', '').strip()
            
            # Set all service type boolean flags
            for service_code, service_name in service_types.items():
                # Create boolean flag for each service type
                mapped_row[f'{service_code}_selected'] = (current_service == service_code)
                # Also create readable name
                mapped_row[f'{service_code}_name'] = service_name
            
            # Legacy support - set the Type variable for template compatibility
            mapped_row['Type'] = current_service
            
            # Add row metadata
            mapped_row['_row_number'] = idx + 1
            mapped_row['_has_warnings'] = len(row_warnings) > 0
            mapped_row['_warnings'] = row_warnings
            
            mapped_rows.append(mapped_row)
            warnings.extend([f"Row {idx + 1}: {w}" for w in row_warnings])
        
        # Log warnings
        if warnings:
            self.logger.warning(f"Data mapping warnings ({len(warnings)} total):")
            for warning in warnings[:10]:  # Show first 10
                self.logger.warning(f"  {warning}")
            if len(warnings) > 10:
                self.logger.warning(f"  ... and {len(warnings) - 10} more warnings")
        
        self.logger.info(f"✅ Data mapping completed: {len(mapped_rows)} rows processed")
        return mapped_rows
    
    def _apply_transformation(self, value: Any, transformation: str) -> Any:
        """Apply data transformation to a value."""
        
        if pd.isna(value) or value == "":
            return value
        
        try:
            if transformation.startswith('date_format:'):
                # Date formatting: date_format:%d/%m/%Y
                date_format = transformation.split(':', 1)[1]
                if isinstance(value, datetime):
                    return value.strftime(date_format)
                elif isinstance(value, str):
                    # Try to parse string as date
                    parsed_date = pd.to_datetime(value)
                    return parsed_date.strftime(date_format)
                else:
                    return str(value)
            
            elif transformation == 'title_case':
                return str(value).title()
            
            elif transformation == 'upper_case':
                return str(value).upper()
            
            elif transformation == 'lower_case':
                return str(value).lower()
            
            elif transformation == 'strip_whitespace':
                return str(value).strip()
            
            elif transformation == 'clean_nan':
                # Handle NaN/null values by returning empty string
                if pd.isna(value) or value is None or str(value).lower() in ['nan', 'null', 'none']:
                    return ""
                return str(value).strip()
            
            else:
                self.logger.warning(f"Unknown transformation: {transformation}")
                return value
                
        except Exception as e:
            self.logger.warning(f"Transformation failed for value '{value}' with '{transformation}': {str(e)}")
            return value
    
    def validate_columns(self, df: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """Validate that required columns exist in DataFrame."""
        
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            self.logger.info(f"Available columns: {list(df.columns)}")
        
        return missing_columns