"""
Data Models & Schema Definitions
Defines the expected structure of GSC and GA4 data after import.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# ============================================================
# GSC (Google Search Console) Data Model
# ============================================================
@dataclass
class GSCRecord:
    """
    Each row represents a query × page combination from GSC.
    Fields match Google Search Console export format.
    """
    date: datetime              # YYYY-MM-DD
    query: str                  # Search query user typed
    page_url: str               # Landing page URL
    country: str                # GEO country (e.g., "United States")
    device: str                 # Device type (Desktop, Mobile, Tablet)
    search_type: str            # Search type (Web, Image, Video)
    clicks: int                 # Number of clicks
    impressions: int            # Number of impressions (search results shown)
    ctr: float                  # Click-through rate (0.0-1.0)
    position: float             # Average position in search results


# ============================================================
# GA4 (Google Analytics 4) Data Model
# ============================================================
@dataclass
class GA4Record:
    """
    Each row represents a landing page session metric from GA4.
    Fields match Google Analytics 4 export format.
    """
    date: datetime              # YYYY-MM-DD
    page_url: str               # Landing page URL
    device: str                 # Device category (desktop, mobile, tablet)
    country: str                # User country
    sessions: int               # Number of sessions
    users: int                  # Number of unique users
    bounces: int                # Number of bounces
    bounce_rate: float          # Bounce rate (0.0-1.0)
    avg_session_duration: float # Avg session duration in seconds
    conversions: int            # Number of conversions/goals
    conversion_value: float     # Total conversion value


# ============================================================
# Aggregated SEO Metrics (for dashboards)
# ============================================================
@dataclass
class SEOMetricsSummary:
    """
    High-level KPIs computed from GSC + GA4.
    Used for the Overview dashboard.
    """
    total_clicks: int
    total_impressions: int
    total_ctr: float
    avg_position: float
    total_sessions: int
    total_conversions: int
    conversion_rate: float
    date_range: str


@dataclass
class QueryMetrics:
    """
    Metrics per unique search query.
    Used for Query Analysis page.
    """
    query: str
    clicks: int
    impressions: int
    ctr: float
    avg_position: float
    top_page: str
    sessions: int  # from GA4


@dataclass
class PageMetrics:
    """
    Metrics per landing page.
    Used for Page Analysis page.
    """
    page_url: str
    total_clicks: int
    total_impressions: int
    total_ctr: float
    avg_position: float
    unique_queries: int
    sessions: int
    conversions: int
    bounce_rate: float


@dataclass
class OpportunityMetrics:
    """
    Pages/queries worth focusing on:
    High impressions but low CTR = optimization opportunity.
    """
    entity_type: str            # 'query' or 'page'
    entity_value: str           # query string or page URL
    impressions: int
    clicks: int
    ctr: float
    avg_position: float
    opportunity_score: float    # 0.0-100.0 (higher = more potential)
    recommendation: str         # Action to take
