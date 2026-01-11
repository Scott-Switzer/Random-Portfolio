[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://emh-random-walk-portfolio-experiment.streamlit.app)

A Monte Carlo simulation testing Burton Malkiel's famous claim that "a blindfolded monkey throwing darts at a newspaper's financial pages could select a portfolio that would do just as well as one carefully selected by experts."

## 🔬 What This Tests

- **Efficient Market Hypothesis (EMH)** — Eugene Fama (1970)
- **Random Walk Theory** — Burton Malkiel (1973)

## 📊 Methodology

- **Data Source**: CRSP via WRDS (survivorship bias-free)
- **Universe**: ~3,000-5,000 US stocks with market cap > $10M
- **Simulations**: User-configurable (100 - 5,000)
- **Metrics**: Sharpe Ratio (risk-adjusted returns)

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/Scott-Switzer/Random-Portfolio.git
cd Random-Portfolio

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py