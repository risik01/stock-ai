import yfinance as yf
import pandas as pd

def get_stock_data(ticker="AAPL", period="1mo", interval="1d"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    return df
