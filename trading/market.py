import sqlite3
import os
import pandas as pd
import random
from trading.database import DB_FILE
from utils.top_stocks import TOP_STOCKS

SIMULATION_STEP = 1  # Number of time intervals to advance (e.g., 1 hour/day)

def execute_trade(ticker, shares, price):
    """Executes a market order, updates portfolio and balance."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check current cash balance
    cursor.execute("SELECT cash FROM balance")
    cash = cursor.fetchone()[0]

    total_cost = shares * price
    if total_cost > cash:
        print("❌ Insufficient funds!")
        conn.close()
        return

    # Deduct the cash from balance
    cursor.execute("UPDATE balance SET cash = cash - ?", (total_cost,))
    
    # Insert trade into the portfolio
    cursor.execute("INSERT INTO trades (ticker, shares, buy_price, status) VALUES (?, ?, ?, 'OPEN')",
                   (ticker, shares, price))

    conn.commit()
    conn.close()
    print(f"✅ Bought {shares} shares of {ticker} at ${price:.2f}. New Balance: ${cash - total_cost:.2f}")

def advance_simulated_time():
    """Move simulation forward, update stock prices, and check P&L."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id, ticker, shares, buy_price FROM trades WHERE status='OPEN'")
    trades = cursor.fetchall()

    for trade in trades:
        trade_id, ticker, shares, buy_price = trade

        # Fetch next simulated price
        next_price = get_next_price(ticker)
        if not next_price:
            continue

        # Sell if price increased by 5% or decreased by 5%
        profit_margin = (next_price - buy_price) / buy_price
        if profit_margin >= 0.05:  # Take profit at +5%
            sell_stock(trade_id, shares, next_price, "Profit Target Hit")
        elif profit_margin <= -0.05:  # Stop-loss at -5%
            sell_stock(trade_id, shares, next_price, "Stop-Loss Triggered")

    conn.close()

def sell_stock(trade_id, shares, sell_price, reason):
    """Sell stock, update portfolio and cash balance."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Fetch original buy price
    cursor.execute("SELECT buy_price FROM trades WHERE id=?", (trade_id,))
    buy_price = cursor.fetchone()[0]

    profit_loss = (sell_price - buy_price) * shares

    # Update cash balance
    cursor.execute("UPDATE balance SET cash = cash + ?", (sell_price * shares,))

    # Close trade
    cursor.execute("UPDATE trades SET sell_price=?, status='CLOSED' WHERE id=?",
                   (sell_price, trade_id))

    conn.commit()
    conn.close()
    print(f"💰 Sold {shares} shares at ${sell_price:.2f} ({reason}) | P&L: ${profit_loss:.2f}")

def get_next_price(ticker):
    """Fetch the next price in historical data."""
    file_path = f"data/real_time/{ticker}.parquet"
    if not os.path.exists(file_path):
        return None

    df = pd.read_parquet(file_path)

    if len(df) > SIMULATION_STEP:
        return df["Close"].iloc[random.randint(0, len(df) - 1)]
    
    return None