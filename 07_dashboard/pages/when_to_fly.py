"""
when_to_fly.py — Page 2: When To Fly (CONFLICT Part 1 — Time Patterns)
Magazine-style layout: hero chart + varied widths, not a rigid grid.
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
    ACCENT_YELLOW,
    ACCENT_TEAL,
    DELAY_CATEGORY_COLORS,
    DELAY_CATEGORY_ORDER,
    PLOTLY_LAYOUT,
)
from utils.styles import section_header, story_banner


def _hour_label(h: int) -> str:
    if h == 0:
        return "12 AM"
    elif h < 12:
        return f"{h} AM"
    elif h == 12:
        return "12 PM"
    else:
        return f"{h - 12} PM"


@st.cache_data(show_spinner=False)
def _calendar_heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    if "DAY_OF_MONTH" not in df.columns or "MONTH_LABEL" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(["MONTH_LABEL", "DAY_OF_MONTH"])["DEP_DELAY"]
        .mean()
        .reset_index()
        .rename(columns={"DEP_DELAY": "AvgDelay"})
    )


@st.cache_data(show_spinner=False)
def _daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    if "DAY_OF_MONTH" not in df.columns or "MONTH_LABEL" not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(["MONTH_LABEL", "DAY_OF_MONTH"])["DEP_DELAY"]
        .mean()
        .reset_index()
        .rename(columns={"DEP_DELAY": "AvgDelay"})
    )


@st.cache_data(show_spinner=False)
def _dow_delay(df: pd.DataFrame) -> pd.DataFrame:
    """Day-of-week delay aggregation using pre-computed DOW_NUM column."""
    dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    if "DOW_NUM" in df.columns:
        tmp = df.copy()
        tmp["DOW"] = pd.to_numeric(tmp["DOW_NUM"], errors="coerce").map(dow_map)
    elif "DAY_OF_WEEK" in df.columns:
        dow_bts = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
        tmp = df.copy()
        tmp["DOW"] = pd.to_numeric(tmp["DAY_OF_WEEK"], errors="coerce").map(dow_bts)
    else:
        return pd.DataFrame()

    grp = tmp.groupby("DOW")["DEP_DELAY"].mean().reindex(order).reset_index()
    grp.columns = ["DOW", "AvgDelay"]
    return grp


@st.cache_data(show_spinner=False)
def _hour_delay(df: pd.DataFrame) -> pd.DataFrame:
    """Hourly average delay — always returns all 24 hours so bars are complete."""
    if "DEP_HOUR" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby("DEP_HOUR")["DEP_DELAY"]
        .mean()
        .reindex(range(24), fill_value=0)   # ← FIX: ensure all 24 hours present
        .reset_index()
        .rename(columns={"DEP_HOUR": "Hour", "DEP_DELAY": "AvgDelay"})
    )
    # Keep Hour as integer so x-axis stays in chronological order (0–23)
    grp["HourLabel"] = grp["Hour"].apply(_hour_label)
    return grp


@st.cache_data(show_spinner=False)
def _hour_category_pct(df: pd.DataFrame) -> pd.DataFrame:
    if "DEP_HOUR" not in df.columns or "DelayCategory" not in df.columns:
        return pd.DataFrame()
    grp = (
        df.groupby(["DEP_HOUR", "DelayCategory"])
        .size()
        .reset_index(name="Count")
    )
    totals = grp.groupby("DEP_HOUR")["Count"].transform("sum")
    grp["Pct"] = grp["Count"] / totals * 100
    return grp


@st.cache_data(show_spinner=False)
def _delay_cat_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if "DelayCategory" not in df.columns:
        return pd.DataFrame()
    grp = df["DelayCategory"].value_counts().reset_index()
    grp.columns = ["DelayCategory", "Count"]
    grp["Pct"] = grp["Count"] / grp["Count"].sum() * 100
    return grp


def render(df: pd.DataFrame) -> None:
    story_banner(
        "The data reveals a clear pattern: when you fly matters more than you think. "
        "Some time slots are structurally broken — not by accident, by design."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # HERO ROW — Full-width calendar heatmap (most impactful visual first)
    # ═══════════════════════════════════════════════════════════════════════════
    section_header("📅 When In The Month Is Dangerous?")
    heat_df = _calendar_heatmap_data(df)
    month_order = ["January", "July", "October"]
    heat_df = heat_df[heat_df["MONTH_LABEL"].isin(month_order)]
    if not heat_df.empty:
        pivot = heat_df.pivot(index="MONTH_LABEL", columns="DAY_OF_MONTH", values="AvgDelay")
        pivot = pivot.reindex(index=[m for m in month_order if m in pivot.index])
        fig = go.Figure(
            go.Heatmap(
                z=pivot.values.round(1),
                x=[str(d) for d in pivot.columns],
                y=pivot.index.tolist(),
                colorscale="RdYlGn_r",
                hovertemplate="<b>%{y} — Day %{x}</b><br>Avg Delay: %{z:.1f} min<extra></extra>",
                text=pivot.values.round(0).astype(str),
                texttemplate="%{text}",
                textfont=dict(size=9),
                colorbar=dict(title="Avg Delay (min)"),
            )
        )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title="Calendar Heatmap — Avg Departure Delay per Day",
            height=220,
            margin_t=44, margin_b=30, margin_l=80, margin_r=20,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption("🔴 Red = worst delay days. January mid-month and late-October stand out across all airlines.")
    else:
        st.info("Calendar data not available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 2 — Day trend (wide) | Day-of-week (narrow)
    # Asymmetric 2:1 split — feels magazine-style not grid-style
    # ═══════════════════════════════════════════════════════════════════════════
    section_header("📈 Day & Week Patterns")
    c_wide, c_narrow = st.columns([2, 1])

    with c_wide:
        trend_df = _daily_trend(df)
        trend_df = trend_df[trend_df["MONTH_LABEL"].isin(["January", "July", "October"])]
        if not trend_df.empty:
            grand_mean = df["DEP_DELAY"].mean()
            color_map = {"January": ACCENT_BLUE, "July": ACCENT_YELLOW, "October": ACCENT_GREEN}
            fig = px.line(
                trend_df,
                x="DAY_OF_MONTH",
                y="AvgDelay",
                color="MONTH_LABEL",
                color_discrete_map=color_map,
                markers=True,
                title="Daily Avg Delay Trend — Jan vs Jul vs Oct",
                labels={"AvgDelay": "Avg Dep Delay (min)", "DAY_OF_MONTH": "Day of Month"},
            )
            fig.add_hline(
                y=grand_mean,
                line_dash="dash",
                line_color=ACCENT_RED,
                annotation_text=f"Grand Mean: {grand_mean:.1f} min",
                annotation_position="top left",
                annotation_font=dict(color=ACCENT_RED, size=10),
            )
            try:
                worst_row = trend_df.loc[trend_df["AvgDelay"].idxmax()]
                fig.add_annotation(
                    x=worst_row["DAY_OF_MONTH"],
                    y=worst_row["AvgDelay"],
                    text=f"⚠️ Worst: {worst_row['AvgDelay']:.1f} min<br>{worst_row['MONTH_LABEL']} Day {int(worst_row['DAY_OF_MONTH'])}",
                    showarrow=True, arrowhead=2,
                    font=dict(color=ACCENT_RED, size=9),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor=ACCENT_RED,
                )
            except Exception:
                pass
            fig.update_traces(line=dict(width=2.5))
            fig.update_layout(**PLOTLY_LAYOUT, height=340)
            fig.update_xaxes(rangeslider_visible=True, dtick=5)
            st.plotly_chart(fig, width="stretch")
            st.caption("Use the range slider below the chart to zoom into specific date ranges.")
        else:
            st.info("Trend data not available.")

    with c_narrow:
        dow_df = _dow_delay(df)
        if not dow_df.empty:
            best_idx = dow_df["AvgDelay"].idxmin()
            worst_idx = dow_df["AvgDelay"].idxmax()
            bar_colors = []
            for i, row in dow_df.iterrows():
                if i == best_idx:
                    bar_colors.append(ACCENT_GREEN)
                elif i == worst_idx:
                    bar_colors.append(ACCENT_RED)
                else:
                    bar_colors.append(ACCENT_BLUE)
            fig = go.Figure(
                go.Bar(
                    x=dow_df["DOW"],
                    y=dow_df["AvgDelay"].round(1),
                    marker=dict(color=bar_colors, line=dict(width=0)),
                    hovertemplate="<b>%{x}</b><br>Avg Delay: %{y:.1f} min<extra></extra>",
                )
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Best & Worst Day",
                height=340,
            )
            st.plotly_chart(fig, width="stretch")
            best_day = dow_df.loc[best_idx, "DOW"]
            worst_day = dow_df.loc[worst_idx, "DOW"]
            day_full = {"Mon":"Monday","Tue":"Tuesday","Wed":"Wednesday","Thu":"Thursday",
                        "Fri":"Friday","Sat":"Saturday","Sun":"Sunday"}
            st.caption(f"✅ **{day_full.get(best_day, best_day)}** is safest  |  ❌ **{day_full.get(worst_day, worst_day)}** is worst")
        else:
            st.info("Day-of-week data not available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 3 — Hour delay (wide hero) | Donut (accent column)
    # AGENT FIX: Use integer x-axis (0–23) to prevent alphabetical sort
    # that was cutting the chart off at "2 PM" (strings were sorting wrong)
    # ═══════════════════════════════════════════════════════════════════════════
    section_header("🕐 Best & Worst Hours to Fly")
    c_main, c_side = st.columns([3, 1])

    with c_main:
        hour_df = _hour_delay(df)
        if not hour_df.empty:
            max_delay = hour_df["AvgDelay"].max()
            min_delay = hour_df["AvgDelay"].min()
            colors = []
            for v in hour_df["AvgDelay"]:
                t = (v - min_delay) / (max_delay - min_delay + 1e-9)
                r = int(63 + t * (220 - 63))
                g = int(185 - t * (185 - 60))
                b = int(80 - t * (80 - 60))
                colors.append(f"rgb({r},{g},{b})")

            fig = go.Figure(
                go.Bar(
                    # FIX: use integer hour (0–23) as x so order is always 0→23
                    x=hour_df["Hour"],
                    y=hour_df["AvgDelay"].round(1),
                    marker=dict(color=colors, line=dict(width=0)),
                    hovertemplate="<b>%{customdata}</b><br>Avg Delay: %{y:.1f} min<extra></extra>",
                    customdata=hour_df["HourLabel"],
                )
            )
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Avg Departure Delay by Hour of Day (Midnight to 11 PM)",
                xaxis=dict(
                    tickmode="array",
                    tickvals=list(range(24)),
                    ticktext=[_hour_label(h) for h in range(24)],
                    tickangle=-45,
                    title="Scheduled Departure Hour",
                ),
                yaxis_title="Avg Dep Delay (min)",
                height=380,
            )
            # Annotate the best hour
            best_hour = int(hour_df.loc[hour_df["AvgDelay"].idxmin(), "Hour"])
            best_val = float(hour_df["AvgDelay"].min())
            fig.add_annotation(
                x=best_hour, y=best_val,
                text=f"✈️ Best: {_hour_label(best_hour)}<br>{best_val:.1f} min",
                showarrow=True, arrowhead=2, ay=-40,
                font=dict(color=ACCENT_GREEN, size=10, family="Inter"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor=ACCENT_GREEN,
            )
            st.plotly_chart(fig, width="stretch")
            worst_hour = int(hour_df.loc[hour_df["AvgDelay"].idxmax(), "Hour"])
            worst_val = float(hour_df["AvgDelay"].max())
            st.caption(
                f"🌙 Worst hour: **{_hour_label(worst_hour)}** ({worst_val:.1f} min avg delay).  "
                f"✈️ Book the **{_hour_label(best_hour)}** flight — delays are lowest."
            )
        else:
            st.info("Hour data not available.")

    with c_side:
        cat_df = _delay_cat_breakdown(df)
        if not cat_df.empty:
            fig = px.pie(
                cat_df,
                names="DelayCategory",
                values="Count",
                color="DelayCategory",
                color_discrete_map=DELAY_CATEGORY_COLORS,
                hole=0.52,
                title="Delay Mix",
                category_orders={"DelayCategory": DELAY_CATEGORY_ORDER},
            )
            fig.update_traces(
                hovertemplate="<b>%{label}</b><br>%{value:,} flights<br>%{percent}<extra></extra>",
                textinfo="percent",
                textfont_size=11,
            )
            fig.update_layout(**PLOTLY_LAYOUT, height=380, showlegend=True,
                              legend_orientation="v", legend_x=0, legend_y=-0.3)
            st.plotly_chart(fig, width="stretch")
            try:
                on_time_pct = cat_df.loc[cat_df["DelayCategory"] == "On-Time/Early", "Pct"].values[0]
                st.caption(f"📊 **{on_time_pct:.1f}%** of flights depart on-time or early.")
            except Exception:
                pass
        else:
            st.info("No category data available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # ROW 4 — Full-width stacked bar (how delays accumulate through the day)
    # ═══════════════════════════════════════════════════════════════════════════
    section_header("⏳ How Delays Accumulate Through the Day")
    hour_cat_df = _hour_category_pct(df)
    if not hour_cat_df.empty:
        fig = go.Figure()
        for cat in DELAY_CATEGORY_ORDER:
            sub = (
                hour_cat_df[hour_cat_df["DelayCategory"] == cat]
                .set_index("DEP_HOUR")
                .reindex(range(24), fill_value=0)  # FIX: all 24 hours
            )
            fig.add_trace(
                go.Bar(
                    name=cat,
                    x=list(range(24)),      # integer hours = correct order
                    y=sub["Pct"].values.round(1),
                    marker_color=DELAY_CATEGORY_COLORS.get(cat, "#8b949e"),
                    hovertemplate=f"<b>{cat}</b><br>%{{customdata}}: %{{y:.1f}}%<extra></extra>",
                    customdata=[_hour_label(h) for h in range(24)],
                )
            )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            barmode="stack",
            title="Delay Category Mix by Hour of Day — % of Flights per Hour",
            yaxis_title="% of Flights",
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(24)),
                ticktext=[_hour_label(h) for h in range(24)],
                tickangle=-45,
                title="Scheduled Departure Hour",
            ),
            height=400,
            legend_orientation="h", legend_yanchor="bottom", legend_y=1.02,
            legend_xanchor="right", legend_x=1,
        )
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "⏰ Green shrinks and red grows through the day — cascading delays build up "
            "as airlines run out of recovery time. 6 AM is the safest slot."
        )
    else:
        st.info("Hourly breakdown data not available.")
