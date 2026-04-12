"""
Forecasts Page
Trend analysis and simple forecasting.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path
import numpy as np

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_daily_trends
from src.utils import calculate_trend, forecast_linear, detect_anomaly, get_last_n_days
from components.filters import render_date_range_filter
from components.charts import render_trend_chart

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(page_title="Forecasts", page_icon="📈")
st.title("📈 Forecasts & Trend Analysis")

st.markdown("""
Understand your SEO trends and make predictions:
- **Historical trends**: What's been happening
- **Moving averages**: Smooth out daily fluctuations
- **Simple forecasts**: Predict next 7-30 days
- **Anomalies**: Detect unusual spikes or dips
""")

# ============================================================
# FILTERS
# ============================================================

st.subheader("Filters")
col1, col2, col3 = st.columns(3)

with col1:
    start_date, end_date = render_date_range_filter("forecast")

with col2:
    metric = st.selectbox(
        "Metric to Forecast",
        ["clicks", "impressions", "sessions"],
        key="forecast_metric"
    )

with col3:
    forecast_days = st.slider(
        "Days to Forecast",
        min_value=7,
        max_value=30,
        value=14,
        help="Predict this many days into the future"
    )

st.markdown("---")

# ============================================================
# TREND ANALYSIS
# ============================================================

try:
    trends_df = get_daily_trends(start_date, end_date, metric)
    
    if trends_df.empty:
        st.warning("No data available for trend analysis")
    else:
        # ---- HISTORICAL TREND ----
        st.subheader("📊 Historical Trend")
        
        render_trend_chart(
            trends_df,
            date_col='date',
            value_col='value',
            title=f"Daily {metric.title()} - Historical"
        )
        
        # ---- TREND STATISTICS ----
        st.markdown("---")
        st.subheader("📈 Trend Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = int(trends_df['value'].sum())
            st.metric(f"Total {metric.title()}", f"{total_value:,}")
        
        with col2:
            avg_value = trends_df['value'].mean()
            st.metric(f"Daily Average", f"{int(avg_value):,}")
        
        with col3:
            max_value = trends_df['value'].max()
            max_date = trends_df[trends_df['value'] == max_value]['date'].values[0]
            st.metric(f"Peak {metric.title()}", f"{int(max_value):,}", f"on {max_date}")
        
        with col4:
            min_value = trends_df['value'].min()
            min_date = trends_df[trends_df['value'] == min_value]['date'].values[0]
            st.metric(f"Low {metric.title()}", f"{int(min_value):,}", f"on {min_date}")
        
        # ---- TREND DIRECTION ----
        st.markdown("---")
        st.subheader("🎯 Trend Direction")
        
        trend_pct = calculate_trend(trends_df['value'].tolist())
        
        if trend_pct > 10:
            st.success(f"📈 **Trending UP**: +{trend_pct:.1f}% over period")
            st.markdown("Your SEO is improving! Keep up the good work.")
        elif trend_pct > 0:
            st.info(f"📊 **Slight UP**: +{trend_pct:.1f}% over period")
            st.markdown("Modest progress. Consider increasing efforts.")
        elif trend_pct > -10:
            st.warning(f"📉 **Slight DOWN**: {trend_pct:.1f}% over period")
            st.markdown("Slight decline. Review recent changes and competitors.")
        else:
            st.error(f"📉 **Trending DOWN**: {trend_pct:.1f}% over period")
            st.markdown("Significant decline. Investigate potential issues.")
        
        # ---- ANOMALIES ----
        st.markdown("---")
        st.subheader("🚨 Anomalies Detected")
        
        anomalies = []
        values_list = trends_df['value'].tolist()
        dates_list = trends_df['date'].tolist()
        
        for i, (date, value) in enumerate(zip(dates_list, values_list)):
            # Check last 7 days as history
            if i >= 7:
                historical = values_list[max(0, i-7):i]
                if detect_anomaly(value, historical, threshold=1.5):
                    anomalies.append({
                        'date': date,
                        'value': int(value),
                        'type': 'spike' if value > np.mean(historical) else 'dip'
                    })
        
        if anomalies:
            for anom in anomalies[-5:]:  # Show last 5
                if anom['type'] == 'spike':
                    st.warning(f"📈 **Spike on {anom['date']}**: {anom['value']:,} {metric} (unusual high)")
                else:
                    st.error(f"📉 **Dip on {anom['date']}**: {anom['value']:,} {metric} (unusual low)")
                st.markdown("""
                *Possible causes:* Algorithm update, backlink change, content update, 
                technical issues, or seasonal pattern. Investigate!
                """)
        else:
            st.success("✓ No major anomalies detected")
        
        # ---- FORECAST ----
        st.markdown("---")
        st.subheader(f"🔮 Forecast - Next {forecast_days} Days")
        
        # Simple linear regression forecast
        forecast = forecast_linear(trends_df['value'], periods=forecast_days)
        
        # Create forecast dataframe
        last_date = pd.to_datetime(trends_df['date'].iloc[-1])
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'value': forecast.values
        })
        
        # Combine historical + forecast
        combined_df = pd.concat([
            trends_df.assign(type='Historical'),
            forecast_df.assign(type='Forecast')
        ])
        
        # Visualization
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        # Historical
        historical = trends_df
        fig.add_trace(go.Scatter(
            x=historical['date'],
            y=historical['value'],
            mode='lines+markers',
            name='Historical',
            line=dict(color='#FF6B35', width=2),
            marker=dict(size=6)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['value'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#FF6B35', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title=f"Forecast: {metric.title()} over next {forecast_days} days",
            xaxis_title="Date",
            yaxis_title=metric.title(),
            template="plotly_white",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ---- FORECAST SUMMARY ----
        st.markdown("---")
        st.subheader("📊 Forecast Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            current_value = int(trends_df['value'].iloc[-1])
            st.metric("Current (Today)", current_value)
        
        with col2:
            forecasted_value = int(forecast_df['value'].iloc[-1])
            change = forecasted_value - current_value
            pct_change = (change / current_value * 100) if current_value > 0 else 0
            st.metric(f"Forecast (Day +{forecast_days})", forecasted_value, f"{pct_change:+.1f}%")
        
        with col3:
            if pct_change > 0:
                st.success(f"📈 Projected growth: +{int(change):,}")
            elif pct_change < 0:
                st.warning(f"📉 Projected decline: {int(change):,}")
            else:
                st.info(f"➡️ Projected stable: ~{int(change):,}")
        
        st.info("""
        **⚠️ Forecast Disclaimer:**
        This is a simple linear regression forecast based on historical trends.
        It assumes:
        - Trends continue as they have
        - No major algorithm updates or site changes
        - No seasonal fluctuations
        
        Use as a guide, not a guarantee. Always monitor actual performance.
        """)
        
        # ---- RECOMMENDATIONS ----
        st.markdown("---")
        st.subheader("💡 Recommendations")
        
        if trend_pct > 0:
            st.success("""
            ✓ **Keep momentum going:**
            - Continue with current SEO strategies
            - Document what's working
            - Scale up successful tactics
            """)
        elif trend_pct < -10:
            st.error("""
            ⚠️ **Address declining trend:**
            - Review recent changes (technical, content, links)
            - Check for algorithm updates
            - Analyze competitor moves
            - Perform SEO audit
            """)
        
        if anomalies:
            st.warning("""
            🔍 **Investigate anomalies:**
            - Check Google Search Console for messages
            - Review analytics for traffic source changes
            - Verify no technical issues
            - Monitor competitor websites
            """)

except Exception as e:
    st.error(f"Error loading forecast data: {str(e)}")
    st.info("💡 Make sure you have data across your selected date range")
