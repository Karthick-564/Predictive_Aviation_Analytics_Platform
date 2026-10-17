# 04 · Feature Engineering

> **Goal:** Transform cleaned data into richer, more informative features that shift analysis from *"how late"* to *"how likely"* and *"why"*.

---

## ⚙️ Features Created

### Categorical Encoding
| Raw Column | Transformation | New Column |
|---|---|---|
| `MONTH` (1, 7, 10) | Mapped to season label | `SEASON` (Winter / Summer / Fall) |
| `CARRIER` | Label encoding + frequency encoding | `CARRIER_FREQ_RANK` |
| `CANCELLATION_CODE` | One-hot encoded | `CANCEL_A`, `CANCEL_B`, `CANCEL_C`, `CANCEL_D` |

### Delay Classification
Binary and multi-class delay labels created for downstream modelling:

```python
# Binary: delayed vs. not delayed (threshold: 15 minutes, per FAA definition)
df['IS_DELAYED'] = (df['ARR_DELAY'] > 15).astype(int)

# Multi-class severity
df['DELAY_SEVERITY'] = pd.cut(df['ARR_DELAY'],
    bins=[-np.inf, 0, 15, 60, 120, np.inf],
    labels=['Early/On-time', 'Minor', 'Moderate', 'Severe', 'Extreme'])
```

### Carrier Risk Score
An aggregate carrier-level risk metric:
```
CARRIER_RISK = (mean_delay × delay_frequency) / max_possible
```
Normalised to [0, 1] — higher score = historically more delay-prone.

### Normalization & Scaling
`StandardScaler` applied to all continuous delay columns before PCA in the next stage:
```
Mean-centered, unit variance → removes bias from different delay magnitude ranges
```

---

## 📊 Key Insight from Feature Engineering

> **Seasonal Predictability:** Engineering the `SEASON` column allowed the analysis to shift from *"how late was the flight?"* to *"what is the probability this flight will be delayed?"* — a far more actionable risk-assessment metric for passengers and airlines.

| Season | Delay Probability |
|---|---|
| Winter | 21.3% |
| Summer | **48.6%** |
| Fall | 19.1% |

---

## 📓 Notebook

See [`feature_engineering.ipynb`](./feature_engineering.ipynb) for full transformation code, distribution plots of engineered features, and correlation analysis with the target variable.
