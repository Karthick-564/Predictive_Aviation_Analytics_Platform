"""
airline_report.py — Page 3: Airline Report Card (CONFLICT Part 2)
Magazine layout: full-width violin hero → 2:1 ontime+scatter → full-width cause → full-width heatmap
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
from utils.styles import section_header, story_banner


@st.cache_data(show_spinner=False)
def _violin_data(df: pd.DataFrame) -> pd.DataFrame:
    if "AIRLINE_NAME" not in df.columns or "DEP_DELAY" not in df.columns:
        return pd.DataFrame()
    sample = df.copy()
    sample["DEP_DELAY_CLIP"] = sample["DEP_DELAY"].clip(-30, 180)
    if len(sample) > 25_000:
        sample = sample.sample(25_000, random_state=42)
    return sample


@st.cache_data(show_spinner=False)
def _violin_airline_order(df: pd.DataFrame) -> list:
    if "AIRLINE_NAME" not in df.columns or "DEP_DELAY" not in df.columns:
        return []
    medians = df.groupby("AIRLINE_NAME")["DEP_DELAY"].median().sort_values(ascending=False)
    return medians.index.tolist()


@st.cache_data(show_spinner=False)
def _ontime_category(df: pd.DataFrame) -> pd.DataFrame:
    if "AIRLINE_NAME" not in df.columns or "DelayCategory" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["AIRLINE_NAME", "DelayCategory"])
        .size()
        .reset_index(name="Count")
    )
    totals = grp.groupby("AIRLINE_NAME")["Count"].transform("sum")
    grp["Pct"] = grp["Count"] / totals * 100
    return grp


@st.cache_data(show_spinner=False)
def _delay_cause_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    cause_cols = list(DELAY_CAUSE_LABELS.keys())
    delayed = df[df["DEP_DELAY"] > 15].copy()
    available_cols = [c for c in cause_cols if c in delayed.columns]
    if not available_cols or delayed.empty:
        return pd.DataFrame()
    cause_sums = delayed.groupby("AIRLINE_NAME")[available_cols].sum().reset_index()
    melted = cause_sums.melt(id_vars="AIRLINE_NAME", var_name="Cause", value_name="Minutes")
    melted["CauseLabel"] = melted["Cause"].map(DELAY_CAUSE_LABELS).fillna(melted["Cause"])
    totals = melted.groupby("AIRLINE_NAME")["Minutes"].transform("sum")
    melted["Pct"] = melted["Minutes"] / (totals + 1e-9) * 100
    return melted


@st.cache_data(show_spinner=False)
def _airline_scatter(df: pd.DataFrame) -> pd.DataFrame:
    agg = {"DEP_DELAY": ["count", "mean", "std"]}
    if "CANCELLED" in df.columns:
        agg["CANCELLED"] = "mean"
    grp = df.groupby("AIRLINE_NAME").agg(agg).reset_index()
    grp.columns = ["AIRLINE_NAME", "TotalFlights", "AvgDelay", "StdDelay"] + (
        ["CancelRate"] if "CANCELLED" in df.columns else []
    )
    grp["CancelPct"] = grp["CancelRate"] * 100 if "CANCELLED" in df.columns else 0.0
    grp["BubbleSize"] = grp["StdDelay"].fillna(1).clip(lower=1)
    return grp


@st.cache_data(show_spinner=False)
def _airline_month_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    if "MONTH_LABEL" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(["AIRLINE_NAME", "MONTH_LABEL"])["DEP_DELAY"]
        .mean()
        .reset_index()
        .rename(columns={"DEP_DELAY": "AvgDelay"})
    )


def render(df: pd.DataFrame) -> None:
    story_banner(
        "Not all airlines are equal. Behind the same ticket price, "
        "some carriers are far more likely to ruin your journey."
    )

    try:
        violin_sample = _violin_data(df)
        airline_order = _violin_airline_order(df)
    except Exception:
        violin_sample, airline_order = pd.DataFrame(), []

    # ═══ HERO: Full-width violin — most visually impactful chart ══════════════
    section_header("🎻 Delay Distribution — Every Airline, Every Flight")
    if not violin_sample.empty and airline_order:
        fig = px.violin(
            violin_sample,
            x="AIRLINE_NAME",
            y="DEP_DELAY_CLIP",
            color="AIRLINE_NAME",
            box=True,
            points=False,               # hide points for cleaner full-width look
            category_orders={"AIRLINE_NAME": airline_order},
            title="Departure Delay Violin Chart — Width Shows Variability, Height Shows Range",
            labels={"DEP_DELAY_CLIP": "Dep Delay (min, clipped ±180)", "AIRLINE_NAME": ""},
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            showlegend=False,
            xaxis_tickangle=-35,
            height=440,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "🎻 Fatter violin = more unpredictable airline. "
            "Shown sorted worst → best by median delay. Points hidden for readability at full width."
        )
    else:
        st.info("Violin data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ ROW 2: On-Time % (wide) + Volume Scatter (narrow) ═══════════════════
    # 3:2 split — stacked bar needs space for many airlines, scatter is supporting
    section_header("📊 On-Time Report Card & Volume Analysis")
    col_ot, col_scatter = st.columns([3, 2])

    with col_ot:
        ot_df = _ontime_category(df)
        if not ot_df.empty:
            on_time = ot_df[ot_df["DelayCategory"] == "On-Time/Early"].sort_values("Pct", ascending=False)
            airline_sort = on_time["AIRLINE_NAME"].tolist()
            fig = px.bar(
                ot_df,
                x="Pct",
                y="AIRLINE_NAME",
                color="DelayCategory",
                color_discrete_map=DELAY_CATEGORY_COLORS,
                category_orders={
                    "DelayCategory": DELAY_CATEGORY_ORDER,
                    "AIRLINE_NAME": airline_sort[::-1],
                },
                orientation="h",
                barmode="stack",
                title="On-Time Performance — Best to Worst (%)",
                labels={"Pct": "% of Flights", "AIRLINE_NAME": ""},
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=440,
                xaxis_range=[0, 100],
                legend_orientation="h",
                legend_yanchor="bottom", legend_y=1.02,
                legend_xanchor="right", legend_x=1,
            )
            st.plotly_chart(fig, width="stretch")
            if airline_sort:
                st.caption(f"🏆 Best on-time: **{airline_sort[0]}**  |  💀 Worst: **{airline_sort[-1]}**")
        else:
            st.info("On-time data unavailable.")

    with col_scatter:
        scatter_df = _airline_scatter(df)
        if not scatter_df.empty:
            size_col = "CancelPct" if scatter_df["CancelPct"].sum() > 0 else "BubbleSize"
            size_label = "Cancellation %" if size_col == "CancelPct" else "Delay Variability"
            fig = px.scatter(
                scatter_df,
                x="TotalFlights",
                y="AvgDelay",
                color="AIRLINE_NAME",
                size=size_col,
                size_max=50,
                hover_name="AIRLINE_NAME",
                hover_data={
                    "TotalFlights": ":,",
                    "AvgDelay": ":.1f",
                    size_col: ":.2f",
                    "AIRLINE_NAME": False,
                },
                title=f"Volume vs Delay<br><sup>Bubble = {size_label}</sup>",
                labels={"TotalFlights": "Total Flights", "AvgDelay": "Avg Delay (min)"},
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=440, showlegend=False)
            st.plotly_chart(fig, width="stretch")
            st.caption(f"💡 Top-right = high volume + high delay. Worst performers at a glance.")
        else:
            st.info("Scatter data unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ SECTION 3: Delay Cause Breakdown — full width ════════════════════════
    section_header("🔍 What's Causing Delays? Blame Map by Airline")
    cause_df = _delay_cause_breakdown(df)
    if not cause_df.empty:
        airlines_sorted = (
            cause_df.groupby("AIRLINE_NAME")["Minutes"]
            .sum().sort_values(ascending=False).index.tolist()
        )
        cause_labels = cause_df["CauseLabel"].unique().tolist()
        fig = go.Figure()
        for label in cause_labels:
            ldf = cause_df[cause_df["CauseLabel"] == label]
            ldf = ldf.set_index("AIRLINE_NAME").reindex(airlines_sorted).fillna(0)
            fig.add_trace(
                go.Bar(
                    name=label,
                    x=airlines_sorted,
                    y=ldf["Pct"].values,
                    hovertemplate=f"<b>{label}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
                )
            )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            title="Delay Cause Mix by Airline — Delayed Flights Only (>15 min)",
            yaxis_title="% of Delay Minutes",
            height=380,
            xaxis_tickangle=-35,
            legend_orientation="h",
            legend_yanchor="bottom", legend_y=1.02,
            legend_xanchor="right", legend_x=1,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("🔍 Some airlines blame weather more than others — but the data shows carrier issues dominate.")
    else:
        st.info("Cause breakdown unavailable.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══ SECTION 4: Seasonal heatmap — full width ═════════════════════════════
    section_header("📅 Seasonal Performance — Does Your Airline Get Worse in Winter?")
    heat_df = _airline_month_heatmap(df)
    month_order_filter = ["January", "July", "October"]
    heat_df = heat_df[heat_df["MONTH_LABEL"].isin(month_order_filter)]
    if not heat_df.empty:
        pivot = heat_df.pivot(index="MONTH_LABEL", columns="AIRLINE_NAME", values="AvgDelay")
        pivot = pivot.reindex(index=[m for m in month_order_filter if m in pivot.index])
        fig = go.Figure(
            go.Heatmap(
                z=pivot.values.round(1),
                x=pivot.columns.tolist(),
                y=pivot.index.tolist(),
                colorscale="RdYlGn_r",
                text=pivot.values.round(1),
                texttemplate="%{text}",
                textfont=dict(size=10),
                hovertemplate="<b>%{x}</b> — %{y}<br>Avg Delay: %{z:.1f} min<extra></extra>",
                colorbar=dict(title="Avg Delay<br>(min)"),
            )
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Avg Departure Delay: Airline × Month — Red = Worst Performer That Season",
            height=240,
            xaxis_tickangle=-35,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("📅 January winners often collapse in winter — pre-position aircraft or pre-book accordingly.")
    else:
        st.info("Monthly heatmap data unavailable.")
