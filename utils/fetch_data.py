import yfinance as yf
import pandas as pd
import os
from utils.top_stocks import TOP_STOCKS

REAL_TIME_DIR = "data/real_time"

def fetch_real_time_data(period="7d", interval="1h"):
    """Fetch last week's stock data for top stocks."""
    os.makedirs(REAL_TIME_DIR, exist_ok=True)

    for ticker in TOP_STOCKS:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if not df.empty:
            df.to_parquet(f"{REAL_TIME_DIR}/{ticker}.parquet", engine="fastparquet")

    print("✅ Real-time stock data updated!")

if __name__ == "__main__":
    fetch_real_time_data()