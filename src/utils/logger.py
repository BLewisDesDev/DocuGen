# File: src/utils/logger.py
"""
Logging utilities for DocuGen.
"""

import logging
from pathlib import Path
from datetime import datetime

def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """Set up logging configuration."""
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Generate log file name if not provided
    if not log_file:
        log_file = f"logs/docugen_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Configure logging
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    numeric_level = level_map.get(level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        force=True
    )
    
    logging.info(f"Logging configured: level={level}, file={log_file}")
