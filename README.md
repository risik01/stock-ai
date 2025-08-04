# 🚀 Stock AI Trading System v4.0

![Stock AI](https://img.shields.io/badge/Stock%20AI-v4.0-blue)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Sistema di Trading Automatico con Intelligenza Artificiale Dual-Core**

Sistema di trading automatico avanzato che combina **Reinforcement Learning**, **Analisi Tecnica** e **Sentiment Analysis** per decisioni di trading intelligenti in tempo reale.

## ✨ Caratteristiche Principali

### 🤖 **Dual AI System**
- **Price AI**: Analisi tecnica real-time ogni 10 secondi
- **News AI**: Sentiment analysis ogni 10 minuti
- **Ensemble Decision**: Combinazione intelligente dei segnali

### 📊 **Analisi Multi-Livello**
- **Technical Analysis**: RSI, MACD, EMA, SMA, Bollinger Bands
- **News Sentiment**: 10+ RSS feeds finanziari analizzati
- **Risk Management**: Stop-loss automatico e position sizing

### 🎯 **Trading Intelligente**
- **7 Simboli**: AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA
- **Risk Control**: Max 10% investimento per posizione
- **Real-time**: Dati di mercato aggiornati continuamente

## 🚀 Installazione Rapida

### **Su Ubuntu/Linux**
```bash
# Clona repository
git clone https://github.com/risik01/stock-ai.git
cd stock-ai

# Setup automatico
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh

# Configura API keys
nano .env
# Inserisci: ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, NEWS_API_KEY
```

### **Avvio Sistema**
```bash
# Avvia trading automatico
python src/simple_dual_ai.py

# In background (raccomandato per produzione)
nohup python src/simple_dual_ai.py > logs/trading.log 2>&1 &

# Dashboard web
python src/main.py --dashboard
# Apri http://localhost:5000
```

## 🔧 Configurazione API

### **API Keys Richieste** (gratis)
```bash
# File .env
ALPHA_VANTAGE_API_KEY=your_key_here        # https://www.alphavantage.co/
FINNHUB_API_KEY=your_key_here              # https://finnhub.io/
NEWS_API_KEY=your_key_here                 # https://newsapi.org/
```

### **Setup Automatico Dipendenze**
```bash
# Il setup installa automaticamente:
pip install yfinance pandas numpy requests textblob
python -m textblob.download_corpora
```

## 📈 Performance e Metriche

### **Obiettivi di Performance**
- 🎯 **ROI Target**: 3-8% mensile
- 📉 **Max Drawdown**: < 10%
- 📊 **Win Rate**: > 55%
- ⚡ **Sharpe Ratio**: > 1.0

### **Risk Management**
- 💰 **Budget Iniziale**: €1000
- 🛡️ **Max Posizione**: 10% del portfolio
- 🚨 **Stop Loss**: Automatico
- 📊 **Max Loss Giornaliero**: 5%

## 🌐 Dashboard e Monitoring

### **Web Dashboard**
```bash
python src/main.py --dashboard
```
- **Real-time Portfolio**: Valore attuale e P&L
- **Trade History**: Storico operazioni
- **AI Decisions**: Log decisioni AI
- **News Feed**: Feed notizie analizzate

### **Monitoring da Terminale**
```bash
# Stato sistema
python src/main.py --system-status

# Portfolio status
python src/main.py --portfolio status

# Log real-time
tail -f logs/trading_*.log
```

## 🔄 Modalità Operative

### **1. Demo Mode (Sicuro)**
```bash
# Trading simulato - NESSUN RISCHIO
python src/simple_dual_ai.py --demo
```

### **2. Live Trading**
```bash
# Trading reale - ATTENZIONE!
python src/simple_dual_ai.py --live
```

### **3. Backtesting**
```bash
# Test su dati storici
python src/main.py --mode backtest --start-date 2024-01-01 --end-date 2024-12-31
```

## 🤖 Architettura AI

### **Dual AI Core**
```
┌─────────────────┐    ┌──────────────────┐
│   Price AI      │    │    News AI       │
│   (10s cycles)  │    │   (10min cycles) │
│                 │    │                  │
│ • Technical     │    │ • RSS Feeds      │
│ • Momentum      │    │ • Sentiment      │
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

### **Decision Making Process**
1. **Data Collection**: Prezzi real-time + News
2. **Technical Analysis**: Indicatori calcolati
3. **Sentiment Analysis**: Score da news
4. **Score Fusion**: Combinazione intelligente
5. **Risk Check**: Validazione limiti
6. **Execution**: Trade se score > soglia

## 📊 Esempio Output Live

```
2025-08-04 10:15:32 - INFO - 🚀 === AVVIO SISTEMA DUAL AI ===
2025-08-04 10:15:33 - INFO - 🤖 === ANALISI AI PER 7 SIMBOLI ===
2025-08-04 10:15:33 - INFO - 🧠 AAPL: €151.24 | Δ+1.85% | News:+0.125 | Score:+1.547 → BUY
2025-08-04 10:15:33 - INFO - 🎯 SEGNALE TRADING: AAPL → BUY (score: 1.547)
2025-08-04 10:15:33 - INFO - 💰 ACQUISTO: 6 AAPL a €151.24 (Costo: €907.44, Tot: 6)
2025-08-04 10:15:34 - INFO - 📊 Portfolio: €1045.67 (+4.57%) | Trades: 1 | Posizioni: AAPL:6
```

## 🛡️ Sicurezza e Best Practices

### **Protezioni Integrate**
- ✅ **Emergency Stop**: Blocco automatico se loss > 10%
- ✅ **Position Limits**: Max investimento per simbolo
- ✅ **Rate Limiting**: Evita over-trading
- ✅ **Error Handling**: Recovery automatico da errori

### **Raccomandazioni Produzione**
```bash
# 1. Usa screen/tmux per sessioni persistenti
screen -S trading
python src/simple_dual_ai.py
# Ctrl+A, D per detach

# 2. Setup monitoring automatico
crontab -e
# 0 */6 * * * cd /path/to/stock-ai && python src/main.py --system-status

# 3. Backup automatico
# 0 0 * * * cd /path/to/stock-ai && tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

## 📚 Documentazione Completa

### **Wiki GitHub**
- 📖 [Installation Guide](https://github.com/risik01/stock-ai/wiki/Installation-Guide)
- 🚀 [Quick Start](https://github.com/risik01/stock-ai/wiki/Quick-Start)
- 📊 [User Manual](https://github.com/risik01/stock-ai/wiki/User-Manual)
- 🔧 [Configuration](https://github.com/risik01/stock-ai/wiki/Configuration-Guide)

### **API Reference**
- 🤖 [RL Agent Overview](https://github.com/risik01/stock-ai/wiki/RL-Agent-Overview)
- 📰 [News Trading](https://github.com/risik01/stock-ai/wiki/News-Trading-Overview)
- 🔌 [API Reference](https://github.com/risik01/stock-ai/wiki/API-Reference)

## 🚨 Disclaimer

⚠️ **IMPORTANTE**: Questo sistema di trading automatico opera con capitale reale. Il trading comporta sempre rischi di perdite finanziarie. 

- ✅ **Inizia sempre in modalità demo**
- ✅ **Monitora costantemente le performance**
- ✅ **Non investire più di quanto puoi permetterti di perdere**
- ✅ **Mantieni sempre controllo manuale del sistema**

## 🤝 Contributing

Contributi benvenuti! Vedi [CONTRIBUTING.md](CONTRIBUTING.md) per guidelines.

## 📄 License

MIT License - vedi [LICENSE](LICENSE) per dettagli.

---

## 🎯 Quick Start Commands

```bash
# Setup completo (una volta)
git clone https://github.com/risik01/stock-ai.git && cd stock-ai && ./setup_ubuntu.sh

# Trading demo (sicuro)
python src/simple_dual_ai.py --demo

# Dashboard web
python src/main.py --dashboard

# Status sistema
python src/main.py --system-status
```

**🚀 Happy Trading! 📈**

---

![AI Trading](https://img.shields.io/badge/AI-Trading-brightgreen)
![Real Time](https://img.shields.io/badge/Real%20Time-Analytics-blue)
![Risk Management](https://img.shields.io/badge/Risk-Management-red)
