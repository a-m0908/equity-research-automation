"""Download market prices, OHLCV panels, and yfinance fundamentals for configured tickers."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import yfinance as yf

# Asia liquid large caps; yfinance suffixes: .T JP, .HK HK, .KS KR, .TW TW, .SI SG, .NS IN
TICKERS = [
    "7203.T",  # Toyota (JP)
    "6758.T",  # Sony Group (JP)
    "9984.T",  # SoftBank Group (JP)
    "6861.T",  # Keyence (JP)
    "0700.HK",  # Tencent (HK)
    "9988.HK",  # Alibaba (HK)
    "005930.KS",  # Samsung Electronics (KR)
    "000660.KS",  # SK Hynix (KR)
    "2330.TW",  # TSMC (TW)
    "D05.SI",  # DBS Group (SG)
    "RELIANCE.NS",  # Reliance Industries (IN)
]
START = "2022-01-01"
END = "2026-01-01"

ROOT = Path(__file__).resolve().parent.parent


def _write_ohlcv_per_ticker(raw: pd.DataFrame, ohlcv_dir: Path) -> None:
    if raw.empty or not isinstance(raw.columns, pd.MultiIndex):
        return
    tickers = raw.columns.get_level_values(1).unique()
    for t in tickers:
        t = str(t)
        try:
            sub = raw.xs(t, axis=1, level=1, drop_level=True)
        except KeyError:
            continue
        sub = sub.dropna(how="all")
        if not sub.empty:
            sub.to_csv(ohlcv_dir / f"{t}.csv")


def _try_frame(
    ticker: str, label: str, fund_dir: Path, getter: Callable[[], pd.DataFrame | None]
) -> None:
    try:
        frame = getter()
    except Exception as exc:  # noqa: BLE001 — yfinance raises varied errors per call
        print(f"{ticker} {label}: skip ({exc})")
        return
    if frame is None or getattr(frame, "empty", True):
        return
    try:
        frame.to_csv(fund_dir / f"{ticker}_{label}.csv")
    except OSError as exc:
        print(f"{ticker} {label}: write failed ({exc})")


def _save_ticker_fundamentals(ticker: str, fund_dir: Path) -> None:
    tk = yf.Ticker(ticker)

    _try_frame(ticker, "income_stmt_annual", fund_dir, lambda: tk.financials)
    _try_frame(ticker, "income_stmt_quarterly", fund_dir, lambda: tk.quarterly_financials)
    _try_frame(ticker, "balance_sheet_annual", fund_dir, lambda: tk.balance_sheet)
    _try_frame(ticker, "balance_sheet_quarterly", fund_dir, lambda: tk.quarterly_balance_sheet)
    _try_frame(ticker, "cashflow_annual", fund_dir, lambda: tk.cashflow)
    _try_frame(ticker, "cashflow_quarterly", fund_dir, lambda: tk.quarterly_cashflow)

    try:
        info = getattr(tk, "info", None) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"{ticker} info: skip ({exc})")
        info = {}
    if info:
        try:
            path = fund_dir / f"{ticker}_info.json"
            path.write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
        except OSError as exc:
            print(f"{ticker} info: write failed ({exc})")

    try:
        div = tk.dividends
    except Exception as exc:  # noqa: BLE001
        print(f"{ticker} dividends: skip ({exc})")
    else:
        if div is not None and len(div) > 0:
            try:
                div.to_csv(fund_dir / f"{ticker}_dividends.csv", header=["dividend"])
            except OSError as exc:
                print(f"{ticker} dividends: write failed ({exc})")

    try:
        spl = tk.splits
    except Exception as exc:  # noqa: BLE001
        print(f"{ticker} splits: skip ({exc})")
    else:
        if spl is not None and len(spl) > 0:
            try:
                spl.to_csv(fund_dir / f"{ticker}_splits.csv", header=["split"])
            except OSError as exc:
                print(f"{ticker} splits: write failed ({exc})")


def download_market_data() -> None:
    data_dir = ROOT / "data"
    ohlcv_dir = data_dir / "ohlcv"
    fund_dir = data_dir / "fundamentals"
    data_dir.mkdir(exist_ok=True)
    ohlcv_dir.mkdir(exist_ok=True)
    fund_dir.mkdir(exist_ok=True)

    raw = yf.download(
        TICKERS,
        start=START,
        end=END,
        auto_adjust=True,
        group_by="column",
        progress=False,
        threads=True,
    )

    if raw.empty:
        print("No OHLCV data returned (network, tickers, or date range).")
        return

    if isinstance(raw.columns, pd.MultiIndex) and "Close" in raw.columns.get_level_values(0):
        # Keep exchange-specific non-trading days as NaN; only drop rows that are fully empty.
        prices = raw["Close"].dropna(how="all")
        prices.to_csv(data_dir / "prices.csv")
        _write_ohlcv_per_ticker(raw, ohlcv_dir)
    else:
        # Single-ticker download uses a flat column layout.
        if len(TICKERS) == 1 and "Close" in raw.columns:
            raw[["Close"]].rename(columns={"Close": TICKERS[0]}).to_csv(data_dir / "prices.csv")
            raw.to_csv(ohlcv_dir / f"{TICKERS[0]}.csv")
        else:
            print("Unexpected yfinance layout; inspect `raw.columns`.")

    for t in TICKERS:
        _save_ticker_fundamentals(t, fund_dir)

    if not raw.empty and isinstance(raw.columns, pd.MultiIndex):
        print(raw["Close"].dropna(how="all").tail())


if __name__ == "__main__":
    download_market_data()
