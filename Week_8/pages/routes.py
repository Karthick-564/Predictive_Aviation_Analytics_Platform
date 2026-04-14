"""
routes.py — Page 4: Routes & Airports (CONFLICT Part 3)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.constants import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_RED,
    DELAY_CATEGORY_COLORS,
    DELAY_CATEGORY_ORDER,
    PLOTLY_LAYOUT,
)
from utils.styles import section_header, story_banner


@st.cache_data(show_spinner=False)
def _top_origin_delays(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    if "ORIGIN_CITY_SHORT" not in df.columns or "ORIGIN" not in df.columns:
        return pd.DataFrame()
    df2 = df.copy()
    df2["OriginLabel"] = df2["ORIGIN_CITY_SHORT"].fillna(df2["ORIGIN"]) + " (" + df2["ORIGIN"] + ")"
    return (
        df2.groupby("OriginLabel")["DEP_DELAY"]
        .mean()
        .reset_index()
        .rename(columns={"DEP_DELAY": "AvgDelay"})
        .sort_values("AvgDelay", ascending=False)
        .head(n)
    )


@st.cache_data(show_spinner=False)
def _top_dest_delays(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    if "DEST" not in df.columns or "ARR_DELAY" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby("DEST")
        .agg(AvgArrDelay=("ARR_DELAY", "mean"), AvgDepDelay=("DEP_DELAY", "mean"))
        .reset_index()
        .sort_values("AvgArrDelay", ascending=False)
        .head(n)
        .assign(DestLabel=lambda d: d["DEST"] + " Airport")
    )


@st.cache_data(show_spinner=False)
def _duration_scatter(df: pd.DataFrame) -> pd.DataFrame:
    needed = ["CRS_ARR_TIME_SCALED", "CRS_DEP_TIME_SCALED", "ARR_DELAY", "DelayCategory"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        return pd.DataFrame()
    sample = df.dropna(subset=needed)
    if len(sample) > 50000:
        sample = sample.sample(50000, random_state=42)
    sample = sample.copy()
    sample["FlightDurationProxy"] = sample["CRS_ARR_TIME_SCALED"] - sample["CRS_DEP_TIME_SCALED"]
    return sample


@st.cache_data(show_spinner=False)
def _worst_routes(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    if "ROUTE" not in df.columns or "DelayCategory" not in df.columns:
        return pd.DataFrame()
    severe = df[df["DelayCategory"] == "Severe Delay"]
    counts = severe["ROUTE"].value_counts().head(n).reset_index()
    counts.columns = ["ROUTE", "SevereCount"]
    return counts.sort_values("SevereCount", ascending=True)


@st.cache_data(show_spinner=False)
def _airline_airport_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    if "AIRLINE_NAME" not in df.columns or "ORIGIN_CITY_SHORT" not in df.columns:
        return pd.DataFrame()
    top_airlines = df["AIRLINE_NAME"].value_counts().head(10).index.tolist()
    top_airports = df["ORIGIN_CITY_SHORT"].value_counts().head(10).index.tolist()
    filtered = df[
        df["AIRLINE_NAME"].isin(top_airlines) & df["ORIGIN_CITY_SHORT"].isin(top_airports)
    ]
    return (
        filtered.groupby(["ORIGIN_CITY_SHORT", "AIRLINE_NAME"])["DEP_DELAY"]
        .mean()
        .reset_index()
        .rename(columns={"DEP_DELAY": "AvgDelay"})
    )


def render(df: pd.DataFrame) -> None:
    story_banner(
        "Your route is the hidden variable. Some origin-destination pairs "
        "fail repeatedly — not by accident, by design."
    )

    # ── Row 1: Top Origins | Top Destinations ────────────────────────────────
    section_header("Airport Delay Hotspots")
    c1, c2 = st.columns(2)

    with c1:
        origin_df = _top_origin_delays(df)
        if not origin_df.empty:
            mean_delay = origin_df["AvgDelay"].mean()
            bar_colors = [ACCENT_RED if v >= mean_delay else ACCENT_GREEN for v in origin_df["AvgDelay"]]
            fig = go.Figure(
                go.Bar(
                    x=origin_df["AvgDelay"].round(1),
                    y=origin_df["OriginLabel"],
                    orientation="h",
                    marker=dict(color=bar_colors),
                    hovertemplate="<b>%{y}</b><br>Avg Dep Delay: %{x:.1f} min<extra></extra>",
                )
            )
            fig.add_vline(
                x=df["DEP_DELAY"].mean(),
                line_dash="dash",
                line_color="#d29922",
                annotation_text=f"Overall Mean: {df['DEP_DELAY'].mean():.1f} min",
                annotation_position="top right",
                annotation_font=dict(color="#d29922", size=9),
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 15 Origin Airports by Avg Departure Delay",
                yaxis_autorange="reversed",
                height=460,
            )
            st.plotly_chart(fig, width="stretch")
            st.caption("🏢 These cities export delays to the rest of the network.")
        else:
            st.info("Origin airport data unavailable.")

    with c2:
        dest_df = _top_dest_delays(df)
        if not dest_df.empty:
            mean_arr = dest_df["AvgArrDelay"].mean()
            arr_colors = [ACCENT_RED if v >= mean_arr else ACCENT_GREEN for v in dest_df["AvgArrDelay"]]
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=dest_df["AvgArrDelay"].round(1),
                    y=dest_df["DestLabel"],
                    orientation="h",
                    name="Avg Arrival Delay",
                    marker=dict(color=arr_colors),
                    hovertemplate="<b>%{y}</b><br>Avg Arr Delay: %{x:.1f} min<extra></extra>",
                )
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 15 Destination Airports by Avg Arrival Delay",
                yaxis_autorange="reversed",
                height=460,
            )
            st.plotly_chart(fig, width="stretch")
            st.caption("🛬 Arrivals worse than departures = airport congestion on landing.")
        else:
            st.info("Destination airport data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Duration Scatter | Worst Routes ────────────────────────────────
    section_header("Flight Duration vs Delay & Worst Routes")
    c1, c2 = st.columns(2)

    with c1:
        dur_df = _duration_scatter(df)
        if not dur_df.empty:
            fig = px.scatter(
                dur_df,
                x="FlightDurationProxy",
                y="ARR_DELAY",
                color="DelayCategory",
                color_discrete_map=DELAY_CATEGORY_COLORS,
                category_orders={"DelayCategory": DELAY_CATEGORY_ORDER},
                opacity=0.4,
                title="Scheduled Duration Proxy vs Arrival Delay",
                labels={
                    "FlightDurationProxy": "Sched Duration (scaled)",
                    "ARR_DELAY": "Arrival Delay (min)",
                },
            )
            # Add trendline manually
            try:
                x = dur_df["FlightDurationProxy"].dropna()
                y = dur_df["ARR_DELAY"].dropna()
                common_idx = x.index.intersection(y.index)
                coeffs = np.polyfit(x[common_idx], y[common_idx], 1)
                x_line = np.linspace(x.min(), x.max(), 100)
                y_line = np.polyval(coeffs, x_line)
                fig.add_trace(
                    go.Scatter(
                        x=x_line, y=y_line,
                        mode="lines",
                        name="Trend",
                        line=dict(color=ACCENT_RED, width=2, dash="dash"),
                    )
                )
            except Exception:
                pass
            fig.update_traces(marker=dict(size=3), selector=dict(mode="markers"))
            fig.update_layout(**PLOTLY_LAYOUT, height=420)
            st.plotly_chart(fig, width="stretch")
            st.caption("📏 Short scheduled flights delay more — no buffer time built into the schedule.")
        else:
            st.info("Duration-delay scatter unavailable (missing scaled columns).")

    with c2:
        worst_df = _worst_routes(df)
        if not worst_df.empty:
            fig = go.Figure(
                go.Bar(
                    x=worst_df["SevereCount"],
                    y=worst_df["ROUTE"],
                    orientation="h",
                    marker=dict(color=ACCENT_RED),
                    hovertemplate="<b>%{y}</b><br>Severe Delays: %{x:,}<extra></extra>",
                )
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 20 Routes by Severe Delay Count",
                height=420,
                yaxis_title="",
            )
            st.plotly_chart(fig, width="stretch")
            st.caption("⚠️ These routes fail repeatedly. Structural scheduling fixes needed.")
        else:
            st.info("Route data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Airline × Airport Heatmap ─────────────────────────────────────
    section_header("Airline Performance by Origin City")
    aa_df = _airline_airport_heatmap(df)
    if not aa_df.empty:
        pivot = aa_df.pivot(index="ORIGIN_CITY_SHORT", columns="AIRLINE_NAME", values="AvgDelay")
        fig = go.Figure(
            go.Heatmap(
                z=pivot.values.round(1),
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale="RdYlGn_r",
                text=pivot.values.round(1),
                texttemplate="%{text}",
                textfont=dict(size=8),
                hovertemplate="<b>%{x}</b> at <b>%{y}</b><br>Avg Delay: %{z:.1f} min<extra></extra>",
                colorbar=dict(title="Avg Delay (min)"),
            )
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Avg Departure Delay: Top 10 Airlines × Top 10 Origin Cities",
            height=380,
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("🔥 Red = worst airline + airport combination to avoid. Check before you book.")
    else:
        st.info("Airline-airport heatmap data unavailable.")
