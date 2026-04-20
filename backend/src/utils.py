"""
Utility Functions
Helper functions for calculations, formatting, and caching.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import List, Tuple



# FORMATTING UTILITIES


def format_number(value, decimals=0):
    """Format number with thousands separator."""
    if pd.isna(value):
        return "N/A"
    if decimals == 0:
        return f"{int(value):,}"
    return f"{float(value):,.{decimals}f}"


def format_percentage(value, decimals=1):
    """Format as percentage."""
    if pd.isna(value):
        return "N/A"
    return f"{float(value)*100:.{decimals}f}%"


def format_position(value, decimals=2):
    """Format search position."""
    if pd.isna(value) or value == 0:
        return "N/A"
    return f"{float(value):.{decimals}f}"



# SEO CALCULATIONS

def calculate_ctr_potential(current_ctr: float, average_ctr: float) -> str:
    """
    Compare query/page CTR to average.
    Returns insight string.
    """
    if pd.isna(current_ctr) or pd.isna(average_ctr) or average_ctr == 0:
        return "Insufficient data"
    
    potential = (average_ctr - current_ctr) / average_ctr * 100
    
    if potential < -20:
        return "Outperforming average"
    elif potential < 0:
        return "Slightly above average"
    elif potential < 20:
        return "Slight opportunity"
    elif potential < 50:
        return "Moderate opportunity"
    else:
        return "High opportunity"


def calculate_position_impact(position: float, position_ctr_map: dict = None) -> str:
    """
    Estimate CTR impact based on position.
    Based on industry benchmarks.
    
    Default benchmark:
    Position 1: ~30%
    Position 5: ~10%
    Position 10: ~3%
    """
    if pd.isna(position) or position == 0:
        return "N/A"
    
    # Industry benchmark: lower position = lower CTR
    benchmarks = {
        1: 0.28, 2: 0.15, 3: 0.10, 4: 0.08, 5: 0.06,
        6: 0.04, 7: 0.03, 8: 0.03, 9: 0.02, 10: 0.02
    }
    
    pos = int(position)
    if pos in benchmarks:
        expected_ctr = benchmarks[pos]
        return f"Expected CTR: ~{format_percentage(expected_ctr)}"
    elif pos > 10:
        return "Position >10: Very low CTR expected"
    else:
        return "Above benchmark for position"


def estimate_click_uplift(current_position: float, target_position: float, current_clicks: int) -> int:
    """
    Estimate additional clicks if position improves.
    Based on logarithmic position curve.
    """
    if pd.isna(current_position) or pd.isna(target_position) or current_clicks == 0:
        return 0
    
    # Rough position-to-CTR model
    ctr_by_pos = {
        1: 0.28, 2: 0.15, 3: 0.10, 4: 0.08, 5: 0.06,
        6: 0.04, 7: 0.03, 8: 0.03, 9: 0.02, 10: 0.02
    }
    
    current_pos = int(current_position)
    target_pos = int(target_position)
    
    current_ctr = ctr_by_pos.get(current_pos, 0.01)
    target_ctr = ctr_by_pos.get(target_pos, 0.01)
    
    # Impression constant needed to convert clicks to CTR
    # clicks = impressions * ctr
    # If we assume constant impressions, CTR change = clicks change
    additional_clicks = int((target_ctr - current_ctr) / current_ctr * current_clicks)
    
    return max(0, additional_clicks)



# DATE UTILITIES


def get_date_range_label(start_date: str, end_date: str) -> str:
    """Format date range as readable string."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    days = (end - start).days + 1
    
    return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')} ({days} days)"


def get_last_n_days(n: int) -> Tuple[str, str]:
    """Get start and end date for last N days."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=n-1)
    return (str(start_date), str(end_date))


def get_last_month() -> Tuple[str, str]:
    """Get start and end date for last calendar month."""
    end_date = datetime.now().date().replace(day=1) - timedelta(days=1)
    start_date = end_date.replace(day=1)
    return (str(start_date), str(end_date))



# TREND ANALYSIS


def calculate_trend(values: List[float]) -> float:
    """
    Calculate trend direction and magnitude.
    Returns: percentage change from first to last value.
    """
    if len(values) < 2:
        return 0
    
    first = values[0]
    last = values[-1]
    
    if first == 0:
        return 0
    
    return ((last - first) / first) * 100


def calculate_moving_average(series: pd.Series, window: int = 7) -> pd.Series:
    """Calculate rolling moving average."""
    return series.rolling(window=window, min_periods=1).mean()


def detect_anomaly(value: float, historical_values: List[float], threshold: float = 2.0) -> bool:
    """
    Detect if value is anomalous using standard deviation.
    
    Args:
        value: Value to check
        historical_values: List of historical values
        threshold: Number of std deviations to consider anomaly (default: 2)
    
    Returns:
        True if value is an anomaly, False otherwise
    """
    if len(historical_values) < 3:
        return False
    
    mean = np.mean(historical_values)
    std_dev = np.std(historical_values)
    
    if std_dev == 0:
        return False
    
    z_score = abs((value - mean) / std_dev)
    return z_score > threshold


def forecast_linear(series: pd.Series, periods: int = 7) -> pd.Series:
    """
    Simple linear regression forecast.
    
    Args:
        series: Time series with numeric values
        periods: Number of periods to forecast
    
    Returns:
        Forecasted values for next N periods
    """
    if len(series) < 2:
        return pd.Series([series.iloc[-1]] * periods)
    
    x = np.arange(len(series))
    y = series.values
    
    # Linear regression: y = mx + b
    coeffs = np.polyfit(x, y, 1)
    
    # Forecast next periods
    future_x = np.arange(len(series), len(series) + periods)
    forecast = np.polyval(coeffs, future_x)
    
    return pd.Series(forecast, index=range(len(series), len(series) + periods))



# DATAFRAME OPERATIONS


def safe_divide(numerator: pd.Series, denominator: pd.Series, fill_value: float = 0) -> pd.Series:
    """
    Safely divide two series, handling division by zero.
    """
    return numerator.divide(denominator).fillna(fill_value).replace([np.inf, -np.inf], fill_value)


def rank_by_opportunity(df: pd.DataFrame, impressions_col: str, ctr_col: str) -> pd.DataFrame:
    """
    Rank rows by opportunity score.
    opportunity_score = impressions * (1 - ctr)
    """
    df = df.copy()
    df['opportunity_score'] = (
        df[impressions_col].fillna(0) * 
        (1 - df[ctr_col].fillna(0))
    )
    return df.sort_values('opportunity_score', ascending=False)


if __name__ == "__main__":
    # Test utilities
    print(format_number(1234.5, decimals=2))  # 1,234.50
    print(format_percentage(0.156))  # 15.6%
    print(calculate_trend([100, 120, 140]))  # 40.0 (40% increase)
