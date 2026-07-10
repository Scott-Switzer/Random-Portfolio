"""
Engine module for the Dartboard Experiment.
Contains all simulation logic, statistical functions, and data handling.
"""

from typing import Tuple, List, Optional, Dict
import pandas as pd
import numpy as np
import logging
import math
from functools import wraps

try:
    import yfinance as yf
except Exception:  # pragma: no cover - only used when optional deps are absent
    yf = None

try:
    from scipy import stats
except Exception:  # pragma: no cover - fallback paths keep local smoke tests importable
    stats = None

try:
    from numba import jit
except Exception:  # pragma: no cover - numba is an optional accelerator
    def jit(*jit_args, **jit_kwargs):
        if jit_args and callable(jit_args[0]) and len(jit_args) == 1 and not jit_kwargs:
            return jit_args[0]

        def decorator(func):
            return func

        return decorator

try:
    import statsmodels.api as sm
except Exception:  # pragma: no cover - vectorized OLS fallback is used offline
    sm = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================================================
# ERROR HANDLING DECORATOR
# =========================================================
def handle_errors(default_return):
    """Decorator to handle errors gracefully."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


# =========================================================
# DATA LOADING
# =========================================================
def load_and_clean_data(
    filepath: str, 
    min_mkt_cap: float = 10000
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """
    Loads CRSP data, filters for liquidity, and creates aligned matrices.
    
    Args:
        filepath: Path to the CSV file
        min_mkt_cap: Minimum market cap filter (in dataset units, typically $thousands)
    
    Returns:
        Tuple of (return_matrix, cap_matrix, min_date, max_date)
    """
    logger.info("ENGINE: Loading data...")
    try:
        df = pd.read_csv(filepath)
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
        df['total_ret'] = pd.to_numeric(df['total_ret'], errors='coerce')
        df['mkt_cap'] = pd.to_numeric(df['mkt_cap'], errors='coerce')
        
        # Filter: Liquidity Check & valid returns
        df = df[df['mkt_cap'] > min_mkt_cap].dropna(subset=['total_ret', 'mkt_cap'])
        
        # Pivot Returns Matrix
        ret_matrix = df.pivot_table(index='DATE', columns='TICKER', values='total_ret')
        
        # Pivot Market Cap Matrix
        cap_matrix = df.pivot_table(index='DATE', columns='TICKER', values='mkt_cap')
        
        # --- ALIGNMENT ---
        common_dates = ret_matrix.index.intersection(cap_matrix.index)
        common_tickers = ret_matrix.columns.intersection(cap_matrix.columns)
        
        ret_matrix = ret_matrix.loc[common_dates, common_tickers].fillna(0)
        cap_matrix = cap_matrix.loc[common_dates, common_tickers].fillna(0)
        
        logger.info(f"ENGINE: Data ready. {ret_matrix.shape[1]} tickers over {ret_matrix.shape[0]} months.")
        return ret_matrix, cap_matrix, df['DATE'].min(), df['DATE'].max()
        
    except Exception as e:
        logger.error(f"ENGINE ERROR: {e}")
        return pd.DataFrame(), pd.DataFrame(), None, None


def load_ff_factors(path: str) -> pd.DataFrame:
    """
    Load local Fama-French 3-factor monthly data.

    The source file is expected to use Date values in YYYYMM format and factor
    values in percentages. The returned DataFrame uses monthly PeriodIndex
    values and decimal factor returns.
    """
    ff = pd.read_csv(path)
    required_cols = ["Date", "Mkt-RF", "SMB", "HML", "RF"]
    missing = [col for col in required_cols if col not in ff.columns]
    if missing:
        raise ValueError(f"Missing Fama-French columns: {missing}")

    ff = ff[required_cols].copy()
    ff["Date"] = pd.to_datetime(ff["Date"].astype(str), format="%Y%m").dt.to_period("M")
    factor_cols = ["Mkt-RF", "SMB", "HML", "RF"]
    ff[factor_cols] = ff[factor_cols].apply(pd.to_numeric, errors="coerce") / 100.0
    ff = ff.dropna(subset=factor_cols).set_index("Date").sort_index()
    ff.index.name = "Date"
    return ff[factor_cols]


def _period_index_for_returns(index: pd.Index) -> pd.PeriodIndex:
    """Convert a return matrix index to monthly periods for factor alignment."""
    if isinstance(index, pd.PeriodIndex):
        return index.asfreq("M")
    return pd.DatetimeIndex(index).to_period("M")


def _align_ff_to_return_matrix(
    ret_matrix: pd.DataFrame,
    cap_matrix: pd.DataFrame,
    ff: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    periods = _period_index_for_returns(ret_matrix.index)
    ff_aligned = ff.reindex(periods)
    factor_cols = ["Mkt-RF", "SMB", "HML", "RF"]
    valid = ff_aligned[factor_cols].notna().all(axis=1).to_numpy()

    if not valid.any():
        raise ValueError("No overlapping months between returns and Fama-French factors.")

    ret_aligned = ret_matrix.iloc[valid].copy()
    cap_aligned = cap_matrix.iloc[valid].copy()
    ff_aligned = ff_aligned.iloc[valid].copy()
    ff_aligned.index = periods[valid]
    return ret_aligned, cap_aligned, ff_aligned


# =========================================================
# RISK-FREE RATE
# =========================================================
@handle_errors(default_return=0.03)
def get_dynamic_rf(start_date, end_date) -> float:
    """Fetches avg 13-Week T-Bill yield for period."""
    if yf is None:
        logger.warning("ENGINE WARNING: yfinance unavailable. Defaulting to 3%.")
        return 0.03

    s_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    e_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    
    irx = yf.download("^IRX", start=s_str, end=e_str, progress=False)
    if irx.empty: 
        logger.warning("ENGINE WARNING: ^IRX download failed. Defaulting to 3%.")
        return 0.03
    
    col = 'Adj Close' if 'Adj Close' in irx.columns else 'Close'
    if isinstance(irx.columns, pd.MultiIndex):
        try:
            vals = irx.xs('^IRX', level=1, axis=1)[col]
        except KeyError:
            vals = irx[col]
    else:
        vals = irx[col]
        
    return float(vals.mean() / 100.0)


# =========================================================
# SHARPE RATIO CALCULATIONS
# =========================================================
@jit(nopython=True)
def calculate_sharpe_numba(monthly_returns: np.ndarray, rf_rate: float) -> float:
    """
    Numba-accelerated Sharpe calculation for maximum performance.
    
    Args:
        monthly_returns: Array of monthly returns
        rf_rate: Annual risk-free rate
    
    Returns:
        Annualized Sharpe ratio
    """
    n = len(monthly_returns)
    if n < 6:
        return 0.0
    
    # Geometric average annual return
    growth = 1.0
    for r in monthly_returns:
        growth *= (1.0 + r)
    
    n_years = n / 12.0
    ann_ret = (growth ** (1.0 / n_years)) - 1.0 if n_years > 0 else 0.0
    
    # Annualized volatility (manual calculation for numba)
    mean_ret = 0.0
    for r in monthly_returns:
        mean_ret += r
    mean_ret /= n
    
    variance = 0.0
    for r in monthly_returns:
        variance += (r - mean_ret) ** 2
    variance /= (n - 1) if n > 1 else 1
    
    ann_vol = (variance ** 0.5) * (12.0 ** 0.5)
    
    return (ann_ret - rf_rate) / ann_vol if ann_vol > 0 else 0.0


def calculate_sharpe(monthly_returns, rf_rate: float) -> float:
    """
    Calculate Sharpe ratio from monthly returns.
    Wrapper that handles pandas Series and calls numba version.
    """
    if isinstance(monthly_returns, pd.Series):
        monthly_returns = monthly_returns.values
    monthly_returns = np.asarray(monthly_returns, dtype=np.float64)
    return calculate_sharpe_numba(monthly_returns, rf_rate)


def calculate_sharpe_vectorized(monthly_returns: np.ndarray, rf_rate: float) -> np.ndarray:
    """
    Calculate annualized Sharpe ratios for a matrix of monthly returns.

    Args:
        monthly_returns: Array shaped (months, simulations)
        rf_rate: Annual risk-free rate

    Returns:
        One Sharpe ratio per simulation.
    """
    returns = np.asarray(monthly_returns, dtype=np.float64)
    if returns.ndim == 1:
        returns = returns.reshape(-1, 1)

    n_months = returns.shape[0]
    if n_months < 6:
        return np.zeros(returns.shape[1], dtype=np.float64)

    returns = np.where(np.isfinite(returns), returns, 0.0)
    growth = np.prod(1.0 + returns, axis=0)
    ann_ret = np.where(growth > 0, np.power(growth, 12.0 / n_months) - 1.0, -1.0)
    ann_vol = np.std(returns, axis=0, ddof=1) * np.sqrt(12.0)

    return np.divide(
        ann_ret - rf_rate,
        ann_vol,
        out=np.zeros_like(ann_ret, dtype=np.float64),
        where=ann_vol > 0,
    )


# =========================================================
# BENCHMARK STATS
# =========================================================
@handle_errors(default_return=(0.0, 0.0))
def get_benchmark_stats(ticker: str, start_date, end_date, rf_rate: float) -> Tuple[float, float]:
    """
    Fetches external benchmark (SPY/IWM) for comparison.
    
    Args:
        ticker: Benchmark ticker symbol
        start_date: Start date for the period
        end_date: End date for the period
        rf_rate: Risk-free rate
    
    Returns:
        Tuple of (sharpe_ratio, annualized_return)
    """
    if yf is None:
        logger.warning("ENGINE WARNING: yfinance unavailable. Returning empty benchmark stats.")
        return 0.0, 0.0

    s_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    e_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    
    logger.info(f"ENGINE: Fetching {ticker} from {s_str} to {e_str}...")
    data = yf.download(ticker, start=s_str, end=e_str, progress=False)
    
    if data.empty: 
        logger.error(f"ENGINE ERROR: No data found for {ticker}.")
        return 0.0, 0.0
    
    # Handle MultiIndex (New yfinance version)
    if isinstance(data.columns, pd.MultiIndex):
        try:
            data = data.xs(ticker, level=1, axis=1)
        except KeyError:
            pass
        
    col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
    
    # Resample to monthly
    try:
        monthly = data[col].resample('ME').last().pct_change().dropna()
    except ValueError:
        monthly = data[col].resample('M').last().pct_change().dropna()
    
    sharpe = calculate_sharpe(monthly.values, rf_rate)
    ret = monthly.mean() * 12
    return sharpe, ret


# =========================================================
# MONTE CARLO SIMULATION
# =========================================================
def run_monte_carlo(
    ret_matrix: pd.DataFrame, 
    cap_matrix: pd.DataFrame, 
    n_sims: int, 
    n_stocks: int, 
    rf_rate: float, 
    progress_callback=None
) -> Tuple[np.ndarray, np.ndarray, List[List[str]], np.ndarray, np.ndarray]:
    """
    Core vectorized Monte Carlo Simulation.
    
    Args:
        ret_matrix: DataFrame of stock returns (dates x tickers)
        cap_matrix: DataFrame of market caps (dates x tickers)
        n_sims: Number of simulations to run
        n_stocks: Number of stocks per portfolio
        rf_rate: Risk-free rate
        progress_callback: Optional callback function for progress updates
    
    Returns:
        Tuple of (
            equal_weight_sharpes,
            cap_weight_sharpes,
            sample_portfolios,
            equal_weight_monthly_return_series,
            cap_weight_monthly_return_series,
        )
    """
    if n_sims <= 0:
        empty_series = np.empty((len(ret_matrix), 0), dtype=np.float64)
        return (
            np.empty(0, dtype=np.float64),
            np.empty(0, dtype=np.float64),
            [],
            empty_series,
            empty_series.copy(),
        )

    ret_vals = ret_matrix.to_numpy(dtype=np.float64, copy=False)
    cap_lagged_vals = cap_matrix.shift(1).fillna(0).to_numpy(dtype=np.float64, copy=False)

    tickers = ret_matrix.columns.values
    n_tickers = ret_vals.shape[1]

    if n_stocks <= 0:
        raise ValueError("n_stocks must be positive.")
    if n_stocks > n_tickers:
        raise ValueError(f"n_stocks ({n_stocks}) cannot exceed available tickers ({n_tickers}).")

    if progress_callback:
        progress_callback(0.05)

    # Generate one without-replacement sample per simulation, fully vectorized.
    random_scores = np.random.random((n_sims, n_tickers))
    idx = np.argpartition(random_scores, kth=n_stocks - 1, axis=1)[:, :n_stocks]

    sample_portfolios = [tickers[row].tolist() for row in idx[:5]]

    if progress_callback:
        progress_callback(0.25)

    r = ret_vals[:, idx]
    ew_series = r.mean(axis=2)

    if progress_callback:
        progress_callback(0.55)

    lagged_cap = cap_lagged_vals[:, idx]
    denom = lagged_cap.sum(axis=2, keepdims=True)
    weights = np.divide(
        lagged_cap,
        denom,
        out=np.zeros_like(lagged_cap, dtype=np.float64),
        where=denom > 0,
    )
    cw_series = (weights * r).sum(axis=2)

    if progress_callback:
        progress_callback(0.80)

    results_ew = calculate_sharpe_vectorized(ew_series, rf_rate)
    results_cw = calculate_sharpe_vectorized(cw_series, rf_rate)

    if progress_callback:
        progress_callback(1.0)

    return results_ew, results_cw, sample_portfolios, ew_series, cw_series


# =========================================================
# FAMA-FRENCH 3-FACTOR ALPHA
# =========================================================
def _prepare_ff_inputs(
    port_returns_monthly: np.ndarray,
    ff: pd.DataFrame,
) -> Tuple[np.ndarray, pd.DataFrame]:
    returns = np.asarray(port_returns_monthly, dtype=np.float64).reshape(-1)
    factor_cols = ["Mkt-RF", "SMB", "HML", "RF"]
    factors = ff[factor_cols].copy()

    if len(factors) != len(returns):
        if len(factors) < len(returns):
            raise ValueError("Fama-French factor data is shorter than the return series.")
        # Standalone ndarray calls carry no dates, so fall back to the most
        # recent matching factor window. Date-aware callers should pre-align ff.
        factors = factors.iloc[-len(returns):].copy()

    valid = np.isfinite(returns) & np.isfinite(factors.to_numpy(dtype=np.float64)).all(axis=1)
    if valid.sum() <= 4:
        raise ValueError("Not enough valid monthly observations for Fama-French regression.")

    return returns[valid], factors.iloc[valid]


def _ols_alpha_batch(
    return_matrix: np.ndarray,
    factors: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Vectorized OLS for many portfolio return series against FF3 factors.

    Returns annualized alpha, market beta, R-squared, and alpha t-stat arrays.
    """
    y = np.asarray(return_matrix, dtype=np.float64)
    if y.ndim == 1:
        y = y.reshape(-1, 1)

    factor_cols = ["Mkt-RF", "SMB", "HML", "RF"]
    factor_values = factors[factor_cols].to_numpy(dtype=np.float64)
    valid_rows = np.isfinite(factor_values).all(axis=1) & np.isfinite(y).all(axis=1)

    y = y[valid_rows]
    factor_values = factor_values[valid_rows]

    n_obs = y.shape[0]
    n_params = 4
    if n_obs <= n_params:
        raise ValueError("Not enough valid monthly observations for Fama-French regression.")

    excess_y = y - factor_values[:, 3:4]
    x = np.column_stack([np.ones(n_obs), factor_values[:, :3]])

    xtx_inv = np.linalg.pinv(x.T @ x)
    betas = xtx_inv @ x.T @ excess_y
    fitted = x @ betas
    residuals = excess_y - fitted

    sse = np.sum(residuals * residuals, axis=0)
    centered = excess_y - excess_y.mean(axis=0, keepdims=True)
    tss = np.sum(centered * centered, axis=0)
    r2 = np.ones_like(sse)
    r2 = np.subtract(
        1.0,
        np.divide(sse, tss, out=np.ones_like(sse), where=tss > 0),
        out=r2,
    )

    dof = max(n_obs - n_params, 1)
    sigma2 = sse / dof
    alpha_se = np.sqrt(np.maximum(sigma2 * xtx_inv[0, 0], 0.0))
    alpha_t = np.divide(
        betas[0],
        alpha_se,
        out=np.zeros_like(alpha_se),
        where=alpha_se > 0,
    )

    alpha_annualized = betas[0] * 12.0
    beta_mkt = betas[1]
    return alpha_annualized, beta_mkt, r2, alpha_t


def fama_french_alpha(
    port_returns_monthly: np.ndarray,
    ff: pd.DataFrame,
) -> Tuple[float, float, float]:
    """
    Estimate annualized Fama-French alpha for one monthly return series.

    Regresses (portfolio return - RF) on [Mkt-RF, SMB, HML]. statsmodels OLS is
    used when installed; the numpy fallback exists for offline smoke tests.
    """
    returns, factors = _prepare_ff_inputs(port_returns_monthly, ff)

    if sm is not None:
        try:
            y = returns - factors["RF"].to_numpy(dtype=np.float64)
            x = sm.add_constant(factors[["Mkt-RF", "SMB", "HML"]], has_constant="add")
            result = sm.OLS(y, x).fit()
            return (
                float(result.params.iloc[0] * 12.0),
                float(result.params.iloc[1]),
                float(result.rsquared),
            )
        except Exception as exc:  # pragma: no cover - protects mixed local envs
            logger.warning("statsmodels OLS failed; using numpy OLS fallback: %s", exc)

    alpha, beta_mkt, r2, _ = _ols_alpha_batch(returns, factors)
    return float(alpha[0]), float(beta_mkt[0]), float(r2[0])


def _summarize_alpha_distribution(
    alpha_values: np.ndarray,
    alpha_tstats: np.ndarray,
    beta_values: np.ndarray,
    r2_values: np.ndarray,
) -> Dict:
    finite = np.isfinite(alpha_values)
    alpha_values = alpha_values[finite]
    alpha_tstats = alpha_tstats[finite]
    beta_values = beta_values[finite]
    r2_values = r2_values[finite]

    if len(alpha_values) == 0:
        return {
            "n": 0,
            "mean": np.nan,
            "median": np.nan,
            "p5": np.nan,
            "p95": np.nan,
            "pct_sig_positive": np.nan,
            "mean_beta_mkt": np.nan,
            "mean_r2": np.nan,
        }

    percentiles = np.percentile(alpha_values, [5, 50, 95])
    return {
        "n": int(len(alpha_values)),
        "mean": float(np.mean(alpha_values)),
        "median": float(percentiles[1]),
        "p5": float(percentiles[0]),
        "p95": float(percentiles[2]),
        "pct_sig_positive": float(np.mean(alpha_tstats > 1.96) * 100.0),
        "mean_beta_mkt": float(np.mean(beta_values)),
        "mean_r2": float(np.mean(r2_values)),
    }


def run_ff_analysis(
    ret_matrix: pd.DataFrame,
    cap_matrix: pd.DataFrame,
    n_sims: int,
    n_stocks: int,
    rf_rate: float,
    ff: pd.DataFrame,
    chunk_size: int = 500,
) -> Dict[str, Dict]:
    """
    Run batched Monte Carlo portfolios and summarize FF3 alpha distributions.

    Returns separate equal-weight and cap-weight alpha summaries.
    """
    ret_aligned, cap_aligned, ff_aligned = _align_ff_to_return_matrix(ret_matrix, cap_matrix, ff)
    chunk_size = max(1, int(chunk_size))

    buckets = {
        "ew": {"alpha": [], "t": [], "beta": [], "r2": []},
        "cw": {"alpha": [], "t": [], "beta": [], "r2": []},
    }

    for start in range(0, n_sims, chunk_size):
        current_sims = min(chunk_size, n_sims - start)
        _, _, _, ew_series, cw_series = run_monte_carlo(
            ret_aligned,
            cap_aligned,
            current_sims,
            n_stocks,
            rf_rate,
            progress_callback=None,
        )

        for key, series in (("ew", ew_series), ("cw", cw_series)):
            alpha, beta_mkt, r2, alpha_t = _ols_alpha_batch(series, ff_aligned)
            buckets[key]["alpha"].append(alpha)
            buckets[key]["t"].append(alpha_t)
            buckets[key]["beta"].append(beta_mkt)
            buckets[key]["r2"].append(r2)

    summaries = {}
    for key, values in buckets.items():
        concat_alpha = (
            np.concatenate(values["alpha"]) if values["alpha"] else np.empty(0)
        )
        summaries[key] = _summarize_alpha_distribution(
            concat_alpha,
            np.concatenate(values["t"]) if values["t"] else np.empty(0),
            np.concatenate(values["beta"]) if values["beta"] else np.empty(0),
            np.concatenate(values["r2"]) if values["r2"] else np.empty(0),
        )
        # Keep the raw annualized alpha array for visualization (histogram).
        summaries[key]["alphas"] = concat_alpha

    return summaries


# =========================================================
# STATISTICAL FUNCTIONS
# =========================================================
def _normal_two_sided_pvalue(test_stat: float) -> float:
    return float(math.erfc(abs(float(test_stat)) / math.sqrt(2.0)))


def compute_statistics(results: np.ndarray) -> Dict:
    """
    Compute comprehensive statistics for simulation results.
    
    Args:
        results: Array of Sharpe ratios from simulation
    
    Returns:
        Dictionary with mean, std, se, confidence intervals, and percentiles
    """
    results = np.asarray(results)
    n = len(results)
    mean = np.mean(results)
    std = np.std(results, ddof=1)
    se = std / np.sqrt(n)
    
    # 95% Confidence Interval
    if stats is not None and n > 1:
        try:
            ci_95 = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
        except Exception:
            ci_95 = (mean - 1.96 * se, mean + 1.96 * se)
    else:
        ci_95 = (mean - 1.96 * se, mean + 1.96 * se)
    
    # Percentiles
    percentiles = np.percentile(results, [5, 25, 50, 75, 95])
    
    return {
        'mean': mean,
        'std': std,
        'se': se,
        'ci_95_low': ci_95[0],
        'ci_95_high': ci_95[1],
        'p5': percentiles[0],
        'p25': percentiles[1],
        'median': percentiles[2],
        'p75': percentiles[3],
        'p95': percentiles[4]
    }


def test_ew_vs_cw(res_ew: np.ndarray, res_cw: np.ndarray) -> Dict:
    """
    Paired t-test: is equal-weight significantly different from cap-weight?
    
    Args:
        res_ew: Equal-weight Sharpe ratios
        res_cw: Cap-weight Sharpe ratios
    
    Returns:
        Dictionary with t-statistic, p-value, Cohen's d, and significance flag
    """
    if stats is not None:
        try:
            t_stat, p_value = stats.ttest_rel(res_ew, res_cw)
        except Exception:
            t_stat, p_value = None, None
    else:
        t_stat, p_value = None, None

    if t_stat is None or p_value is None:
        diff = np.asarray(res_ew, dtype=np.float64) - np.asarray(res_cw, dtype=np.float64)
        se = np.std(diff, ddof=1) / np.sqrt(len(diff)) if len(diff) > 1 else 0.0
        t_stat = float(np.mean(diff) / se) if se > 0 else 0.0
        p_value = _normal_two_sided_pvalue(t_stat)

    cohens_d = (np.mean(res_ew) - np.mean(res_cw)) / np.sqrt(
        (np.std(res_ew)**2 + np.std(res_cw)**2) / 2
    )
    return {
        't_stat': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'significant': p_value < 0.05
    }


def test_vs_benchmark(results: np.ndarray, benchmark_sharpe: float) -> Dict:
    """
    One-sample t-test: do results significantly differ from benchmark?
    
    Args:
        results: Array of Sharpe ratios
        benchmark_sharpe: Benchmark Sharpe ratio to compare against
    
    Returns:
        Dictionary with t-statistic, p-value, and significance flag
    """
    if stats is not None:
        try:
            t_stat, p_value = stats.ttest_1samp(results, benchmark_sharpe)
        except Exception:
            t_stat, p_value = None, None
    else:
        t_stat, p_value = None, None

    if t_stat is None or p_value is None:
        results = np.asarray(results, dtype=np.float64)
        se = np.std(results, ddof=1) / np.sqrt(len(results)) if len(results) > 1 else 0.0
        t_stat = float((np.mean(results) - benchmark_sharpe) / se) if se > 0 else 0.0
        p_value = _normal_two_sided_pvalue(t_stat)

    return {
        't_stat': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def bootstrap_ci(data: np.ndarray, n_bootstrap: int = 1000, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Bootstrap confidence interval for the mean.
    
    Args:
        data: Array of values
        n_bootstrap: Number of bootstrap samples
        confidence: Confidence level (default 0.95)
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    boot_means = np.zeros(n_bootstrap)
    n = len(data)
    
    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        boot_means[i] = np.mean(sample)
    
    lower = np.percentile(boot_means, (1 - confidence) / 2 * 100)
    upper = np.percentile(boot_means, (1 + confidence) / 2 * 100)
    
    return lower, upper


def run_rolling_analysis(
    ret_matrix: pd.DataFrame, 
    cap_matrix: pd.DataFrame, 
    window_years: int = 5, 
    n_sims: int = 100, 
    n_stocks: int = 30, 
    rf_rate: float = 0.03
) -> pd.DataFrame:
    """
    Run simulation over rolling windows to show time-varying results.
    
    Args:
        ret_matrix: DataFrame of returns
        cap_matrix: DataFrame of market caps
        window_years: Rolling window size in years
        n_sims: Simulations per window
        n_stocks: Stocks per portfolio
        rf_rate: Risk-free rate
    
    Returns:
        DataFrame with rolling analysis results
    """
    results = []
    window_months = window_years * 12
    dates = ret_matrix.index
    
    for start_idx in range(0, len(dates) - window_months, 12):
        end_idx = start_idx + window_months
        
        sub_ret = ret_matrix.iloc[start_idx:end_idx]
        sub_cap = cap_matrix.iloc[start_idx:end_idx]
        
        res_ew, res_cw, _, _, _ = run_monte_carlo(sub_ret, sub_cap, n_sims, n_stocks, rf_rate, None)
        
        results.append({
            'start_date': dates[start_idx],
            'end_date': dates[end_idx-1],
            'ew_mean': np.mean(res_ew),
            'cw_mean': np.mean(res_cw),
            'ew_win_rate': np.mean(res_ew > res_cw) * 100
        })
    
    return pd.DataFrame(results)
