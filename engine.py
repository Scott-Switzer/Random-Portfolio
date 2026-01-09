# engine.py
import pandas as pd
import numpy as np
import yfinance as yf

def load_and_clean_data(filepath, min_mkt_cap=10000):
    """
    Loads CRSP data, filters for liquidity, and creates aligned matrices.
    """
    print("ENGINE: Loading data...")
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
        
        print(f"ENGINE: Data ready. {ret_matrix.shape[1]} tickers over {ret_matrix.shape[0]} months.")
        return ret_matrix, cap_matrix, df['DATE'].min(), df['DATE'].max()
        
    except Exception as e:
        print(f"ENGINE ERROR: {e}")
        return pd.DataFrame(), pd.DataFrame(), None, None

def get_dynamic_rf(start_date, end_date):
    """Fetches avg 13-Week T-Bill yield for period."""
    try:
        # Ensure dates are strings YYYY-MM-DD
        s_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        e_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        irx = yf.download("^IRX", start=s_str, end=e_str, progress=False)
        if irx.empty: 
            print("ENGINE WARNING: ^IRX (Risk Free Rate) download failed. Defaulting to 3%.")
            return 0.03
        
        col = 'Adj Close' if 'Adj Close' in irx.columns else 'Close'
        if isinstance(irx.columns, pd.MultiIndex):
            # Handle yfinance multi-index (Ticker, Price Type)
            try:
                vals = irx.xs('^IRX', level=1, axis=1)[col]
            except KeyError:
                 # Fallback if structure is different
                vals = irx[col]
        else:
            vals = irx[col]
            
        return float(vals.mean() / 100.0)
    except Exception as e:
        print(f"ENGINE RF ERROR: {e}. Defaulting to 3%.")
        return 0.03

def calculate_sharpe(monthly_returns, rf_rate):
    """Helper for vectorized Sharpe calculation."""
    if len(monthly_returns) < 6: return 0.0
    
    # Geometric average annual return
    growth = np.prod(1 + monthly_returns)
    n_years = len(monthly_returns) / 12
    ann_ret = (growth ** (1/n_years)) - 1 if n_years > 0 else 0
    
    # Annualized volatility
    ann_vol = np.std(monthly_returns) * np.sqrt(12)
    
    return (ann_ret - rf_rate) / ann_vol if ann_vol > 0 else 0

def get_benchmark_stats(ticker, start_date, end_date, rf_rate):
    """Fetches external benchmark (SPY/IWM) for comparison."""
    try:
        # 1. Format Dates strictly for yfinance
        s_str = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        e_str = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        print(f"ENGINE: Fetching {ticker} from {s_str} to {e_str}...")
        data = yf.download(ticker, start=s_str, end=e_str, progress=False)
        
        if data.empty: 
            print(f"ENGINE ERROR: No data found for {ticker}.")
            return 0.0, 0.0
        
        # 2. Handle MultiIndex (New yfinance version)
        if isinstance(data.columns, pd.MultiIndex):
            try:
                data = data.xs(ticker, level=1, axis=1)
            except KeyError:
                pass # Structure might be simple already
            
        col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
        
        # 3. Resample
        # Try 'ME' (Month End) for new pandas, fallback to 'M'
        try:
            monthly = data[col].resample('ME').last().pct_change().dropna()
        except ValueError:
            monthly = data[col].resample('M').last().pct_change().dropna()
        
        sharpe = calculate_sharpe(monthly, rf_rate)
        ret = monthly.mean() * 12 # Simple arithmetic mean for display
        return sharpe, ret
        
    except Exception as e:
        print(f"ENGINE BENCHMARK ERROR ({ticker}): {e}")
        return 0.0, 0.0

# engine.py (Partial Update - Replace run_monte_carlo only)

def run_monte_carlo(ret_matrix, cap_matrix, n_sims, n_stocks, rf_rate, progress_callback=None):
    """
    Core Simulation Loop. Returns results AND sample portfolios for transparency.
    """
    results_ew = []
    results_cw = []
    sample_portfolios = [] # Store first 5 portfolios for display
    
    ret_vals = ret_matrix.values
    cap_lagged_vals = cap_matrix.shift(1).fillna(0).values
    
    # Get Ticker Names (Columns)
    tickers = ret_matrix.columns.values
    n_tickers = ret_vals.shape[1]
    
    for i in range(n_sims):
        # 1. Select random stock indices
        idxs = np.random.choice(range(n_tickers), n_stocks, replace=False)
        
        # Store the first 5 random portfolios for the user to inspect
        if i < 5:
            sample_portfolios.append(tickers[idxs].tolist())
            
        r_subset = ret_vals[:, idxs]
        c_lagged_subset = cap_lagged_vals[:, idxs]
        
        # A) Equal Weighted
        ew_port_ret = np.mean(r_subset, axis=1)
        results_ew.append(calculate_sharpe(ew_port_ret, rf_rate))
        
        # B) Cap Weighted
        row_sums = np.sum(c_lagged_subset, axis=1)
        weights = np.zeros_like(c_lagged_subset)
        mask = row_sums > 0
        weights[mask] = c_lagged_subset[mask] / row_sums[mask, None]
        
        cw_port_ret = np.sum(weights * r_subset, axis=1)
        results_cw.append(calculate_sharpe(cw_port_ret, rf_rate))
        
        if progress_callback and i % 25 == 0:
            progress_callback(i / n_sims)
            
    if progress_callback: progress_callback(1.0)
    
    return np.array(results_ew), np.array(results_cw), sample_portfolios