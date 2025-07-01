# File: src/core/document_processor.py

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from tqdm import tqdm

from ..importers.excel_importer import ExcelImporter
from ..templates.jinja_processor import JinjaProcessor
from ..generators.care_plan_generator import CarePlanGenerator
from ..utils.logger import setup_logging

class DocumentProcessor:
    """
    Main document processing pipeline.
    Coordinates data import, template processing, and document generation.
    """
    
    def __init__(self, app_config: Dict[str, Any], mapper_config: Dict[str, Any], output_dir: str):
        self.app_config = app_config
        self.mapper_config = mapper_config
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.importer = ExcelImporter()
        self.template_processor = JinjaProcessor()
        self.generator = CarePlanGenerator(self.output_dir, app_config)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_and_preview(self, data_file: str, start_row: Optional[int] = None, end_row: Optional[int] = None):
        """Validate configuration and preview data without generating documents."""
        
        self.logger.info("🔍 Starting validation and preview...")
        
        # Validate template
        template_path = self._get_template_path()
        self.validate_template(template_path)
        
        # Load and preview data
        data = self.importer.read_file(data_file)
        
        # Apply row filtering
        if start_row or end_row:
            data = self._filter_rows(data, start_row, end_row)
        
        # Map data
        mapped_data = self.importer.map_data(data, self.mapper_config)
        
        # Show preview
        self._show_data_preview(mapped_data)
        
        self.logger.info("✅ Validation and preview completed successfully!")
    
    def process_documents(self, data_file: str, start_row: Optional[int] = None, 
                         end_row: Optional[int] = None, generate_pdf: bool = True, 
                         resume: bool = False):
        """Process all documents from data file."""
        
        self.logger.info("🚀 Starting document processing...")
        
        # Load data
        data = self.importer.read_file(data_file)
        
        # Apply row filtering
        if start_row or end_row:
            data = self._filter_rows(data, start_row, end_row)
        
        # Map data
        mapped_data = self.importer.map_data(data, self.mapper_config)
        
        # Get template
        template_path = self._get_template_path()
        
        # Process each row
        success_count = 0
        failed_count = 0
        
        with tqdm(total=len(mapped_data), desc="Generating documents") as pbar:
            for idx, row_data in enumerate(mapped_data):
                try:
                    # Generate document
                    self.generator.generate_document(
                        template_path=template_path,
                        data=row_data,
                        template_processor=self.template_processor,
                        generate_pdf=generate_pdf
                    )
                    success_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process row {idx + 1}: {str(e)}")
                    failed_count += 1
                
                pbar.update(1)
        
        # Summary
        self.logger.info(f"✅ Processing completed!")
        self.logger.info(f"   Success: {success_count}")
        self.logger.info(f"   Failed: {failed_count}")
        self.logger.info(f"   Output: {self.output_dir}")
    
    def validate_template(self, template_path: Path):
        """Validate template file and extract variables."""
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        # Validate template syntax
        variables = self.template_processor.extract_template_variables(template_path)
        
        self.logger.info(f"✅ Template validation successful!")
        self.logger.info(f"   Template: {template_path}")
        self.logger.info(f"   Variables found: {len(variables)}")
        self.logger.debug(f"   Variables: {variables}")
        
        return variables
    
    def _get_template_path(self) -> Path:
        """Get the full path to the template file."""
        template_file = self.mapper_config['template_file']
        template_path = Path(template_file)
        
        if not template_path.is_absolute():
            template_path = Path('templates') / template_path
        
        return template_path
    
    def _filter_rows(self, data, start_row: Optional[int], end_row: Optional[int]):
        """Filter data rows based on start/end parameters."""
        if start_row is not None:
            start_idx = max(0, start_row - 1)  # Convert to 0-based index
        else:
            start_idx = 0
        
        if end_row is not None:
            end_idx = min(len(data), end_row)  # Convert to 0-based index
        else:
            end_idx = len(data)
        
        filtered = data.iloc[start_idx:end_idx].copy()
        
        self.logger.info(f"📊 Row filtering: {len(data)} → {len(filtered)} rows")
        return filtered
    
    def _show_data_preview(self, mapped_data):
        """Show a preview of the mapped data."""
        
        self.logger.info(f"📊 Data Preview:")
        self.logger.info(f"   Total rows: {len(mapped_data)}")
        
        if len(mapped_data) > 0:
            # Show first row as sample
            sample_row = mapped_data[0]
            self.logger.info(f"   Sample data:")
            for key, value in sample_row.items():
                self.logger.info(f"     {key}: {value}")