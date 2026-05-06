import pandas as pd
import numpy as np

prices = pd.read_csv(
    "data/prices.csv",
    index_col=0,
    parse_dates=True
)

returns = prices.pct_change()

momentum_20d = prices.pct_change(20)

volatility_20d = (
    returns.rolling(20).std() * np.sqrt(252)
)

latest = pd.DataFrame({
    "momentum_20d": momentum_20d.iloc[-1],
    "volatility_20d": volatility_20d.iloc[-1],
    "last_price": prices.iloc[-1]
})

latest["risk_adjusted_momentum"] = (
    latest["momentum_20d"]
    / latest["volatility_20d"]
)

latest = latest.sort_values(
    "risk_adjusted_momentum",
    ascending=False
)

latest.to_csv("data/factors.csv")

print(latest)