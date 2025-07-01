# File: create_sample_data.py
"""
Script to create sample Excel data for testing DocuGen.

Run this to create test data matching the care plans configuration.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import random

def create_sample_excel_data():
    """Create sample Excel data for testing."""
    
    # Sample data matching the care plans configuration
    sample_data = [
        {
            'ACN': 'C001',
            'GivenName': 'John',
            'FamilyName': 'Smith',
            'BirthDate': '1985-03-15',
            'GenderCode': 'Male',
            'AddressLine1': '123 Main Street',
            'AddressLine2': '',
            'Suburb': 'Sydney',
            'Postcode': '2000',
            'Type': 'HM'
        },
        {
            'ACN': 'C002',
            'GivenName': 'Jane',
            'FamilyName': 'Doe',
            'BirthDate': '1978-07-22',
            'GenderCode': 'Female',
            'AddressLine1': '456 Oak Avenue',
            'AddressLine2': 'Unit 2',
            'Suburb': 'Melbourne',
            'Postcode': '3000',
            'Type': 'DA'
        },
        {
            'ACN': 'C003',
            'GivenName': 'Bob',
            'FamilyName': 'Wilson',
            'BirthDate': '1960-12-05',
            'GenderCode': 'Male',
            'AddressLine1': '789 Pine Road',
            'AddressLine2': '',
            'Suburb': 'Brisbane',
            'Postcode': '4000',
            'Type': 'PC'
        },
        {
            'ACN': 'C004',
            'GivenName': 'Mary',
            'FamilyName': 'Johnson',
            'BirthDate': '1972-09-18',
            'GenderCode': 'Female',
            'AddressLine1': '321 Cedar Lane',
            'AddressLine2': 'Apt 5B',
            'Suburb': 'Perth',
            'Postcode': '6000',
            'Type': 'CA'
        },
        {
            'ACN': 'C005',
            'GivenName': 'David',
            'FamilyName': 'Brown',
            'BirthDate': '1955-04-30',
            'GenderCode': 'Male',
            'AddressLine1': '654 Elm Street',
            'AddressLine2': '',
            'Suburb': 'Adelaide',
            'Postcode': '5000',
            'Type': 'HM'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Ensure data directory exists
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save to Excel
    excel_path = data_dir / "sample_clients.xlsx"
    df.to_excel(excel_path, index=False)
    
    print(f"✓ Created sample Excel data: {excel_path}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    
    return excel_path

def create_larger_sample(num_rows=50):
    """Create a larger sample dataset for performance testing."""
    
    first_names = ['John', 'Jane', 'Bob', 'Mary', 'David', 'Sarah', 'Mike', 'Lisa', 'Tom', 'Anna']
    last_names = ['Smith', 'Doe', 'Wilson', 'Johnson', 'Brown', 'Davis', 'Miller', 'Garcia', 'Rodriguez', 'Martinez']
    suburbs = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Canberra', 'Darwin', 'Hobart']
    postcodes = ['2000', '3000', '4000', '6000', '5000', '2600', '0800', '7000']
    service_types = ['HM', 'DA', 'PC', 'CA']
    genders = ['Male', 'Female']
    
    data = []
    for i in range(num_rows):
        # Generate random birth date between 1940 and 1990
        start_date = datetime(1940, 1, 1)
        end_date = datetime(1990, 12, 31)
        birth_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Random suburb and postcode (matching)
        suburb_idx = random.randint(0, len(suburbs) - 1)
        
        row = {
            'ACN': f'C{i+1:03d}',
            'GivenName': random.choice(first_names),
            'FamilyName': random.choice(last_names),
            'BirthDate': birth_date.strftime('%Y-%m-%d'),
            'GenderCode': random.choice(genders),
            'AddressLine1': f'{random.randint(1, 999)} {random.choice(["Main", "Oak", "Pine", "Elm", "Cedar"])} {random.choice(["Street", "Avenue", "Road", "Lane"])}',
            'AddressLine2': random.choice(['', f'Unit {random.randint(1, 20)}', f'Apt {random.randint(1, 10)}A']),
            'Suburb': suburbs[suburb_idx],
            'Postcode': postcodes[suburb_idx],
            'Type': random.choice(service_types)
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save to Excel
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    excel_path = data_dir / f"sample_clients_{num_rows}.xlsx"
    df.to_excel(excel_path, index=False)
    
    print(f"✓ Created large sample Excel data: {excel_path}")
    print(f"  Rows: {len(df)}")
    
    return excel_path

if __name__ == "__main__":
    # Create small sample
    create_sample_excel_data()
    
    # Create larger sample for testing
    create_larger_sample(50)