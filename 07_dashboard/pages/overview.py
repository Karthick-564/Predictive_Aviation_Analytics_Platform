"""
overview.py — Page 1: The Big Picture (CONTEXT)
Magazine layout: KPI strip → 1:2 donut+bar → full-width monthly → full-width routes
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_RED, ACCENT_YELLOW,
    DELAY_CATEGORY_COLORS, DELAY_CATEGORY_ORDER,
    DELAY_CAUSE_LABELS, PLOTLY_LAYOUT,
)
from utils.styles import insight_card, kpi_card, section_header, story_banner


def _safe_airline_name(df: pd.DataFrame, col: str = "AIRLINE_NAME") -> str:
    try:
        return str(df.iloc[0][col])
    except Exception:
        return "N/A"


@st.cache_data(show_spinner=False)
def _cause_totals(df: pd.DataFrame) -> pd.DataFrame:
    cause_cols = list(DELAY_CAUSE_LABELS.keys())
    totals = {DELAY_CAUSE_LABELS[c]: df[c].fillna(0).sum()
              for c in cause_cols if c in df.columns}
    return pd.DataFrame(list(totals.items()), columns=["Cause", "Minutes"])


@st.cache_data(show_spinner=False)
def _airline_avg_delay(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("AIRLINE_NAME", as_index=False)["DEP_DELAY"]
        .mean()
        .sort_values("DEP_DELAY", ascending=False)
    )


@st.cache_data(show_spinner=False)
def _monthly_delay_cat(df: pd.DataFrame) -> pd.DataFrame:
    if "MONTH_LABEL" not in df.columns or "DelayCategory" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["MONTH_LABEL", "DelayCategory"])
        .size()
        .reset_index(name="Count")
    )
    totals = grp.groupby("MONTH_LABEL")["Count"].transform("sum")
    grp["Pct"] = (grp["Count"] / totals * 100).round(1)
    return grp


@st.cache_data(show_spinner=False)
def _top_routes_by_delay(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if "ROUTE" not in df.columns or "DelayCategory" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["ROUTE", "DelayCategory"])
        .size()
        .reset_index(name="Count")
    )
    severe = grp[grp["DelayCategory"] == "Severe Delay"].sort_values(
        "Count", ascending=False
    )
    top_routes = severe.head(n)["ROUTE"].tolist()
    return grp[grp["ROUTE"].isin(top_routes)]


def render(df: pd.DataFrame) -> None:
    story_banner(
        "Every year, US flight delays cost passengers billions of hours and airlines "
        "billions of dollars. Here is where we stand."
    )

    # ═══ KPI STRIP ═══════════════════════════════════════════════════════════
    if "DelayCategory" in df.columns:
        on_time_rate = (df["DelayCategory"] == "On-Time/Early").mean() * 100
    else:
        on_time_rate = 0.0
    avg_delay = df["DEP_DELAY"].mean() if "DEP_DELAY" in df.columns else 0.0
    cancel_rate = df["CANCELLED"].mean() * 100 if "CANCELLED" in df.columns else 0.0
    worst_airline_df = _airline_avg_delay(df)
    worst_airline = _safe_airline_name(worst_airline_df) if not worst_airline_df.empty else "N/A"
    worst_avg = float(worst_airline_df.iloc[0]["DEP_DELAY"]) if not worst_airline_df.empty else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total Flights Analyzed", f"{len(df):,}", "Jan + Jul + Oct 2024")
    with c2:
        color_class = "kpi-good" if on_time_rate > 75 else ("kpi-warn" if on_time_rate >= 70 else "kpi-bad")
        kpi_card("On-Time Rate", f"{on_time_rate:.1f}%", "flights departed without delay", color_class)
    with c3:
        delay_class = "kpi-bad" if avg_delay > 15 else "kpi-good"
        kpi_card("Average Delay", f"{avg_delay:.1f} min", "per flight inc. on-time flights", delay_class)
    with c4:
        cancel_class = "kpi-bad" if cancel_rate > 2 else "kpi-good"
        kpi_card("Cancellation Rate", f"{cancel_rate:.1f}%", "flights that never departed", cancel_class)
    with c5:
        kpi_card("Worst Airline", worst_airline, f"avg {worst_avg:.0f} min delay per flight", "kpi-bad")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ SECTION 1: Cause Donut (narrow) + Airline leaderboard (wide) ════════
    # 1:2 asymmetric — donut is supporting context, bar is the main story
    section_header("Who's To Blame? Delay Causes & Airline Rankings")
    col_donut, col_bar = st.columns([1, 2])

    with col_donut:
        cause_df = _cause_totals(df)
        if not cause_df.empty and cause_df["Minutes"].sum() > 0:
            largest_cause = cause_df.loc[cause_df["Minutes"].idxmax(), "Cause"]
            fig = go.Figure(
                go.Pie(
                    labels=cause_df["Cause"],
                    values=cause_df["Minutes"],
                    hole=0.62,
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>%{value:,.0f} min<br>%{percent}<extra></extra>",
                    marker=dict(colors=[ACCENT_RED, ACCENT_YELLOW, ACCENT_BLUE, "#f0883e", "#94a3b8"]),
                    direction="clockwise",
                )
            )
            fig.add_annotation(
                text=f"<b>{largest_cause.split('(')[0].strip()}</b><br><span style='font-size:10px'>biggest cause</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=11, color="#1e293b"), align="center",
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Delay Cause Breakdown",
                showlegend=True,
                legend_orientation="v",
                legend_x=0, legend_y=-0.25,
                height=360,
            )
            st.plotly_chart(fig, width="stretch")
            st.caption(f"⚠️ **{largest_cause.split('(')[0].strip()}** accounts for the most delay minutes.")
        else:
            st.info("No delay cause data available.")

    with col_bar:
        if not worst_airline_df.empty:
            overall_mean = float(df["DEP_DELAY"].mean())
            bar_colors = [
                ACCENT_GREEN if v <= overall_mean else ACCENT_RED
                for v in worst_airline_df["DEP_DELAY"]
            ]
            fig = go.Figure(
                go.Bar(
                    x=worst_airline_df["DEP_DELAY"].round(1),
                    y=worst_airline_df["AIRLINE_NAME"],
                    orientation="h",
                    marker=dict(color=bar_colors, line=dict(width=0)),
                    hovertemplate="<b>%{y}</b><br>Avg Delay: %{x:.1f} min<extra></extra>",
                )
            )
            fig.add_vline(
                x=overall_mean, line_dash="dash", line_color=ACCENT_YELLOW,
                annotation_text=f"Industry Mean: {overall_mean:.1f} min",
                annotation_position="top right",
                annotation_font=dict(color=ACCENT_YELLOW, size=10),
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="All Airlines Ranked by Avg Departure Delay — Red = Above Industry Average",
                yaxis_autorange="reversed",
                height=360,
            )
            st.plotly_chart(fig, width="stretch")
            best_airline = worst_airline_df.iloc[-1]["AIRLINE_NAME"]
            st.caption(f"🏆 **{best_airline}** leads with lowest avg delay | ❌ **{worst_airline}** is the worst")
        else:
            st.info("No airline data available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ SECTION 2: Monthly stacked bar — full width ══════════════════════════
    section_header("How Delay Severity Changes by Season")
    monthly_df = _monthly_delay_cat(df)
    if not monthly_df.empty:
        month_order = ["January", "July", "October"]
        monthly_df = monthly_df[monthly_df["MONTH_LABEL"].isin(month_order)]
        fig = go.Figure()
        for cat in DELAY_CATEGORY_ORDER:
            cat_sub = monthly_df[monthly_df["DelayCategory"] == cat]
            cat_sub = cat_sub.set_index("MONTH_LABEL").reindex(month_order).fillna(0)
            fig.add_trace(
                go.Bar(
                    name=cat,
                    x=month_order,
                    y=cat_sub["Pct"].values,
                    text=[f"{v:.0f}%" if v > 5 else "" for v in cat_sub["Pct"].values],
                    textposition="inside",
                    insidetextanchor="middle",
                    marker_color=DELAY_CATEGORY_COLORS.get(cat, "#94a3b8"),
                    hovertemplate=f"<b>{cat}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
                )
            )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            title="Delay Category Mix by Month — Does January Really Fly Worse? (%)",
            yaxis_title="% of Flights",
            yaxis_range=[0, 100],
            height=320,
            legend_orientation="h",
            legend_yanchor="bottom", legend_y=1.02,
            legend_xanchor="right", legend_x=1,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("📅 January shows the highest severe delay share — winter operations take their toll.")
    else:
        st.info("No monthly breakdown data available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ SECTION 3: Top Routes — full width, tall ═════════════════════════════
    section_header("Top 20 Most-Delayed Routes in America")
    route_df = _top_routes_by_delay(df, n=20)
    if not route_df.empty:
        severe_sorted = (
            route_df[route_df["DelayCategory"] == "Severe Delay"]
            .sort_values("Count", ascending=True)
        )
        route_order = severe_sorted["ROUTE"].tolist()
        fig = px.bar(
            route_df,
            x="Count",
            y="ROUTE",
            color="DelayCategory",
            color_discrete_map=DELAY_CATEGORY_COLORS,
            category_orders={"DelayCategory": DELAY_CATEGORY_ORDER, "ROUTE": route_order},
            orientation="h",
            title="Top 20 Routes: Full Delay Profile — Sorted by Severe Delay Count",
            labels={"Count": "Flight Count", "ROUTE": ""},
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=560,
            legend_title="Delay Category",
            legend_orientation="h",
            legend_yanchor="bottom", legend_y=1.01,
            legend_xanchor="right", legend_x=1,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("🔴 These routes fail structurally — airport congestion + scheduling are the root causes.")
    else:
        st.info("Route data not available.")
