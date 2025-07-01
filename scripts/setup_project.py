# File: setup_project.py
"""
Script to create the DocuGen project structure
Run this to set up the initial directory structure and files.
"""

import os
from pathlib import Path

def create_project_structure():
    """Create the complete DocuGen project directory structure."""
    
    # Project root (current directory)
    root = Path(".")
    
    # Directory structure
    directories = [
        "src",
        "src/config",
        "src/data", 
        "src/templates",
        "src/output",
        "src/utils",
        "config",
        "templates",
        "data",
        "output",
        "logs"
    ]
    
    # Create directories
    for dir_path in directories:
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {full_path}")
    
    # Create __init__.py files for Python packages
    init_files = [
        "src/__init__.py",
        "src/config/__init__.py", 
        "src/data/__init__.py",
        "src/templates/__init__.py",
        "src/output/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for init_file in init_files:
        full_path = root / init_file
        full_path.touch()
        print(f"✓ Created: {full_path}")
    
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Run: pip install -r requirements.txt")
    print("2. Place your Excel file in: data/")
    print("3. Place your Word template in: templates/")

if __name__ == "__main__":
    create_project_structure()