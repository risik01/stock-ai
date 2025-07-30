class Portfolio:
    def __init__(self, initial=10.0):
        self.cash = initial
        self.holdings = {}
        self.history = []

    def buy(self, ticker, price):
        if self.cash >= price:
            qty = self.cash // price
            self.cash -= qty * price
            self.holdings[ticker] = self.holdings.get(ticker, 0) + qty
            self.history.append(f"BUY {qty}x {ticker} at {price:.2f}")

    def report(self):
        print("\n--- Portfolio Report ---")
        print(f"Cash: €{self.cash:.2f}")
        print("Holdings:", self.holdings)
        print("History:")
        for h in self.history:
            print(" ", h)
