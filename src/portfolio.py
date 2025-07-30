import numpy as np

class Portfolio:
    """Classe per gestire un portafoglio di investimenti"""
    
    def __init__(self, initial_cash=10000):
        """
        Inizializza il portafoglio
        
        Args:
            initial_cash (float): Denaro iniziale disponibile
        """
        self.cash = initial_cash
        self.positions = {}  # {ticker: {"shares": num, "avg_price": price}}
        self.transactions = []  # Lista delle transazioni
    
    def buy(self, ticker, price, shares=1):
        """
        Compra azioni
        
        Args:
            ticker (str): Simbolo del titolo
            price (float): Prezzo per azione
            shares (int): Numero di azioni da comprare
        """
        total_cost = price * shares
        
        if total_cost > self.cash:
            print(f"Fondi insufficienti per comprare {shares} azioni di {ticker}")
            return False
        
        self.cash -= total_cost
        
        if ticker in self.positions:
            # Aggiorna posizione esistente
            old_shares = self.positions[ticker]["shares"]
            old_avg_price = self.positions[ticker]["avg_price"]
            
            new_shares = old_shares + shares
            new_avg_price = ((old_shares * old_avg_price) + (shares * price)) / new_shares
            
            self.positions[ticker] = {
                "shares": new_shares,
                "avg_price": new_avg_price
            }
        else:
            # Nuova posizione
            self.positions[ticker] = {
                "shares": shares,
                "avg_price": price
            }
        
        self.transactions.append({
            "type": "BUY",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "total": total_cost
        })
        
        print(f"✅ Acquistato {shares} azioni di {ticker} a ${price:.2f} (Totale: ${total_cost:.2f})")
        return True
    
    def sell(self, ticker, price, shares=None):
        """
        Vendi azioni
        
        Args:
            ticker (str): Simbolo del titolo
            price (float): Prezzo per azione
            shares (int): Numero di azioni da vendere (None = tutte)
        """
        if ticker not in self.positions:
            print(f"Non possiedi azioni di {ticker}")
            return False
        
        available_shares = self.positions[ticker]["shares"]
        if shares is None:
            shares = available_shares
        
        if shares > available_shares:
            print(f"Non puoi vendere {shares} azioni di {ticker}, ne possiedi solo {available_shares}")
            return False
        
        total_value = price * shares
        self.cash += total_value
        
        # Aggiorna posizione
        self.positions[ticker]["shares"] -= shares
        if self.positions[ticker]["shares"] == 0:
            del self.positions[ticker]
        
        self.transactions.append({
            "type": "SELL",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "total": total_value
        })
        
        print(f"✅ Venduto {shares} azioni di {ticker} a ${price:.2f} (Totale: ${total_value:.2f})")
        return True
    
    def get_portfolio_value(self, current_prices=None):
        """
        Calcola il valore totale del portafoglio
        
        Args:
            current_prices (dict): Prezzi attuali {ticker: price}
        
        Returns:
            float: Valore totale del portafoglio
        """
        total_value = self.cash
        
        for ticker, position in self.positions.items():
            if current_prices and ticker in current_prices:
                market_value = position["shares"] * current_prices[ticker]
            else:
                market_value = position["shares"] * position["avg_price"]
            total_value += market_value
        
        return total_value
    
    def get_performance_metrics(self, initial_value=10000):
        """
        Calcola metriche di performance del portafoglio
        
        Args:
            initial_value: Valore iniziale del portafoglio
            
        Returns:
            dict: Metriche di performance
        """
        current_value = self.get_portfolio_value()
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Calcola profitti/perdite per transazione
        profits = []
        for i, transaction in enumerate(self.transactions):
            if transaction["type"] == "SELL":
                # Trova la transazione di acquisto corrispondente
                ticker = transaction["ticker"]
                sell_price = transaction["price"]
                
                # Cerca l'ultimo acquisto per questo ticker
                buy_price = None
                for j in range(i-1, -1, -1):
                    if (self.transactions[j]["type"] == "BUY" and 
                        self.transactions[j]["ticker"] == ticker):
                        buy_price = self.transactions[j]["price"]
                        break
                
                if buy_price:
                    profit_pct = ((sell_price - buy_price) / buy_price) * 100
                    profits.append(profit_pct)
        
        win_rate = (sum(1 for p in profits if p > 0) / len(profits) * 100) if profits else 0
        avg_profit = np.mean(profits) if profits else 0
        
        return {
            "total_return": total_return,
            "current_value": current_value,
            "win_rate": win_rate,
            "avg_profit_per_trade": avg_profit,
            "total_trades": len(self.transactions),
            "cash_remaining": self.cash
        }

    def report(self, show_performance=True):
        """Stampa un report del portafoglio con metriche di performance"""
        print("=== REPORT PORTAFOGLIO ===")
        print(f"Liquidità disponibile: ${self.cash:.2f}")
        print()
        
        if self.positions:
            print("Posizioni aperte:")
            for ticker, position in self.positions.items():
                shares = position["shares"]
                avg_price = position["avg_price"]
                market_value = shares * avg_price
                print(f"  {ticker}: {shares} azioni @ ${avg_price:.2f} = ${market_value:.2f}")
        else:
            print("Nessuna posizione aperta")
        
        print()
        total_value = self.get_portfolio_value()
        print(f"Valore totale portafoglio: ${total_value:.2f}")
        
        if self.transactions:
            print(f"Transazioni effettuate: {len(self.transactions)}")
        
        if show_performance:
            metrics = self.get_performance_metrics()
            print(f"\n=== METRICHE PERFORMANCE ===")
            print(f"Rendimento totale: {metrics['total_return']:.2f}%")
            print(f"Win rate: {metrics['win_rate']:.1f}%")
            print(f"Profitto medio per trade: {metrics['avg_profit_per_trade']:.2f}%")
