"""
styles.py — CSS for Flight Delay Intelligence Dashboard.
Theme: "Clear Skies" — light, airy, colorful. Inspired by airline boarding-pass design.
Background is a soft sky-white gradient. Cards use crisp white + coloured accents.
Sidebar uses a vibrant sky-blue → indigo gradient (colorful, not monotonous).
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 0.5rem;
    max-width: 1480px;
}

/* ── Main background: light sky gradient ── */
.stApp {
    background: linear-gradient(160deg, #f0f7ff 0%, #e8f4fd 40%, #f5f0ff 100%);
    min-height: 100vh;
}

/* ── Top navigation buttons ── */
/* Secondary (inactive) nav buttons */
div[data-testid="stColumn"] .stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #475569 !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 6px 4px !important;
    transition: all 0.15s !important;
}
div[data-testid="stColumn"] .stButton > button[kind="secondary"]:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    color: #1d4ed8 !important;
}
/* Primary (active) nav button */
div[data-testid="stColumn"] .stButton > button[kind="primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    padding: 6px 4px !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.35) !important;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px 14px;
    text-align: center;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s, transform 0.15s;
}
.kpi-card:hover {
    box-shadow: 0 6px 20px rgba(37,99,235,0.12);
    transform: translateY(-2px);
}
.kpi-value {
    font-size: clamp(1.1rem, 2.8vw, 1.9rem);
    font-weight: 800;
    color: #2563eb;
    margin: 0;
    line-height: 1.15;
    word-break: break-word;
}
.kpi-label {
    font-size: 0.68rem;
    color: #64748b;
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
}
.kpi-sub {
    font-size: 0.68rem;
    color: #16a34a;
    margin-top: 3px;
    font-weight: 500;
}
.kpi-bad  { color: #dc2626 !important; }
.kpi-warn { color: #d97706 !important; }
.kpi-good { color: #16a34a !important; }

/* ── Insight Cards ── */
.insight-card {
    background: #ffffff;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563eb;
}
.insight-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 6px;
}
.insight-body {
    font-size: 0.78rem;
    color: #475569;
    line-height: 1.55;
}
.insight-action {
    font-size: 0.74rem;
    color: #2563eb;
    margin-top: 8px;
    font-style: italic;
    font-weight: 500;
}

/* ── Section Header ── */
.section-header {
    font-size: 0.78rem;
    font-weight: 700;
    color: #2563eb;
    border-left: 3px solid #2563eb;
    padding-left: 10px;
    margin: 22px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Story Banner ── */
.story-banner {
    background: linear-gradient(135deg, #eff6ff 0%, #f5f3ff 100%);
    border: 1px solid #bfdbfe;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 14px 20px;
    margin-bottom: 18px;
    font-size: 0.88rem;
    color: #3730a3;
    font-style: italic;
    line-height: 1.65;
}

/* ── Sidebar — clean blue-tinted white (gradient caused toggle to disappear) ── */
[data-testid="stSidebar"] {
    background: #f0f7ff !important;
    border-right: 2px solid #bfdbfe !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #1e40af !important;
    font-weight: 700;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: #1e3a8a !important;
    font-size: 0.84rem;
}
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
}

/* ── Plotly charts ── */
.stPlotlyChart {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    background: #ffffff;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f8fafc;
    border-bottom: 2px solid #e2e8f0;
    border-radius: 8px 8px 0 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    font-size: 0.84rem;
    font-weight: 500;
    padding: 10px 20px;
    border-radius: 6px 6px 0 0;
}
.stTabs [aria-selected="true"] {
    background: #eff6ff !important;
    color: #2563eb !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #2563eb;
}

/* ── DataFrames ── */
.stDataFrame { border-radius: 10px; border: 1px solid #e2e8f0 !important; box-shadow: 0 1px 6px rgba(0,0,0,0.04); }
.stDataFrame table { background: #ffffff !important; color: #1e293b !important; }
.stDataFrame th {
    background: #f8fafc !important;
    color: #2563eb !important;
    border-bottom: 2px solid #e2e8f0 !important;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.stDataFrame td { color: #334155 !important; border-color: #f1f5f9 !important; font-size: 0.82rem; }
.stDataFrame tr:hover td { background: #f0f7ff !important; }

hr { border-color: #e2e8f0; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def story_banner(text: str) -> None:
    st.markdown(f"<div class='story-banner'>{text}</div>", unsafe_allow_html=True)


def kpi_card(label: str, value: str, sub: str = "", color_class: str = "") -> None:
    st.markdown(
        f"""<div class='kpi-card'>
            <div class='kpi-value {color_class}'>{value}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-sub'>{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def insight_card(title: str, body: str, action: str = "") -> None:
    action_html = f"<div class='insight-action'>▶ {action}</div>" if action else ""
    st.markdown(
        f"""<div class='insight-card'>
            <div class='insight-title'>{title}</div>
            <div class='insight-body'>{body}</div>
            {action_html}
        </div>""",
        unsafe_allow_html=True,
    )


def section_header(text: str) -> None:
    st.markdown(f"<div class='section-header'>{text}</div>", unsafe_allow_html=True)
