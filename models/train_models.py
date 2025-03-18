import os
import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
from concurrent.futures import ThreadPoolExecutor
from utils.top_stocks import TOP_STOCKS

MODEL_DIR = "models/"
REAL_TIME_DIR = "data/real_time"

def train_model(ticker):
    """Train and save a trend prediction model for a given stock."""
    file_path = f"{REAL_TIME_DIR}/{ticker}.parquet"
    model_path = f"{MODEL_DIR}/{ticker}.pkl"

    if not os.path.exists(file_path):
        return

    df = pd.read_parquet(file_path)
    df["time_index"] = range(len(df))
    X = df["time_index"].values.reshape(-1, 1)
    y = df["Close"].values

    model = LinearRegression()
    model.fit(X, y)

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

def train_all_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    with ThreadPoolExecutor() as executor:
        executor.map(train_model, TOP_STOCKS)

if __name__ == "__main__":
    train_all_models()