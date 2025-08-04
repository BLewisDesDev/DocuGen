#!/usr/bin/env python3
# File: scripts/test_headless_export.py

import sys
import os
import logging
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.exporters.headless_pdf_exporter import HeadlessPdfExporter
from src.core.config_loader import ConfigLoader

def main():
    """Test headless PDF export capabilities."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Load config
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        
        # Initialize exporter
        exporter = HeadlessPdfExporter(app_config)
        
        # Check available converters
        print("=== Checking Available PDF Converters ===")
        availability = exporter.check_available_converters()
        
        for tool, available in availability.items():
            status = "✅ Available" if available else "❌ Not Available"
            print(f"{tool}: {status}")
        
        # Show installation suggestions for missing tools
        print("\n=== Installation Suggestions for Missing Tools ===")
        suggestions = exporter.install_suggestions()
        
        for tool, available in availability.items():
            if not available:
                print(f"\n{tool}:")
                print(suggestions.get(tool, "No installation instructions available"))
        
        # Test conversion if we have any available converters
        available_converters = [tool for tool, available in availability.items() if available]
        
        if available_converters:
            print(f"\n=== Available Converters: {', '.join(available_converters)} ===")
            
            # Look for a test DOCX file
            test_files = [
                "output/test_client_map/*.docx",
                "output/*.docx", 
                "templates/*.docx"
            ]
            
            import glob
            test_docx = None
            
            for pattern in test_files:
                matches = glob.glob(pattern)
                if matches:
                    test_docx = Path(matches[0])
                    break
            
            if test_docx and test_docx.exists():
                print(f"\nTesting conversion with: {test_docx}")
                
                pdf_result = exporter.convert_to_pdf(test_docx)
                
                if pdf_result:
                    print(f"✅ Successfully converted to: {pdf_result}")
                    print(f"PDF size: {pdf_result.stat().st_size} bytes")
                else:
                    print("❌ Conversion failed")
            else:
                print("\nNo test DOCX files found. Run the main generation script first.")
        else:
            print("\n❌ No PDF converters available. Install one of the suggested tools.")
            
    except Exception as e:
        logger.error(f"Error in headless export test: {e}")
        raise

if __name__ == "__main__":
    main()