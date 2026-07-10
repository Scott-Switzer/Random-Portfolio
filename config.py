"""Configuration constants for the Dartboard app."""

# Data settings
MIN_MARKET_CAP = 10_000  # $10M in CRSP units
DATA_FILE = "US_SPYdata_2000_2024.csv"

# Simulation defaults
DEFAULT_N_STOCKS = 30
DEFAULT_N_SIMS = 500
MIN_SIMS = 100
MAX_SIMS = 5000
MIN_STOCKS = 10
MAX_STOCKS = 100

# Benchmarks
BENCHMARKS = {
    "SPY": "S&P 500",
    "IWM": "Russell 2000"
}

# Long-running, actively managed equity funds selected as credible professional
# comparators: Contrafund (large-growth), Dodge & Cox Stock (deep value), Growth
# Fund of America (large-growth), Blue Chip Growth (large-growth), and Low-Priced
# Stock (small/mid-value). Each has a multi-decade public record on Yahoo Finance.
EXPERT_FUNDS = {
    "FCNTX": "Fidelity Contrafund",
    "DODGX": "Dodge & Cox Stock Fund",
    "AGTHX": "American Funds Growth Fund of America",
    "TRBCX": "T. Rowe Price Blue Chip Growth Fund",
    "FLPSX": "Fidelity Low-Priced Stock Fund",
}

# Cache settings
CACHE_TTL_SECONDS = 3600  # 1 hour

# Risk-free rate fallback
DEFAULT_RF_RATE = 0.03
