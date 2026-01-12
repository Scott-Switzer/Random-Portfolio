import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import engine as eng
import streamlit.components.v1 as components
import config as cfg
from styles import apply_styles, get_theme, toggle_theme, render_footer, render_metric_card, render_section_title, render_quote_box


st.set_page_config(
    page_title="Dartboard Experiment | EMH Test",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed", 
)

# --- APPLY CUSTOM STYLES ---
apply_styles()

# =============================================================================
# TOP NAVIGATION BAR
# =============================================================================

def render_top_nav(current_page):
    """Render the top navigation bar with theme toggle."""
    theme_icon = "🌙" if get_theme() == "light" else "☀️"
    
    nav_html = f"""
    <div class="top-nav">
        <div class="nav-brand">
            🎯 The Dartboard Experiment
        </div>
        <div class="nav-tabs">
            <span class="nav-tab {'active' if current_page == 'Home' else ''}" 
                  onclick="window.location.href='?page=home'">🏠 Home</span>
            <span class="nav-tab {'active' if current_page == 'Experiment' else ''}"
                  onclick="window.location.href='?page=experiment'">🚀 Experiment</span>
            <span class="nav-tab {'active' if current_page == 'Theory' else ''}"
                  onclick="window.location.href='?page=theory'">📚 Theory</span>
            <span class="nav-tab {'active' if current_page == 'About' else ''}"
                  onclick="window.location.href='?page=about'">ℹ️ About</span>
        </div>
        <div class="nav-right">
            <span class="theme-toggle" title="Toggle theme">{theme_icon}</span>
        </div>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# Since Streamlit doesn't support onclick well, we'll use a cleaner approach:
# Use query params for navigation and a button for theme toggle

# Get current page from query params
query_params = st.query_params
current_page = query_params.get("page", "home")

# Create columns for navigation
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6 = st.columns([2, 1, 1, 1, 1, 0.5])

with nav_col1:
    st.markdown("### 🎯 The Dartboard Experiment")

with nav_col2:
    if st.button("🏠 Home", use_container_width=True, type="secondary" if current_page != "home" else "primary"):
        st.query_params["page"] = "home"
        st.rerun()

with nav_col3:
    if st.button("🚀 Experiment", use_container_width=True, type="secondary" if current_page != "experiment" else "primary"):
        st.query_params["page"] = "experiment"
        st.rerun()

with nav_col4:
    if st.button("📚 Theory", use_container_width=True, type="secondary" if current_page != "theory" else "primary"):
        st.query_params["page"] = "theory"
        st.rerun()

with nav_col5:
    if st.button("ℹ️ About", use_container_width=True, type="secondary" if current_page != "about" else "primary"):
        st.query_params["page"] = "about"
        st.rerun()

with nav_col6:
    theme_icon = "🌙" if get_theme() == "light" else "☀️"
    if st.button(theme_icon, help="Toggle dark/light mode"):
        toggle_theme()
        st.rerun()

st.divider()

# =============================================================================
# PAGE: HOME
# =============================================================================

if current_page == "home":
    # Hero Section
    st.markdown("""
    <div class="hero">
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
    
    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("▶️ Run the Experiment", type="primary", use_container_width=True):
                st.query_params

# --- SESSION STATE ---
if 'results' not in st.session_state:
    st.session_state.results = None
    st.session_state.last_params = None

# --- CACHED BENCHMARK FUNCTION ---
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_cached_benchmark(ticker, start, end, rf):
    return eng.get_benchmark_stats(ticker, start, end, rf)



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
    """
    Build a dynamic explanation string based on the realized distributions.
    res_ew/res_cw: arrays of Sharpe ratios from the simulation.
    spy_sh/iwm_sh: benchmark Sharpes (floats). Can be None.
    """
    res_ew = np.asarray(res_ew, dtype=float)
    res_cw = np.asarray(res_cw, dtype=float)

    # Drop NaNs safely
    res_ew = res_ew[np.isfinite(res_ew)]
    res_cw = res_cw[np.isfinite(res_cw)]

    if len(res_ew) < 10 or len(res_cw) < 10:
        return """
        <div class="theory-box">
        <h3>Interpreting the Simulation Results</h3>
        <p>Not enough valid simulation output to generate a reliable distribution summary.</p>
        </div>
        """, 200

    def summarize(x):
        q10, q25, q50, q75, q90 = np.percentile(x, [10, 25, 50, 75, 90])
        return {
            "n": len(x),
            "mean": float(np.mean(x)),
            "median": float(q50),
            "std": float(np.std(x, ddof=1)) if len(x) > 1 else 0.0,
            "q10": float(q10),
            "q25": float(q25),
            "q75": float(q75),
            "q90": float(q90),
            "iqr": float(q75 - q25),
        }

    ew = summarize(res_ew)
    cw = summarize(res_cw)

    # Paired comparison
    n_pair = min(len(res_ew), len(res_cw))
    pair_win = float(np.mean(res_ew[:n_pair] > res_cw[:n_pair]) * 100.0)

    # Benchmark positioning
    bench_lines = []
    def bench_block(name, b):
        if b is None or not np.isfinite(b):
            return None
        ew_pct = float(np.mean(res_ew <= b) * 100.0)
        cw_pct = float(np.mean(res_cw <= b) * 100.0)
        ew_win = float(np.mean(res_ew >= b) * 100.0)
        cw_win = float(np.mean(res_cw >= b) * 100.0)
        return (name, b, ew_pct, cw_pct, ew_win, cw_win)

    for name, b in [("S&P 500 (SPY)", spy_sh), ("Russell 2000 (IWM)", iwm_sh)]:
        blk = bench_block(name, b)
        if blk:
            bench_lines.append(blk)

    header = f" ({regime_label})" if regime_label else ""

    # FIXED CSS - Forces light theme regardless of Streamlit's dark mode
    css = """
    <style>
    * {
        box-sizing: border-box;
    }
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #f8f9fa !important;
    }
    .theory-box {
        background-color: #f8f9fa !important;
        color: #111111 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin-bottom: 15px !important;
        line-height: 1.7 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif !important;
    }
    .theory-box h3 { 
        color: #0b3c5d !important; 
        margin-top: 0 !important; 
        margin-bottom: 12px !important;
    }
    .theory-box p {
        color: #111111 !important;
        margin-bottom: 10px !important;
    }
    .theory-box ul { 
        margin: 0.5rem 0 1rem 1.2rem !important; 
        color: #111111 !important;
    }
    .theory-box li {
        color: #111111 !important;
        margin-bottom: 8px !important;
    }
    .theory-box b, .theory-box strong {
        color: #0b3c5d !important;
    }
    </style>
    """

    # Build content
    html_content = f"""
    <div class="theory-box">
      <h3>Interpreting the Simulation Results{header}</h3>

      <p><b>What this chart shows:</b> Each histogram is the distribution of Sharpe ratios from repeated portfolio simulations over the selected period.
      A wide distribution means outcomes are highly sensitive to which stocks were randomly drawn (dispersion), not just the weighting scheme.</p>

      <p><b>Distribution summary (from your actual output):</b></p>
      <ul>
        <li><b>Dartboard (Equal-Weight):</b> mean = {ew["mean"]:.2f}, median = {ew["median"]:.2f},
            middle 50% = [{ew["q25"]:.2f}, {ew["q75"]:.2f}] (IQR = {ew["iqr"]:.2f}),
            10–90% range = [{ew["q10"]:.2f}, {ew["q90"]:.2f}]</li>
        <li><b>Index Proxy (Cap-Weight):</b> mean = {cw["mean"]:.2f}, median = {cw["median"]:.2f},
            middle 50% = [{cw["q25"]:.2f}, {cw["q75"]:.2f}] (IQR = {cw["iqr"]:.2f}),
            10–90% range = [{cw["q10"]:.2f}, {cw["q90"]:.2f}]</li>
      </ul>

      <p><b>Equal-weight vs cap-weight (in this run):</b> The equal-weight portfolio beats the cap-weight proxy in
      <b>{pair_win:.0f}%</b> of paired simulations. This is not "skill" — it reflects systematic differences in exposure (often size + rebalancing effects).</p>
    </div>
    """

    if bench_lines:
        html_content += """
        <div class="theory-box">
          <h3>Benchmark Positioning</h3>
          <p><b>How do the benchmarks compare to our random portfolios?</b></p>
          <ul>
        """
        for (name, b, ew_pct, cw_pct, ew_win, cw_win) in bench_lines:
            html_content += f"""
            <li><b>{name} Sharpe = {b:.2f}</b>:
                sits in the <b>{_tail_label(ew_pct)}</b> of the Dartboard distribution (≈ {ew_pct:.0f}th percentile; <b>{ew_win:.0f}%</b> of dartboards beat it),
                and the <b>{_tail_label(cw_pct)}</b> of the Index Proxy distribution (≈ {cw_pct:.0f}th percentile; <b>{cw_win:.0f}%</b> beat it).</li>
            """
        html_content += """
          </ul>
          <p><b>What this means:</b> If the benchmark lines sit in the right tail, it means matching that benchmark Sharpe is difficult. 
          If they sit near the middle, many random draws are comparable on a risk-adjusted basis.</p>
        </div>
        """

    # Calculate dynamic height based on content
    base_height = 420
    bench_height = 280 if bench_lines else 0
    total_height = base_height + bench_height

    full_html = f"""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    </head>
    <body>
    {css}
    {html_content}
    </body>
    </html>
    """

    return full_html, total_height



st.markdown("""
<style>
.theory-box {
    background-color: #f8f9fa;   /* light gray */
    color: #111111;              /* dark text */
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    line-height: 1.6;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.theory-box h3 {
    color: #0b3c5d;               /* dark blue header */
}

.theory-box a {
    color: #1f77b4;
    text-decoration: none;
}

.theory-box a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# --- DATA ---
@st.cache_data
def get_data():
    return eng.load_and_clean_data('US_SPYdata_2000_2024.csv')

ret_matrix, cap_matrix, min_date, max_date = get_data()

# --- DATA ---
@st.cache_data
def get_data():
    return eng.load_and_clean_data('US_SPYdata_2000_2024.csv')

ret_matrix, cap_matrix, min_date, max_date = get_data()


def about_page():
    st.title("About")

    st.header("Scott T. Switzer")
    st.subheader("Finance and Economics Student at Chapman University")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.link_button("💼 LinkedIn", "https://www.linkedin.com/in/scottswitzer-/")
    with col2:
        st.link_button("💻 GitHub", "https://github.com/Scott-Switzer")

    st.divider()

    st.header("📊 About This Project")

    st.info('''
*"A blindfolded monkey throwing darts at a newspaper's financial pages could select 
a portfolio that would do just as well as one carefully selected by experts."*  
— Burton Malkiel, *A Random Walk Down Wall Street* (1973)
    ''')

    st.markdown('''
After learning about the **Random Walk Hypothesis** and **Efficient Market Theory** in class, 
I wanted to put Malkiel's provocative claim to the test—at scale. Research has shown 
interesting results: one simulation of 100 "monkey" portfolios found that **98 out of 100 
beat the market**.

**Why I Built This:**
- To empirically test a foundational theory in finance using real market data
- To practice building end-to-end data science projects with financial applications
- To deploy a live experiment that continuously tracks random vs. strategic portfolio performance
- To bridge my coursework in econometrics and quantitative methods with hands-on application
    ''')

    with st.expander("🎓 What I Learned Building This Project"):
        st.markdown('''
- Full-stack deployment of a financial analytics application
- Working with financial APIs and real-time market data pipelines
- Statistical analysis of portfolio performance and benchmark comparison
- Cloud deployment and automation for continuous data collection
- The practical challenges of turning academic theory into a working experiment
        ''')

    st.divider()

    st.header("🎓 Education")

    st.markdown('''
**Chapman University** — Argyros College of Business & Economics  
*B.A. Economics & B.S. Business Administration (Finance) | Minor in Analytics*  
📅 Expected Graduation: **May 2027**
    ''')

    with st.expander("📚 Relevant Coursework"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
**Quantitative & Data:**
- Econometrics
- Introduction to Data Science
- Statistical Models in Business
- Foundations of Business Analytics
- Computer Science I
            ''')
        with col2:
            st.markdown('''
**Finance & Economics:**
- Investments
- Intermediate Financial Management
- Quantitative Methods in Finance
- Managerial Economics
- Intermediate Micro/Macro Theory
            ''')

    st.divider()

    st.header("💼 Experience")

    st.markdown('''
**Investment Research Analyst Intern**  
*4TH Exit Capital* — May 2024 – August 2024
    ''')

    st.divider()

    st.header("🛠️ Technical Skills")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('''
**Programming:**  
`Python` `NumPy` `pandas` `scikit-learn` `statsmodels` `SQL` `R`

**Financial Data:**  
`Bloomberg (BQL)` `WRDS/Compustat` `FRED` `FMP API`
        ''')

    with col2:
        st.markdown('''
**Statistical Methods:**  
`OLS/LASSO` `PCA` `Factor Models` `Classification`

**Tools & Platforms:**  
`Jupyter` `VS Code` `Excel` `Git` `Streamlit` `Cloud Deployment`
        ''')

    st.divider()

    st.header("🎯 What I'm Looking For")

    st.success("**Seeking Summer 2026 internships in quantitative trading**")

    st.markdown('''
I'm interested in roles at the intersection of finance, data science, and algorithmic 
decision-making—particularly in **financial engineering** and **algorithmic trading**.
    ''')

    st.divider()

    st.header("🏀 Beyond Finance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🃏 **Bridge** player")
    with col2:
        st.markdown("🏀 **Basketball** enthusiast")
    with col3:
        st.markdown("📈 **Quant strategies** explorer")

    st.divider()

    st.header("📬 Contact")

    st.markdown('''
📧 **Email:** scott.t.switzer@gmail.com  
💼 **LinkedIn:** [linkedin.com/in/scottswitzer-/](https://www.linkedin.com/in/scottswitzer-/)  
💻 **GitHub:** [github.com/Scott-Switzer](https://github.com/Scott-Switzer)
    ''')

    st.caption("Feel free to reach out if you'd like to discuss the project, collaborate, or chat about opportunities in quantitative finance!")



# --- SIDEBAR NAV ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["🚀 The Experiment", "📚 Theory & Methodology","ℹ️ About"])

# =========================================================
# PAGE 1: THE EXPERIMENT (SIMULATOR)
# =========================================================
if page == "🚀 The Experiment":
    st.markdown('<p class="big-header">🎯 The Dartboard Experiment</p>', unsafe_allow_html=True)
    st.markdown("### Can a blindfolded monkey beat the S&P 500?")
    
    # --- THEORY EXPANDER (NEW) ---
    with st.expander("📖 Why are we doing this? (The Theory)", expanded=False):
        st.markdown("""
        **1. The Efficient Market Hypothesis (EMH):**
        Proposed by **Eugene Fama** (Nobel Laureate), this theory suggests that asset prices reflect all available information. Therefore, it's impossible to consistently "beat the market" on a risk-adjusted basis because market price movements are random.
        
        **2. A Random Walk Down Wall Street:**
        In 1973, **Burton Malkiel** famously claimed:
        > "A blindfolded monkey throwing darts at a newspaper's financial pages could select a portfolio that would do just as well as one carefully selected by experts."
        
        **The Goal:** We are testing Malkiel's claim mathematically. We will throw thousands of "darts" (random portfolios) and compare them against the **S&P 500 (SPY)** and **Russell 2000 (IWM)**.
        """)

    if ret_matrix.empty:
        st.error("Data not loaded.")
        st.stop()

    # --- CONTROLS ---
    st.sidebar.header("🧪 Experiment Settings")

    date_mode = st.sidebar.radio("Time Period", ["Preset Eras", "Custom Range"])

    if date_mode == "Preset Eras":
        regime = st.sidebar.selectbox("Market Era", [
            "Full History (2000-2024)", 
            "Dotcom Bubble (2000-2002)", 
            "2008 GFC (2007-2009)", 
            "Bull Market (2010-2019)",
            "COVID Crash & Recovery (2020-2021)",
            "Post-Covid (2020-2024)"
        ])
        
        d_map = {
            "Full History (2000-2024)": (min_date, max_date),
            "Dotcom Bubble (2000-2002)": (datetime.datetime(2000,1,1), datetime.datetime(2002,12,31)),
            "2008 GFC (2007-2009)": (datetime.datetime(2007,10,1), datetime.datetime(2009,3,31)),
            "Bull Market (2010-2019)": (datetime.datetime(2010,1,1), datetime.datetime(2019,12,31)),
            "COVID Crash & Recovery (2020-2021)": (datetime.datetime(2020,1,1), datetime.datetime(2021,12,31)),
            "Post-Covid (2020-2024)": (datetime.datetime(2020,3,1), max_date)
        }
        s, e = d_map[regime]
    else:
        regime = "Custom Range"
        col1, col2 = st.sidebar.columns(2)
        s = col1.date_input("Start", min_date, min_value=min_date, max_value=max_date)
        e = col2.date_input("End", max_date, min_value=min_date, max_value=max_date)
        s = datetime.datetime.combine(s, datetime.time())
        e = datetime.datetime.combine(e, datetime.time())
    

    n_stocks = st.sidebar.slider("Darts per Portfolio", cfg.MIN_STOCKS, cfg.MAX_STOCKS, cfg.DEFAULT_N_STOCKS)
    n_sims = st.sidebar.slider("Simulations", cfg.MIN_SIMS, cfg.MAX_SIMS, cfg.DEFAULT_N_SIMS)

    # --- EXECUTION ---
    current_params = (regime, n_stocks, n_sims)

    if st.button("▶️ Run the Experiment", type="primary"):
        sub_ret = ret_matrix.loc[str(s):str(e)]
        sub_cap = cap_matrix.loc[str(s):str(e)]
        
        if len(sub_ret) < 12: st.error("Period too short."); st.stop()
        
        # 1. Context
        with st.spinner("Fetching Benchmarks (SPY & IWM)..."):
            rf = eng.get_dynamic_rf(s, e)
            spy_sh, spy_r = eng.get_benchmark_stats("SPY", s, e, rf)
            iwm_sh, iwm_r = eng.get_benchmark_stats("IWM", s, e, rf)
            
        st.caption(f"Risk-Free Rate: {rf:.2%} (Avg 13-Wk T-Bill)")
        
        # 2. Run Simulation with progress bar
        import time

        start_time = time.time()
        pb = st.progress(0)
        status_text = st.empty()

        def progress_with_eta(pct):
            pb.progress(pct)
            if pct > 0.1:
                elapsed = time.time() - start_time
                eta = (elapsed / pct) * (1 - pct)
                status_text.text(f"Running... {pct*100:.0f}% complete | ETA: {eta:.0f}s remaining")

        res_ew, res_cw, sample_ports = eng.run_monte_carlo(
            sub_ret, sub_cap, n_sims, n_stocks, rf, progress_with_eta
        )
        status_text.text("✅ Complete!")

        # Calculate win rate BEFORE using it
        win_vs_spy = np.mean(res_ew > spy_sh) * 100

        # 3. Metrics
        st.divider()

        # Row 1: Main Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🎯 Dartboard (EW)", f"{np.mean(res_ew):.2f}", f"Win Rate: {win_vs_spy:.0f}%")
        col2.metric("📊 Index Proxy (CW)", f"{np.mean(res_cw):.2f}")
        col3.metric("🏆 S&P 500", f"{spy_sh:.2f}", delta_color="off")
        col4.metric("📈 Russell 2000", f"{iwm_sh:.2f}", delta_color="off")

        # Row 2: Additional Stats
        st.markdown("##### Detailed Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("EW Volatility", f"{np.std(res_ew):.2f}")
        col2.metric("CW Volatility", f"{np.std(res_cw):.2f}")
        col3.metric("EW vs CW Win %", f"{np.mean(res_ew > res_cw)*100:.0f}%")
        col4.metric("Best EW Sharpe", f"{np.max(res_ew):.2f}")
        
        # After running simulation:
        ew_stats = eng.compute_statistics(res_ew)
        cw_stats = eng.compute_statistics(res_cw)

        col1.metric(
            "Dartboard (Equal Wgt)", 
            f"{ew_stats['mean']:.2f}",
            help=f"95% CI: [{ew_stats['ci_95_low']:.2f}, {ew_stats['ci_95_high']:.2f}]"
        )

        # Add after metrics:
        st.markdown("##### Side-by-Side Comparison")

        comparison_df = pd.DataFrame({
            'Metric': ['Mean Sharpe', 'Median Sharpe', 'Std Dev', 'Min', 'Max', '5th Percentile', '95th Percentile'],
            'Dartboard (EW)': [
                f"{np.mean(res_ew):.3f}",
                f"{np.median(res_ew):.3f}",
                f"{np.std(res_ew):.3f}",
                f"{np.min(res_ew):.3f}",
                f"{np.max(res_ew):.3f}",
                f"{np.percentile(res_ew, 5):.3f}",
                f"{np.percentile(res_ew, 95):.3f}"
            ],
            'Index Proxy (CW)': [
                f"{np.mean(res_cw):.3f}",
                f"{np.median(res_cw):.3f}",
                f"{np.std(res_cw):.3f}",
                f"{np.min(res_cw):.3f}",
                f"{np.max(res_cw):.3f}",
                f"{np.percentile(res_cw, 5):.3f}",
                f"{np.percentile(res_cw, 95):.3f}"
            ],
            'SPY': [f"{spy_sh:.3f}", '-', '-', '-', '-', '-', '-'],
            'IWM': [f"{iwm_sh:.3f}", '-', '-', '-', '-', '-', '-']
        })

        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Add after metrics:
        st.subheader("📈 Statistical Significance")

        sig_test = eng.test_ew_vs_cw(res_ew, res_cw)
        if sig_test['significant']:
            st.success(f"✅ EW vs CW difference is **statistically significant** (p = {sig_test['p_value']:.4f}, Cohen's d = {sig_test['cohens_d']:.2f})")
        else:
            st.info(f"ℹ️ EW vs CW difference is **not statistically significant** (p = {sig_test['p_value']:.4f})")

        spy_test = eng.test_vs_benchmark(res_ew, spy_sh)
        st.markdown(f"**Dartboard vs SPY:** {'Significantly different' if spy_test['significant'] else 'Not significantly different'} (p = {spy_test['p_value']:.4f})")

        # 4. Visualization

        fig = go.Figure()

        # Add histograms
        fig.add_trace(go.Histogram(
            x=res_ew,
            name='Dartboard (Equal Wgt)',
            opacity=0.6,
            marker_color='#1f77b4',
            histnorm='probability density',
            nbinsx=40
        ))

        fig.add_trace(go.Histogram(
            x=res_cw,
            name='Index Proxy (Cap Wgt)',
            opacity=0.6,
            marker_color='#ff7f0e',
            histnorm='probability density',
            nbinsx=40
        ))

        # Add benchmark lines
        fig.add_vline(x=spy_sh, line_color="green", line_width=3,
                    annotation_text=f"SPY: {spy_sh:.2f}",
                    annotation_position="top")
        fig.add_vline(x=iwm_sh, line_color="purple", line_width=3, line_dash="dash",
                    annotation_text=f"IWM: {iwm_sh:.2f}",
                    annotation_position="bottom")

        # Add mean lines
        fig.add_vline(x=np.mean(res_ew), line_color="#1f77b4", line_width=2, line_dash="dot",
                    annotation_text=f"EW Mean: {np.mean(res_ew):.2f}")

        fig.update_layout(
            title=f"<b>Performance Distribution vs Benchmarks</b><br><sub>{regime}</sub>",
            xaxis_title="Sharpe Ratio (Risk-Adjusted Return)",
            yaxis_title="Density",
            barmode='overlay',
            template='plotly_white',
            height=500,
            hovermode='x unified',
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("📥 Export Results")

        col1, col2 = st.columns(2)

        # Download simulation data
        results_df = pd.DataFrame({
            'Simulation': range(1, len(res_ew) + 1),
            'EqualWeight_Sharpe': res_ew,
            'CapWeight_Sharpe': res_cw
        })

        with col1:
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Raw Data (CSV)",
                data=csv,
                file_name=f"dartboard_results_{regime.replace(' ', '_')}.csv",
                mime="text/csv"
            )

        # Download summary statistics
        with col2:
            summary = f"""
        Dartboard Experiment Results
        ============================
        Regime: {regime}
        Simulations: {n_sims}
        Stocks per Portfolio: {n_stocks}
        Risk-Free Rate: {rf:.2%}

        Equal-Weight (Dartboard):
        Mean Sharpe: {np.mean(res_ew):.4f}
        Std Dev: {np.std(res_ew):.4f}
        95% CI: [{ew_stats['ci_95_low']:.4f}, {ew_stats['ci_95_high']:.4f}]

        Cap-Weight (Index Proxy):
        Mean Sharpe: {np.mean(res_cw):.4f}
        Std Dev: {np.std(res_cw):.4f}

        Benchmarks:
        SPY Sharpe: {spy_sh:.4f}
        IWM Sharpe: {iwm_sh:.4f}

        Win Rate vs SPY: {np.mean(res_ew > spy_sh) * 100:.1f}%
        """
            st.download_button(
                label="📝 Download Summary Report",
                data=summary,
                file_name=f"dartboard_summary_{regime.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        
        # Get HTML and dynamic height
        html_output, component_height = describe_simulation_distribution(
            res_ew,
            res_cw,
            spy_sh=spy_sh,
            iwm_sh=iwm_sh,
            regime_label=regime
        )

        components.html(
            html_output,
            height=component_height,
            scrolling=False  # Changed to False - no more scrolling needed
        )


        # 5. TRANSPARENCY SECTION (New)
        st.markdown("---")
        st.subheader("🔍 Inspect the Darts")
        st.markdown("To prove these are truly random, here are the stocks picked in the first 3 simulations:")
        
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                st.markdown(f"**Portfolio #{i+1}**")
                # Show top 10 tickers just to save space
                st.text(", ".join(sample_ports[i][:10]) + "...")
                with st.expander("See full list"):
                    st.write(sample_ports[i])

# =========================================================
# PAGE 2: THEORY & METHODOLOGY
# =========================================================
elif page == "📚 Theory & Methodology":
    st.markdown('<p class="big-header">📚 The Academic Framework</p>', unsafe_allow_html=True)

    # =========================================================
    # 1) EMH
    # =========================================================
    st.markdown("""
    <div class="theory-box">
    <h3>1. The Efficient Market Hypothesis (EMH)</h3>
    <p>Popularized by <b>Eugene Fama</b> in his 1970 paper <i>"Efficient Capital Markets: A Review of Theory and Empirical Work."</i></p>

    <p><b>The core claim:</b> Prices rapidly incorporate available information. If everyone can see the same public information, then any "obvious" mispricing gets competed away.</p>

    <p><b>Three forms of efficiency:</b></p>
    <ul>
        <li><b>Weak-form:</b> Prices reflect all <i>past</i> price/volume data → technical patterns should not reliably predict returns.</li>
        <li><b>Semi-strong:</b> Prices reflect all <i>public</i> information → public news and fundamentals are quickly impounded.</li>
        <li><b>Strong-form:</b> Prices reflect <i>all</i> information, including private → implies even insiders can't win (not supported in reality).</li>
    </ul>

    <p><b>What EMH does NOT say:</b> It does not claim prices are "always correct" or that anomalies never appear. It claims that <b>systematic, scalable outperformance is hard</b> once you account for risk, fees, and trading costs.</p>

    <br>
    <a href="https://www.investopedia.com/terms/e/efficientmarkethypothesis.asp" target="_blank">👉 Read more on Investopedia</a>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================
    # 2) RANDOM WALK
    # =========================================================
    st.markdown("""
    <div class="theory-box">
    <h3>2. The Random Walk Theory</h3>
    <p>Popularized by <b>Burton Malkiel</b> in his 1973 classic <i>"A Random Walk Down Wall Street."</i></p>

    <p><b>Intuition:</b> If markets incorporate information quickly, then tomorrow's price change is driven mainly by <b>new information</b>—and truly new information is unpredictable.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**The Random Walk Model (with drift):**")
    st.latex(r"P_{t+1} = P_t + \mu + \varepsilon_{t+1}")
    
    st.markdown("""
    Where:
    - $P_t$ = Price at time $t$
    - $\mu$ = Drift term (expected return / risk premium)
    - $\\varepsilon_{t+1}$ = Random shock with $E[\\varepsilon] = 0$ (unpredictable noise)
    """)
    
    st.markdown("""
    <div class="theory-box">
    <p><b>The "Blindfolded Monkey" Experiment:</b> Malkiel's thought experiment is not about intelligence—it's about <b>information symmetry</b>. 
    If most public information is already in prices, then many "smart" selections become indistinguishable from randomness <b>before costs</b>, 
    and can be worse <b>after costs</b>.</p>

    <p><b>Important nuance:</b> Random walk behavior is most closely tied to <b>weak-form efficiency</b>. 
    It does not require markets to be perfectly efficient at every moment—only that reliably extracting direction from past prices is very difficult.</p>

    <br>
    <a href="https://en.wikipedia.org/wiki/A_Random_Walk_Down_Wall_Street" target="_blank">👉 Read more about the book</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # 3) MONTE CARLO METHODOLOGY
    # =========================================================
    st.header("3. Monte Carlo Simulation Methodology")
    
    st.markdown("""
    <div class="theory-box">
    <h3>What is Monte Carlo Simulation?</h3>
    <p><b>Monte Carlo simulation</b> is a computational technique that uses <b>repeated random sampling</b> to estimate the distribution of possible outcomes. 
    Named after the famous casino in Monaco, it's used when analytical solutions are difficult or impossible.</p>
    
    <p><b>In this experiment:</b> Instead of calculating every possible portfolio combination (computationally infeasible), 
    we randomly sample thousands of portfolios to approximate what a "typical" random selection would produce.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("3.1 The Random Selection Process")
    
    st.markdown("**Step 1: Define the Universe**")
    st.markdown("""
    We start with all stocks that meet our liquidity filter (market cap > $10M) for the selected time period.
    """)
    st.latex(r"\text{Universe} = \{s_1, s_2, ..., s_N\} \text{ where } N \approx 3000-5000 \text{ stocks}")
    
    st.markdown("**Step 2: Random Sampling (The 'Dart Throw')**")
    st.markdown("""
    For each simulation, we randomly select $k$ stocks from the universe **without replacement** (each stock can only be picked once per portfolio).
    """)
    st.latex(r"\text{Portfolio}_i = \text{RandomSample}(\text{Universe}, k) \text{ where } k = \text{number of darts}")
    
    st.markdown("""
    This is equivalent to:
    """)
    st.latex(r"P(\text{stock } j \text{ selected}) = \frac{k}{N} \text{ for each stock}")
    
    st.markdown("**Step 3: Apply Weighting Scheme**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Equal-Weight (Dartboard):**")
        st.latex(r"w_i = \frac{1}{k}")
        st.markdown("Each stock gets the same weight. If you pick 30 stocks, each gets 3.33% of the portfolio.")
    
    with col2:
        st.markdown("**Cap-Weight (Index Proxy):**")
        st.latex(r"w_i = \frac{\text{MarketCap}_i}{\sum_{j=1}^{k} \text{MarketCap}_j}")
        st.markdown("Larger companies get proportionally more weight, mimicking index construction.")
    
    st.markdown("**Step 4: Calculate Portfolio Returns**")
    st.markdown("Monthly portfolio return is the weighted sum of individual stock returns:")
    st.latex(r"R_{portfolio,t} = \sum_{i=1}^{k} w_i \cdot R_{i,t}")
    
    st.markdown("**Step 5: Repeat Many Times**")
    st.latex(r"\text{For } n = 1 \text{ to } N_{simulations}: \text{ repeat steps 2-4}")
    st.markdown("""
    By running hundreds or thousands of simulations, we build a **distribution** of possible outcomes, 
    not just a single point estimate.
    """)

    st.divider()
    
    # =========================================================
    # 4) SHARPE RATIO
    # =========================================================
    st.subheader("3.2 Measuring Performance: The Sharpe Ratio")
    
    st.markdown("""
    <div class="theory-box">
    <p>Raw returns are misleading because they ignore <b>risk</b>. A 20% return with wild swings is worse than 15% with steady growth.
    The <b>Sharpe Ratio</b> (developed by Nobel laureate William Sharpe) measures <b>risk-adjusted return</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**The Sharpe Ratio Formula:**")
    st.latex(r"\text{Sharpe Ratio} = \frac{R_p - R_f}{\sigma_p}")
    
    st.markdown("""
    Where:
    - $R_p$ = Annualized portfolio return
    - $R_f$ = Risk-free rate (we use the 13-week T-Bill yield)
    - $\\sigma_p$ = Annualized portfolio volatility (standard deviation of returns)
    """)
    
    st.markdown("**How We Calculate It:**")
    
    st.markdown("*Annualized Return (Geometric):*")
    st.latex(r"R_{annual} = \left( \prod_{t=1}^{T} (1 + R_t) \right)^{\frac{12}{T}} - 1")
    
    st.markdown("*Annualized Volatility:*")
    st.latex(r"\sigma_{annual} = \sigma_{monthly} \times \sqrt{12}")
    
    st.markdown("""
    | Sharpe Ratio | Interpretation |
    |--------------|----------------|
    | < 0 | Losing money relative to risk-free rate |
    | 0 - 0.5 | Poor risk-adjusted returns |
    | 0.5 - 1.0 | Acceptable |
    | 1.0 - 2.0 | Good |
    | > 2.0 | Excellent (rare for long periods) |
    """)

    st.divider()

    # =========================================================
    # 5) DATA METHODOLOGY
    # =========================================================
    st.header("4. Data Source & Methodology")
    
    st.markdown("""
    <div class="theory-box">
    <h3>✅ Data Integrity: Survivorship Bias-Free</h3>

    <p>This experiment uses <b>CRSP data via WRDS</b> (Wharton Research Data Services) — 
    the gold standard for academic finance research.</p>

    <p><b>Dataset Statistics:</b></p>
    <ul>
        <li><b>4,936 delisting events</b> captured (bankruptcies, mergers, acquisitions)</li>
        <li><b>4,826 unique delisted tickers</b> included in the simulation universe</li>
        <li><b>Coverage:</b> January 2000 – December 2024</li>
    </ul>

    <p><b>Why this matters:</b> Studies using survivorship-biased data (like Yahoo Finance) can 
    overstate returns by <b>1-2% annually</b>. Our results reflect what a real investor 
    would have experienced, including the pain of holding stocks that went to zero.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Delisting Return Adjustment:**")
    st.markdown("When a stock is delisted (bankruptcy, merger, etc.), CRSP provides a delisting return. We incorporate it:")
    st.latex(r"R_{total} = (1 + R_{regular}) \times (1 + R_{delisting}) - 1")
    
    st.markdown("**Liquidity Filter:**")
    st.latex(r"\text{Include stock if: MarketCap} > \$10\text{M}")
    st.markdown("This removes penny stocks and illiquid securities that would be difficult to trade in practice.")

    st.divider()

    # =========================================================
    # 6) WEIGHTING SCHEMES DEEP DIVE
    # =========================================================
    st.header("5. Weighting Schemes: Why They Matter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="theory-box">
        <h3>Equal-Weight Portfolio</h3>
        <p><b>Construction:</b> Every stock gets identical weight</p>
        <p><b>Characteristics:</b></p>
        <ul>
            <li>Higher exposure to <b>small-cap stocks</b></li>
            <li>Built-in <b>contrarian rebalancing</b> (sell winners, buy losers)</li>
            <li>Requires frequent rebalancing → higher turnover</li>
            <li>Historically shows a <b>small-cap premium</b></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="theory-box">
        <h3>Cap-Weight Portfolio</h3>
        <p><b>Construction:</b> Weight proportional to market cap</p>
        <p><b>Characteristics:</b></p>
        <ul>
            <li>Dominated by <b>mega-cap stocks</b></li>
            <li>Built-in <b>momentum tilt</b> (winners grow in weight)</li>
            <li>Low turnover, tax efficient</li>
            <li>How most major indices (S&P 500) are built</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="theory-box">
    <h3>⚠️ Important Interpretation Note</h3>
    <p>If equal-weight portfolios outperform cap-weight in our simulation, this is <b>NOT evidence of market inefficiency</b>. 
    It likely reflects:</p>
    <ul>
        <li><b>Size factor exposure</b> — small stocks have historically earned a premium (Fama-French)</li>
        <li><b>Rebalancing bonus</b> — systematically buying low and selling high</li>
        <li><b>Different risk profile</b> — equal-weight portfolios are more volatile</li>
    </ul>
    <p>A fair comparison requires adjusting for these factor exposures.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # 7) STATISTICAL INTERPRETATION
    # =========================================================
    st.header("6. Interpreting the Results")
    
    st.markdown("""
    <div class="theory-box">
    <h3>Reading the Histogram</h3>
    <p>The output histogram shows the <b>distribution of Sharpe Ratios</b> across all simulations.</p>
    <ul>
        <li><b>Center (mean/median):</b> The "typical" outcome of a random portfolio</li>
        <li><b>Spread (width):</b> How much outcomes vary based on stock selection</li>
        <li><b>Benchmark lines:</b> Where SPY and IWM fall in the distribution</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Key Questions the Simulation Answers:**")
    st.markdown("""
    | Question | How to Read It |
    |----------|----------------|
    | "Can random selection match the market?" | If benchmark is near the **middle** of distribution → Yes, many random portfolios are comparable |
    | "Is beating the market hard?" | If benchmark is in the **right tail** → Yes, few random portfolios beat it |
    | "Does weighting matter?" | Compare the **two histograms** — if they're shifted, weighting has systematic effects |
    """)

    st.markdown("**Win Rate Calculation:**")
    st.latex(r"\text{Win Rate} = \frac{\sum_{i=1}^{N} \mathbf{1}(Sharpe_i > Sharpe_{SPY})}{N} \times 100\%")
    st.markdown("Where $\mathbf{1}(\\cdot)$ is an indicator function that equals 1 when the condition is true, 0 otherwise.")

    st.divider()

    # =========================================================
    # 8) LIMITATIONS
    # =========================================================
    st.markdown("""
    <div class="theory-box">
    <h3>7. Limitations & Caveats</h3>
    <ul>
        <li><b>No transaction costs:</b> Real rebalancing incurs fees, bid-ask spreads, and market impact</li>
        <li><b>No taxes:</b> Capital gains taxes would reduce returns, especially for equal-weight (high turnover)</li>
        <li><b>Perfect execution assumed:</b> We assume you can trade at exactly the historical prices</li>
        <li><b>Hindsight universe:</b> We know which stocks existed; in real-time, you wouldn't know future listings</li>
        <li><b>No capacity constraints:</b> Small stocks may not have enough liquidity for large positions</li>
    </ul>
    <p><b>Bottom line:</b> These results represent a <b>theoretical upper bound</b>. Real-world implementation would likely show lower returns.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # 9) SOURCE CODE
    # =========================================================
    # Replace the source code section with:
    st.header("8. The Source Code")
    st.markdown("We believe in **open, reproducible research**.")

    with st.expander("📄 Click to view engine.py source code"):
        try:
            with open("engine.py", "r") as f:
                st.code(f.read(), language="python")
        except FileNotFoundError:
            st.error("engine.py not found")
        
    # =========================================================
    # 10) REFERENCES
    # =========================================================
    st.header("9. Academic References")
    st.markdown("""
    <div class="theory-box">
    <h3>📚 Key Papers & Books</h3>
    <ul>
        <li>Fama, E. (1970). <i>"Efficient Capital Markets: A Review of Theory and Empirical Work."</i> Journal of Finance.</li>
        <li>Malkiel, B. (1973). <i>"A Random Walk Down Wall Street."</i> W.W. Norton & Company.</li>
        <li>Sharpe, W. (1966). <i>"Mutual Fund Performance."</i> Journal of Business.</li>
        <li>Fama, E. & French, K. (1993). <i>"Common Risk Factors in the Returns on Stocks and Bonds."</i> Journal of Financial Economics.</li>
        <li>Elton, E., Gruber, M., & Blake, C. (1996). <i>"Survivorship Bias and Mutual Fund Performance."</i> Review of Financial Studies.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8em;">
        <p>Built with ❤️ using Streamlit | Data: CRSP via WRDS | 
        <a href="https://github.com/Scott-Switzer/Random-Portfolio" target="_blank">GitHub</a></p>
        <p>⚠️ This is an educational tool. Not financial advice. Past performance ≠ future results.</p>
    </div>
    """, unsafe_allow_html=True)

elif page == "ℹ️ About":
    about_page()