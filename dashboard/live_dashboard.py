#!/usr/bin/env python3
"""
Dashboard Live Trading - Versione Funzionante
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import time

# Configurazione pagina
st.set_page_config(
    page_title="🚀 AI Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def parse_trading_log():
    """Parse completo del log di trading"""
    log_file = Path("data/dual_ai_simple.log")
    
    if not log_file.exists():
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Dati da estrarre
        latest_portfolio = 1000.0
        latest_positions = {}
        trades = []
        prices = {}
        
        # Parse al contrario per dati più recenti
        for line in reversed(lines[-200:]):  # Ultime 200 righe
            # Parse Portfolio
            if "📊 Portfolio:" in line and "€" in line:
                try:
                    parts = line.split("Portfolio: €")[1]
                    latest_portfolio = float(parts.split(" ")[0])
                    
                    # Parse posizioni
                    if "Posizioni: " in line:
                        pos_part = line.split("Posizioni: ")[1]
                        positions = {}
                        for pos in pos_part.split(", "):
                            if ":" in pos:
                                symbol, qty = pos.strip().split(":")
                                positions[symbol] = int(qty)
                        latest_positions = positions
                except:
                    pass
            
            # Parse Trades
            elif "💰 ACQUISTO:" in line or "💰 VENDITA:" in line:
                try:
                    timestamp_str = line.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    
                    if "ACQUISTO:" in line:
                        parts = line.split("ACQUISTO: ")[1]
                        trade_type = "🟢 BUY"
                    else:
                        parts = line.split("VENDITA: ")[1]
                        trade_type = "🔴 SELL"
                    
                    quantity = int(parts.split(" ")[0])
                    symbol = parts.split(" ")[1]
                    price = float(parts.split("€")[1].split(" ")[0])
                    
                    trades.append({
                        'Time': timestamp.strftime('%H:%M:%S'),
                        'Type': trade_type,
                        'Symbol': symbol,
                        'Qty': quantity,
                        'Price': f"€{price:.2f}",
                        'Total': f"€{price * quantity:.2f}"
                    })
                except:
                    pass
            
            # Parse Prezzi AI
            elif "🧠 " in line and "€" in line and "→" in line:
                try:
                    parts = line.split("🧠 ")[1]
                    symbol = parts.split(":")[0].strip()
                    price = float(parts.split("€")[1].split(" ")[0])
                    action = parts.split("→ ")[1].strip()
                    
                    prices[symbol] = {
                        'price': price,
                        'action': action
                    }
                except:
                    pass
        
        return {
            'portfolio_value': latest_portfolio,
            'positions': latest_positions,
            'trades': list(reversed(trades))[:20],  # Ultimi 20 trades
            'prices': prices,
            'total_lines': len(lines)
        }
    
    except Exception as e:
        st.error(f"Errore nel parsing: {e}")
        return None

def main():
    st.title("🚀 AI Trading Dashboard Live")
    st.markdown("### 📊 Monitoraggio Real-Time del Sistema di Trading AI")
    
    # Sidebar controls
    st.sidebar.header("⚙️ Controlli Dashboard")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (3s)", value=True)
    
    if st.sidebar.button("🔄 Aggiorna Dati Manualmente"):
        st.rerun()
    
    # Parse dati
    data = parse_trading_log()
    
    if data is None:
        st.error("❌ Impossibile caricare i dati del trading")
        st.info("💡 Assicurati che il sistema di trading sia stato avviato")
        return
    
    # Debug info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Debug Info")
    st.sidebar.write(f"📁 Log righe: {data['total_lines']}")
    st.sidebar.write(f"💰 Portfolio: €{data['portfolio_value']:.2f}")
    st.sidebar.write(f"📊 Trades: {len(data['trades'])}")
    st.sidebar.write(f"📈 Posizioni: {len(data['positions'])}")
    st.sidebar.write(f"💹 Prezzi: {len(data['prices'])}")
    st.sidebar.write(f"🕐 Aggiornato: {datetime.now().strftime('%H:%M:%S')}")
    
    # === METRICHE PRINCIPALI ===
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        profit_loss = data['portfolio_value'] - 1000.0
        profit_pct = (profit_loss / 1000.0) * 100
        
        st.metric(
            "💰 Portfolio Value", 
            f"€{data['portfolio_value']:.2f}",
            f"{profit_loss:+.2f} ({profit_pct:+.2f}%)"
        )
    
    with col2:
        st.metric("📊 Total Trades", len(data['trades']))
    
    with col3:
        open_positions = len([p for p in data['positions'].values() if p > 0])
        st.metric("📈 Open Positions", open_positions)
    
    with col4:
        cash_remaining = 1000.0 - sum([float(t['Total'].replace('€', '')) for t in data['trades'] if t['Type'] == '🟢 BUY'])
        cash_remaining += sum([float(t['Total'].replace('€', '')) for t in data['trades'] if t['Type'] == '🔴 SELL'])
        st.metric("💵 Cash Available", f"€{cash_remaining:.2f}")
    
    st.markdown("---")
    
    # === SEZIONE PRINCIPALE ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💼 Posizioni Aperte")
        if data['positions']:
            positions_df = pd.DataFrame([
                {'Symbol': symbol, 'Quantity': qty}
                for symbol, qty in data['positions'].items() if qty > 0
            ])
            if not positions_df.empty:
                st.dataframe(positions_df, use_container_width=True)
            else:
                st.info("📊 Nessuna posizione aperta")
        else:
            st.info("📊 Nessuna posizione aperta")
    
    with col2:
        st.subheader("📊 Trades Recenti")
        if data['trades']:
            trades_df = pd.DataFrame(data['trades'][:10])  # Ultimi 10
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("📊 Nessun trade ancora")
    
    st.markdown("---")
    
    # === PREZZI E SEGNALI ===
    st.subheader("💹 Prezzi e Segnali AI")
    if data['prices']:
        prices_data = []
        for symbol, info in data['prices'].items():
            prices_data.append({
                'Symbol': symbol,
                'Price': f"€{info['price']:.2f}",
                'AI Signal': info['action']
            })
        
        if prices_data:
            prices_df = pd.DataFrame(prices_data)
            st.dataframe(prices_df, use_container_width=True)
    else:
        st.info("💹 Nessun prezzo disponibile")
    
    # === PERFORMANCE CHART ===
    if data['trades']:
        st.markdown("---")
        st.subheader("📈 Performance Portfolio")
        
        # Calcola P&L cumulativo
        cumulative_pnl = 0
        pnl_data = []
        
        for i, trade in enumerate(data['trades']):
            if trade['Type'] == '🟢 BUY':
                cumulative_pnl -= float(trade['Total'].replace('€', ''))
            else:
                cumulative_pnl += float(trade['Total'].replace('€', ''))
            
            pnl_data.append({
                'Trade': i + 1,
                'P&L': cumulative_pnl
            })
        
        if pnl_data:
            pnl_df = pd.DataFrame(pnl_data)
            st.line_chart(pnl_df.set_index('Trade'))
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(3)
        st.rerun()

if __name__ == "__main__":
    main()
