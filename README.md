# equity-research-automation

A small set of tools for US large-cap tech names: build a cross-sectional factor snapshot from daily closing prices, then compare names in a simple dashboard.

## Data scope

- **Tickers**: `AAPL`, `MSFT`, `NVDA`, `GOOGL`, `AMZN` (downloaded together on a shared calendar)
- **Price series**: Split-adjusted OHLCV from `yfinance` (`auto_adjust=True`), stored at daily frequency
- **Horizon**: As configured in code, downloads target the range 2022-01-01 through 2026-01-01

### Persisted datasets (`src/data_pipeline.py`)

| Artifact | Role |
|----------|------|
| `data/prices.csv` | Wide matrix of **adjusted closes** only (input to the factor engine) |
| `data/ohlcv/{TICKER}.csv` | Per-name daily bars with `auto_adjust=True`: **Open, High, Low, Close, Volume** (split/dividend-adjusted; yfinance does not emit a separate **Adj Close** column in this mode) |
| `data/fundamentals/{TICKER}_income_stmt_{annual,quarterly}.csv` | Income statement tables from `yfinance` |
| `data/fundamentals/{TICKER}_balance_sheet_{annual,quarterly}.csv` | Balance sheet tables |
| `data/fundamentals/{TICKER}_cashflow_{annual,quarterly}.csv` | Cash flow statement tables |
| `data/fundamentals/{TICKER}_info.json` | Issuer metadata / summary fields (`Ticker.info`) |
| `data/fundamentals/{TICKER}_dividends.csv` | Dividend history (if any) |
| `data/fundamentals/{TICKER}_splits.csv` | Split history (if any) |

These three trees are **gitignored** by default (`data/ohlcv/`, `data/fundamentals/`, `data/edinet/`) so the repo stays small; regenerate with the pipelines. Commit `data/prices.csv` / `data/factors.csv` only if you explicitly want versioned snapshots.

### EDINET (`src/edinet_pipeline.py`)

Japanese corporate filings indexed by the FSA EDINET API v2 ([disclosure portal / API docs](https://disclosure.edinet-fsa.go.jp/)). Set `EDINET_SUBSCRIPTION_KEY`, then run with a calendar `--date` to write `data/edinet/documents_{date}_type{type}.json` (daily document list).

The API `type` parameter controls **which list/metadata layout** the endpoint returns for that date; it is **not** a filing-kind filter (e.g. it does not mean “annual securities reports only”). Expect **broad same-day submissions** in the payload; narrow filtering must be done client-side using fields in each record.

This path is **independent** of the US ticker list above. Parsing XBRL or downloading individual filing binaries is not implemented here.

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

- US market and statement tables depend on `yfinance`, not an official exchange vendor feed; availability, terms of use, and latency constraints apply. Intended as a research aid, not a sole source for live trading decisions.
- EDINET access requires a registered subscription key and is subject to FSA rate limits and terms.
