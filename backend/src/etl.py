"""
ETL (Extract, Transform, Load) Pipeline
Imports CSV exports from GSC and GA4 into the database.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
import sqlite3
from datetime import datetime

from .database import insert_gsc_data, insert_ga4_data, init_database, DB_PATH



# GSC DATA CLEANING & TRANSFORMATION

def clean_gsc_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw GSC export into clean format.
    
    Expected columns in raw CSV:
    - Date
    - Query
    - Page
    - Country
    - Device
    - Search Type (optional)
    - Clicks
    - Impressions
    - CTR
    - Position (Avg. position)
    """
    
    df = df.copy()
    
    # Column Standardization 
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    
    # Handle different column name variations
    col_mapping = {
        'Avg. position': 'Position',
        'Average Position': 'Position',
        'Avg Position': 'Position',
        'Country': 'Country',
        'Country/Territory': 'Country',
    }
    df = df.rename(columns=col_mapping)
    
    # Data Type Conversion 
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0).astype(int)
    df['Impressions'] = pd.to_numeric(df['Impressions'], errors='coerce').fillna(0).astype(int)
    df['CTR'] = pd.to_numeric(df.get('CTR', 0), errors='coerce').fillna(0)
    df['Position'] = pd.to_numeric(df['Position'], errors='coerce').fillna(0)
    
    # CTR comes as percentage (e.g., "3.5%"), convert to decimal (0.035)
    if df['CTR'].max() > 1:  # If values > 1, assume it's percentage
        df['CTR'] = df['CTR'] / 100
    
    # Data Cleaning 
    df['Query'] = df['Query'].str.strip()
    df['Page'] = df['Page'].str.strip().str.lower()  # Normalize URLs
    
    # Fill missing values
    df['Country'] = df.get('Country', 'Unknown').fillna('Unknown')
    df['Device'] = df.get('Device', 'Desktop').fillna('Desktop')
    df['Search Type'] = df.get('Search Type', 'Web').fillna('Web')
    
    #  Remove Duplicates 
    df = df.drop_duplicates(subset=['Date', 'Query', 'Page', 'Country', 'Device'])
    
    # Remove Spam/Invalid Data 
    df = df[df['Page'].str.startswith('http')]  # Only keep valid URLs
    df = df[df['Impressions'] > 0]  # Only keep rows with impressions
    
    print(f"✓ Cleaned GSC data: {len(df)} rows")
    return df


def clean_ga4_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw GA4 export into clean format.
    
    Expected columns:
    - Date
    - Page (Landing page)
    - Device Category
    - Country
    - Sessions
    - Bounce Rate
    - Avg. Session Duration
    - Conversions (optional)
    """
    
    df = df.copy()
    
    # Column Standardization
    df.columns = df.columns.str.strip()
    
    col_mapping = {
        'Page': 'Page',
        'Landing Page': 'Page',
        'Device Category': 'Device',
        'Device': 'Device',
        'Country': 'Country',
        'Bounce Rate': 'Bounce Rate',
        'Avg. Session Duration': 'Avg Session Duration',
        'Conversion Rate': 'Conversion Rate',
    }
    df = df.rename(columns=col_mapping)
    
    # Data Type Conversion
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df['Sessions'] = pd.to_numeric(df.get('Sessions', 0), errors='coerce').fillna(0).astype(int)
    df['Users'] = pd.to_numeric(df.get('Users', 0), errors='coerce').fillna(0).astype(int)
    df['Bounces'] = pd.to_numeric(df.get('Bounces', 0), errors='coerce').fillna(0).astype(int)
    
    bounce_rate = df.get('Bounce Rate', '0%')
    if isinstance(bounce_rate, str):
        df['Bounce Rate'] = bounce_rate.str.rstrip('%').astype(float) / 100
    else:
        df['Bounce Rate'] = pd.to_numeric(bounce_rate, errors='coerce').fillna(0) / 100
    
    df['Avg Session Duration'] = pd.to_numeric(df.get('Avg Session Duration', 0), errors='coerce').fillna(0)
    df['Conversions'] = pd.to_numeric(df.get('Conversions', 0), errors='coerce').fillna(0).astype(int)
    df['Conversion Value'] = pd.to_numeric(df.get('Conversion Value', 0), errors='coerce').fillna(0)
    
    # ---- Data Cleaning ----
    df['Page'] = df['Page'].str.strip().str.lower()  # Normalize URLs
    df['Device'] = df.get('Device', 'desktop').fillna('desktop').str.lower()
    df['Country'] = df.get('Country', 'Unknown').fillna('Unknown')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['Date', 'Page', 'Device', 'Country'])
    
    # Only keep rows with sessions
    df = df[df['Sessions'] > 0]
    
    print(f"✓ Cleaned GA4 data: {len(df)} rows")
    return df



# FILE IMPORT HELPERS

def load_gsc_csv(file_path: str) -> pd.DataFrame:
    """
    Load and clean GSC CSV export.
    """
    print(f"Loading GSC data from: {file_path}")
    df = pd.read_csv(file_path)
    df = clean_gsc_data(df)
    return df


def load_ga4_csv(file_path: str) -> pd.DataFrame:
    """
    Load and clean GA4 CSV export.
    """
    print(f"Loading GA4 data from: {file_path}")
    df = pd.read_csv(file_path)
    df = clean_ga4_data(df)
    return df



# MAIN ETL ORCHESTRATION


def run_full_etl(gsc_file: str, ga4_file: str = None) -> Tuple[int, int]:
    """
    Main ETL function: init database, load CSVs, insert data.
    
    Returns:
        Tuple of (gsc_rows_inserted, ga4_rows_inserted)
    """
    
    print("\n" + "="*60)
    print("ETL PIPELINE STARTING")
    print("="*60 + "\n")
    
    # 1. Initialize database
    init_database()
    
    # 2. Load and transform GSC
    gsc_rows = 0
    if gsc_file and Path(gsc_file).exists():
        print("\n[1/2] Processing GSC data...")
        gsc_df = load_gsc_csv(gsc_file)
        gsc_rows = insert_gsc_data(gsc_df)
        print(f"✓ Inserted {gsc_rows} GSC records\n")
    
    # 3. Load and transform GA4
    ga4_rows = 0
    if ga4_file and Path(ga4_file).exists():
        print("[2/2] Processing GA4 data...")
        ga4_df = load_ga4_csv(ga4_file)
        ga4_rows = insert_ga4_data(ga4_df)
        print(f"✓ Inserted {ga4_rows} GA4 records\n")
    
    print("="*60)
    print("ETL PIPELINE COMPLETE")
    print(f"Total: {gsc_rows + ga4_rows} rows imported")
    print("="*60 + "\n")
    
    return (gsc_rows, ga4_rows)


if __name__ == "__main__":
    # For testing
    GSC_FILE = Path(__file__).parent.parent / "data" / "gsc_sample.csv"
    GA4_FILE = Path(__file__).parent.parent / "data" / "ga4_sample.csv"
    
    run_full_etl(str(GSC_FILE), str(GA4_FILE))
