"""
Overview Page - KPI Dashboard
Main landing page with health metrics and summary charts.
"""

import streamlit as st
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_kpi_summary, get_daily_trends, get_data_date_range
from components.filters import render_date_range_filter
from components.charts import render_kpi_card, render_kpi_grid, render_trend_chart
from src.utils import format_number, format_percentage, get_date_range_label

# PAGE SETUP


st.set_page_config(page_title="Overview", page_icon="📊")
st.title("📊 Overview - SEO Health Dashboard")

# FILTERS

st.subheader("Filters")
col1, col2, col3 = st.columns(3)

with col1:
    start_date, end_date = render_date_range_filter("overview")

with col2:
    st.markdown("**No additional filters on this page**")

with col3:
    st.markdown("")  # Placeholder for alignment

st.markdown("---")

# FETCH DATA

try:
    kpi_data = get_kpi_summary(start_date, end_date)
    
    #  KPI CARDS 
    st.subheader("Key Performance Indicators")
    
    metrics = {
        'clicks': {
            'label': 'Total Clicks',
            'value': format_number(kpi_data['total_clicks']),
            'change': '🖱️ From search results',
            'icon': '🖱️'
        },
        'impressions': {
            'label': 'Total Impressions',
            'value': format_number(kpi_data['total_impressions']),
            'change': '📍 Times shown in search',
            'icon': '📍'
        },
        'ctr': {
            'label': 'Avg CTR',
            'value': format_percentage(kpi_data['avg_ctr']),
            'change': f"Good CTR is >2%",
            'icon': '📈'
        },
        'position': {
            'label': 'Avg Position',
            'value': format_number(kpi_data['avg_position'], 1),
            'change': 'Lower is better (rank 1-10)',
            'icon': '🥇'
        },
    }
    
    render_kpi_grid(metrics)
    
    #  SECONDARY METRICS (GA4) 
    st.markdown("---")
    st.subheader("Engagement Metrics (from GA4)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_kpi_card(
            label="Total Sessions",
            value=format_number(kpi_data['total_sessions']),
            change="Users who landed on your pages",
            icon="👥"
        )
    
    with col2:
        render_kpi_card(
            label="Conversions",
            value=format_number(kpi_data['total_conversions']),
            change="Goals/transactions completed",
            icon="✅"
        )
    
    with col3:
        # Calculate conversion rate
        conv_rate = (
            (kpi_data['total_conversions'] / kpi_data['total_sessions'] * 100)
            if kpi_data['total_sessions'] > 0 else 0
        )
        render_kpi_card(
            label="Conversion Rate",
            value=f"{conv_rate:.2f}%",
            change="Sessions → Conversions",
            icon="🎯"
        )
    
    #  TREND CHARTS 
    st.markdown("---")
    st.subheader("Daily Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Clicks Over Time")
        clicks_trends = get_daily_trends(start_date, end_date, 'clicks')
        if not clicks_trends.empty:
            render_trend_chart(clicks_trends, 'date', 'value', "Daily Clicks Trend")
        else:
            st.info("No trend data available for this period")
    
    with col2:
        st.markdown("#### Impressions Over Time")
        impression_trends = get_daily_trends(start_date, end_date, 'impressions')
        if not impression_trends.empty:
            render_trend_chart(impression_trends, 'date', 'value', "Daily Impressions Trend")
        else:
            st.info("No trend data available for this period")
    
    #  INSIGHTS 
    st.markdown("---")
    st.subheader("💡 Quick Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        if kpi_data['avg_position'] < 3:
            st.success("🏆 Great ranking position! Average position is in top 3")
        elif kpi_data['avg_position'] < 10:
            st.info("📈 Moderate ranking. You're in top 10, but room for improvement")
        else:
            st.warning("⚠️ Low ranking. Most pages beyond top 10. Focus on SEO optimization")
    
    with insight_col2:
        if kpi_data['avg_ctr'] > 0.05:
            st.success("✨ Excellent CTR! Your titles/descriptions are compelling")
        elif kpi_data['avg_ctr'] > 0.02:
            st.info("📝 Moderate CTR. Test A/B variations of titles and meta descriptions")
        else:
            st.warning("⚠️ Low CTR. Improve meta titles and descriptions")
    
    with insight_col3:
        if kpi_data['total_clicks'] > 100:
            st.success(f"🎉 Strong search traffic: {format_number(kpi_data['total_clicks'])} clicks")
        elif kpi_data['total_clicks'] > 10:
            st.info("📊 Building momentum. Continue SEO efforts")
        else:
            st.warning("⏳ Low search traffic. Need SEO improvements")
    
    #  EXPORT OPTION 
    st.markdown("---")
    st.markdown("### 📥 Export Report")
    
    report_data = {
        'Metric': [
            'Total Clicks',
            'Total Impressions',
            'Avg CTR',
            'Avg Position',
            'Total Sessions',
            'Total Conversions'
        ],
        'Value': [
            kpi_data['total_clicks'],
            kpi_data['total_impressions'],
            f"{kpi_data['avg_ctr']:.4f}",
            f"{kpi_data['avg_position']:.2f}",
            kpi_data['total_sessions'],
            kpi_data['total_conversions']
        ]
    }
    
    import pandas as pd
    report_df = pd.DataFrame(report_data)
    
    csv = report_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"seo_overview_report_{start_date}_{end_date}.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("💡 Tip: Upload GSC and GA4 data using the sidebar first")
