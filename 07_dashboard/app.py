"""
app.py — Flight Delay Intelligence Dashboard
Entry point. Run with: python -m streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

# ── Page config must be FIRST Streamlit call ──────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Flight Delay Intelligence",
    page_icon="✈️",
    initial_sidebar_state="expanded",
)

# ── Imports (after page config) ───────────────────────────────────────────────
from utils.loader import apply_filters, convert_to_parquet, load_engineered, load_pca
from utils.styles import inject_css

# ── CSS ───────────────────────────────────────────────────────────────────────
inject_css()

# ── One-time CSV → Parquet conversion ────────────────────────────────────────
convert_to_parquet()

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading flight intelligence data…"):
    df_full = load_engineered()
    try:
        pca_df = load_pca()
    except Exception:
        pca_df = None

# ── Sidebar — filters only, no page navigation ────────────────────────────────
with st.sidebar:
    st.markdown("### ✈️ Flight Delay Intel")
    st.caption("US Domestic · Jan · Jul · Oct 2024")
    st.caption(f"{1_747_822:,} flights analyzed")
    st.divider()

    month_filter = st.selectbox(
        "📅 Month",
        ["All", "January", "July", "October"],
        index=0,
    )

    airline_options = (
        sorted(df_full["AIRLINE_NAME"].dropna().unique().tolist())
        if "AIRLINE_NAME" in df_full.columns
        else []
    )
    carrier_filter = st.multiselect(
        "✈️ Airline",
        options=airline_options,
        default=[],
        placeholder="All airlines",
    )

    delay_type_filter = st.radio(
        "🔍 Delay Cause Focus",
        ["All Causes", "Carrier", "Weather", "NAS (Air Traffic)", "Late Aircraft", "Security"],
        index=0,
    )

    st.divider()
    st.caption("Source: BTS On-Time Performance")
    st.caption("Bureau of Transportation Statistics")

# ── Apply filters ──────────────────────────────────────────────────────────────
df = apply_filters(df_full, month_filter, carrier_filter)

# ── TOP NAVIGATION BAR (always visible regardless of sidebar state) ────────────
PAGE_LABELS = [
    "🏠 Big Picture",
    "⏰ When To Fly",
    "✈️ Airline Report",
    "🗺️ Routes & Airports",
    "💡 What Should Change",
]

# Use session state to persist the current page across reruns
if "current_page" not in st.session_state:
    st.session_state.current_page = 0

# Render as clickable column buttons
nav_cols = st.columns(len(PAGE_LABELS))
for i, (col, label) in enumerate(zip(nav_cols, PAGE_LABELS)):
    with col:
        active = st.session_state.current_page == i
        # Use primary type for active page button
        if st.button(
            label,
            key=f"nav_{i}",
            type="primary" if active else "secondary",
            use_container_width=True,
        ):
            st.session_state.current_page = i
            st.rerun()

st.divider()

# ── Guard empty filter ─────────────────────────────────────────────────────────
if df.empty:
    st.warning("⚠️ No flights match the current filter combination. Please widen your selection.")
    st.stop()

# ── Route to pages ─────────────────────────────────────────────────────────────
page_idx = st.session_state.current_page

if page_idx == 0:
    from pages.overview import render
    render(df)

elif page_idx == 1:
    from pages.when_to_fly import render
    render(df)

elif page_idx == 2:
    from pages.airline_report import render
    render(df)

elif page_idx == 3:
    from pages.routes import render
    render(df)

elif page_idx == 4:
    from pages.resolution import render
    render(df, pca_df)
