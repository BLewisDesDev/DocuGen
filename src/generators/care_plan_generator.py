# File: src/generators/care_plan_generator.py

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any
from docx2pdf import convert

class CarePlanGenerator:
    """Handles care plan document generation and PDF conversion."""
    
    def __init__(self, output_dir: Path, app_config: Dict[str, Any]):
        self.output_dir = Path(output_dir)
        self.app_config = app_config
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_document(self, template_path: Path, data: Dict[str, Any], 
                         template_processor, generate_pdf: bool = True) -> Dict[str, Path]:
        """Generate a single document from template and data."""
        
        try:
            # Process template
            doc = template_processor.process_template(template_path, data)
            
            # Generate filename
            filename = self._generate_filename(data)
            
            # Save Word document
            docx_path = self.output_dir / f"{filename}.docx"
            docx_path = self._handle_duplicate_file(docx_path)
            
            doc.save(str(docx_path))
            self.logger.debug(f"Generated Word document: {docx_path}")
            
            result = {'docx': docx_path}
            
            # Generate PDF if requested
            if generate_pdf:
                pdf_path = self._generate_pdf(docx_path)
                if pdf_path:
                    result['pdf'] = pdf_path
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate document for {data.get('client_name', 'unknown')}: {str(e)}")
            raise
    
    def _generate_filename(self, data: Dict[str, Any]) -> str:
        """Generate filename from data using configured pattern."""
        
        # Get naming pattern from config or use default
        pattern = self.app_config.get('output', {}).get('naming_pattern', 
                                                       "{client_name}_{date_processed}")
        
        # Prepare variables for filename
        filename_data = {
            'client_name': self._sanitize_filename(data.get('client_name', 'Unknown')),
            'template_name': 'care_plan',
            'date_processed': self._get_current_date(),
            'row_number': data.get('_row_number', '001')
        }
        
        # Add custom client ID if available
        if 'client_id' in data and data['client_id']:
            filename_data['client_id'] = self._sanitize_filename(str(data['client_id']))
            # Use client_id instead of client_name if available
            pattern = pattern.replace('{client_name}', '{client_id}')
        
        try:
            filename = pattern.format(**filename_data)
        except KeyError as e:
            self.logger.warning(f"Missing variable in filename pattern: {e}")
            # Fallback to simple pattern
            filename = f"{filename_data['client_name']}_{filename_data['row_number']}"
        
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing invalid characters."""
        
        import re
        # Remove or replace invalid filename characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', str(filename))
        sanitized = re.sub(r'\s+', '_', sanitized)  # Replace spaces with underscores
        sanitized = sanitized.strip('._')  # Remove leading/trailing dots and underscores
        
        return sanitized[:50]  # Limit length
    
    def _get_current_date(self) -> str:
        """Get current date in YYYYMMDD format."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d')
    
    def _handle_duplicate_file(self, file_path: Path) -> Path:
        """Handle duplicate files by adding suffix."""
        
        if not file_path.exists():
            return file_path
        
        # Get duplicate handling strategy from config
        strategy = self.app_config.get('output', {}).get('duplicate_handling', 'rename')
        
        if strategy == 'overwrite':
            return file_path
        elif strategy == 'skip':
            self.logger.info(f"Skipping duplicate file: {file_path}")
            return file_path
        else:  # rename (default)
            counter = 1
            stem = file_path.stem
            suffix = file_path.suffix
            parent = file_path.parent
            
            while True:
                new_name = f"{stem}_{counter:03d}{suffix}"
                new_path = parent / new_name
                if not new_path.exists():
                    return new_path
                counter += 1
    
    def _generate_pdf(self, docx_path: Path) -> Path:
        """Generate PDF from Word document."""
        
        pdf_path = docx_path.with_suffix('.pdf')
        
        try:
            # Try docx2pdf first
            convert(str(docx_path), str(pdf_path))
            
            if pdf_path.exists():
                self.logger.debug(f"Generated PDF: {pdf_path}")
                return pdf_path
            else:
                raise Exception("PDF file was not created")
                
        except Exception as e:
            self.logger.warning(f"docx2pdf failed: {str(e)}")
            
            # Fallback to LibreOffice if available
            return self._generate_pdf_libreoffice(docx_path)
    
    def _generate_pdf_libreoffice(self, docx_path: Path) -> Path:
        """Generate PDF using LibreOffice as fallback."""
        
        try:
            # Try LibreOffice command line
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(docx_path.parent),
                str(docx_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            pdf_path = docx_path.with_suffix('.pdf')
            if result.returncode == 0 and pdf_path.exists():
                self.logger.debug(f"Generated PDF with LibreOffice: {pdf_path}")
                return pdf_path
            else:
                self.logger.warning(f"LibreOffice conversion failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.warning("LibreOffice conversion timed out")
            return None
        except FileNotFoundError:
            self.logger.warning("LibreOffice not found in PATH")
            return None
        except Exception as e:
            self.logger.warning(f"LibreOffice conversion error: {str(e)}")
            return None