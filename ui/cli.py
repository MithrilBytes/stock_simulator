from rich.console import Console
from rich.table import Table
import sqlite3
import os
import shutil
import pandas as pd
from trading.database import DB_FILE, setup_database
from models.predict_trends import predict_all_trends, get_recommended_trades
from trading.market import execute_trade, advance_simulated_time

console = Console()

DATA_DIR = "data/"
MODELS_DIR = "models/"

def display_menu():
    console.print("[bold cyan]Stock Simulator[/bold cyan]", justify="center")
    console.print("1. View Portfolio")
    console.print("2. Buy Stock")
    console.print("3. Sell Stock")  # ✅ NEW: Sell option
    console.print("4. Predict Stock Trends")
    console.print("5. Auto-Trade Recommended Stocks")
    console.print("6. Advance Simulated Time")
    console.print("7. View Profit & Loss")
    console.print("8. View a Specific Stock")
    console.print("9. Start Over (Wipe Everything)")
    console.print("10. Exit")
    return input("Choose an option: ")

def buy_stock():
    """Handles manual stock purchases, ensuring users do not buy below market price."""
    ticker = input("Enter Stock Ticker (e.g., AAPL): ").upper()
    
    # Get the latest market price
    current_price = get_current_price(ticker)
    
    if current_price is None:
        console.print("[bold red]Stock data not available![/bold red]")
        return

    console.print(f"📈 Current Market Price of {ticker}: ${current_price:.2f}")

    while True:
        try:
            shares = int(input("Enter Number of Shares: "))
            price = float(input("Enter Purchase Price: "))

            if price < current_price:
                console.print(f"[bold red]❌ Cannot buy below the current market price (${current_price:.2f})![/bold red]")
                continue  # Ask for input again

            execute_trade(ticker, shares, price)
            console.print(f"✅ Bought {shares} shares of {ticker} at ${price:.2f}")
            break

        except ValueError:
            console.print("[bold red]Invalid input! Please enter a valid number.[/bold red]")

def sell_stock():
    """Allows the user to sell shares of a stock they own."""
    ticker = input("Enter Stock Ticker to Sell (e.g., AAPL): ").upper()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if user owns the stock
    cursor.execute("SELECT SUM(shares) FROM trades WHERE ticker=? AND status='OPEN'", (ticker,))
    owned_shares = cursor.fetchone()[0]

    if owned_shares is None or owned_shares == 0:
        console.print("[bold red]❌ You do not own any shares of this stock.[/bold red]")
        conn.close()
        return

    console.print(f"📊 You own {owned_shares} shares of {ticker}.")

    try:
        shares_to_sell = int(input("Enter Number of Shares to Sell: "))
        if shares_to_sell <= 0 or shares_to_sell > owned_shares:
            console.print("[bold red]❌ Invalid number of shares.[/bold red]")
            conn.close()
            return
    except ValueError:
        console.print("[bold red]❌ Please enter a valid number.[/bold red]")
        conn.close()
        return

    # Get latest market price
    current_price = get_current_price(ticker)
    if current_price is None:
        console.print("[bold red]❌ Market data unavailable! Cannot sell.[/bold red]")
        conn.close()
        return

    # Calculate profit/loss
    cursor.execute("SELECT id, buy_price, shares FROM trades WHERE ticker=? AND status='OPEN' ORDER BY id ASC", (ticker,))
    remaining_shares = shares_to_sell
    total_profit_loss = 0

    while remaining_shares > 0:
        row = cursor.fetchone()
        if not row:
            break

        trade_id, buy_price, trade_shares = row
        sell_shares = min(trade_shares, remaining_shares)

        # Profit/Loss calculation
        profit_loss = (current_price - buy_price) * sell_shares
        total_profit_loss += profit_loss

        # Update trade record
        if trade_shares == sell_shares:
            cursor.execute("UPDATE trades SET sell_price=?, status='CLOSED' WHERE id=?", (current_price, trade_id))
        else:
            cursor.execute("UPDATE trades SET shares=? WHERE id=?", (trade_shares - sell_shares, trade_id))

        remaining_shares -= sell_shares

    # Update user balance
    cursor.execute("UPDATE balance SET cash = cash + ?", (shares_to_sell * current_price,))

    conn.commit()
    conn.close()

    console.print(f"\n✅ Sold {shares_to_sell} shares of {ticker} at ${current_price:.2f}")
    console.print(f"💰 [bold green]Profit/Loss from this sale: ${total_profit_loss:.2f}[/bold green]")

def view_stock():
    """Displays details of a specific stock based on user input."""
    ticker = input("Enter Stock Ticker to View (e.g., AAPL): ").upper()
    
    # Fetch current market price
    current_price = get_current_price(ticker)

    if current_price is None:
        console.print("[bold red]Stock data not available![/bold red]")
        return

    # Load stock data
    file_path = f"data/real_time/{ticker}.parquet"
    df = pd.read_parquet(file_path)

    last_row = df.iloc[-1]
    close_price = last_row["Close"]
    volume = last_row["Volume"]

    console.print("\n📊 [bold cyan]Stock Details:[/bold cyan]\n")
    console.print(f"🔹 [bold yellow]Ticker:[/bold yellow] {ticker}")
    console.print(f"🔹 [bold green]Last Close Price:[/bold green] ${close_price:.2f}")
    console.print(f"🔹 [bold blue]Trading Volume:[/bold blue] {volume}")

def start_over():
    """Wipes the database, stored stock data, and trained models while preserving necessary files."""
    
    console.print("\n⚠️ [bold red]WARNING: This will DELETE all data and reset everything![/bold red]")
    confirm = input("Are you sure you want to reset everything? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        console.print("[bold yellow]Operation canceled.[/bold yellow]\n")
        return

    confirm_final = input("❗ Type 'RESET' to confirm: ").strip().upper()
    
    if confirm_final != "RESET":
        console.print("[bold yellow]Operation canceled. No data was deleted.[/bold yellow]\n")
        return

    # Remove database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        console.print("🗑️ [bold red]Database wiped![/bold red]")

    # Delete stock data
    for folder in ["data/real_time", "data/historical"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder)  # Recreate empty directory
            console.print(f"🗑️ [bold red]Deleted stock data: {folder}[/bold red]")

    # Remove only trained model files (.pkl), but keep train_models.py & predict_trends.py
    if os.path.exists("models"):
        for file in os.listdir("models"):
            if file.endswith(".pkl"):  # Only delete trained models
                os.remove(os.path.join("models", file))
                console.print(f"🗑️ [bold red]Deleted model: {file}[/bold red]")

    # Ensure __init__.py exists to keep the module functional
    open("models/__init__.py", "a").close()

    # Reinitialize database
    setup_database()
    console.print("\n✅ [bold green]Everything has been reset! You are starting fresh.[/bold green]\n")

def view_profit_loss():
    """Displays profit and loss tracking."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get cash balance
    cursor.execute("SELECT cash FROM balance")
    cash = cursor.fetchone()[0]

    # Get realized P&L
    cursor.execute("SELECT SUM((sell_price - buy_price) * shares) FROM trades WHERE status='CLOSED'")
    realized_pl = cursor.fetchone()[0] or 0

    console.print("\n💰 [bold cyan]Account Summary[/bold cyan]\n")
    console.print(f"💵 Cash Balance: [bold green]${cash:.2f}[/bold green]")
    console.print(f"📊 Realized P&L: [bold yellow]${realized_pl:.2f}[/bold yellow]\n")

    conn.close()

def predict_trends():
    """Calls the function to predict stock trends."""
    console.print("\n📊 [bold yellow]Stock Trend Predictions:[/bold yellow]\n")
    predict_all_trends()

def auto_trade():
    """Automatically buys stocks based on ML predictions."""
    recommended_trades = get_recommended_trades()
    if not recommended_trades:
        console.print("[bold red]No strong buy signals at this time.[/bold red]")
        return

    for ticker, price in recommended_trades:
        execute_trade(ticker, shares=1, price=price)
        console.print(f"🚀 Auto-bought 1 share of {ticker} at ${price:.2f}")

def get_current_price(ticker):
    """Fetch the latest price from stored data."""
    file_path = f"data/real_time/{ticker}.parquet"
    if not os.path.exists(file_path):
        return None

    df = pd.read_parquet(file_path)
    return df["Close"].iloc[-1] if not df.empty else None

def view_portfolio():
    """Displays the user's portfolio."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades WHERE status='OPEN'")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        console.print("[bold red]No active trades.[/bold red]")
        return

    table = Table(title="Portfolio")
    table.add_column("ID")
    table.add_column("Ticker")
    table.add_column("Shares")
    table.add_column("Buy Price")

    for row in rows:
        table.add_row(str(row[0]), row[1], str(row[2]), f"${row[3]:.2f}")

    console.print(table)

if __name__ == "__main__":
    setup_database()
    
    while True:
        choice = display_menu()
        if choice == "1":
            view_portfolio()
        elif choice == "2":
            buy_stock()
        elif choice == "3":
            sell_stock()
        elif choice == "4":
            predict_trends()
        elif choice == "5":
            auto_trade()
        elif choice == "6":
            advance_simulated_time()
        elif choice == "7":
            view_profit_loss()
        elif choice == "8":
            view_stock()
        elif choice == "9":
            start_over()
        elif choice == "10":
            break