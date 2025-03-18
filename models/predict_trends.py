import os
import pickle
import pandas as pd
from tabulate import tabulate
from utils.top_stocks import TOP_STOCKS

MODEL_DIR = "models/"
REAL_TIME_DIR = "data/real_time"

def load_model(ticker):
    """Load a trained model for a stock."""
    model_path = f"{MODEL_DIR}/{ticker}.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            return pickle.load(f)
    return None

def predict_stock_trend(ticker):
    """Predict stock trend using the trained model."""
    model = load_model(ticker)
    if model is None:
        return None

    # Fetch last known data point
    file_path = f"{REAL_TIME_DIR}/{ticker}.parquet"
    if not os.path.exists(file_path):
        return None

    df = pd.read_parquet(file_path)
    if df.empty or "Close" not in df:
        return None

    last_time_index = [[len(df)]]
    predicted_price = model.predict(last_time_index)[0]
    last_close_price = df["Close"].iloc[-1]
    
    trend = "⬆️ UP" if predicted_price > last_close_price else "⬇️ DOWN"
    return ticker, last_close_price, predicted_price, trend

def predict_all_trends():
    """Predict trends for all stocks and display in a table."""
    results = []
    for ticker in TOP_STOCKS:
        prediction = predict_stock_trend(ticker)
        if prediction:
            results.append(prediction)

    headers = ["Ticker", "Last Price", "Predicted Price", "Trend"]
    print(tabulate(results, headers=headers, tablefmt="fancy_grid"))

def get_recommended_trades():
    """Find stocks that have a strong buy signal."""
    recommendations = []
    for ticker in TOP_STOCKS:
        prediction = predict_stock_trend(ticker)
        if prediction and prediction[3] == "⬆️ UP":
            recommendations.append((ticker, prediction[2]))  # Predicted price

    return recommendations