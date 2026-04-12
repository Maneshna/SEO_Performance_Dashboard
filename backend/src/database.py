"""
SQLite Database Setup & Queries
All the SQL logic for creating tables, inserting data, and fetching reports.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta

# Path to database file
DB_PATH = Path(__file__).parent.parent.parent / "data" / "seo_dashboard.db"

# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_database():
    """
    Create SQLite database and all required tables if they don't exist.
    Run this ONCE at the very beginning.
    """
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ---- GSC TABLE (Google Search Console data) ----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gsc_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        query TEXT NOT NULL,
        page_url TEXT NOT NULL,
        country TEXT,
        device TEXT,
        search_type TEXT DEFAULT 'Web',
        clicks INTEGER NOT NULL DEFAULT 0,
        impressions INTEGER NOT NULL DEFAULT 0,
        ctr REAL,
        position REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, query, page_url, country, device)
    )
    """)
    
    # ---- GA4 TABLE (Google Analytics 4 data) ----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ga4_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        page_url TEXT NOT NULL,
        device TEXT,
        country TEXT,
        sessions INTEGER NOT NULL DEFAULT 0,
        users INTEGER NOT NULL DEFAULT 0,
        bounces INTEGER NOT NULL DEFAULT 0,
        bounce_rate REAL,
        avg_session_duration REAL,
        conversions INTEGER NOT NULL DEFAULT 0,
        conversion_value REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, page_url, device, country)
    )
    """)
    
    # ---- METADATA TABLE (for tracking ingestions) ----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingestion_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,  -- 'gsc' or 'ga4'
        file_name TEXT,
        rows_imported INTEGER,
        imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indexes for faster queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsc_date ON gsc_data(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsc_query ON gsc_data(query)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_gsc_page ON gsc_data(page_url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ga4_date ON ga4_data(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ga4_page ON ga4_data(page_url)")
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized at {DB_PATH}")


# ============================================================
# DATA INSERTION
# ============================================================

def insert_gsc_data(df: pd.DataFrame) -> int:
    """
    Insert GSC data from DataFrame into database.
    Returns number of rows inserted.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO gsc_data 
            (date, query, page_url, country, device, search_type, clicks, impressions, ctr, position)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row['Date']),
                str(row['Query']),
                str(row['Page']),
                str(row.get('Country', 'Unknown')),
                str(row.get('Device', 'Desktop')),
                str(row.get('Search Type', 'Web')),
                int(row['Clicks']),
                int(row['Impressions']),
                float(row.get('CTR', 0)),
                float(row.get('Position', 0))
            ))
            inserted += cursor.rowcount
        except Exception as e:
            print(f"Error inserting GSC row: {e}")
    
    conn.commit()
    conn.close()
    return inserted


def insert_ga4_data(df: pd.DataFrame) -> int:
    """
    Insert GA4 data from DataFrame into database.
    Returns number of rows inserted.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO ga4_data 
            (date, page_url, device, country, sessions, users, bounces, bounce_rate, avg_session_duration, conversions, conversion_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row['Date']),
                str(row['Page']),
                str(row.get('Device', 'desktop')),
                str(row.get('Country', 'Unknown')),
                int(row.get('Sessions', 0)),
                int(row.get('Users', 0)),
                int(row.get('Bounces', 0)),
                float(row.get('Bounce Rate', 0)),
                float(row.get('Avg Session Duration', 0)),
                int(row.get('Conversions', 0)),
                float(row.get('Conversion Value', 0))
            ))
            inserted += cursor.rowcount
        except Exception as e:
            print(f"Error inserting GA4 row: {e}")
    
    conn.commit()
    conn.close()
    return inserted


# ============================================================
# KPI QUERIES (for Overview page)
# ============================================================

def get_kpi_summary(start_date: str, end_date: str, country: str = None, device: str = None) -> Dict:
    """
    Get overall SEO health metrics.
    Returns: dict with clicks, impressions, CTR, position, sessions, conversions.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_clauses = [
        f"date BETWEEN '{start_date}' AND '{end_date}'"
    ]
    if country:
        where_clauses.append(f"country = '{country}'")
    if device:
        where_clauses.append(f"device = '{device}'")
    
    where_filter = " AND ".join(where_clauses)
    
    # GSC metrics
    cursor.execute(f"""
    SELECT 
        SUM(clicks) as total_clicks,
        SUM(impressions) as total_impressions,
        ROUND(AVG(ctr), 4) as avg_ctr,
        ROUND(AVG(position), 2) as avg_position
    FROM gsc_data
    WHERE {where_filter}
    """)
    gsc_row = cursor.fetchone()
    
    # GA4 metrics
    cursor.execute(f"""
    SELECT 
        SUM(sessions) as total_sessions,
        SUM(conversions) as total_conversions
    FROM ga4_data
    WHERE {where_filter}
    """)
    ga4_row = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_clicks': gsc_row[0] or 0,
        'total_impressions': gsc_row[1] or 0,
        'avg_ctr': gsc_row[2] or 0,
        'avg_position': gsc_row[3] or 999,
        'total_sessions': ga4_row[0] or 0,
        'total_conversions': ga4_row[1] or 0,
    }


def get_top_queries(start_date: str, end_date: str, limit: int = 10, metric: str = 'clicks') -> pd.DataFrame:
    """
    Get top performing queries sorted by metric (clicks, impressions, or position).
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = f"""
    SELECT 
        query,
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        ROUND(AVG(ctr), 4) as ctr,
        ROUND(AVG(position), 2) as position,
        COUNT(DISTINCT page_url) as pages
    FROM gsc_data
    WHERE date BETWEEN ? AND ?
    GROUP BY query
    ORDER BY {metric} DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date, limit))
    conn.close()
    return df


def get_bottom_queries(start_date: str, end_date: str, limit: int = 10) -> pd.DataFrame:
    """
    Get lowest performing queries (high impressions, low CTR).
    Opportunity for improvement!
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        query,
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        ROUND(AVG(ctr), 4) as ctr,
        ROUND(AVG(position), 2) as position
    FROM gsc_data
    WHERE date BETWEEN ? AND ?
        AND impressions >= 10
    GROUP BY query
    ORDER BY ctr ASC, impressions DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date, limit))
    conn.close()
    return df


# ============================================================
# PAGE QUERIES (for Page Analysis)
# ============================================================

def get_top_pages(start_date: str, end_date: str, limit: int = 20) -> pd.DataFrame:
    """
    Get best performing landing pages.
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        page_url,
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        ROUND(AVG(ctr), 4) as ctr,
        ROUND(AVG(position), 2) as position,
        COUNT(DISTINCT query) as unique_queries
    FROM gsc_data
    WHERE date BETWEEN ? AND ?
    GROUP BY page_url
    ORDER BY clicks DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date, limit))
    conn.close()
    return df


def get_pages_with_ga4(start_date: str, end_date: str, limit: int = 20) -> pd.DataFrame:
    """
    Get pages with both GSC and GA4 metrics (full view).
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        COALESCE(g.page_url, a.page_url) as page_url,
        SUM(g.clicks) as gsc_clicks,
        SUM(g.impressions) as impressions,
        ROUND(AVG(g.ctr), 4) as ctr,
        ROUND(AVG(g.position), 2) as position,
        SUM(a.sessions) as sessions,
        SUM(a.conversions) as conversions,
        ROUND(AVG(a.bounce_rate), 2) as bounce_rate
    FROM gsc_data g
    FULL OUTER JOIN ga4_data a 
        ON g.page_url = a.page_url 
        AND g.date = a.date
    WHERE (g.date BETWEEN ? AND ?) OR (a.date BETWEEN ? AND ?)
    GROUP BY page_url
    ORDER BY gsc_clicks DESC
    LIMIT ?
    """
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date, start_date, end_date, limit))
    conn.close()
    return df


# ============================================================
# OPPORTUNITY QUERIES (for Opportunities page)
# ============================================================

def get_opportunities(start_date: str, end_date: str, min_impressions: int = 50) -> pd.DataFrame:
    """
    Find high-impression, low-CTR queries/pages worth optimizing.
    Formula: opportunity_score = impressions * (1 - ctr)
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        query,
        'Query' as type,
        SUM(clicks) as clicks,
        SUM(impressions) as impressions,
        ROUND(AVG(ctr), 4) as ctr,
        ROUND(AVG(position), 2) as position,
        ROUND(SUM(impressions) * (1 - ROUND(AVG(ctr), 4)), 0) as opportunity_score
    FROM gsc_data
    WHERE date BETWEEN ? AND ?
        AND impressions >= ?
    GROUP BY query
    ORDER BY opportunity_score DESC
    LIMIT 20
    """
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date, min_impressions))
    conn.close()
    return df


# ============================================================
# TREND QUERIES (for Forecasting page)
# ============================================================

def get_daily_trends(start_date: str, end_date: str, metric: str = 'clicks') -> pd.DataFrame:
    """
    Get daily aggregated metrics for trend charting.
    """
    conn = sqlite3.connect(DB_PATH)
    
    if metric in ['clicks', 'impressions']:
        query = f"""
        SELECT 
            date,
            SUM({metric}) as value
        FROM gsc_data
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """
    elif metric == 'sessions':
        query = """
        SELECT 
            date,
            SUM(sessions) as value
        FROM ga4_data
        WHERE date BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """
    else:
        raise ValueError(f"Unknown metric: {metric}")
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df


def get_unique_values(column: str, table: str = 'gsc_data') -> List[str]:
    """
    Get unique values for filtering (countries, devices, etc).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT DISTINCT {column} FROM {table} ORDER BY {column}")
    values = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return values


def get_data_date_range() -> Tuple[str, str]:
    """
    Get min and max dates in database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT 
        MIN(date) as min_date,
        MAX(date) as max_date
    FROM (
        SELECT date FROM gsc_data
        UNION ALL
        SELECT date FROM ga4_data
    )
    """)
    
    result = cursor.fetchone()
    conn.close()
    
    return (result[0] or '2024-01-01', result[1] or '2024-01-31')


if __name__ == "__main__":
    # For testing: initialize database
    init_database()
    print("Database ready!")
