# 05 · Dimensionality Reduction

> **Goal:** Reduce the high-dimensional feature space to a compact set of principal components that retain maximum variance — enabling efficient downstream visualisation and analysis.

---

## 🔢 Why Dimensionality Reduction?

After feature engineering, the dataset has **30+ correlated features**. Many delay-cause columns are highly collinear (e.g., `CARRIER_DELAY` and `LATE_AIRCRAFT_DELAY` correlate at r = 0.78). PCA:
- Removes multicollinearity
- Reduces computational cost for visualisation
- Reveals latent structure in delay patterns

---

## 📉 PCA Results

| Component | Variance Explained | Cumulative |
|---|---|---|
| PC1 | 38.4% | 38.4% |
| PC2 | 21.7% | 60.1% |
| PC3 | 12.3% | 72.4% |
| PC4 | 7.8% | 80.2% |
| PC5 | 4.1% | 84.3% |
| PC6 | 2.9% | **87.2%** |

**6 components explain 87% of the total variance** — reducing from 30+ features to 6 without significant information loss.

---

## 🔍 Component Interpretation

| Component | Dominant Features | Interpretation |
|---|---|---|
| PC1 | `CARRIER_DELAY`, `LATE_AIRCRAFT_DELAY` | *Operational / Carrier efficiency axis* |
| PC2 | `WEATHER_DELAY`, `NAS_DELAY` | *External/environmental disruption axis* |
| PC3 | `DEP_DELAY`, `TAXI_OUT` | *Ground operations axis* |

---

## ⚙️ Implementation

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=6)
X_pca = pca.fit_transform(X_scaled)

# Explained variance
print(pca.explained_variance_ratio_.cumsum())
```

---

## 📊 Outputs

- **Scree plot** — elbow at component 6 confirms the 6-component selection
- **2D PCA scatter** — coloured by `DELAY_SEVERITY`, showing natural cluster separation
- **Biplot** — feature loadings overlaid on PC1 vs PC2 space
- `flight_delay_dashboard_ready.csv` — PCA-reduced dataset used by the dashboard

> ⚠️ Output CSVs (~380 MB) are not tracked in git. Run this notebook to regenerate.

---

## 📓 Notebook

See [`dimensionality_reduction.ipynb`](./dimensionality_reduction.ipynb) for full PCA implementation, scree plot, 2D visualisation, and feature loading analysis.
