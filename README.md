# SEO Performance Dashboard

A comprehensive, full-stack analytics platform for tracking, analyzing, and optimizing search engine performance. Built with **Python** (data engineering), **SQLite** (storage), and **Streamlit** (interactive frontend) for college project & resume portfolio.

---

## 📊 Dashboard Features

### 1. **Overview** - KPI Dashboard
- Total clicks, impressions, CTR, average ranking position
- GA4 engagement metrics (sessions, conversions, conversion rate)
- Daily trend charts for clicks and impressions
- Smart insight cards with traffic health assessment

### 2. **Query Analysis** - Search Keywords
- Top performing search queries sorted by clicks/impressions/CTR
- Bottom performers: high impressions + low CTR (optimization opportunities)
- Opportunity scoring to prioritize what to fix first
- Actionable recommendations for each query

### 3. **Page Analysis** - Landing Pages
- Best performing pages by search traffic
- Combined GSC + GA4 metrics (clicks, sessions, bounce rate, conversions)
- Pages with high bounce rates (UX issues)
- Cannibalization detection

### 4. **Opportunities** - Quick Wins
- Finds high-impression, low-CTR pages/queries worth optimizing
- **Opportunity Score** = impressions × (1 - CTR) = Lost clicks
- Ranks by ROI potential
- Specific recommendations (improve ranking vs. improve CTR)
- Estimates potential clicks if you improve positioning

### 5. **Forecasts** - Trends & Predictions
- Historical trend analysis with moving averages
- Simple linear regression forecasting (7-30 days)
- Anomaly detection (unusual spikes/dips)
- Trend direction and growth rate
- Recommendations based on trends

---

## 🏗️ Architecture

```
SEO_Performance_Dashboard/
│
├── backend/                      # Data pipeline & business logic
│   ├── src/
│   │   ├── database.py          # SQLite queries and schema
│   │   ├── etl.py               # CSV import and cleaning
│   │   ├── models.py            # Data class definitions
│   │   └── utils.py             # Helper functions (formatting, calculations)
│   ├── data/
│   │   ├── gsc_sample.csv       # Sample Google Search Console export
│   │   └── ga4_sample.csv       # Sample Google Analytics 4 export
│   └── requirements.txt
│
├── frontend/                     # Streamlit UI
│   ├── app.py                   # Main entry point
│   ├── pages/
│   │   ├── 01_Overview.py       # KPI dashboard
│   │   ├── 02_Query_Analysis.py # Query insights
│   │   ├── 03_Page_Analysis.py  # Page performance
│   │   ├── 04_Opportunities.py  # Growth opportunities
│   │   └── 05_Forecasts.py      # Trend forecasting
│   ├── components/
│   │   ├── filters.py           # Reusable filter components
│   │   └── charts.py            # Reusable chart components
│   └── .streamlit/config.toml   # Streamlit config
│
├── data/
│   └── seo_dashboard.db         # SQLite database (auto-created)
│
├── README.md                    # This file
├── requirements.txt             # All Python dependencies
└── start.sh                     # Quick start script
```

---

## 🚀 Quick Start

### 1. Clone/Download the Project
```bash
# Navigate to the project
cd SEO_Performance_Dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard
```bash
streamlit run frontend/app.py
```

The dashboard will open at `http://localhost:8501`

### 4. Load Data
- **Option A**: Click the "Initialize Database & Load Sample Data" button in the sidebar
- **Option B**: Upload your own GSC/GA4 CSV exports in the sidebar

---

## 📥 How to Get Your Data

### Google Search Console Export
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Select your property
3. Go to **Performance** > Set date range
4. Click the **Download** button → **Download as CSV**
5. Save with "GSC" in filename (e.g., `gsc_export_2024.csv`)
6. Upload in dashboard sidebar

**Expected columns:**
- Date
- Query
- Page
- Country
- Device
- Search Type (Web/Image/Video)
- Clicks
- Impressions
- CTR
- Position (Avg. position)

### Google Analytics 4 Export
1. Go to [Google Analytics](https://analytics.google.com)
2. Select your property
3. Go to **Reports** > **Landing page** or **Pages and screens**
4. Set date range and segment by country/device
5. Click **Export** → **Google Sheets** → **Download CSV**
6. Save with "GA4" in filename (e.g., `ga4_export_2024.csv`)
7. Upload in dashboard sidebar

**Expected columns:**
- Date
- Page (Landing page)
- Device Category
- Country
- Sessions
- Users
- Bounces
- Bounce Rate
- Avg. Session Duration
- Conversions (optional)
- Conversion Value (optional)

---

## 🔍 Understanding the Dashboards

### KPI Metrics Explained

| Metric | What It Means | Target |
|--------|---------------|--------|
| **Clicks** | Users who clicked your link in search | Higher = better |
| **Impressions** | Times your link appeared in search results | Higher = more visibility |
| **CTR** (Click-Through Rate) | Clicks ÷ Impressions. % of people who click | 2-5% = good; 5%+ = excellent |
| **Position** | Average ranking in search results | 1-3 = excellent; 1-10 = visible |
| **Sessions** | Unique user visits from search | Higher = more traffic |
| **Conversions** | Goals completed (sign-ups, purchases) | Higher = better ROI |

### Opportunity Score

**Formula:** `Impressions × (1 - CTR)`

**What it means:**
- Shows potential clicks you're NOT getting
- High score = lots of lost opportunity
- Example: 100 impressions, 2% CTR = 98 lost clicks

**Use case:** If you can improve a high-opportunity query by 1 ranking position, you might capture many more clicks with minimal effort.

---

## 💻 Tech Stack Explained

### Backend
- **Python 3.8+**: Data processing and calculations
- **SQLite3**: Lightweight embedded database (no server needed)
- **Pandas**: CSV loading and data manipulation

### Frontend
- **Streamlit**: Interactive web UI (no HTML/CSS/JavaScript needed)
- **Plotly**: Interactive charts and forecasting

### Why This Stack?
✅ **Fast to build** - Perfect for 10-day college project
✅ **Production-grade** - SQLite can handle millions of rows
✅ **Resume-ready** - Shows data engineering + backend + frontend skills
✅ **No servers needed** - Single Python app, portable
✅ **Easy to deploy** - Ship to Streamlit Cloud in 2 clicks

---

## 📚 Learning Path

When you explore this code, you'll learn:

### Database Design
```python
# backend/src/database.py
- SQL schema design
- Indexes for performance
- Aggregate queries
- Date filtering
```

### Data Pipeline (ETL)
```python
# backend/src/etl.py
- CSV parsing and validation
- Data cleaning and transformation
- Duplicate detection
- Type conversion and error handling
```

### Data Analysis
```python
# backend/src/utils.py
- Trend calculations
- Opportunity scoring
- Moving averages
- Linear regression forecasting
- Anomaly detection
```

### Web UI
```python
# frontend/app.py, pages/*.py
- Streamlit layout and widgets
- Component reusability
- State management
- File uploads
```

---

## 🎓 Resume Talking Points

Frame this project as:

> "Built end-to-end SEO analytics dashboard using Python, SQLite, and Streamlit, integrating Google Search Console and Google Analytics 4 data pipelines. Designed ETL workflows with CSV parsing, data validation, and reconciliation. Implemented interactive BI dashboards with 5 views (KPIs, query analysis, page analysis, opportunity scoring, forecasting). Created library of reusable analytic functions: opportunity scoring, trend analysis, anomaly detection, and linear regression forecasting. Project emphasized data modeling, backend optimization, and user-centric UI/UX."

**Skills this demonstrates:**
- 🐍 Python (pandas, sqlite3)
- 🗄️ Database design and SQL
- 📊 Data engineering & ETL
- 📈 Analytics & metrics
- 🎨 UI/UX (Streamlit)
- 🔬 Business intelligence
- 📱 Full-stack thinking

---

## 🚀 Next Steps to Level Up

Want to add more? Here are ideas (in order of difficulty):

### Easy (1-2 days)
- [ ] Add email reports (send daily digest)
- [ ] Export to PDF reports
- [ ] Add more KPI calculations
- [ ] Dark mode toggle

### Medium (2-3 days)
- [ ] Live API integration with Google Search Console
- [ ] User authentication & multi-user support
- [ ] Custom metric builder
- [ ] Competitor comparison

### Hard (3-5 days)
- [ ] FastAPI backend + React frontend (upgrade from Streamlit)
- [ ] Advanced forecasting (ARIMA, Prophet)
- [ ] Automated alerts for anomalies
- [ ] Machine learning: predict CTR improvement

---

## 📋 Checklist for Submission

- [ ] All 5 pages working with sample data
- [ ] README.md with architecture diagram
- [ ] Comments explaining key code sections
- [ ] Sample CSVs included
- [ ] Database initializes on first run
- [ ] Handles missing/invalid data gracefully
- [ ] Mobile-friendly (Streamlit) ✓
- [ ] Error messages are helpful
- [ ] Git repo with clean history

---

## 🤔 FAQ

**Q: Can I use this with real company data?**
A: Yes! Just upload your actual GSC/GA4 CSVs. All data stays local in your SQLite database.

**Q: How much data can SQLite handle?**
A: Easily millions of rows. Good for sites with up to 1M+ keywords.

**Q: Can I deploy this online?**
A: Yes! Deploy to Streamlit Cloud for free (streamlit.io/cloud). Or Docker to AWS/Heroku.

**Q: How do I update with fresh data?**
A: Re-export CSVs from GSC/GA4, upload in sidebar. Dashboard auto-deduplicates.

**Q: Can I add my own metrics?**
A: Yes! Edit `backend/src/database.py` to add new queries, then use in pages.

---

## 📞 Support

For issues:
1. Check if data is properly formatted (use sample CSVs as template)
2. Delete `data/seo_dashboard.db` and reinitialize
3. Check Python version (3.8+)
4. Verify all packages installed: `pip install -r requirements.txt`

---

## 📝 License

Built for educational purposes. Free to use, modify, and share.

---

**Happy analyzing! 🚀**
