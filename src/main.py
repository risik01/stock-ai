import sys
import os
import time
from data_collector import get_stock_data
from strategy_engine import should_buy
from portfolio import Portfolio

def show_help():
    """Mostra le opzioni disponibili"""
    print("🤖 STOCK AI TRADING BOT - Opzioni Disponibili")
    print("=" * 50)
    print()
    print("📊 ANALISI E TRADING:")
    print("  python src/main.py /RUN")
    print("    Esegue analisi multi-titolo e trading singolo")
    print()
    print("🤖 GESTIONE BOT:")
    print("  python src/aggressive_trader.py")
    print("    Avvia il bot di trading aggressivo (continuo)")
    print()
    print("  python src/main.py /CLOSEALLBOT")
    print("    Ferma tutti i bot attivi (mantiene posizioni)")
    print()
    print("💰 GESTIONE POSIZIONI:")
    print("  python src/main.py /SELLALL")
    print("    Vende tutte le posizioni aperte immediatamente")
    print()
    print("📊 MONITORAGGIO:")
    print("  python src/cli_monitor.py status")
    print("    Mostra stato generale del portfolio")
    print()
    print("  python src/cli_monitor.py positions")
    print("    Mostra dettaglio posizioni aperte")
    print()
    print("  python src/cli_monitor.py watch")
    print("    Monitoraggio continuo (modalità watch)")
    print()
    print("  python src/web_dashboard.py")
    print("    Avvia dashboard web su http://localhost:5000")
    print()
    print("🔧 ESEMPI D'USO:")
    print("  # Avvia trading continuo")
    print("  python src/aggressive_trader.py")
    print()
    print("  # In un altro terminale, monitora")
    print("  python src/cli_monitor.py watch")
    print()
    print("  # Per fermare tutto e vendere")
    print("  python src/main.py /SELLALL")
    print("  python src/main.py /CLOSEALLBOT")

def handle_sellall_command():
    """Gestisce il comando SELLALL per vendere tutte le posizioni"""
    portfolio_file = "/workspaces/stock-ai/data/current_portfolio.pkl"
    
    try:
        # Carica portfolio esistente
        if not os.path.exists(portfolio_file):
            print("❌ Nessun portfolio trovato - nessuna posizione da vendere")
            return
        
        import pickle
        with open(portfolio_file, "rb") as f:
            portfolio = pickle.load(f)
        
        if not portfolio.positions:
            print("💰 Nessuna posizione aperta da vendere")
            print(f"   Liquidità attuale: ${portfolio.cash:.2f}")
            return
        
        print("🔥 VENDITA FORZATA DI TUTTE LE POSIZIONI")
        print("=" * 50)
        
        total_sold_value = 0
        positions_to_sell = list(portfolio.positions.keys())
        
        for ticker in positions_to_sell:
            try:
                position = portfolio.positions[ticker]
                shares = position["shares"]
                entry_price = position["avg_price"]
                
                # Ottieni prezzo attuale
                df = get_stock_data(ticker, period="1d")
                if len(df) > 0:
                    current_price = df["Close"].iloc[-1]
                    
                    # Calcola P&L
                    total_value = shares * current_price
                    cost_basis = shares * entry_price
                    pnl = total_value - cost_basis
                    pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    # Vendi
                    portfolio.sell(ticker, current_price)
                    total_sold_value += total_value
                    
                    # Status emoji
                    status = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                    
                    print(f"{status} Venduto {shares} azioni di {ticker}:")
                    print(f"   Entry: ${entry_price:.2f} -> Exit: ${current_price:.2f}")
                    print(f"   P&L: ${pnl:.2f} ({pnl_pct:+.1f}%) = ${total_value:.2f}")
                else:
                    print(f"❌ Impossibile ottenere prezzo per {ticker}")
                    
            except Exception as e:
                print(f"❌ Errore nella vendita di {ticker}: {e}")
        
        # Salva portfolio aggiornato
        with open(portfolio_file, "wb") as f:
            pickle.dump(portfolio, f)
        
        # Report finale
        print("\n📈 RIEPILOGO VENDITE:")
        print(f"   Valore vendite: ${total_sold_value:.2f}")
        print(f"   Liquidità finale: ${portfolio.cash:.2f}")
        
        metrics = portfolio.get_performance_metrics()
        print(f"   Rendimento totale: {metrics['total_return']:.2f}%")
        print(f"   Trades totali: {metrics['total_trades']}")
        print(f"   Win rate: {metrics['win_rate']:.1f}%")
        print("\n✅ Tutte le posizioni sono state vendute")
        
    except Exception as e:
        print(f"❌ Errore nell'esecuzione SELLALL: {e}")

def handle_closeallbot_command():
    """Gestisce il comando CLOSEALLBOT per fermare tutti i bot"""
    control_file = "/workspaces/stock-ai/data/trader_control.txt"
    
    try:
        os.makedirs(os.path.dirname(control_file), exist_ok=True)
        with open(control_file, "w") as f:
            f.write("CLOSEALLBOT")
        
        print("🛑 COMANDO CLOSEALLBOT INVIATO")
        print("=" * 30)
        print("   Tutti i bot di trading verranno fermati")
        print("   Le posizioni aperte saranno MANTENUTE")
        print("   Per vendere tutto usa: python src/main.py /SELLALL")
        print()
        print("⏳ Attendere alcuni secondi per la fermata dei bot...")
        
        # Attendi un po' per permettere ai bot di processare
        time.sleep(5)
        
        # Rimuovi il file di controllo
        if os.path.exists(control_file):
            os.remove(control_file)
            print("✅ Comando processato e file di controllo rimosso")
        
        print("✅ Tutti i bot sono stati fermati")
            
    except Exception as e:
        print(f"❌ Errore nell'invio del comando CLOSEALLBOT: {e}")

def analyze_stock(ticker):
    """Analizza un singolo titolo e restituisce un punteggio di profittabilità"""
    try:
        df = get_stock_data(ticker)
        if len(df) < 3:
            return None, 0, 0
        
        current_price = df["Close"].iloc[-1]
        avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
        
        # Calcola trend e volatilità
        price_change_pct = ((current_price - df["Close"].iloc[-5]) / df["Close"].iloc[-5]) * 100 if len(df) >= 5 else 0
        volatility = df["Close"].pct_change().std() * 100
        
        # Punteggio di profittabilità (più alto = migliore)
        # Favorisce titoli con trend positivo ma non troppo volatili
        profitability_score = price_change_pct - (volatility * 0.5)
        
        return df, current_price, profitability_score
    except Exception as e:
        print(f"Errore nell'analisi di {ticker}: {e}")
        return None, 0, 0

def run_single_analysis():
    """Esegue l'analisi e trading singolo"""
    print("📊 ANALISI MULTI-TITOLO E TRADING SINGOLO")
    print("=" * 50)
    
    # Lista di titoli da analizzare
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX", "AMD", "INTC"]
    
    port = Portfolio()
    best_stock = None
    best_score = float('-inf')
    best_df = None
    best_price = 0
    
    print(f"Analizzando {len(tickers)} titoli...")
    print()
    
    # Analizza tutti i titoli
    for ticker in tickers:
        df, current_price, score = analyze_stock(ticker)
        
        if df is not None and len(df) >= 3:
            avg_3d = df['Close'].rolling(window=3).mean().iloc[-1]
            buy_signal = should_buy(df)
            
            print(f"{ticker}:")
            print(f"  Prezzo: ${current_price:.2f}")
            print(f"  Media 3g: ${avg_3d:.2f}")
            print(f"  Punteggio: {score:.2f}")
            print(f"  Segnale acquisto: {buy_signal}")
            
            # Aggiorna il migliore se ha segnale di acquisto e punteggio superiore
            if buy_signal and score > best_score:
                best_stock = ticker
                best_score = score
                best_df = df
                best_price = current_price
            
            print()
    
    # Esegui l'operazione sul titolo migliore
    if best_stock:
        print(f"=== TITOLO SELEZIONATO: {best_stock} ===")
        print(f"Punteggio di profittabilità: {best_score:.2f}")
        print(f"Prezzo di acquisto: ${best_price:.2f}")
        port.buy(best_stock, best_price)
    else:
        print("=== NESSUN TITOLO IDONEO ===")
        print("Nessun titolo presenta segnali di acquisto favorevoli oggi.")
    
    print()
    port.report()

def main():
    # Controlla argomenti della riga di comando
    if len(sys.argv) > 1:
        command = sys.argv[1].upper()
        
        if command == "/SELLALL":
            handle_sellall_command()
            return
        elif command == "/CLOSEALLBOT":
            handle_closeallbot_command()
            return
        elif command == "/RUN":
            run_single_analysis()
            return
        else:
            print(f"❌ Comando sconosciuto: {sys.argv[1]}")
            print("   Usa uno dei comandi supportati o esegui senza parametri per vedere le opzioni")
            print()
    
    # Se nessun comando o comando non riconosciuto, mostra help
    show_help()

if __name__ == "__main__":
    main()