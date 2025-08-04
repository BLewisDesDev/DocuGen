# File: src/exporters/headless_pdf_exporter.py

import logging
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

class HeadlessPdfExporter:
    """Headless PDF export using multiple conversion tools without GUI dependencies."""
    
    def __init__(self, app_config: Dict[str, Any]):
        self.app_config = app_config
        self.logger = logging.getLogger(__name__)
    
    def convert_to_pdf(self, docx_path: Path) -> Optional[Path]:
        """Convert DOCX to PDF using available headless tools."""
        
        pdf_path = docx_path.with_suffix('.pdf')
        
        # Try conversion methods in order of preference
        converters = [
            self._try_libreoffice,
            self._try_pandoc,
            self._try_docx2pdf,
            self._try_unoconv,
            self._try_python_docx2pdf
        ]
        
        for converter in converters:
            try:
                if converter(docx_path, pdf_path):
                    self.logger.info(f"Successfully converted {docx_path} to PDF using {converter.__name__}")
                    return pdf_path
            except Exception as e:
                self.logger.debug(f"{converter.__name__} failed: {e}")
                continue
        
        self.logger.error(f"All PDF conversion methods failed for {docx_path}")
        return None
    
    def _try_pandoc(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert using pandoc (requires pandoc + LaTeX)."""
        
        if not shutil.which('pandoc'):
            raise Exception("pandoc not found in PATH")
        
        cmd = [
            'pandoc',
            str(docx_path),
            '-o', str(pdf_path),
            '--pdf-engine=xelatex',  # or pdflatex
            '--variable', 'geometry:margin=1in'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and pdf_path.exists():
            return True
        else:
            raise Exception(f"pandoc failed: {result.stderr}")
    
    def _try_libreoffice(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert using LibreOffice headless mode."""
        
        if not shutil.which('libreoffice'):
            raise Exception("libreoffice not found in PATH")
        
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(pdf_path.parent),
            str(docx_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and pdf_path.exists():
            return True
        else:
            raise Exception(f"LibreOffice failed: {result.stderr}")
    
    def _try_docx2pdf(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert using docx2pdf (may still require Word on macOS)."""
        
        try:
            from docx2pdf import convert
            convert(str(docx_path), str(pdf_path))
            
            if pdf_path.exists():
                return True
            else:
                raise Exception("PDF file was not created")
                
        except ImportError:
            raise Exception("docx2pdf package not installed")
    
    def _try_unoconv(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert using unoconv (LibreOffice Python bridge)."""
        
        if not shutil.which('unoconv'):
            raise Exception("unoconv not found in PATH")
        
        cmd = [
            'unoconv',
            '-f', 'pdf',
            '-o', str(pdf_path),
            str(docx_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and pdf_path.exists():
            return True
        else:
            raise Exception(f"unoconv failed: {result.stderr}")
    
    def _try_python_docx2pdf(self, docx_path: Path, pdf_path: Path) -> bool:
        """Convert using python-docx + reportlab (pure Python solution)."""
        
        try:
            from docx import Document
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Read DOCX content
            doc = Document(str(docx_path))
            
            # Create PDF
            pdf_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Convert paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    para = Paragraph(paragraph.text, styles['Normal'])
                    story.append(para)
                    story.append(Spacer(1, 12))
            
            # Build PDF
            pdf_doc.build(story)
            
            if pdf_path.exists():
                return True
            else:
                raise Exception("PDF file was not created")
                
        except ImportError as e:
            raise Exception(f"Required packages not installed: {e}")
    
    def check_available_converters(self) -> Dict[str, bool]:
        """Check which conversion tools are available on the system."""
        
        availability = {}
        
        # Check command-line tools
        tools = {
            'pandoc': 'pandoc',
            'libreoffice': 'libreoffice',
            'unoconv': 'unoconv'
        }
        
        for name, command in tools.items():
            availability[name] = shutil.which(command) is not None
        
        # Check Python packages
        python_packages = {
            'docx2pdf': 'docx2pdf',
            'python-docx + reportlab': ['docx', 'reportlab']
        }
        
        for name, packages in python_packages.items():
            if isinstance(packages, str):
                packages = [packages]
            
            try:
                for package in packages:
                    __import__(package)
                availability[name] = True
            except ImportError:
                availability[name] = False
        
        return availability
    
    def install_suggestions(self) -> Dict[str, str]:
        """Provide installation suggestions for missing tools."""
        
        suggestions = {
            'pandoc': 'brew install pandoc basictex  # macOS\nsudo apt install pandoc texlive-latex-base  # Ubuntu',
            'libreoffice': 'brew install --cask libreoffice  # macOS\nsudo apt install libreoffice  # Ubuntu',
            'unoconv': 'brew install unoconv  # macOS\nsudo apt install unoconv  # Ubuntu',
            'docx2pdf': 'pip install docx2pdf',
            'python-docx + reportlab': 'pip install python-docx reportlab'
        }
        
        return suggestions