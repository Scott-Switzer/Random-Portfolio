"""Independent verification of Codex's Dartboard upgrade (Pass 1: vectorized
engine + Fama-French 3-factor alpha). Run with the project venv:
    source .venv/bin/activate && python verify_codex.py
"""
import time
import numpy as np
import engine as eng

print("="*60)
print("VERIFY 1: engine imports")
print("="*60)
print("ok")

print("\n" + "="*60)
print("VERIFY 2: load data (CRSP, survivorship-bias-free)")
print("="*60)
ret_matrix, cap_matrix, min_date, max_date = eng.load_and_clean_data("US_SPYdata_2000_2024.csv")
print(f"tickers={ret_matrix.shape[1]}, months={ret_matrix.shape[0]}, "
      f"range={min_date.date()}..{max_date.date()}")

print("\n" + "="*60)
print("VERIFY 3: vectorized Monte Carlo speed (5000 sims, 30 stocks)")
print("="*60)
rf = 0.03
t0 = time.perf_counter()
res_ew, res_cw, portfolios, ew_series, cw_series = eng.run_monte_carlo(
    ret_matrix, cap_matrix, 5000, 30, rf, None)
dt = time.perf_counter() - t0
print(f"elapsed={dt:.3f}s  | EW Sharpe mean={res_ew.mean():.3f} median={np.median(res_ew):.3f}")
print(f"CW Sharpe mean={res_cw.mean():.3f} median={np.median(res_cw):.3f}")
print(f"EW series shape={ew_series.shape}  CW series shape={cw_series.shape}")
assert ew_series.shape == (ret_matrix.shape[0], 5000), "series shape wrong"
assert isinstance(portfolios, list) and len(portfolios) == 5, "portfolios sample wrong"
print("series matrices + sample portfolios returned: PASS")

print("\n" + "="*60)
print("VERIFY 4: Fama-French 3-factor alpha distribution")
print("="*60)
ff = eng.load_ff_factors("data/ff3_monthly.csv")
dist = eng.run_ff_analysis(ret_matrix, cap_matrix, 1000, 30, rf, ff)
print(f"FF factors loaded: {len(ff)} months, cols={list(ff.columns)}")
print("EW alpha distribution (equal-weight darts):")
for k, v in dist.get("ew", {}).items():
    print(f"   {k}: {v}")
print("CW alpha distribution (cap-weight darts):")
for k, v in dist.get("cw", {}).items():
    print(f"   {k}: {v}")
# The point of the experiment: random portfolios should show ~0 alpha.
print("\nINTERPRETATION: median alpha near 0 means random darts carry no")
print("skill beyond market/size/value exposure (FF-adjusted).")

print("\n" + "="*60)
print("ALL VERIFICATIONS RAN")
print("="*60)
