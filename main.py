#!/usr/bin/env python3
# File: main.py
"""
DocuGen - Document Generator CLI

Main entry point for the DocuGen document processing system.
Processes Excel data through Word templates to generate personalized documents.

Usage:
    python main.py --help
    python main.py process --config mappers/care_plans_mapper.yaml --data data/clients.xlsx
    python main.py validate --config mappers/care_plans_mapper.yaml

Author: Byron
Date: June 30, 2025
"""

from src.cli import cli

if __name__ == '__main__':
    cli()