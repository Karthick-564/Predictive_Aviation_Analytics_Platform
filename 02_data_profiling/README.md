# 02 · Data Profiling — "Know Your Data"

> **Goal:** Load the raw dataset, inspect its structure, understand data types, and generate an initial impression report before any transformation.

---

## 🔍 What Was Done

| Task | Finding |
|---|---|
| Shape inspection | 1,724,318 rows × 32 columns |
| Data types | Mix of int64, float64, object — delay-cause columns stored as float |
| Null count | 4.2M missing values, concentrated in delay-cause columns |
| Duplicate rows | 0 exact duplicates found |
| Value ranges | `ARR_DELAY` ranges from −82 to +2,832 minutes |
| Unique carriers | 18 unique airline carrier codes |
| Unique airports | 362 unique origin airports |

---

## 📋 Column Categories Identified

```
Identity       → YEAR, MONTH, DAY_OF_MONTH, DAY_OF_WEEK, FL_DATE
Carrier        → OP_CARRIER, OP_CARRIER_FL_NUM
Route          → ORIGIN, DEST, ORIGIN_CITY_NAME, DEST_CITY_NAME
Schedule       → CRS_DEP_TIME, DEP_TIME, CRS_ARR_TIME, ARR_TIME
Delay (target) → DEP_DELAY, ARR_DELAY
Delay causes   → CARRIER_DELAY, WEATHER_DELAY, NAS_DELAY,
                 SECURITY_DELAY, LATE_AIRCRAFT_DELAY
Cancellations  → CANCELLED, CANCELLATION_CODE, DIVERTED
Ground ops     → TAXI_OUT, TAXI_IN, WHEELS_OFF, WHEELS_ON
```

---

## 💡 Key Early Observations

1. **Structural missingness** — delay-cause columns are only populated when a delay actually occurs. This is not random missingness; it's domain-meaningful and must be imputed with 0, not dropped.
2. **Right-skewed distribution** — most flights are on time; delay values have a long right tail with extreme outliers.
3. **Date fragmentation** — date/time fields are split across multiple columns; will need consolidation in feature engineering.

---

## 📓 Notebook

See [`data_profiling.ipynb`](./data_profiling.ipynb) for full profiling code, null heatmaps, and data type summary tables.
