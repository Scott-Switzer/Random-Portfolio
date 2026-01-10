import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import engine as eng
import streamlit.components.v1 as components

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
        """

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

    # Paired comparison: how often EW > CW (works because your engine returns both per-sim)
    n_pair = min(len(res_ew), len(res_cw))
    pair_win = float(np.mean(res_ew[:n_pair] > res_cw[:n_pair]) * 100.0)

    # Benchmark positioning + win rates
    bench_lines = []
    def bench_block(name, b):
        if b is None or not np.isfinite(b):
            return None
        ew_pct = float(np.mean(res_ew <= b) * 100.0)  # percentile of benchmark in EW dist
        cw_pct = float(np.mean(res_cw <= b) * 100.0)
        ew_win = float(np.mean(res_ew >= b) * 100.0)
        cw_win = float(np.mean(res_cw >= b) * 100.0)
        return (name, b, ew_pct, cw_pct, ew_win, cw_win)

    for name, b in [("S&P 500 (SPY)", spy_sh), ("Russell 2000 (IWM)", iwm_sh)]:
        blk = bench_block(name, b)
        if blk:
            bench_lines.append(blk)

    # Build dynamic narrative
    header = f" ({regime_label})" if regime_label else ""

    css = """
    <style>
    .theory-box {
        background-color: #f8f9fa;
        color: #111111;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        line-height: 1.6;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    }
    .theory-box h3 { color: #0b3c5d; margin-top: 0; }
    .theory-box ul { margin: 0.5rem 0 0 1.2rem; }
    </style>
    """

    html = css + f"""
    <div class="theory-box">
      <h3>Interpreting the Simulation Results{header}</h3>

      <p><b>What this chart is:</b> Each histogram is the distribution of Sharpe ratios from repeated portfolio simulations over the selected period.
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

      <p><b>Equal-weight vs cap-weight (in this run):</b> the equal-weight portfolio beats the cap-weight proxy in
      <b>{pair_win:.0f}%</b> of paired simulations. This is not “skill” — it reflects systematic differences in exposure (often size + rebalancing effects).</p>
    </div>
    """
    

    if bench_lines:
        html += """
        <p><b>Benchmark positioning (relative to the simulated distributions):</b></p>
        <ul>
        """
        for (name, b, ew_pct, cw_pct, ew_win, cw_win) in bench_lines:
            html += f"""
            <li><b>{name} Sharpe = {b:.2f}</b>:
                sits in the <b>{_tail_label(ew_pct)}</b> of the Dartboard distribution (≈ {ew_pct:.0f}th percentile; <b>{ew_win:.0f}%</b> of dartboards beat it),
                and the <b>{_tail_label(cw_pct)}</b> of the Index Proxy distribution (≈ {cw_pct:.0f}th percentile; <b>{cw_win:.0f}%</b> beat it).</li>
        """
        html += "</ul>"

    html += """
      <p><b>What this simulation actually demonstrates:</b> Over the chosen history window, “randomly diversified” portfolios produce a broad spread of risk-adjusted outcomes.
      If the benchmark lines sit in the right tail, it means matching that benchmark Sharpe is difficult; if they sit near the middle, it means many random draws are comparable on a risk-adjusted basis.</p>
    </div>
    """

    return f"""
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    html, body {{
    margin: 0;
    padding: 0;
    }}
    </style>
    </head>
    <body>
    {html}
    </body>
    </html>
    """





st.set_page_config(page_title="Quant Dartboard Lab", page_icon="🎯", layout="wide")

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

# --- SIDEBAR NAV ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["🚀 The Experiment", "📚 Theory & Methodology"])

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
    regime = st.sidebar.selectbox("Market Era", ["Full History (2000-2024)", "Dotcom Bubble", "2008 GFC", "Post-Covid"])
    
    d_map = {
        "Full History (2000-2024)": (min_date, max_date),
        "Dotcom Bubble": (datetime.datetime(2000,1,1), datetime.datetime(2002,12,31)),
        "2008 GFC": (datetime.datetime(2007,10,1), datetime.datetime(2009,3,31)),
        "Post-Covid": (datetime.datetime(2020,3,1), max_date)
    }
    s, e = d_map[regime]
    
    n_stocks = st.sidebar.slider("Darts per Portfolio", 10, 100, 30)
    n_sims = st.sidebar.slider("Simulations (The Sample Size)", 100, 2000, 500)
    
    # --- EXECUTION ---
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
        
        # 2. Simulation
        pb = st.progress(0)
        # Note: We now unpack 3 values (Added sample_ports)
        res_ew, res_cw, sample_ports = eng.run_monte_carlo(sub_ret, sub_cap, n_sims, n_stocks, rf, pb.progress)
        
        # 3. Metrics
        st.divider()
        win_vs_spy = np.mean(res_ew > spy_sh) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Dartboard (Equal Wgt)", f"{np.mean(res_ew):.2f}", f"{win_vs_spy:.0f}% Win Rate")
        col2.metric("Index Proxy (Cap Wgt)", f"{np.mean(res_cw):.2f}")
        col3.metric("S&P 500 (SPY)", f"{spy_sh:.2f}", delta_color="off")
        col4.metric("Small Cap (IWM)", f"{iwm_sh:.2f}", delta_color="off")
        
        # 4. Visualization
        fig, ax = plt.subplots(figsize=(10,6))
        ax.hist(res_ew, bins=40, alpha=0.6, density=True, label='Dartboard (Equal Wgt)', color='#1f77b4')
        ax.hist(res_cw, bins=40, alpha=0.6, density=True, label='Index Proxy (Cap Wgt)', color='#ff7f0e')
        ax.axvline(spy_sh, color='green', linewidth=3, label=f'S&P 500: {spy_sh:.2f}')
        ax.axvline(iwm_sh, color='purple', linewidth=3, linestyle='-.', label=f'Russell 2000: {iwm_sh:.2f}')
        ax.legend()
        ax.set_title(f"Performance Distribution vs Benchmarks ({regime})")
        ax.set_xlabel("Sharpe Ratio (Risk-Adjusted Return)")
        st.pyplot(fig)
        
        components.html(
            describe_simulation_distribution(
                res_ew,
                res_cw,
                spy_sh=spy_sh,
                iwm_sh=iwm_sh,
                regime_label=regime
            ),
            height=520,       # give it room
            scrolling=True    # critical: don't silently clip
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

    <p><b>The core claim:</b> Prices rapidly incorporate available information. If everyone can see the same public information, then any “obvious” mispricing gets competed away.</p>

    <p><b>Three forms of efficiency:</b></p>
    <ul>
        <li><b>Weak-form:</b> Prices reflect all <i>past</i> price/volume data → technical patterns should not reliably predict returns.</li>
        <li><b>Semi-strong:</b> Prices reflect all <i>public</i> information → public news and fundamentals are quickly impounded.</li>
        <li><b>Strong-form:</b> Prices reflect <i>all</i> information, including private → implies even insiders can’t win (not supported in reality).</li>
    </ul>

    <p><b>What EMH does NOT say:</b> It does not claim prices are “always correct” or that anomalies never appear. It claims that <b>systematic, scalable outperformance is hard</b> once you account for risk, fees, and trading costs.</p>

    <br>
    <a href="https://www.investopedia.com/terms/e/efficientmarkethypothesis.asp" target="_blank">👉 Read more on Investopedia</a>
    </div>
    <br>
    """, unsafe_allow_html=True)

    # =========================================================
    # 2) RANDOM WALK
    # =========================================================
    st.markdown("""
    <div class="theory-box">
    <h3>2. The Random Walk Theory</h3>
    <p>Popularized by <b>Burton Malkiel</b> in his 1973 classic <i>"A Random Walk Down Wall Street."</i></p>

    <p><b>Intuition:</b> If markets incorporate information quickly, then tomorrow’s price change is driven mainly by <b>new information</b>—and truly new information is unpredictable.</p>

    <p><b>Canonical model (random walk with drift):</b></p>
    <p style="margin-left: 15px;">
        \\( P_{t+1} = P_t + \\mu + \\varepsilon_{t+1} \\)
        <br>
        where \\(\\mu\\) is the long-run expected return (risk premium) and \\(\\varepsilon\\) is an unpredictable shock with \\(E[\\varepsilon]=0\\) and minimal serial dependence.
    </p>

    <p><b>The experiment:</b> Malkiel’s “blindfolded monkey throwing darts” is not about intelligence—it’s about <b>information symmetry</b>. If most public information is already in prices, then many “smart” selections become indistinguishable from randomness <b>before costs</b>, and can be worse <b>after costs</b>.</p>

    <p><b>Important nuance:</b> Random walk behavior is most closely tied to <b>weak-form efficiency</b>. It does not require markets to be perfectly efficient at every moment—only that reliably extracting direction from past prices is very difficult.</p>

    <br>
    <a href="https://en.wikipedia.org/wiki/A_Random_Walk_Down_Wall_Street" target="_blank">👉 Read more about the book</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # =========================================================
    # 3) METHODOLOGY
    # =========================================================
    st.header("3. Mathematical Methodology")
    st.markdown(r"""
    **A. Data Source:** CRSP-style monthly stock data (via WRDS export).  
    **B. Return Definition:** Uses `total_ret` (includes delisting return when available), aligned into a monthly return matrix.  
    **C. Universe Filter (Liquidity / Microcap Filter):** `mkt_cap > 10,000` in the dataset’s units (CRSP market cap is commonly reported in **$ thousands**, so this is approximately a **$10M** cutoff).  
    **D. Simulation Setup:** Each simulation draws **N stocks** from the eligible universe for the chosen time window, then computes portfolio returns and performance statistics.  

    **E. Weighting Schemes (What This App Tests):**
    * **Equal-Weighted (The Dartboard):**  \(\; w_i = 1/N \;\)  
      - Mechanically increases exposure to smaller firms  
      - Tends to rebalance away from recent winners (a contrarian tilt)  
      - Often shows different risk/return behavior than cap-weighting  
    * **Cap-Weighted (The Index):**  \(\; w_i = \frac{Cap_i}{\sum_j Cap_j} \;\)  
      - Mimics major index construction  
      - Concentrates in the largest constituents  
      - Naturally becomes momentum-biased as winners grow in weight  

    **F. How To Interpret Results (Tell-it-like-it-is):**
    * If a large fraction of random portfolios match or beat the benchmark over long horizons, it supports the idea that **security selection is difficult** without a real edge.  
    * Outperformance by equal-weighting is not automatically “inefficiency.” It can reflect **systematic factor exposure** (size, rebalancing effects) and different risk.  
    * Gross outperformance is not the same as net outperformance once you include **turnover, fees, and slippage** (not modeled here unless explicitly added).
    """)

    # Optional: add a short “limitations” box (keeps you honest and looks academic)
    st.markdown("""
    <div class="theory-box">
    <h3>4. Practical Caveats (Why Results Can Differ From Real Life)</h3>
    <ul>
        <li><b>Trading frictions:</b> turnover + bid/ask spreads can materially reduce equal-weight results.</li>
        <li><b>Constraints:</b> real portfolios face capacity limits, borrow constraints, and risk controls.</li>
        <li><b>Benchmark mismatch:</b> your benchmark choice (SPY / IWM) changes the interpretation.</li>
        <li><b>Distribution reality:</b> equity returns are skewed—few stocks drive most gains—so diversification matters more than “picking.”</li>
    </ul>
    </div>
    <br>
    """, unsafe_allow_html=True)

    st.subheader("5. The Source Code")
    st.markdown("We believe in open research. Below is the exact python code (`engine.py`) used to run these simulations.")
    st.code(open("engine.py").read())
