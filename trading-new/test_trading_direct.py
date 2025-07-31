#!/usr/bin/env python3
"""
Test diretto del trading AI per debug
"""

from news_based_trading_ai import NewsBasedTradingAI

def test_trading_ai():
    print("💼 TEST TRADING AI")
    print("="*50)
    
    ai = NewsBasedTradingAI()
    
    # Portfolio status
    portfolio = ai.portfolio
    print(f"💰 PORTFOLIO:")
    print(f"   Cash: ${portfolio.cash:,.2f}")
    print(f"   Valore totale: ${portfolio.get_total_value():,.2f}")
    print(f"   Posizioni aperte: {len(portfolio.positions)}")
    print(f"   Trades totali: {len(portfolio.trade_history)}")
    print()
    
    print("🔄 ESEGUENDO CICLO TRADING...")
    result = ai.run_trading_cycle()
    print(f"Risultato: {result}")

if __name__ == "__main__":
    test_trading_ai()
