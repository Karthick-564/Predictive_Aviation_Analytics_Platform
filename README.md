[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/PlqmsmDX)



# ✈️ Predictive Aviation Analytics Pipeline & Interactive Dashboard

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)
![Data Size](https://img.shields.io/badge/Data-1.7M%20Rows-success.svg)

##  Executive Summary
This repository contains an end-to-end data science and machine learning pipeline designed to analyze, process, and cluster **1.7 million+ US flight records**. The primary objective of this project is to identify structural bottlenecks in the national aviation network, isolate severe weather and carrier-induced anomalies, and present these findings through an enterprise-grade, interactive web dashboard.

By utilizing advanced feature engineering, Principal Component Analysis (PCA),, this project successfully separates standard day-to-day flight operations from severe, cascading network meltdowns.

---

##  Repository Structure & Project Timeline

The project is structured chronologically, representing an 8-week agile data science sprint. **Inside every weekly folder, you will find a detailed documentation report alongside the `.ipynb` Jupyter Notebook containing the executable code.**

*  **`week_1` & `week_2` : Data Acquisition & Exploratory Data Analysis (EDA)**
  * Initial ingestion of 1.7M rows of Bureau of Transportation Statistics data.
  * Identification of heavy right-skew distributions in delay columns and seasonal traffic spikes.

*  **`Week_3` & `Week_4` : Data Cleaning & Outlier Management**
  * Handled severe structural missingness (NaN values) using median imputation.
  * Capped extreme operational breakdowns at 24 hours (1440 mins) to preserve minority-class anomaly integrity without destroying model weights.

*  **`Week_6` : Advanced Feature Engineering**
  * Applied Cube Root mathematical transformations to normalize right-skewed delay data.
  * Executed high-cardinality Label Encoding for hundreds of distinct US airport codes and carrier identifiers.

*  **`Week_7` : Dimensionality Reduction (PCA)**
  * Eliminated target leakage by strictly isolating delay variables from the feature matrix.
  * Applied `StandardScaler` to expose massive, sparse operational anomalies.
  * Compressed 15+ complex features down to **11 Principal Components**, successfully retaining **>85% of the mathematical variance**.

*  **`Week_8` :  Dashboard Deployment**
  *  Built a low-latency, highly interactive **Streamlit** dashboard for executive storytelling.
  * Mapped PCA outputs and temporal trends to dynamic filters, allowing users to visually isolate network failures by carrier and season without performance degradation.

* **`Final_presentation`**
  * Contains the final slide decks and visualizations summarizing the business impact and statistical findings.

---

## 🛠️ Tech Stack & Methodologies
* **Language:** Python 3.x
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (PCA, K-Means, StandardScaler, VarianceThreshold)
* **Data Visualization:** Matplotlib, Seaborn, Plotly
* **Web Deployment:** Streamlit (Cached for high-performance memory management on large datasets)

---


The capstone of this project is the interactive Streamlit dashboard located in `Week_8`. The app uses `@st.cache_data` and the use of parquet  to instantly load the 1.7 million rows into RAM, ensuring a minimum lag analytical experience.

