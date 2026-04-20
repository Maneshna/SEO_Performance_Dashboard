"""
Page Analysis Page
Landing page performance: best pages, engagement metrics, opportunities.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_top_pages, get_pages_with_ga4, get_data_date_range
from components.filters import render_date_range_filter
from components.charts import render_data_table, render_metric_table, render_bar_chart

# PAGE SETUP

st.set_page_config(page_title="Page Analysis", page_icon="📄")
st.title("📄 Page Analysis - Landing Page Performance")

st.markdown("""
Which of your pages are winning in search?
- **Top Pages**: Pages driving the most search traffic
- **Engagement**: Sessions, bounce rate, conversions per page
- **Cannibalization**: Pages competing for same query
""")

# FILTERS

st.subheader("Filters")
col1, col2 = st.columns(2)

with col1:
    start_date, end_date = render_date_range_filter("pages")

with col2:
    view_type = st.radio(
        "View",
        ["Search Only", "With Engagement Metrics"],
        index=1
    )

st.markdown("---")

# TOP PAGES

try:
    if view_type == "Search Only":
        # GSC data only
        st.subheader("🏆 Top Pages by Search Traffic")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Ranked by **Clicks** from search")
        with col2:
            limit = st.slider("Show top N", 5, 50, 20, key="page_limit")
        
        top_pages = get_top_pages(start_date, end_date, limit=limit)
        
        if not top_pages.empty:
            # Format display
            display_pages = top_pages.copy()
            display_pages['ctr'] = display_pages['ctr'].apply(lambda x: f"{x:.2%}")
            display_pages['position'] = display_pages['position'].apply(lambda x: f"{x:.1f}")
            
            render_metric_table(display_pages, "Pages")
            
            # Chart
            st.markdown("#### Clicks by Page")
            render_bar_chart(
                top_pages.head(10),
                x_col='page_url',
                y_col='clicks',
                title="Top 10 Pages by Clicks",
                orientation='h'
            )
            
            #  INSIGHTS 
            st.markdown("---")
            st.subheader("📊 Page Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_ctr = top_pages['ctr'].mean()
                st.metric("Avg CTR across pages", f"{avg_ctr:.2%}")
            
            with col2:
                avg_pos = top_pages['position'].mean()
                st.metric("Avg Position", f"{avg_pos:.1f}")
            
            with col3:
                uniqueness = (top_pages['unique_queries'].sum() / len(top_pages)).round(0)
                st.metric("Avg Keywords per Page", f"{int(uniqueness)}")
        
        else:
            st.info("No page data available")
    
    else:
        # GSC + GA4 combined
        st.subheader("🏆 Pages with Full Engagement Data")
        st.markdown("Combining **search performance** + **user engagement**")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("Shows clicks, sessions, conversions, bounce rate")
        with col2:
            limit = st.slider("Show top N", 5, 50, 20, key="ga4_limit")
        
        pages_ga4 = get_pages_with_ga4(start_date, end_date, limit=limit)
        
        if not pages_ga4.empty:
            # Fill NaN values
            pages_ga4 = pages_ga4.fillna(0)
            
            # Format display
            display_ga4 = pages_ga4.copy()
            display_ga4['ctr'] = display_ga4['ctr'].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
            display_ga4['bounce_rate'] = display_ga4['bounce_rate'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
            display_ga4['position'] = display_ga4['position'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/A")
            
            render_metric_table(display_ga4, "Pages with Engagement Metrics")
            
            #  MULTI-METRIC ANALYSIS 
            st.markdown("---")
            st.subheader("🎯 Multi-Metric Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Sessions by Page")
                render_bar_chart(
                    pages_ga4.head(10),
                    x_col='page_url',
                    y_col='sessions',
                    title="Top Pages by Sessions",
                    orientation='h'
                )
            
            with col2:
                st.markdown("#### Conversions by Page")
                render_bar_chart(
                    pages_ga4[pages_ga4['conversions'] > 0].head(10),
                    x_col='page_url',
                    y_col='conversions',
                    title="Pages with Conversions",
                    orientation='h'
                )
            
            #  HIGH BOUNCE RATE PAGES 
            st.markdown("---")
            st.subheader("⚠️ High Bounce Rate Pages (Optimization Opportunity)")
            
            high_bounce = pages_ga4[pages_ga4['bounce_rate'] > 0.5].sort_values('bounce_rate', ascending=False).head(10)
            
            if not high_bounce.empty:
                display_bounce = high_bounce.copy()
                display_bounce['bounce_rate'] = display_bounce['bounce_rate'].apply(lambda x: f"{x:.1%}")
                display_bounce['sessions'] = display_bounce['sessions'].astype(int)
                
                st.dataframe(display_bounce[['page_url', 'bounce_rate', 'sessions']], use_container_width=True)
                
                st.info("""
                **High bounce rate means:**
                - Visitors land but don't explore further
                - Page may have poor UX, slow load, or mismatched content
                
                **Fix it:**
                1. Improve page load speed
                2. Add clear internal links
                3. Ensure content matches search intent
                4. Improve mobile responsiveness
                """)
            else:
                st.success("✓ All pages have healthy bounce rates!")
        
        else:
            st.info("No page data available")

except Exception as e:
    st.error(f"Error loading page data: {str(e)}")
    st.info("💡 Upload both GSC and GA4 data for best results")
