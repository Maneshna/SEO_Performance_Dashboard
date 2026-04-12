"""
Query Analysis Page
Deep dive into search queries: top performers, bottom performers, trends.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_top_queries, get_bottom_queries, get_data_date_range
from components.filters import render_date_range_filter, render_metric_filter
from components.charts import render_data_table, render_metric_table, render_bar_chart

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(page_title="Query Analysis", page_icon="🔍")
st.title("🔍 Query Analysis - Search Keywords")

st.markdown("""
Every query tells a story:
- **Top Queries**: Keywords already performing well
- **Bottom Queries**: Keywords with high impressions but low CTR (optimize!)
- **Opportunities**: Where you can gain the most clicks with minimal effort
""")

# ============================================================
# FILTERS
# ============================================================

st.subheader("Filters & Settings")
col1, col2 = st.columns(2)

with col1:
    start_date, end_date = render_date_range_filter("query")

with col2:
    metric = render_metric_filter()

st.markdown("---")

# ============================================================
# TOP QUERIES
# ============================================================

try:
    st.subheader("🏆 Top Performing Queries")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Sorted by **{metric.title()}**")
    with col2:
        limit = st.slider("Show top N", 5, 50, 10, key="top_limit")
    
    top_queries = get_top_queries(start_date, end_date, limit=limit, metric=metric)
    
    if not top_queries.empty:
        # Format table columns
        top_queries_display = top_queries.copy()
        top_queries_display['ctr'] = top_queries_display['ctr'].apply(lambda x: f"{x:.2%}")
        top_queries_display['position'] = top_queries_display['position'].apply(lambda x: f"{x:.1f}")
        
        render_metric_table(top_queries_display, "Top Queries")
        
        # Bar chart
        st.markdown("#### Clicks by Query")
        render_bar_chart(
            top_queries.head(15),
            x_col='query',
            y_col='clicks',
            title="Top 15 Queries by Clicks",
            orientation='h'
        )
    else:
        st.info("No query data available for selected period")
    
    # ============================================================
    # BOTTOM QUERIES (OPPORTUNITIES)
    # ============================================================
    
    st.markdown("---")
    st.subheader("⚠️ Optimization Opportunities")
    st.markdown("""
    These queries have **high impressions but low CTR**.
    They're "almost winning" — improve your ranking or title/description to capture more clicks!
    """)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**High Impressions, Low CTR**")
    with col2:
        opp_limit = st.slider("Show top N", 5, 50, 15, key="opp_limit")
    
    bottom_queries = get_bottom_queries(start_date, end_date, limit=opp_limit)
    
    if not bottom_queries.empty:
        # Calculate opportunity score
        bottom_queries['opportunity_score'] = (
            bottom_queries['impressions'] * (1 - bottom_queries['ctr'])
        )
        
        # Format for display
        display_queries = bottom_queries.copy()
        display_queries['ctr'] = display_queries['ctr'].apply(lambda x: f"{x:.2%}")
        display_queries['position'] = display_queries['position'].apply(lambda x: f"{x:.1f}")
        display_queries['opportunity_score'] = display_queries['opportunity_score'].apply(
            lambda x: f"{int(x)}"
        )
        
        render_metric_table(display_queries, "Queries Worth Optimizing")
        
        st.markdown("#### Opportunity Score by Query")
        render_bar_chart(
            bottom_queries.head(10),
            x_col='query',
            y_col='opportunity_score',
            title="Top 10 Optimization Opportunities",
            orientation='h'
        )
        
        # ---- RECOMMENDATION ----
        st.markdown("---")
        st.subheader("💡 Next Steps for Opportunities")
        
        top_opp = bottom_queries.iloc[0]
        st.info(f"""
        **Top Opportunity: "{top_opp['query']}"**
        - **Impressions**: {int(top_opp['impressions'])} (people seeing your result)
        - **Current CTR**: {top_opp['ctr']:.2%} (only {int(top_opp['clicks'])} clicks)
        - **Avg Position**: {top_opp['position']:.1f}
        
        **What to do:**
        1. **Improve Ranking**: Target position 1-3 with better content or backlinks
        2. **Improve CTR**: If ranking well (#1-3), optimize meta title and description
        3. **Check Intent Match**: Ensure your page truly answers the query
        """)
    else:
        st.info("No opportunity data available")

except Exception as e:
    st.error(f"Error loading query data: {str(e)}")
    st.info("💡 Make sure you've uploaded GSC data in the sidebar")
