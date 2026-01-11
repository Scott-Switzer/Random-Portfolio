"""
Engine module for the Dartboard Experiment.
Contains all simulation logic, statistical functions, and data handling.
"""

from typing import Tuple, List, Optional, Dict
import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats
from numba import jit
import logging
from functools import wraps

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


# =========================================================
# RISK-FREE RATE
# =========================================================
@handle_errors(default_return=0.03)
def get_dynamic_rf(start_date, end_date) -> float:
    """Fetches avg 13-Week T-Bill yield for period."""
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
) -> Tuple[np.ndarray, np.ndarray, List[List[str]]]:
    """
    Core Monte Carlo Simulation Loop.
    
    Args:
        ret_matrix: DataFrame of stock returns (dates x tickers)
        cap_matrix: DataFrame of market caps (dates x tickers)
        n_sims: Number of simulations to run
        n_stocks: Number of stocks per portfolio
        rf_rate: Risk-free rate
        progress_callback: Optional callback function for progress updates
    
    Returns:
        Tuple of (equal_weight_sharpes, cap_weight_sharpes, sample_portfolios)
    """
    results_ew = np.zeros(n_sims)
    results_cw = np.zeros(n_sims)
    sample_portfolios = []
    
    ret_vals = ret_matrix.values
    cap_lagged_vals = cap_matrix.shift(1).fillna(0).values
    
    tickers = ret_matrix.columns.values
    n_tickers = ret_vals.shape[1]
    
    # Pre-generate all random indices for consistency
    all_idxs = np.array([
        np.random.choice(n_tickers, n_stocks, replace=False) 
        for _ in range(n_sims)
    ])
    
    for i in range(n_sims):
        idxs = all_idxs[i]
        
        # Store first 5 portfolios for transparency
        if i < 5:
            sample_portfolios.append(tickers[idxs].tolist())
            
        r_subset = ret_vals[:, idxs]
        c_lagged_subset = cap_lagged_vals[:, idxs]
        
        # A) Equal Weighted
        ew_port_ret = np.mean(r_subset, axis=1)
        results_ew[i] = calculate_sharpe_numba(ew_port_ret, rf_rate)
        
        # B) Cap Weighted
        row_sums = np.sum(c_lagged_subset, axis=1)
        weights = np.zeros_like(c_lagged_subset)
        mask = row_sums > 0
        weights[mask] = c_lagged_subset[mask] / row_sums[mask, None]
        
        cw_port_ret = np.sum(weights * r_subset, axis=1)
        results_cw[i] = calculate_sharpe_numba(cw_port_ret, rf_rate)
        
        if progress_callback and i % 25 == 0:
            progress_callback(i / n_sims)
            
    if progress_callback:
        progress_callback(1.0)
    
    return results_ew, results_cw, sample_portfolios


# =========================================================
# STATISTICAL FUNCTIONS
# =========================================================
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
    ci_95 = stats.t.interval(0.95, df=n-1, loc=mean, scale=se)
    
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
    t_stat, p_value = stats.ttest_rel(res_ew, res_cw)
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
    t_stat, p_value = stats.ttest_1samp(results, benchmark_sharpe)
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
        
        res_ew, res_cw, _ = run_monte_carlo(sub_ret, sub_cap, n_sims, n_stocks, rf_rate, None)
        
        results.append({
            'start_date': dates[start_idx],
            'end_date': dates[end_idx-1],
            'ew_mean': np.mean(res_ew),
            'cw_mean': np.mean(res_cw),
            'ew_win_rate': np.mean(res_ew > res_cw) * 100
        })
    
    return pd.DataFrame(results)