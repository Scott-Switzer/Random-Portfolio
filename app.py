import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time
import engine as eng
import streamlit.components.v1 as components
import config as cfg
from styles import (
    apply_styles, get_theme, toggle_theme, get_colors,
    render_footer, render_metric_cards, render_quote_box, render_section_header
)

# =============================================================================
# PAGE CONFIG - Must be first Streamlit command
# =============================================================================
st.set_page_config(
    page_title="Dartboard Experiment | EMH Test",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# APPLY STYLES
# =============================================================================
apply_styles()

# =============================================================================
# SESSION STATE
# =============================================================================
if 'results' not in st.session_state:
    st.session_state.results = None
    st.session_state.last_params = None

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def get_data():
    return eng.load_and_clean_data('US_SPYdata_2000_2024.csv')

ret_matrix, cap_matrix, min_date, max_date = get_data()

# =============================================================================
# NAVIGATION
# =============================================================================
def get_current_page():
    """Get current page from query params, default to home."""
    params = st.query_params
    return params.get("page", "home")

def navigate_to(page):
    """Navigate to a different page."""
    st.query_params["page"] = page

# Get current page
current_page = get_current_page()

# Top Navigation Bar
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_spacer, nav_col6 = st.columns([2.5, 1, 1.2, 1, 0.8, 0.5, 0.5])

with nav_col1:
    st.markdown("#### 🎯 The Dartboard Experiment")

with nav_col2:
    if st.button("🏠 Home", use_container_width=True, 
                 type="primary" if current_page == "home" else "secondary"):
        navigate_to("home")
        st.rerun()

with nav_col3:
    if st.button("🚀 Experiment", use_container_width=True,
                 type="primary" if current_page == "experiment" else "secondary"):
        navigate_to("experiment")
        st.rerun()

with nav_col4:
    if st.button("📚 Theory", use_container_width=True,
                 type="primary" if current_page == "theory" else "secondary"):
        navigate_to("theory")
        st.rerun()

with nav_col5:
    if st.button("ℹ️ About", use_container_width=True,
                 type="primary" if current_page == "about" else "secondary"):
        navigate_to("about")
        st.rerun()

with nav_col6:
    theme_icon = "🌙" if get_theme() == "light" else "☀️"
    if st.button(theme_icon, help="Toggle dark/light mode"):
        toggle_theme()
        st.rerun()

st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0;'>", unsafe_allow_html=True)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _tail_label(pct: float) -> str:
    """Human-readable location of a value inside a distribution."""
    if pct >= 95: return "extreme right tail"
    if pct >= 85: return "right tail"
    if pct >= 65: return "upper half"
    if pct >= 35: return "middle"
    if pct >= 15: return "lower half"
    if pct >= 5:  return "left tail"
    return "extreme left tail"

def describe_simulation_distribution(res_ew, res_cw, spy_sh=None, iwm_sh=None, regime_label=""):
    """Build a dynamic explanation string based on the realized distributions."""
    c = get_colors()
    res_ew = np.asarray(res_ew, dtype=float)
    res_cw = np.asarray(res_cw, dtype=float)
    res_ew = res_ew[np.isfinite(res_ew)]
    res_cw = res_cw[np.isfinite(res_cw)]

    if len(res_ew) < 10 or len(res_cw) < 10:
        return "<p>Not enough valid simulation output.</p>", 100

    def summarize(x):
        q10, q25, q50, q75, q90 = np.percentile(x, [10, 25, 50, 75, 90])
        return {
            "mean": float(np.mean(x)), "median": float(q50),
            "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
            "q10": float(q10), "q25": float(q25), "q75": float(q75), "q90": float(q90),
            "iqr": float(q75 - q25),
        }

    ew = summarize(res_ew)
    cw = summarize(res_cw)
    n_pair = min(len(res_ew), len(res_cw))
    pair_win = float(np.mean(res_ew[:n_pair] > res_cw[:n_pair]) * 100.0)

    bench_lines = []
    for name, b in [("S&P 500 (SPY)", spy_sh), ("Russell 2000 (IWM)", iwm_sh)]:
        if b is not None and np.isfinite(b):
            ew_pct = float(np.mean(res_ew <= b) * 100.0)
            cw_pct = float(np.mean(res_cw <= b) * 100.0)
            ew_win = float(np.mean(res_ew >= b) * 100.0)
            cw_win = float(np.mean(res_cw >= b) * 100.0)
            bench_lines.append((name, b, ew_pct, cw_pct, ew_win, cw_win))

    header = f" ({regime_label})" if regime_label else ""

    css = f"""
    <style>
    .results-box {{
        background-color: {c['bg_secondary']};
        color: {c['text_primary']};
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        line-height: 1.7;
        font-family: 'IBM Plex Sans', sans-serif;
    }}
    .results-box h3 {{ color: {c['accent']}; margin-top: 0; }}
    .results-box b {{ color: {c['accent']}; }}
    .results-box ul {{ margin: 0.5rem 0 1rem 1.2rem; }}
    .results-box li {{ margin-bottom: 0.5rem; }}
    </style>
    """

    html = f"""
    <div class="results-box">
      <h3>Interpreting the Results{header}</h3>
      <p><b>What this chart shows:</b> Each histogram is the distribution of Sharpe ratios from repeated portfolio simulations.</p>
      <p><b>Distribution summary:</b></p>
      <ul>
        <li><b>Dartboard (EW):</b> mean = {ew["mean"]:.2f}, median = {ew["median"]:.2f}, IQR = {ew["iqr"]:.2f}</li>
        <li><b>Index Proxy (CW):</b> mean = {cw["mean"]:.2f}, median = {cw["median"]:.2f}, IQR = {cw["iqr"]:.2f}</li>
      </ul>
      <p>The equal-weight portfolio beats cap-weight in <b>{pair_win:.0f}%</b> of paired simulations.</p>
    </div>
    """

    if bench_lines:
        html += f'<div class="results-box"><h3>Benchmark Positioning</h3><ul>'
        for (name, b, ew_pct, cw_pct, ew_win, cw_win) in bench_lines:
            html += f"<li><b>{name} = {b:.2f}</b>: {_tail_label(ew_pct)} of EW distribution ({ew_win:.0f}% beat it)</li>"
        html += "</ul></div>"

    height = 350 + (150 if bench_lines else 0)
    return f"<!doctype html><html><head><meta charset='utf-8'></head><body>{css}{html}</body></html>", height

# =============================================================================
# PAGE: HOME
# =============================================================================
if current_page == "home":
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">🎯</div>
        <h1 class="hero-title">The Dartboard Experiment</h1>
        <p class="hero-subtitle">Can random chance match indices?</p>
        <p class="hero-description">
            Burton Malkiel claimed a blindfolded monkey throwing darts at the 
            financial pages could match Wall Street experts. I built a Monte Carlo 
            simulator to test it.
            <br><br>
            Thousands of randomly-generated portfolios. Real CRSP data. 
            No survivorship bias. See how randomness stacks up against the S&P 500.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons - Centered
    col1, col2, col3 = st.columns([