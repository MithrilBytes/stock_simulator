# Stock Market Simulator  

This is a Python-based stock market simulator that allows users to **trade stocks**, **track profit/loss**, **predict stock trends**, and **simulate market conditions** using real-time or historical data. The project includes **machine learning models** for price prediction and a **fully interactive CLI** for trading.

---

## Installation and Setup  

### **1. Create and Activate a Virtual Environment**  
It is recommended to run the project inside a **Python virtual environment** to manage dependencies.

#### **MacOS/Linux**  
```sh
python3 -m venv venv
source venv/bin/activate
```

#### **Windows**  
```sh
python -m venv venv
venv\Scripts\activate
```

### **2. Install Dependencies**  
Once the virtual environment is activated, install the required Python packages:  

```sh
pip install -r requirements.txt
```

---

## Running the Project  

### **Start the Stock Simulator**
Run the project using the following command:  

```sh
python -m main
```

This will:  
1. **Initialize the database** (if not already set up).  
2. **Fetch real-time stock data** for the top 200 stocks.  
3. **Train machine learning models** for trend predictions.  
4. **Launch the interactive CLI** for trading.  

---

## Usage Guide  

After launching the CLI, you will see a menu with the following options:  

```
1. View Portfolio  
2. Buy Stock  
3. Sell Stock  
4. Predict Stock Trends  
5. Auto-Trade Recommended Stocks  
6. Advance Simulated Time  
7. View Profit & Loss  
8. View a Specific Stock  
9. Start Over (Wipe Everything)  
10. Exit  
```

### **Buying a Stock**  
1. Select **Option 2** from the menu.  
2. Enter a valid **stock ticker symbol** (e.g., `AAPL`).  
3. Enter the **number of shares** to buy.  
4. Enter the **purchase price**, which must be **equal to or above the current market price**.  
5. The stock will be added to your portfolio.

### **Selling a Stock**  
1. Select **Option 3** from the menu.  
2. Enter the **stock ticker symbol** you want to sell.  
3. Enter the **number of shares** to sell.  
4. The stock will be sold at the **latest market price**, and your balance will be updated.

### **Predicting Stock Trends**  
1. Select **Option 4** to generate **ML-based stock trend predictions**.  
2. The system will display predicted trends for multiple stocks.  

### **Auto-Trading Based on ML Predictions**  
1. Select **Option 5** to automatically trade stocks that the machine learning model predicts will rise.  
2. The system will execute **buy orders** based on strong buy signals.  

### **Simulating Time Progression**  
1. Select **Option 6** to **advance simulated time**.  
2. This will update stock prices and **execute any pending sell triggers** based on profit/loss conditions.

### **Viewing Profit & Loss**  
1. Select **Option 7** to see your **account balance, realized profits, and unrealized gains**.  

### **Viewing a Specific Stock**  
1. Select **Option 8** to check **latest market details** for a stock.  
2. Enter a **valid stock ticker**, and the system will display **closing price and volume**.  

### **Resetting the Simulator**  
1. Select **Option 9** to **wipe all data** and start fresh.  
2. The system will ask for **two confirmations** before proceeding.  
3. This action **deletes all trades, stock data, and resets the balance**.  

---

## Notes  
- Stock prices are simulated using real-time or historical data.  
- The trading system enforces **market price validation** for realistic simulations.  
- Machine learning models are retrained automatically after fetching new stock data.  

---

## Troubleshooting  

### **1. Virtual Environment Issues**  
If the project does not recognize installed packages, ensure the virtual environment is activated:  
```sh
source venv/bin/activate  # MacOS/Linux  
venv\Scripts\activate     # Windows  
```

### **2. Module Import Errors**  
If you get `ModuleNotFoundError` for `models.train_models` or `models.predict_trends`, ensure the `models/` directory contains `__init__.py`:  
```sh
touch models/__init__.py
```

### **3. Resetting the Database Manually**  
If the database is corrupted or outdated, delete it manually and rerun the project:  
```sh
rm data/portfolio.db  # MacOS/Linux  
del data\portfolio.db # Windows  
python -m main
```

---

## Future Improvements  
- Implement **dividend tracking** for stocks.  
- Add **chart visualizations** for portfolio performance.  
- Expand **backtesting features** for trade strategy evaluation.  

---

## License  
This project is open-source and available under the **MIT License**.  
