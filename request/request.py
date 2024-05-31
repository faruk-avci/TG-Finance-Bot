import requests
import threading
import time
class Request:
    def __init__(self, token):
        self.token = token
        self.indice_id = 1269
        self.stock_symbols = []
        self.stock_prices = {}
        self.stock_names_url = "https://fcsapi.com/api-v3/stock/list"
        self.stock_prices_url = "https://fcsapi.com/api-v3/stock/latest"
   
    def get_stock_names(self):
        response = requests.get(f"{self.stock_names_url}?indices_id={self.indice_id}&access_key={self.token}")
        print(f"{self.stock_names_url}?indice_id={self.indice_id}&apikey={self.token}")
        print()
        if response.status_code == 200:
            data = response.json()
            for stock in data["response"]:
                self.stock_symbols.append(stock["short_name"])
        else:
            print("Error fetching stock names")
        
    def get_stock_prices(self):
        if self.stock_symbols:
            response = requests.get(f"{self.stock_prices_url}?symbol={','.join(self.stock_symbols)}&access_key={self.token}")
            print(",".join(self.stock_symbols))
            if response.status_code == 200:
                data = response.json()
                if data["code"] == 200:
                    print(data)
                    for stock in data["response"]:
                        self.stock_prices[stock["s"]] = stock["c"]
                        print(stock)
            else:
                print("Error fetching stock prices")
            print(self.stock_prices)
            return self.stock_prices
        else:
            print("No stock symbols to fetch prices for")

    def start_periodic_fetch(self):
        self.get_stock_names()
        threading.Thread(target=self._periodic_fetch, daemon=True).start()

    def _periodic_fetch(self):
        while True:
            self.get_stock_prices()
            time.sleep(300)