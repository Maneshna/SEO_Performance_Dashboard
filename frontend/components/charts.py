"""
Reusable Chart Components
Plotly charts for all pages.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st


# KPI METRICS CARDS


def render_kpi_card(label: str, value: str, change: str = None, icon: str = "📈"):
    """
    Render single KPI metric card.
    
    Args:
        label: Metric name (e.g., "Total Clicks")
        value: Main metric value (e.g., "1,234")
        change: Trend indicator (e.g., "+12% vs last month")
        icon: Emoji icon
    """
    with st.container():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"# {icon}")
        
        with col2:
            st.markdown(f"### {label}")
            st.markdown(f"# {value}")
            if change:
                st.markdown(f"*{change}*")


def render_kpi_grid(metrics: dict):
    """
    Render 4 KPI cards in a grid.
    
    Args:
        metrics: Dict with keys like:
        {
            'clicks': {'value': '1234', 'change': '+4%', 'icon': '🖱️'},
            'impressions': {...},
            'ctr': {...},
            'position': {...}
        }
    """
    
    cols = st.columns(4)
    
    for i, (key, data) in enumerate(metrics.items()):
        with cols[i]:
            render_kpi_card(
                label=data.get('label', key.title()),
                value=data['value'],
                change=data.get('change'),
                icon=data.get('icon', '📊')
            )



# LINE CHARTS


def render_trend_chart(df: pd.DataFrame, date_col: str = 'date', value_col: str = 'value', title: str = "Trend"):
    """
    Line chart for daily/time series metrics.
    
    Args:
        df: DataFrame with date and value columns
        date_col: Name of date column
        value_col: Name of value column
        title: Chart title
    """
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df[date_col],
        y=df[value_col],
        mode='lines+markers',
        name=value_col.title(),
        fill='tozeroy',
        line=dict(color='#FF6B35', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=value_col.title(),
        template="plotly_white",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# BAR CHART


def render_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, orientation: str = "v"):
    """
    Bar chart for categorical comparisons.
    
    Args:
        df: Input DataFrame
        x_col: Column for X-axis
        y_col: Column for Y-axis
        title: Chart title
        orientation: 'v' (vertical) or 'h' (horizontal)
    """
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = px.bar(
        df,
        x=x_col if orientation == "v" else y_col,
        y=y_col if orientation == "v" else x_col,
        title=title,
        template="plotly_white",
        color=y_col,
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(height=400, hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)


# SCATTER PLOT


def render_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, size_col: str = None, color_col: str = None, title: str = "Scatter"):
    """
    Scatter plot for relationship analysis (e.g., position vs CTR).
    
    Args:
        df: Input DataFrame
        x_col: X-axis column
        y_col: Y-axis column
        size_col: Column for bubble size (optional)
        color_col: Column for color (optional)
        title: Chart title
    """
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        hover_data=df.columns,
        title=title,
        template="plotly_white"
    )
    
    fig.update_layout(height=400, hovermode='closest')
    st.plotly_chart(fig, use_container_width=True)


# TABLE RENDERING

def render_data_table(df: pd.DataFrame, title: str = None, max_rows: int = 20):
    """
    Render interactive data table.
    """
    
    if df.empty:
        st.info("No data available")
        return
    
    # Show top N rows only
    display_df = df.head(max_rows)
    
    if title:
        st.subheader(title)
    
    st.dataframe(display_df, use_container_width=True)
    
    if len(df) > max_rows:
        st.caption(f"Showing {max_rows} of {len(df)} rows")


def render_metric_table(df: pd.DataFrame, title: str = None):
    """
    Render styled metric table with key columns highlighted.
    """
    
    if df.empty:
        st.info("No data available")
        return
    
    if title:
        st.subheader(title)
    
    # Format common columns
    display_df = df.copy()
    
    # Highlight columns with conditional formatting
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            'ctr': st.column_config.NumberColumn(format="%.2%%"),
            'position': st.column_config.NumberColumn(format="%.1f"),
            'bounce_rate': st.column_config.NumberColumn(format="%.1%%"),
        }
    )
