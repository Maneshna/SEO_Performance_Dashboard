"""
Main Streamlit App - Entry Point
Run with: streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# PAGE CONFIGURATION


st.set_page_config(
    page_title="SEO Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIDEBAR - INITIALIZATION & ETL


st.sidebar.title("🔧 Dashboard Setup")

# Check if database exists
from src.database import DB_PATH

if not DB_PATH.exists():
    st.sidebar.warning("⚠️ Database not initialized")
    
    if st.sidebar.button("🚀 Initialize Database & Load Sample Data"):
        from src.etl import run_full_etl
        
        gsc_file = backend_path / "data" / "gsc_sample.csv"
        ga4_file = backend_path / "data" / "ga4_sample.csv"
        
        gsc_rows, ga4_rows = run_full_etl(str(gsc_file), str(ga4_file))
        st.sidebar.success(f"✓ Loaded {gsc_rows + ga4_rows} rows from sample data!")
        st.rerun()
else:
    st.sidebar.success("✓ Database is ready")


# Upload custom data section
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Upload Your Data")

uploaded_files = st.sidebar.file_uploader(
    "Upload CSV files (GSC or GA4 exports)",
    type=['csv'],
    accept_multiple_files=True
)

if uploaded_files:
    from src.etl import load_gsc_csv, load_ga4_csv
    from src.database import insert_gsc_data, insert_ga4_data
    
    for uploaded_file in uploaded_files:
        try:
            if 'gsc' in uploaded_file.name.lower() or 'search' in uploaded_file.name.lower():
                df = load_gsc_csv(uploaded_file)
                rows = insert_gsc_data(df)
                st.sidebar.success(f"✓ Imported {rows} GSC records from {uploaded_file.name}")
            
            elif 'ga4' in uploaded_file.name.lower() or 'analytics' in uploaded_file.name.lower():
                df = load_ga4_csv(uploaded_file)
                rows = insert_ga4_data(df)
                st.sidebar.success(f"✓ Imported {rows} GA4 records from {uploaded_file.name}")
            
            else:
                st.sidebar.info(f"Could not auto-detect {uploaded_file.name}. Include 'GSC' or 'GA4' in filename.")
        
        except Exception as e:
            st.sidebar.error(f"Error importing {uploaded_file.name}: {str(e)}")

# MAIN CONTENT


st.title("📊 SEO Performance Dashboard")
st.markdown("""
Welcome! This dashboard helps you analyze:
- **Search Performance**: Clicks, impressions, CTR, ranking positions from Google Search Console
- **User Behavior**: Sessions, conversions, bounce rates from Google Analytics 4
- **Growth Opportunities**: Pages/queries with high potential for improvement
- **Trends & Forecasts**: Historical trends and future predictions
""")

st.markdown("---")

# Get data date range
from src.database import get_data_date_range

min_date, max_date = get_data_date_range()
st.info(f"📅 Data available: {min_date} to {max_date}")

st.markdown("""
### How to Use:
1. **Upload Data** (sidebar): Add your GSC and GA4 CSV exports
2. **Explore Pages**: Navigate using the menu on the left
3. **Apply Filters**: Use date ranges, countries, and devices
4. **Find Opportunities**: Identify pages/queries to optimize

### Key Pages:
- **Overview**: KPI summary and health metrics
- **Query Analysis**: Top/bottom search queries
- **Page Analysis**: Landing page performance
- **Opportunities**: High-impression, low-CTR pages
- **Forecasts**: Trend analysis and future predictions

---

**Ready?** Select a page from the menu → to get started!
""")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("🔗 [Learn how to export GSC data](https://support.google.com/webmasters/answer/7042828)")
st.sidebar.markdown("🔗 [Learn how to export GA4 data](https://support.google.com/analytics/answer/12444625)")
