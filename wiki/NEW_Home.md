# 🚀 Stock AI Trading System v4.0 - Wiki

**Sistema Trading Automatico con Intelligenza Artificiale**

Benvenuto nella documentazione completa del **Stock AI Trading System v4.0** - un sistema di trading automatico avanzato che combina Reinforcement Learning, Analisi Tecnica e Sentiment Analysis per decisioni di trading intelligenti.

## 🎯 Quick Start

### **Installazione Rapida Ubuntu**
```bash
git clone https://github.com/risik01/stock-ai.git
cd stock-ai
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

### **Avvio Immediato**
```bash
# Demo sicuro (raccomandato per iniziare)
python src/simple_dual_ai.py --demo

# Dashboard web
python src/main.py --dashboard  # http://localhost:5000
```

## 📚 Documentazione

### **Guide Essenziali**
- 🚀 **[Quick Start](Quick-Start)** - Avvio in 5 minuti
- 🔧 **[Installation Guide](Installation-Guide)** - Setup dettagliato  
- 📖 **[User Manual](User-Manual)** - Utilizzo completo
- ⚙️ **[Configuration Guide](Configuration-Guide)** - Configurazione avanzata

### **Approfondimenti Tecnici**
- 🤖 **[RL Agent Overview](RL-Agent-Overview)** - Intelligenza Artificiale
- 📰 **[News Trading Overview](News-Trading-Overview)** - Sentiment Analysis
- 🔌 **[API Reference](API-Reference)** - Riferimenti API

## ✨ Caratteristiche v4.0

### **🤖 Dual AI Core**
- **Price AI**: Analisi tecnica real-time (10s)
- **News AI**: Sentiment analysis (10min)
- **Ensemble Logic**: Decisioni combinate

### **📊 Trading Intelligente**
- **7 Simboli**: AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA
- **Risk Management**: Stop-loss automatico
- **Portfolio**: €1000 budget iniziale
- **Performance Target**: 3-8% ROI mensile

### **🛡️ Sicurezza Avanzata**
- **Demo Mode**: Trading simulato sicuro
- **Position Limits**: Max 10% per simbolo
- **Emergency Stop**: Blocco automatico perdite
- **Real-time Monitoring**: Dashboard web

## 🚀 Modalità Operative

### **1. Demo Mode (Raccomandato)**
```bash
python src/simple_dual_ai.py --demo
```
- ✅ **Sicuro**: Nessun rischio finanziario
- ✅ **Realistico**: Usa dati di mercato reali
- ✅ **Completo**: Tutte le funzionalità AI

### **2. Live Trading**
```bash
python src/simple_dual_ai.py --live
```
- ⚠️ **ATTENZIONE**: Trading con capitale reale
- 🔑 **Richiede**: API keys configurate
- 📊 **Monitoring**: Obbligatorio

### **3. Background Production**
```bash
nohup python src/simple_dual_ai.py --live > logs/trading.log 2>&1 &
```
- 🔄 **Continuo**: Funziona 24/7
- 📝 **Logged**: Tutto registrato in logs/
- 🛡️ **Robusto**: Recovery automatico errori

## 📈 Performance Monitoring

### **Dashboard Web Real-time**
- **URL**: http://localhost:5000
- **Features**: Portfolio, trades, AI decisions, news feed
- **Aggiornamento**: Real-time con WebSocket

### **Metriche Chiave**
- 📊 **Portfolio Value**: Valore totale corrente
- 📈 **P&L %**: Profit/Loss percentuale
- 🎯 **Win Rate**: % trade vincenti
- ⚡ **Sharpe Ratio**: Rapporto rischio/rendimento

## 🔧 API Configuration

### **API Keys Necessarie** (tutte gratuite)
```bash
# .env file
ALPHA_VANTAGE_API_KEY=your_key    # https://www.alphavantage.co/
FINNHUB_API_KEY=your_key          # https://finnhub.io/
NEWS_API_KEY=your_key             # https://newsapi.org/
```

### **Setup Automatico**
Il sistema configura automaticamente:
- Python virtual environment
- Dipendenze (yfinance, pandas, numpy, etc.)
- Struttura directory
- File di configurazione

## 🛠️ Troubleshooting

### **Problemi Comuni**
```bash
# Sistema non si avvia
python src/main.py --system-status

# Errori API
grep "ERROR" logs/*.log | tail -10

# Performance issues
python src/main.py --portfolio status
```

### **Recovery Steps**
1. Stop sistema: `pkill -f simple_dual_ai`
2. Check logs: `tail -50 logs/trading_*.log`
3. Reset cache: `rm -rf data/cache/`
4. Restart: `python src/simple_dual_ai.py --demo`

## 🚨 Safety & Risk Management

### **Protezioni Integrate**
- ✅ **Position Limits**: Max 10% investimento per simbolo
- ✅ **Daily Loss Limit**: Blocco a 5% perdita giornaliera
- ✅ **Emergency Stop**: Halt automatico se loss > 10%
- ✅ **Rate Limiting**: Evita over-trading

### **Best Practices**
1. **Inizia sempre in Demo Mode**
2. **Monitora costantemente le performance**
3. **Non investire più di quanto puoi perdere**
4. **Mantieni controllo manuale del sistema**

## 📊 Technical Architecture

```
┌─────────────────┐    ┌──────────────────┐
│   Price AI      │    │    News AI       │
│   (10s cycles)  │    │   (10min cycles) │
│                 │    │                  │
│ • Technical     │    │ • Momentum      │
│ • Patterns      │    │ • Impact Score   │
└─────────────────┘    └──────────────────┘
         │                       │
         └───────┬───────────────┘
                 │
         ┌───────▼────────┐
         │ Ensemble Logic │
         │ • Score Fusion │
         │ • Risk Check   │
         │ • Execute      │
         └────────────────┘
```

## 🤝 Support & Community

### **Documentazione**
- 📖 **Wiki**: Guide complete e tutorial
- 💻 **GitHub**: Codice sorgente e issues
- 📊 **Examples**: Esempi di configurazione

### **Getting Help**
1. Controlla la [documentazione wiki](https://github.com/risik01/stock-ai/wiki)
2. Cerca in [GitHub Issues](https://github.com/risik01/stock-ai/issues)
3. Crea nuovo issue con dettagli completi

---

## 🎯 Quick Commands

```bash
# Setup completo
./setup_ubuntu.sh

# Demo sicuro
python src/simple_dual_ai.py --demo

# Dashboard
python src/main.py --dashboard

# Status
python src/main.py --system-status

# Background production
nohup python src/simple_dual_ai.py --live > logs/trading.log 2>&1 &
```

---

**🚀 Pronto per iniziare? Vai alla [Quick Start Guide](Quick-Start)!**
