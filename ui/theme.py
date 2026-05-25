"""Dark SaaS-style Streamlit theme CSS."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

h1, h2, h3 {
    color: #e8e8f0 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12121f 0%, #1a1a2e 100%);
    border-right: 1px solid #2d2d44;
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 1.4rem;
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid #2d2d44;
    border-radius: 12px;
    padding: 16px;
}

div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #6366f1);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: transform 0.15s, box-shadow 0.15s;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}

/* Cards via containers */
.agent-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.agent-card h4 {
    margin: 0 0 0.5rem 0;
    color: #a78bfa;
}

.status-running { color: #fbbf24; }
.status-completed { color: #34d399; }
.status-error { color: #f87171; }
.status-idle { color: #94a3b8; }

.tagline {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

.insight-box {
    background: rgba(124, 58, 237, 0.1);
    border-left: 4px solid #7c3aed;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
    margin: 1rem 0;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg, #7c3aed, #06b6d4);
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.02);
    border-radius: 8px;
}

/* Hide Streamlit branding footer space */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

hr {
    border-color: #334155;
}
</style>
"""


def apply_theme():
  import streamlit as st
  st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
