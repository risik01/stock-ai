import time
import threading
import signal
import sys
import os
from datetime import datetime, timedelta
from data_collector import get_stock_data
from strategy_engine import should_buy, should_sell
from portfolio import Portfolio
from rl_agent import TradingAgent
import numpy as np
import pickle
from config_manager import TradingConfig

class AggressiveTrader:
    """Bot di trading aggressivo con monitoraggio continuo"""
    
    def __init__(self, initial_cash=10000, aggressiveness_level=None):
        """
        Inizializza il trader aggressivo
        
        Args:
            initial_cash (float): Capitale iniziale (solo per nuovo portfolio)
            aggressiveness_level (int): Livello di aggressività 1-10 (opzionale)
        """
        # Carica configurazione
        self.config = TradingConfig(aggressiveness=aggressiveness_level)
        self.config.print_current_config()
        
        # Parametri da configurazione
        self.check_interval = self.config.get('check_interval_seconds')
        self.max_positions = self.config.get('max_positions')
        self.risk_per_trade = self.config.get('risk_per_trade')
        self.stop_loss_pct = self.config.get('stop_loss_percentage')
        self.take_profit_pct = self.config.get('take_profit_percentage')
        
        # Parametri dati migliorati
        self.analysis_period = self.config.get('analysis_period')
        self.price_update_period = self.config.get('price_update_period')
        self.min_data_points = self.config.get('min_data_points')
        self.max_retries = self.config.get('max_retries')
        self.retry_delay = self.config.get('retry_delay_seconds')
        
        # Filtri di mercato
        self.aggressiveness_threshold = self.config.get('aggressiveness_threshold')
        self.max_volatility = self.config.get('max_volatility')
        self.min_stock_price = self.config.get('min_stock_price')
        
        self.is_running = False
        self.thread = None
        
        # Titoli da monitorare (aggiornati e verificati)
        self.watchlist = [
            # Tech Giants
            "AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX", 
            # Growth Stocks
            "TSLA", "AMD", "INTC", "CRM", "ORCL", "ADBE", 
            # Cloud & Software
            "NOW", "SNOW", "ZM", "DDOG", "NET", "OKTA", "TWLO",
            # Other High-Growth
            "SHOP", "PYPL", "ROKU", "CRWD", "MDB", "PLTR"
        ]
        
        # Blacklist per titoli problematici
        self.blacklist = ["SQ"]  # Ticker che causano problemi
        
        # Tracking
        self.cycle_count = 0
        self.last_prices = {}
        self.position_entry_prices = {}
        
        # File di controllo e log
        self.control_file = "/workspaces/stock-ai/data/trader_control.txt"
        self.log_file = "/workspaces/stock-ai/data/aggressive_trader.log"
        self.portfolio_file = "/workspaces/stock-ai/data/current_portfolio.pkl"
        
        # Crea directory se non esiste
        os.makedirs(os.path.dirname(self.control_file), exist_ok=True)
        
        # Inizializza RL agent
        self.rl_agent = TradingAgent()
        
        # Carica portfolio esistente o crea nuovo
        self.portfolio = self.load_portfolio(initial_cash)
        
        # Setup signal handlers - NON vendere mai automaticamente
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def log(self, message):
        """
        Logga un messaggio con timestamp
        
        Args:
            message (str): Messaggio da loggare
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        # Salva su file
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Errore nel log: {e}")
    
    def signal_handler(self, signum, frame):
        """Handler per segnali di terminazione - MANTIENE le posizioni"""
        self.log(f"🛑 Ricevuto segnale {signum} (Ctrl+C) - Fermata bot")
        self.log("💎 Le posizioni vengono MANTENUTE")
        self.stop()
    
    def check_control_file(self):
        """Controlla se esiste il file di controllo per fermare il bot"""
        if os.path.exists(self.control_file):
            try:
                with open(self.control_file, "r") as f:
                    command = f.read().strip().upper()
                if command == "CLOSEALLBOT":
                    return True
                # Mantieni compatibilità con il vecchio comando
                elif command == "CLOSEALL":
                    return True
            except Exception:
                pass
        return False
    
    def is_ticker_valid(self, ticker):
        """Controlla se un ticker è valido e non in blacklist"""
        if ticker in self.blacklist:
            return False
        return True
    
    def get_stock_data_safe(self, ticker, period=None, max_retries=None):
        """Ottiene dati stock con gestione errori migliorata"""
        if not self.is_ticker_valid(ticker):
            return None
        
        if period is None:
            period = self.price_update_period
        if max_retries is None:
            max_retries = self.max_retries
        
        for attempt in range(max_retries):
            try:
                df = get_stock_data(ticker, period=period)
                if len(df) >= self.min_data_points:
                    return df
                else:
                    if attempt == 0:  # Solo al primo tentativo
                        self.log(f"⚠️  {ticker}: Dati insufficienti ({len(df)} giorni), periodo: {period}")
                    
                    # Prova con un periodo più lungo
                    if period == "1d":
                        period = "2d"
                    elif period == "2d":
                        period = "5d"
                    elif period == "5d":
                        return None  # Impossibile ottenere dati
                    
                    continue
            except Exception as e:
                error_msg = str(e).lower()
                if "delisted" in error_msg or "no data found" in error_msg:
                    self.log(f"❌ {ticker}: Ticker probabilmente delistato - aggiunto alla blacklist")
                    self.blacklist.append(ticker)
                    return None
                elif attempt == max_retries - 1:  # Ultimo tentativo
                    self.log(f"❌ {ticker}: Errore persistente dopo {max_retries} tentativi: {e}")
                    return None
                else:
                    # Retry con delay
                    time.sleep(self.retry_delay)
        return None
    
    def load_portfolio(self, initial_cash):
        """Carica portfolio esistente o crea nuovo"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, "rb") as f:
                    portfolio = pickle.load(f)
                
                self.log(f"✅ Portfolio esistente caricato:")
                self.log(f"   Liquidità: ${portfolio.cash:.2f}")
                self.log(f"   Posizioni aperte: {len(portfolio.positions)}")
                self.log(f"   Trades totali: {len(portfolio.transactions)}")
                
                # REPORT DETTAGLIATO delle posizioni attuali con P&L aggiornato
                if portfolio.positions:
                    self.log("🔍 ANALISI POSIZIONI ESISTENTI:")
                    total_unrealized_pnl = 0
                    
                    for ticker, pos in portfolio.positions.items():
                        try:
                            # Ottieni prezzo attuale
                            df = get_stock_data(ticker, period="1d")
                            if len(df) > 0:
                                current_price = df["Close"].iloc[-1]
                                entry_price = pos['avg_price']
                                shares = pos['shares']
                                
                                # Calcola P&L
                                position_value = shares * current_price
                                cost_basis = shares * entry_price
                                unrealized_pnl = position_value - cost_basis
                                unrealized_pnl_pct = (unrealized_pnl / cost_basis) * 100
                                total_unrealized_pnl += unrealized_pnl
                                
                                # Status con emoji
                                if unrealized_pnl > 0:
                                    status = "🟢 PROFITTO"
                                elif unrealized_pnl < 0:
                                    status = "🔴 PERDITA"
                                else:
                                    status = "⚪ PARI"
                                
                                self.log(f"   {status} {ticker}:")
                                self.log(f"     Azioni: {shares}")
                                self.log(f"     Entry: ${entry_price:.2f} -> Attuale: ${current_price:.2f}")
                                self.log(f"     Valore: ${position_value:.2f} (costo: ${cost_basis:.2f})")
                                self.log(f"     P&L: ${unrealized_pnl:.2f} ({unrealized_pnl_pct:+.2f}%)")
                            else:
                                self.log(f"   ⚠️  {ticker}: Impossibile ottenere prezzo attuale")
                                self.log(f"     Azioni: {pos['shares']} @ ${pos['avg_price']:.2f}")
                        except Exception as e:
                            self.log(f"   ❌ Errore aggiornamento {ticker}: {e}")
                    
                    # Riepilogo totale
                    total_status = "🟢" if total_unrealized_pnl > 0 else "🔴" if total_unrealized_pnl < 0 else "⚪"
                    self.log(f"📊 RIEPILOGO P&L NON REALIZZATO:")
                    self.log(f"   {total_status} Totale: ${total_unrealized_pnl:.2f}")
                    
                    # Calcola rendimento del portfolio
                    current_value = portfolio.get_portfolio_value()
                    try:
                        # Prova a calcolare con prezzi attuali
                        current_prices = {}
                        for ticker in portfolio.positions.keys():
                            df = get_stock_data(ticker, period="1d")
                            if len(df) > 0:
                                current_prices[ticker] = df["Close"].iloc[-1]
                        current_value = portfolio.get_portfolio_value(current_prices)
                    except Exception:
                        pass
                    
                    initial_value = 10000  # Valore iniziale
                    total_return = ((current_value - initial_value) / initial_value) * 100
                    return_status = "🟢" if total_return > 0 else "🔴" if total_return < 0 else "⚪"
                    self.log(f"   {return_status} Rendimento Portfolio: {total_return:.2f}%")
                    self.log(f"   💰 Valore Totale: ${current_value:.2f}")
                
                return portfolio
            else:
                portfolio = Portfolio(initial_cash)
                self.log(f"📁 Nuovo portfolio creato con ${initial_cash:.2f}")
                self.save_portfolio(portfolio)
                return portfolio
        except Exception as e:
            self.log(f"❌ Errore nel caricamento portfolio: {e}")
            portfolio = Portfolio(initial_cash)
            self.log(f"📁 Portfolio di backup creato con ${initial_cash:.2f}")
            return portfolio
    
    def save_portfolio(self, portfolio=None):
        """Salva portfolio corrente"""
        try:
            if portfolio is None:
                portfolio = self.portfolio
            
            with open(self.portfolio_file, "wb") as f:
                pickle.dump(portfolio, f)
        except Exception as e:
            self.log(f"❌ Errore nel salvataggio portfolio: {e}")
    
    def calculate_position_size(self, price):
        """
        Calcola la dimensione della posizione basata sul risk management
        
        Args:
            price (float): Prezzo del titolo
            
        Returns:
            int: Numero di azioni da comprare
        """
        available_cash = self.portfolio.cash
        max_investment = available_cash * self.risk_per_trade
        shares = int(max_investment / price)
        return max(1, shares)  # Almeno 1 azione
    
    def should_close_position(self, ticker, current_price):
        """
        Determina se chiudere una posizione basandosi su stop loss/take profit
        
        Args:
            ticker (str): Simbolo del titolo
            current_price (float): Prezzo attuale
            
        Returns:
            bool: True se dovremmo chiudere la posizione
        """
        if ticker not in self.portfolio.positions:
            return False
        
        entry_price = self.portfolio.positions[ticker]["avg_price"]
        price_change_pct = (current_price - entry_price) / entry_price
        
        # Stop loss
        if price_change_pct <= self.stop_loss_pct:
            self.log(f"🔴 STOP LOSS triggered per {ticker}: {price_change_pct:.2%}")
            return True
        
        # Take profit
        if price_change_pct >= self.take_profit_pct:
            self.log(f"🟢 TAKE PROFIT triggered per {ticker}: {price_change_pct:.2%}")
            return True
        
        return False
    
    def analyze_and_trade(self):
        """Analizza i titoli e esegue operazioni di trading"""
        try:
            valid_tickers = [t for t in self.watchlist if t not in self.blacklist]
            self.log(f"🔄 Ciclo #{self.cycle_count} - Analizzando {len(valid_tickers)} titoli validi...")
            
            # Prima di tutto, aggiorna i prezzi delle posizioni esistenti
            if self.portfolio.positions:
                self.log(f"📊 Aggiornamento posizioni esistenti ({len(self.portfolio.positions)} posizioni):")
                for ticker, position in self.portfolio.positions.items():
                    try:
                        df = self.get_stock_data_safe(ticker, period=self.price_update_period)
                        if df is not None and len(df) > 0:
                            current_price = df["Close"].iloc[-1]
                            entry_price = position["avg_price"]
                            shares = position["shares"]
                            pnl = (current_price - entry_price) * shares
                            pnl_pct = ((current_price - entry_price) / entry_price) * 100
                            
                            status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                            self.log(f"   {status} {ticker}: ${current_price:.2f} (entry: ${entry_price:.2f}) P&L: ${pnl:.2f} ({pnl_pct:+.1f}%)")
                        else:
                            self.log(f"   ⚠️  {ticker}: Impossibile aggiornare prezzo (usando periodo {self.price_update_period})")
                    except Exception as e:
                        self.log(f"   ❌ Errore aggiornamento {ticker}: {e}")
            
            opportunities = []
            
            # Analizza tutti i titoli validi
            for ticker in valid_tickers:
                try:
                    df = self.get_stock_data_safe(ticker, period="5d")
                    if df is None:
                        continue
                    
                    current_price = df["Close"].iloc[-1]
                    self.last_prices[ticker] = current_price
                    
                    # Controlla se vendere posizioni esistenti (SOLO stop loss/take profit)
                    if ticker in self.portfolio.positions:
                        if self.should_close_position(ticker, current_price):
                            self.portfolio.sell(ticker, current_price)
                            if ticker in self.position_entry_prices:
                                del self.position_entry_prices[ticker]
                            # Salva subito dopo la vendita
                            self.save_portfolio()
                            continue
                    
                    # Logica di acquisto solo se non abbiamo già la posizione
                    if ticker not in self.portfolio.positions and len(self.portfolio.positions) < self.max_positions:
                        # Usa RL agent per decidere
                        state = self.rl_agent.get_state(df, ticker)
                        rl_action = self.rl_agent.get_action(state)
                        
                        # Usa anche strategia tradizionale
                        traditional_buy = should_buy(df)
                        
                        # Calcola volatilità e momentum
                        volatility = df["Close"].pct_change().std()
                        momentum = (current_price - df["Close"].iloc[-5]) / df["Close"].iloc[-5] if len(df) >= 5 else 0
                        
                        # Punteggio aggressivo
                        aggressiveness_score = momentum * 100 + (volatility * 50)
                        
                        # Decisione finale con parametri configurabili
                        should_buy_aggressive = (
                            (rl_action == "buy" or traditional_buy) and
                            aggressiveness_score > self.aggressiveness_threshold and
                            volatility < self.max_volatility and
                            current_price > self.min_stock_price
                        )
                        
                        if should_buy_aggressive:
                            opportunities.append({
                                "ticker": ticker,
                                "price": current_price,
                                "score": aggressiveness_score,
                                "state": state,
                                "momentum": momentum
                            })
                
                except Exception as e:
                    # Log solo errori non gestiti
                    if "delisted" not in str(e).lower():
                        self.log(f"❌ Errore imprevisto nell'analisi di {ticker}: {e}")
            
            # Ordina le opportunità per punteggio
            opportunities.sort(key=lambda x: x["score"], reverse=True)
            
            # Esegui trades sulle migliori opportunità
            trades_executed = 0
            for opp in opportunities[:3]:  # Massimo 3 trade per ciclo
                if len(self.portfolio.positions) >= self.max_positions:
                    break
                
                ticker = opp["ticker"]
                price = opp["price"]
                shares = self.calculate_position_size(price)
                
                if self.portfolio.buy(ticker, price, shares):
                    self.position_entry_prices[ticker] = price
                    trades_executed += 1
                    
                    # Aggiorna RL agent
                    self.rl_agent.add_experience(
                        opp["state"], "buy", 1.0, opp["state"], 
                        self.portfolio.get_portfolio_value()
                    )
                    
                    self.log(f"🚀 ACQUISTO AGGRESSIVO: {shares} azioni di {ticker} @ ${price:.2f} (Score: {opp['score']:.2f})")
            
            if trades_executed == 0 and len(opportunities) > 0:
                self.log(f"💤 Opportunità trovate ma non eseguite (posizioni: {len(self.portfolio.positions)}/{self.max_positions})")
            elif trades_executed == 0:
                self.log(f"💤 Nessuna opportunità trovata in questo ciclo")
            
            # Mostra blacklist se non vuota
            if self.blacklist and self.cycle_count % 20 == 0:  # Ogni 20 cicli
                self.log(f"🚫 Ticker in blacklist: {', '.join(self.blacklist)}")
            
            # Salva portfolio dopo ogni ciclo di trading
            self.save_portfolio()
            
            # Report periodico
            if self.cycle_count % 5 == 0:  # Ogni 5 cicli
                self.log("📊 REPORT PERIODICO:")
                
                # Calcola valore attuale del portfolio
                current_prices = {}
                for ticker in self.portfolio.positions.keys():
                    try:
                        df = self.get_stock_data_safe(ticker, period="1d")
                        if df is not None and len(df) > 0:
                            current_prices[ticker] = df["Close"].iloc[-1]
                    except Exception:
                        current_prices[ticker] = self.portfolio.positions[ticker]["avg_price"]
                
                current_value = self.portfolio.get_portfolio_value(current_prices)
                metrics = self.portfolio.get_performance_metrics()
                
                self.log(f"   Liquidità: ${self.portfolio.cash:.2f}")
                self.log(f"   Valore portafoglio: ${current_value:.2f}")
                self.log(f"   Rendimento: {metrics['total_return']:.2f}%")
                self.log(f"   Posizioni aperte: {len(self.portfolio.positions)}")
                self.log(f"   Trades totali: {metrics['total_trades']}")
                self.log(f"   Titoli validi: {len(valid_tickers)}")
                
                # Dettaglio posizioni
                if self.portfolio.positions:
                    self.log("   Dettaglio posizioni:")
                    for ticker, position in self.portfolio.positions.items():
                        current_price = current_prices.get(ticker, position["avg_price"])
                        pnl = (current_price - position["avg_price"]) * position["shares"]
                        pnl_pct = ((current_price - position["avg_price"]) / position["avg_price"]) * 100
                        status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                        self.log(f"     {status} {ticker}: {position['shares']} @ ${position['avg_price']:.2f} -> ${current_price:.2f} (P&L: ${pnl:.2f}, {pnl_pct:+.1f}%)")
                
                # Salva modello RL
                self.rl_agent.save_model()
                
                # Decay epsilon per RL
                self.rl_agent.decay_epsilon()
            
        except Exception as e:
            self.log(f"❌ Errore generale nell'analisi e trading: {e}")
    
    def trading_loop(self):
        """Loop principale di trading"""
        self.log("🤖 AGGRESSIVE TRADER AVVIATO")
        self.log(f"   Capitale disponibile: ${self.portfolio.cash:.2f}")
        self.log(f"   Intervallo controlli: {self.check_interval}s")
        self.log(f"   Titoli monitorati: {len(self.watchlist)}")
        self.log(f"   Max posizioni: {self.max_positions}")
        self.log("   ⚠️  CTRL+C = Ferma bot ma MANTIENE posizioni")
        self.log("   ⚠️  Per vendere tutto: python src/main.py /SELLALL")
        
        while self.is_running:
            try:
                # Controlla file di controllo
                if self.check_control_file():
                    self.log("🛑 COMANDO CLOSEALLBOT ricevuto!")
                    self.log("💎 Fermata bot - Le posizioni vengono MANTENUTE")
                    break
                
                # Esegui analisi e trading
                self.analyze_and_trade()
                self.cycle_count += 1
                
                # Attendi prima del prossimo ciclo
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("🛑 Interruzione da tastiera ricevuta (Ctrl+C)")
                self.log("💎 Fermata bot - Le posizioni vengono MANTENUTE")
                break
            except Exception as e:
                self.log(f"❌ Errore nel loop di trading: {e}")
                time.sleep(5)  # Attendi 5 secondi prima di riprovare
        
        self.log("🔴 AGGRESSIVE TRADER FERMATO")
    
    def close_all_positions(self):
        """Chiude tutte le posizioni aperte - SOLO per comando /SELLALL"""
        self.log("🔥 COMANDO /SELLALL - Chiusura forzata di tutte le posizioni...")
        
        for ticker in list(self.portfolio.positions.keys()):
            try:
                df = get_stock_data(ticker, period="1d")
                if len(df) > 0:
                    current_price = df["Close"].iloc[-1]
                    entry_price = self.portfolio.positions[ticker]["avg_price"]
                    shares = self.portfolio.positions[ticker]["shares"]
                    pnl = (current_price - entry_price) * shares
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                    
                    self.portfolio.sell(ticker, current_price)
                    self.log(f"✅ Venduto tutto {ticker}: {shares} azioni @ ${current_price:.2f} (P&L: ${pnl:.2f}, {pnl_pct:+.1f}%)")
            except Exception as e:
                self.log(f"❌ Errore nella vendita di {ticker}: {e}")
        
        # Salva portfolio finale
        self.save_portfolio()
        
        # Report finale
        metrics = self.portfolio.get_performance_metrics()
        self.log("📈 REPORT FINALE VENDITA:")
        self.log(f"   Liquidità finale: ${self.portfolio.cash:.2f}")
        self.log(f"   Valore finale: ${metrics['current_value']:.2f}")
        self.log(f"   Rendimento totale: {metrics['total_return']:.2f}%")
        self.log(f"   Trades totali: {metrics['total_trades']}")
        self.log(f"   Win rate: {metrics['win_rate']:.1f}%")
        
        # Salva modello finale
        self.rl_agent.save_model()
    
    def start(self):
        """Avvia il trader aggressivo"""
        if self.is_running:
            self.log("⚠️ Trader già in esecuzione")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self.trading_loop, daemon=True)
        self.thread.start()
        
        return self.thread
    
    def stop(self):
        """Ferma il trader aggressivo SENZA vendere le posizioni"""
        self.log("🛑 FERMATA TRADER - Le posizioni vengono MANTENUTE")
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)
        
        # Salva stato attuale SENZA vendere
        self.save_portfolio()
        self.rl_agent.save_model()
        
        # Log delle posizioni mantenute
        if self.portfolio.positions:
            self.log("💎 Posizioni mantenute:")
            for ticker, position in self.portfolio.positions.items():
                self.log(f"   {ticker}: {position['shares']} azioni @ ${position['avg_price']:.2f}")
        
        self.log("💾 Stato salvato - Il bot può essere riavviato senza perdere posizioni")

def main():
    """Funzione principale per avviare il trader aggressivo"""
    import sys
    
    # Controlla se è stato specificato un livello di aggressività
    aggressiveness = None
    if len(sys.argv) > 1:
        try:
            aggressiveness = int(sys.argv[1])
            if aggressiveness < 1 or aggressiveness > 10:
                print("❌ Livello di aggressività deve essere tra 1 e 10")
                print("📖 Uso: python src/aggressive_trader.py [1-10]")
                print("   1 = Molto Conservativo")
                print("   5 = Moderato")
                print("   10 = Molto Aggressivo")
                return
        except ValueError:
            print("❌ Livello di aggressività deve essere un numero tra 1 e 10")
            return
    
    trader = AggressiveTrader(
        initial_cash=10000,
        aggressiveness_level=aggressiveness
    )
    
    try:
        thread = trader.start()
        
        # Mantieni il programma in vita
        while trader.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Fermando il trader (posizioni mantenute)...")
        trader.stop()

if __name__ == "__main__":
    main()
