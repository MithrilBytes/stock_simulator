import sqlite3
import os

DB_FILE = "data/portfolio.db"

def setup_database():
    """Ensures the necessary database tables exist before running the simulator."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table for trades
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            shares INTEGER,
            buy_price REAL,
            sell_price REAL DEFAULT NULL,
            status TEXT DEFAULT 'OPEN'
        )
    """)

    # Table for balance tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cash REAL DEFAULT 10000  -- Starting with $10,000
        )
    """)

    # Ensure a balance entry exists
    cursor.execute("SELECT * FROM balance")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO balance (cash) VALUES (10000)")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()