"""
Reusable Filter Components
Date ranges, country, device filters used across all pages.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from backend.src.utils import get_last_n_days, get_last_month
from backend.src.database import get_unique_values


def render_date_range_filter(key_prefix: str = ""):
    """
    Date range picker with presets (Last 7 days, Last 30, etc).
    
    Returns:
        Tuple of (start_date_str, end_date_str)
    """
    
    # Create two columns: preset buttons + custom date pickers
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("**Presets:**")
        preset = st.radio(
            "Select period",
            ["Last 7 days", "Last 30 days", "Last Month", "Custom"],
            key=f"{key_prefix}_preset"
        )
    
    with col2:
        if preset == "Last 7 days":
            start, end = get_last_n_days(7)
        elif preset == "Last 30 days":
            start, end = get_last_n_days(30)
        elif preset == "Last Month":
            start, end = get_last_month()
        else:  # Custom
            start = str(st.date_input(
                "Start date",
                value=datetime.now() - timedelta(days=30),
                key=f"{key_prefix}_start"
            ))
            end = str(st.date_input(
                "End date",
                value=datetime.now(),
                key=f"{key_prefix}_end"
            ))
    
    return start, end


def render_location_filter():
    """
    Country/region filter multiselect.
    Returns list of selected countries or None (all).
    """
    try:
        countries = get_unique_values('country', 'gsc_data')
        
        selected = st.multiselect(
            "📍 Filter by Country",
            options=countries,
            default=None,
            key="country_filter"
        )
        
        return selected if selected else None
    except Exception as e:
        st.warning(f"Could not load countries: {str(e)}")
        return None


def render_device_filter():
    """
    Device type filter (Desktop, Mobile, Tablet).
    Returns list of selected devices or None (all).
    """
    try:
        devices = get_unique_values('device', 'gsc_data')
        
        selected = st.multiselect(
            "📱 Filter by Device",
            options=devices,
            default=None,
            key="device_filter"
        )
        
        return selected if selected else None
    except Exception as e:
        st.warning(f"Could not load devices: {str(e)}")
        return None


def apply_filters(df: pd.DataFrame, countries: list = None, devices: list = None) -> pd.DataFrame:
    """
    Apply selected filters to DataFrame.
    """
    if countries:
        df = df[df['country'].isin(countries)] if 'country' in df.columns else df
    
    if devices:
        df = df[df['device'].isin(devices)] if 'device' in df.columns else df
    
    return df


def render_metric_filter():
    """
    Select which metric to sort/analyze (clicks, impressions, CTR, position).
    Returns selected metric name.
    """
    metric = st.selectbox(
        "📊 Primary Metric",
        ["Clicks", "Impressions", "CTR", "Position"],
        index=0,
        key="metric_filter"
    )
    
    return metric.lower()
