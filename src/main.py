from data_collector import get_stock_data
from strategy_engine import should_buy
from portfolio import Portfolio

def main():
    ticker = "AAPL"
    df = get_stock_data(ticker)
    port = Portfolio()

    if should_buy(df):
        price = df["Close"].iloc[-1]
        port.buy(ticker, price)

    port.report()

if __name__ == "__main__":
    main()
