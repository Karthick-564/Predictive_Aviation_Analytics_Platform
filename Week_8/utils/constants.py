"""
constants.py — Shared constants for the Flight Delay Intelligence Dashboard.
"""

AIRLINE_NAMES = {
    "AA": "American Airlines",
    "AS": "Alaska Airlines",
    "B6": "JetBlue Airways",
    "DL": "Delta Air Lines",
    "F9": "Frontier Airlines",
    "G4": "Allegiant Air",
    "HA": "Hawaiian Airlines",
    "NK": "Spirit Airlines",
    "OH": "PSA Airlines",
    "OO": "SkyWest Airlines",
    "QX": "Horizon Air",
    "UA": "United Airlines",
    "WN": "Southwest Airlines",
    "WS": "WestJet",
    "YX": "Midwest Express / Republic",
    "9E": "Endeavor Air",
    "YV": "Mesa Airlines",
    "MQ": "Envoy Air",
    "EV": "ExpressJet Airlines",
    "CP": "Compass Airlines",
}

DELAY_CATEGORY_ORDER = [
    "On-Time/Early",
    "Slight Delay",
    "Moderate Delay",
    "Severe Delay",
]

DELAY_CATEGORY_COLORS = {
    "On-Time/Early": "#22c55e",
    "Slight Delay":  "#f59e0b",
    "Moderate Delay":"#f97316",
    "Severe Delay":  "#ef4444",
    "Cancelled":     "#94a3b8",
}

DELAY_CAUSE_LABELS = {
    "CARRIER_DELAY":      "Carrier (Airline's Fault)",
    "LATE_AIRCRAFT_DELAY":"Late Incoming Aircraft",
    "NAS_DELAY":          "Air Traffic Control (NAS)",
    "WEATHER_DELAY":      "Weather",
    "SECURITY_DELAY":     "Security",
}

DELAY_CAUSE_COLS = list(DELAY_CAUSE_LABELS.keys())

MONTH_MAP = {1: "January", 7: "July", 10: "October"}

# ── Light-theme accent palette ─────────────────────────────────────────────────
ACCENT_BLUE   = "#2563eb"   # vivid blue
ACCENT_GREEN  = "#16a34a"   # rich green
ACCENT_RED    = "#dc2626"   # clear red
ACCENT_YELLOW = "#d97706"   # warm amber
ACCENT_ORANGE = "#ea580c"   # deep orange
ACCENT_TEAL   = "#0891b2"   # teal
ACCENT_GREY   = "#64748b"   # slate

# ── Plotly layout — light theme ────────────────────────────────────────────────
# AGENT DECISION: removed xaxis/yaxis from PLOTLY_LAYOUT to prevent
# "multiple values for keyword argument 'yaxis'" crash when callers
# also pass yaxis=dict(...) in update_layout(). Callers must set their own axes.
PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.8)",
    font=dict(color="#1e293b", size=11, family="Inter, sans-serif"),
    margin=dict(t=44, b=44, l=44, r=16),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#e2e8f0",
        borderwidth=1,
        font=dict(size=10, color="#334155"),
    ),
)
