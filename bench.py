"""Simple performance benchmark for the vectorized Monte Carlo engine."""

import time

import engine


def main() -> None:
    ret_matrix, cap_matrix, _, _ = engine.load_and_clean_data("US_SPYdata_2000_2024.csv")
    if ret_matrix.empty or cap_matrix.empty:
        raise RuntimeError("Input data failed to load.")

    start = time.perf_counter()
    res_ew, res_cw, _, ew_series, cw_series = engine.run_monte_carlo(
        ret_matrix,
        cap_matrix,
        n_sims=5000,
        n_stocks=30,
        rf_rate=0.03,
        progress_callback=None,
    )
    elapsed = time.perf_counter() - start

    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"EW Sharpe sims: {res_ew.shape[0]}")
    print(f"CW Sharpe sims: {res_cw.shape[0]}")
    print(f"EW series shape: {ew_series.shape}")
    print(f"CW series shape: {cw_series.shape}")


if __name__ == "__main__":
    main()
