# File: src/cli/commands.py

import click
import os
from pathlib import Path
from ..core.config_loader import ConfigLoader
from ..importers.excel_importer import ExcelImporter
from ..core.document_processor import DocumentProcessor
from ..utils.logger import setup_logging

@click.group()
def cli():
    """DocuGen - Document Generator CLI"""
    pass

@cli.command()
@click.option('--config', required=True, help='Path to mapper configuration file')
@click.option('--data', required=True, help='Path to Excel data file')
@click.option('--output', default='output', help='Output directory')
@click.option('--dry-run', is_flag=True, help='Validate configuration and preview data without generating documents')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--start-row', type=int, help='Start processing from specific row number')
@click.option('--end-row', type=int, help='End processing at specific row number')
@click.option('--no-pdf', is_flag=True, help='Skip PDF generation (Word documents only)')
@click.option('--resume', is_flag=True, help='Resume from previous session')
def process(config, data, output, dry_run, verbose, start_row, end_row, no_pdf, resume):
    """Process Excel data through templates to generate documents."""
    
    # Setup logging
    log_level = 'DEBUG' if verbose else 'INFO'
    logger = setup_logging(log_level)
    
    try:
        # Load configuration
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        mapper_config = config_loader.load_mapper_config(config)
        
        # Initialize processor
        processor = DocumentProcessor(app_config, mapper_config, output)
        
        if dry_run:
            processor.validate_and_preview(data, start_row, end_row)
        else:
            processor.process_documents(
                data_file=data,
                start_row=start_row,
                end_row=end_row,
                generate_pdf=not no_pdf,
                resume=resume
            )
            
    except Exception as e:
        if logger:
            logger.error(f"Processing failed: {str(e)}")
        else:
            click.echo(f"Error: Processing failed: {str(e)}", err=True)
        raise click.ClickException(str(e))

@cli.command()
@click.option('--config', required=True, help='Path to mapper configuration file')
def validate(config):
    """Validate configuration and template files."""
    
    logger = setup_logging('INFO')
    
    try:
        config_loader = ConfigLoader()
        app_config = config_loader.load_app_config()
        mapper_config = config_loader.load_mapper_config(config)
        
        # Create processor for validation
        processor = DocumentProcessor(app_config, mapper_config, 'temp')
        
        # Validate template
        template_path = Path(mapper_config['template_file'])
        if not template_path.is_absolute():
            template_path = Path('templates') / template_path
            
        processor.validate_template(template_path)
        
        click.echo("✅ Configuration and template validation successful!")
        
    except Exception as e:
        if logger:
            logger.error(f"Validation failed: {str(e)}")
        else:
            click.echo(f"Error: Validation failed: {str(e)}", err=True)
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()