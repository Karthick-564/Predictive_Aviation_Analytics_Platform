# ✈️ Predictive Aviation Analytics Platform

> **Decoding 1.7 million flight records into visual narratives that reveal the true structural drivers of US flight delays.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🧭 Project Overview

The US aviation network loses millions of operational minutes annually to flight delays. This project builds a complete end-to-end data science pipeline — from raw data ingestion to an interactive analytics dashboard — to answer a deceptively hard question:

> *Are delays caused by the airline, the weather, the airport, or a cascading domino effect?*

Working with **1.7 million flight records** from the US Bureau of Transportation Statistics (BTS), this project applies statistical rigor and visual storytelling to decompose delay root causes across carriers, airports, seasons, and routes.

---

## 📊 Key Findings

| Insight | Finding |
|---|---|
| **Top delay driver** | Carrier-caused delays account for ~42% of total delay minutes |
| **Worst season** | Summer (June–August) shows 2.3× higher delay probability than winter |
| **Cascading effect** | ~38% of arrival delays are directly inherited from departure delays |
| **PCA variance** | 6 principal components explain 87% of variance in delay features |
| **High-risk airports** | ORD, ATL, EWR consistently appear in top-5 delay generators |

---

## 🗂️ Repository Structure

```
predictive-aviation-analytics-platform/
│
├── 01_data_collection/          # Dataset sourcing, schema exploration, initial load
├── 02_eda/                      # Exploratory data analysis & visual storytelling
├── 03_data_cleaning/            # Missing value imputation, outlier detection
├── 04_feature_engineering/      # Feature creation, encoding, normalization
├── 05_dimensionality_reduction/ # PCA, feature selection, variance analysis
└── 06_dashboard/                # Interactive Streamlit dashboard (run locally)
```

---

## 🚀 Tech Stack

| Layer | Tools |
|---|---|
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn, Plotly |
| **Machine Learning** | Scikit-learn (PCA, StandardScaler) |
| **Dashboard** | Streamlit |
| **Data Source** | [BTS Airline On-Time Performance Data](https://www.transtats.bts.gov/) |

---

## 📁 Dataset

The dataset is sourced from the **US Department of Transportation – Bureau of Transportation Statistics (BTS)**:
- **Records:** ~1.7 million flight operations (Jan, Jul, Oct)
- **Features:** 30+ columns including carrier, origin, destination, delay causes, cancellation codes
- **Source:** https://www.transtats.bts.gov/OT_Delay/OT_DelayCause1.asp

> ⚠️ Raw and processed CSV files are not tracked in this repo due to size (~380 MB each). Download from the BTS link above or see the data loading instructions in `01_data_collection/`.

---

## ⚡ Getting Started

```bash
# Clone the repo
git clone https://github.com/Karthick-564/predictive-aviation-analytics-platform.git
cd predictive-aviation-analytics-platform

# Install dependencies
pip install -r 06_dashboard/requirements.txt

# Run the dashboard
streamlit run 06_dashboard/app.py
```

---

## 📈 Pipeline at a Glance

```
Raw BTS Data (1.7M rows)
        │
        ▼
01 Data Collection ──► Schema validation, initial profiling
        │
        ▼
02 EDA ──────────────► Univariate, Bivariate, Temporal, Correlation analysis
        │
        ▼
03 Data Cleaning ────► Missing value imputation, outlier removal (Z-score/IQR)
        │
        ▼
04 Feature Engineering ► Delay categories, SEASON column, carrier risk scores
        │
        ▼
05 Dimensionality Reduction ► PCA (6 components, 87% variance explained)
        │
        ▼
06 Dashboard ────────► Interactive Streamlit app with filters & drill-downs
```

---

