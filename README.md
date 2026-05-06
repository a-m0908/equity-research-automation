# equity-research-automation

A small set of tools for US large-cap tech names: build a cross-sectional factor snapshot from daily closing prices, then compare names in a simple dashboard.

## Data scope

- **Tickers**: `AAPL`, `MSFT`, `NVDA`, `GOOGL`, `AMZN` (downloaded together on a shared calendar)
- **Price series**: Split-adjusted closes from `yfinance` (`auto_adjust=True`), stored at daily frequency
- **Horizon**: As configured in code, downloads target the range 2022-01-01 through 2026-01-01

## Computed factors

| Column | Definition |
|--------|------------|
| `momentum_20d` | 20-trading-day simple return on close (`pct_change(20)`) |
| `volatility_20d` | 20-day rolling standard deviation of daily returns, annualized (`×√252`) |
| `last_price` | Latest close in the series |
| `risk_adjusted_momentum` | `momentum_20d / volatility_20d` (momentum scaled by trailing vol) |

Outputs are aggregated as a **latest-date snapshot** per ticker, sorted by descending `risk_adjusted_momentum`.

## Dashboard behavior

- **Table**: All factor columns, one row per ticker
- **Bar chart**: Cross-sectional comparison of `risk_adjusted_momentum`

## Functional pipeline

1. **Market data ingest**: Merge closes across tickers, drop missing values, persist the price matrix as intermediate data
2. **Factor engine**: From the price matrix, compute returns and rolling statistics, then write the latest row as the cross-sectional score file
3. **Visualization**: Read the score file and present it in a table and chart

## Data source limitations

- Prices depend on `yfinance`, not an official exchange vendor feed; availability, terms of use, and latency constraints apply. Intended as a research aid, not a sole source for live trading decisions.
