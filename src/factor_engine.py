"""Cross-sectional factors from a wide close matrix (possibly misaligned calendars)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MIN_OBS = 21


def _latest_for_series(close: pd.Series) -> dict[str, float] | None:
    s = close.dropna()
    if len(s) < MIN_OBS:
        return None
    rets = s.pct_change()
    mom = s.pct_change(20)
    vol = rets.rolling(20).std() * np.sqrt(252)
    return {
        "momentum_20d": float(mom.iloc[-1]),
        "volatility_20d": float(vol.iloc[-1]),
        "last_price": float(s.iloc[-1]),
    }


def compute_latest_factors(prices: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for col in prices.columns:
        snap = _latest_for_series(prices[col])
        if snap is None:
            continue
        row = {"ticker": col, **snap}
        rows.append(row)
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows).set_index("ticker")
    vol = out["volatility_20d"].replace(0, np.nan)
    out["risk_adjusted_momentum"] = out["momentum_20d"] / vol
    return out.sort_values("risk_adjusted_momentum", ascending=False)


def main() -> None:
    prices = pd.read_csv(
        ROOT / "data" / "prices.csv",
        index_col=0,
        parse_dates=True,
    )
    latest = compute_latest_factors(prices)
    latest.to_csv(ROOT / "data" / "factors.csv")
    print(latest)


if __name__ == "__main__":
    main()
