"""
loader.py — Parquet conversion, caching, and data loading for the dashboard.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.constants import AIRLINE_NAMES, MONTH_MAP

# ── Path constants ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

ENGINEERED_CSV = DATA_DIR / "flight_delay_engineered.csv"
PCA_CSV = DATA_DIR / "flight_delay_pca.csv"
CLEANED_CSV = DATA_DIR / "cleaned_flights.csv"

ENGINEERED_PARQUET = DATA_DIR / "engineered.parquet"
PCA_PARQUET = DATA_DIR / "pca.parquet"
CLEANED_PARQUET = DATA_DIR / "cleaned.parquet"

# Fallback locations (original dataset folder in project)
_FALLBACK_ENG_CSV = ROOT.parent / "dataset" / "flight_delay_engineered.csv"
_FALLBACK_PCA_CSV = ROOT.parent / "dataset" / "flight_delay_PCA_final.csv"


def _resolve_csv(primary: Path, fallback: Path) -> Path:
    """Return first path that exists."""
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    raise FileNotFoundError(
        f"Dataset not found at {primary} or {fallback}.\n"
        "Please place the CSV files in the flight_intel_v2/data/ directory."
    )


def convert_to_parquet() -> None:
    """
    Convert CSV datasets to Parquet on first run only.
    Also adds AIRLINE_NAME and MONTH_LABEL columns.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── Engineered dataset ────────────────────────────────────────────────
    if not ENGINEERED_PARQUET.exists():
        csv_path = _resolve_csv(ENGINEERED_CSV, _FALLBACK_ENG_CSV)
        with st.spinner(f"Converting {csv_path.name} to Parquet (one-time) …"):
            df = pd.read_csv(csv_path, low_memory=False)

            # Ensure numeric types
            for col in [
                "DEP_DELAY", "ARR_DELAY", "CARRIER_DELAY", "WEATHER_DELAY",
                "NAS_DELAY", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY",
                "CANCELLED", "MONTH", "DAY_OF_MONTH", "CRS_DEP_TIME",
                "CRS_ARR_TIME", "CRS_DEP_TIME_SCALED", "CRS_ARR_TIME_SCALED",
            ]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Airline full name
            if "OP_UNIQUE_CARRIER" in df.columns:
                df["AIRLINE_NAME"] = (
                    df["OP_UNIQUE_CARRIER"]
                    .map(AIRLINE_NAMES)
                    .fillna(df["OP_UNIQUE_CARRIER"])
                )

            # Month label
            if "MONTH" in df.columns:
                df["MONTH_LABEL"] = df["MONTH"].map(MONTH_MAP).fillna("Other")

            # ── Departure hour — smart format detection ──────────────────────
            # BTS data can store CRS_DEP_TIME as either:
            #   (a) HHMM integer  e.g. 835 = 8:35 AM, 2359 = 11:59 PM  → max ~2400
            #   (b) minutes since midnight  e.g. 840 = 14:00 = 2 PM     → max ~1440
            # Using // 100 on (b) gives max 14, which looks like chart stops at 2 PM.
            # Fix: detect format by max value and use the correct divisor.
            if "CRS_DEP_TIME" in df.columns:
                dep_time = pd.to_numeric(df["CRS_DEP_TIME"], errors="coerce").fillna(0)
                max_val = dep_time.max()
                if max_val <= 1440:
                    # minutes-since-midnight format → divide by 60
                    df["DEP_HOUR"] = (dep_time // 60).clip(0, 23).astype("Int8")
                else:
                    # HHMM format → divide by 100 (standard BTS)
                    df["DEP_HOUR"] = (dep_time // 100).clip(0, 23).astype("Int8")

            # Readable route: city part → DEST Airport
            if "ORIGIN_CITY_NAME" in df.columns and "DEST" in df.columns:
                city_part = df["ORIGIN_CITY_NAME"].str.split(",").str[0].str.strip()
                df["ROUTE"] = city_part + " → " + df["DEST"].str.strip() + " Airport"
                df["ORIGIN_CITY_SHORT"] = city_part

            # DEST city fallback (code + Airport)
            if "DEST" in df.columns:
                df["DEST_CITY"] = df["DEST"].str.strip() + " Airport"

            # DelayCategory — ensure it exists
            if "DelayCategory" not in df.columns:
                conditions = [
                    df["DEP_DELAY"] <= 0,
                    (df["DEP_DELAY"] > 0) & (df["DEP_DELAY"] <= 15),
                    (df["DEP_DELAY"] > 15) & (df["DEP_DELAY"] <= 45),
                    df["DEP_DELAY"] > 45,
                ]
                choices = ["On-Time/Early", "Slight Delay", "Moderate Delay", "Severe Delay"]
                df["DelayCategory"] = pd.Categorical(
                    pd.cut(df["DEP_DELAY"], bins=[-999, 0, 15, 45, 9999],
                           labels=choices),
                    categories=choices,
                    ordered=True,
                )

            # ── PERFORMANCE: Vectorized Day-of-Week (avoids apply() on 1.7M rows) ──
            # AGENT DECISION: pre-compute DOW in parquet to eliminate slow .apply()
            if "YEAR" in df.columns and "MONTH" in df.columns and "DAY_OF_MONTH" in df.columns:
                try:
                    dates = pd.to_datetime({
                        "year": df["YEAR"].fillna(2024).astype(int),
                        "month": df["MONTH"].fillna(1).astype(int),
                        "day": df["DAY_OF_MONTH"].fillna(1).astype(int),
                    }, errors="coerce")
                    # 0=Monday, 6=Sunday (matches Python weekday())
                    df["DOW_NUM"] = dates.dt.dayofweek.astype("Int8")
                except Exception:
                    df["DOW_NUM"] = pd.NA

            df.to_parquet(ENGINEERED_PARQUET, index=False)

    # ── PCA dataset ───────────────────────────────────────────────────────
    if not PCA_PARQUET.exists():
        csv_path = _resolve_csv(PCA_CSV, _FALLBACK_PCA_CSV)
        with st.spinner(f"Converting {csv_path.name} to Parquet (one-time) …"):
            df = pd.read_csv(csv_path, low_memory=False)
            df.to_parquet(PCA_PARQUET, index=False)


@st.cache_data(show_spinner=False)
def load_engineered() -> pd.DataFrame:
    """Load the engineered flight dataset from Parquet."""
    return pd.read_parquet(ENGINEERED_PARQUET)


@st.cache_data(show_spinner=False)
def load_pca() -> pd.DataFrame:
    """Load the PCA dataset from Parquet."""
    return pd.read_parquet(PCA_PARQUET)


@st.cache_data(show_spinner=False)
def apply_filters(
    df: pd.DataFrame,
    month_filter: str,
    carrier_filter: list[str],
) -> pd.DataFrame:
    """Apply sidebar filters to the dataframe."""
    month_map = {"January": 1, "July": 7, "October": 10}
    if month_filter != "All":
        month_num = month_map.get(month_filter)
        if month_num is not None:
            df = df[df["MONTH"] == month_num]
    if carrier_filter:
        df = df[df["AIRLINE_NAME"].isin(carrier_filter)]
    return df
