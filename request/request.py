import requests
import yfinance as yf
import threading
import time
import logging
from datetime import datetime
logging.basicConfig(filename="request.log", level=logging.DEBUG,filemode="a")

class Request:
    def __init__(self, token):
        self.token = token
        self.indice_id = 1269
        self.stock_symbols = []
        self.stock_prices = {}
        self.stock_names_url = "https://fcsapi.com/api-v3/stock/list"
        self.stock_prices_url = "https://fcsapi.com/api-v3/stock/latest"
    

    def get_price(self, symbol):
        if not symbol.endswith(".IS"):
            symbol += ".IS" 
        
        stock = yf.Ticker(symbol)
        quote = stock.history(period="1d")
        
        if not quote.empty:
            return {
            "symbol": symbol,
            "price": float(quote['Close'].iloc[0]),
            "open": float(quote['Open'].iloc[0]),
            "high": float(quote['High'].iloc[0]),
            "low": float(quote['Low'].iloc[0]),
            "volume": int(quote['Volume'].iloc[0]),
            "date": quote.index[0].strftime("%Y-%m-%d")
        }
        else:
            return {"error": "No data found for ticker"}

    def get_stock_dict(self):
        return self.stock_prices

    def get_stock_names(self):
        response = requests.get(f"{self.stock_names_url}?indices_id={self.indice_id}&access_key={self.token}")
        print(f"{self.stock_names_url}?indices_id={self.indice_id}&access_key={self.token}")
        print()
        if response.status_code == 200:
            data = response.json()
            print(data)
            for stock in data["response"]:
                self.stock_symbols.append(stock["short_name"])
        else:
            print("Error fetching stock names")
        
    def get_stock_prices(self):
        if self.stock_symbols:
            response = requests.get(f"{self.stock_prices_url}?symbol={','.join(self.stock_symbols)}&access_key={self.token}")
            logging.info(f"{self.stock_prices_url}?symbol={','.join(self.stock_symbols)}&access_key={self.token}")
            print(response)
            if response.status_code == 200:
                data = response.json()
                print(data)
                if data["code"] == 200:
                    logging.info("Stock prices fetched successfully at {}".format(time.ctime()))
                    print(data)
                    for stock in data["response"]:
                        self.stock_prices[stock["s"]] = stock["c"]
                        print(stock)
            else:
                print("Error fetching stock prices")
                logging.error("Error fetching stock prices at {}".format(time.ctime())) 
            print(self.stock_prices)
            return self.stock_prices
        else:
            print("No stock symbols to fetch prices for")

    def start_periodic_fetch(self):
        self.get_stock_names()
        print("get_stock_name çalıştı")
        threading.Thread(target=self._periodic_fetch, daemon=True).start()

    def _periodic_fetch(self):
         while True:
            if not self.stock_prices:
                self.get_stock_prices()
            print(self.stock_prices)
            now = datetime.now()
            if now.weekday() < 5 and 10 <= now.hour < 23:
                logging.info("Fetching stock prices at {}".format(time.ctime()))
                self.get_stock_prices()
            time.sleep(30)  # Check every 5 minutes