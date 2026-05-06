import yfinance as yf
from pathlib import Path

TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]

def download_market_data():
    Path("data").mkdir(exist_ok=True)

    data = yf.download(
        TICKERS,
        start="2022-01-01",
        end="2026-01-01",
        auto_adjust=True
    )

    prices = data["Close"].dropna()

    prices.to_csv("data/prices.csv")

    print(prices.tail())

if __name__ == "__main__":
    download_market_data()