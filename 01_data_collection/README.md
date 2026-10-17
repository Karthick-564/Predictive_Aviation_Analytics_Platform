# 01 · Data Collection & Initial Profiling

> **Goal:** Source a credible, large-scale aviation dataset and understand its raw structure before any transformation.

---

## 📦 Dataset

| Attribute | Value |
|---|---|
| **Source** | US Bureau of Transportation Statistics (BTS) |
| **URL** | https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp |
| **Coverage** | January, July, October flight operations |
| **Records** | ~1.7 million rows |
| **Format** | CSV |

The BTS Airline On-Time Performance dataset is the authoritative source for US domestic flight delay data. It is used in academic research, government policy analysis, and industry benchmarking due to its comprehensive coverage and structured format.

---

## 🗂️ Key Columns

| Column | Description |
|---|---|
| `CARRIER` | Airline carrier code |
| `ORIGIN` / `DEST` | Origin and destination airport codes |
| `DEP_DELAY` | Departure delay in minutes |
| `ARR_DELAY` | Arrival delay in minutes |
| `CARRIER_DELAY` | Minutes attributed to carrier |
| `WEATHER_DELAY` | Minutes attributed to weather |
| `NAS_DELAY` | National Airspace System delay |
| `SECURITY_DELAY` | Security-caused delay |
| `LATE_AIRCRAFT_DELAY` | Cascading delay from late incoming aircraft |
| `CANCELLED` | 1 if flight was cancelled |
| `CANCELLATION_CODE` | Reason code: A=Carrier, B=Weather, C=NAS, D=Security |

---

## 🔍 Initial Observations

- The raw dataset is **heavily right-skewed** — the majority of flights are on-time, but extreme outliers (delays > 300 min) exist
- **Missing values** are concentrated in delay-cause columns (only populated when a delay occurs)
- Three months (Jan, Jul, Oct) were selected to capture **seasonal variation**: winter operations, summer peak, and fall baseline
- Merging all three months yields **~1.7 million records** for a statistically robust analysis

---

## 📓 Notebook

See [`data_collection.ipynb`](./data_collection.ipynb) for:
- Library setup and environment validation
- Raw data loading and `df.head()` / `df.info()` profiling
- Column type inspection and null count summary
- Decision log: why this dataset was chosen over alternatives
