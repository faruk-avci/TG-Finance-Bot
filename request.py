import requests
import yfinance as yf

class Request:
    def __init__(self, token):
        self.token = token
    
    def get_price(self, symbol):
        if not symbol.endswith(".IS"):
            symbol += ".IS" 
        
        stock = yf.Ticker(symbol)
        quote = stock.history(period="1d")
        
        if not quote.empty:
            return {
            "symbol": stock.ticker,
            "price": float(quote['Close'].iloc[0]),
            "open": float(quote['Open'].iloc[0]),
            "high": float(quote['High'].iloc[0]),
            "low": float(quote['Low'].iloc[0]),
            "volume": int(quote['Volume'].iloc[0]),
            "date": quote.index[0].strftime("%Y-%m-%d")
        }
        else:
            return {"error": "No data found for ticker"}