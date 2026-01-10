import pandas as pd
df = pd.read_csv('US_SPYdata_2000_2024.csv')

# Find rows with actual delisting returns
delistings = df[df['DLRET'].notna()]
print(f"Total delisting events: {len(delistings)}")
print(f"Unique delisted tickers: {delistings['TICKER'].nunique()}")
print("\nSample delisting events:")
print(delistings[['DATE', 'TICKER', 'COMNAM', 'RET', 'DLRET', 'total_ret']].head(10))