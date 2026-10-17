# 03 · Data Cleaning

> **Goal:** Transform raw, messy flight records into an analysis-ready dataset by handling missing values and detecting/treating outliers.

---

## 🧹 Cleaning Strategy

The raw dataset has two classes of missing data with fundamentally different semantics:

| Column Type | Missing Reason | Strategy |
|---|---|---|
| Delay-cause columns (`CARRIER_DELAY`, `WEATHER_DELAY`, etc.) | Structurally missing — only populated when a delay occurs | **Impute with 0** (non-delayed flight = 0 minutes of that delay type) |
| Operational columns (`DEP_TIME`, `ARR_TIME`) | Data entry gaps or cancellations | **Drop rows** where flight was cancelled AND operational data is absent |

---

## 📐 Outlier Detection

Two methods applied in tandem:

### Z-Score Method
Applied to continuous delay columns. Flights with `|z| > 3` (beyond 3 standard deviations) flagged as extreme outliers.

```
Before: Max ARR_DELAY = 2,832 minutes (47 hours)
After:  Max ARR_DELAY = 428 minutes (capped at 99th percentile)
```

### IQR / Box-Plot Method
Applied to validate Z-score results. Whiskers set at 1.5×IQR to visualise the outlier boundary.

---

## 📊 Before vs. After

| Metric | Before | After |
|---|---|---|
| Total rows | 1,724,318 | 1,698,441 |
| Null values | 4.2M | 0 |
| Max delay (minutes) | 2,832 | 428 |
| Skewness (ARR_DELAY) | 9.47 | 3.21 |

---

## 📁 Output

The cleaned dataset (`flight_delay_cleaned.csv`) is used as the input for all downstream notebooks.

> ⚠️ This file (~273 MB) is not tracked in git. Download raw data from BTS and run this notebook to regenerate it.

---

## 📓 Notebook

See [`data_cleaning.ipynb`](./data_cleaning.ipynb) for step-by-step cleaning code, before/after distribution plots, and null-handling rationale.
