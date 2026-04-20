"""
Opportunities Page
Find high-impression, low-CTR pages/queries worth optimizing.
"""

import streamlit as st
import sys
import pandas as pd
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from src.database import get_opportunities, get_data_date_range
from components.filters import render_date_range_filter
from components.charts import render_data_table, render_bar_chart

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(page_title="Opportunities", page_icon="🎯")
st.title("🎯 Opportunities - Quick Wins")

st.markdown("""
The 80/20 of SEO: Find the 20% of work that gives 80% of results.

**Opportunity Score = Impressions × (1 - CTR)**

This metric finds keywords/pages that:
- Already have search visibility (high impressions)
- But have low conversion rate (low CTR)
- Can be "quick wins" with minimal ranking improvement
""")

# ============================================================
# FILTERS
# ============================================================

st.subheader("Filters")
col1, col2, col3 = st.columns(3)

with col1:
    start_date, end_date = render_date_range_filter("opp")

with col2:
    min_impressions = st.slider(
        "Minimum Impressions",
        min_value=10,
        max_value=500,
        value=50,
        step=10,
        help="Only show queries/pages with this many impressions"
    )

with col3:
    st.markdown("*Requirement: At least this many impressions to qualify*")

st.markdown("---")

# ============================================================
# OPPORTUNITIES TABLE
# ============================================================

try:
    st.subheader("🚀 Top Optimization Opportunities")
    
    opportunities = get_opportunities(start_date, end_date, min_impressions=min_impressions)
    
    if not opportunities.empty:
        # Format columns
        opp_display = opportunities.copy()
        opp_display['ctr'] = opp_display['ctr'].apply(lambda x: f"{x:.2%}")
        opp_display['position'] = opp_display['position'].apply(lambda x: f"{x:.1f}")
        opp_display['opportunity_score'] = opp_display['opportunity_score'].astype(int)
        
        st.dataframe(opp_display, use_container_width=True)
        
        # ============================================================
        # VISUALIZATION
        # ============================================================
        
        st.markdown("---")
        st.subheader("📊 Opportunity Visualization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 10 by Opportunity Score")
            render_bar_chart(
                opportunities.head(10),
                x_col='query',
                y_col='opportunity_score',
                title="Biggest Quick Wins",
                orientation='h'
            )
        
        with col2:
            st.markdown("#### Impressions vs CTR")
            # Scatter plot would be ideal, but we'll use a simple view
            render_bar_chart(
                opportunities.head(10),
                x_col='query',
                y_col='impressions',
                title="Impressions (Visibility)",
                orientation='h'
            )
        
        # ============================================================
        # ACTION PLAN
        # ============================================================
        
        st.markdown("---")
        st.subheader("💡 Action Plan - How to Capitalize")
        
        top_5_opps = opportunities.head(5)
        
        for idx, (_, opp) in enumerate(top_5_opps.iterrows(), 1):
            with st.expander(f"#{idx} - {opp['query'][:60]}...", expanded=(idx == 1)):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Impressions", int(opp['impressions']))
                with col2:
                    st.metric("Clicks", int(opp['clicks']))
                with col3:
                    st.metric("CTR", f"{opp['ctr']:.2%}")
                with col4:
                    st.metric("Position", f"{opp['position']:.1f}")
                
                st.markdown("**How many more clicks if you rank higher?**")
                
                # Simple estimation
                if opp['position'] > 5:
                    target_pos = 3
                    improvement = "to top 3"
                elif opp['position'] > 3:
                    target_pos = 2
                    improvement = "to top 2"
                else:
                    target_pos = 1
                    improvement = "to #1"
                
                # CTR improvement estimate
                ctr_improvement = {
                    1: 0.28, 2: 0.15, 3: 0.10, 4: 0.08, 5: 0.06,
                    6: 0.04, 7: 0.03, 8: 0.03, 9: 0.02, 10: 0.02
                }
                
                current_ctr = opp['ctr']
                if target_pos in ctr_improvement:
                    improved_ctr = ctr_improvement[target_pos]
                    new_clicks = int(opp['impressions'] * improved_ctr)
                    additional_clicks = new_clicks - opp['clicks']
                    
                    st.success(f"""
                    **If you improve {improvement} ({target_pos} position):**
                    - New estimated CTR: {improved_ctr:.2%}
                    - New estimated clicks: {new_clicks}
                    - **Additional clicks: +{additional_clicks}** ⬆️
                    """)
                
                st.markdown("**Optimization tactics:**")
                if opp['position'] > 5:
                    st.markdown("""
                    1. **Get more backlinks** - Quality links boost rankings
                    2. **Create better content** - More comprehensive than competitors
                    3. **Improve UX signals** - Faster load time, mobile-friendly
                    4. **Update existing content** - Refresh with latest data
                    """)
                elif opp['position'] > 2:
                    st.markdown("""
                    1. **Optimize title tag** - Include keyword, make it compelling
                    2. **Improve meta description** - Clear, actionable, with CTR-boosting language
                    3. **Add rich snippets** - Schema markup for featured snippets
                    4. **Minor content tweaks** - Better formatting, clear headings
                    """)
                else:
                    st.markdown("""
                    1. **A/B test title variations** - Test different versions
                    2. **Improve meta description** - You're ranking well, boost the clickthrough
                    3. **Add call-to-action** - Clear next steps in description
                    4. **Optimize featured snippets** - If applicable, target Position 0
                    """)
        
        # ============================================================
        # SUMMARY
        # ============================================================
        
        st.markdown("---")
        st.subheader("📈 Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_opp_impressions = int(opportunities['impressions'].sum())
            st.metric("Total Impressions", total_opp_impressions)
        
        with col2:
            total_opp_clicks = int(opportunities['clicks'].sum())
            st.metric("Total Clicks", total_opp_clicks)
        
        with col3:
            avg_opp_score = opportunities['opportunity_score'].mean()
            st.metric("Avg Opportunity", int(avg_opp_score))
        
        with col4:
            # Potential additional clicks if all opportunities improved by 50%
            potential_clicks = int(opportunities['opportunity_score'].sum() * 0.5)
            st.metric("💰 Potential Clicks", potential_clicks, f"+{potential_clicks} if optimized")
    
    else:
        st.warning(f"""
        No opportunities found with ≥{min_impressions} impressions.
        Try lowering the minimum impressions threshold.
        """)

except Exception as e:
    st.error(f"Error loading opportunities: {str(e)}")
