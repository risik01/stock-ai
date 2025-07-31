# ⚡ Quick Start Guide - Stock AI Trading System

Inizia subito con il **Stock AI Trading System**! Questa guida ti porterà dall'installazione alla prima sessione di trading in **meno di 15 minuti**.

---

## 🎯 **Obiettivo Quick Start**

Al termine di questa guida avrai:
- ✅ Sistema completamente funzionante
- ✅ Portfolio virtuale attivo con $10K
- ✅ News Trading AI operativo
- ✅ Dashboard web accessibili
- ✅ Prima sessione di trading simulato

---

## ⏱️ **15-Minute Setup**

### **⚡ Step 1: Clone & Setup (3 min)**

```bash
# Clone repository
git clone https://github.com/risik01/stock-ai.git
cd stock-ai

# Crea virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### **⚡ Step 2: News Dependencies (2 min)**

```bash
# Install News Trading dependencies
pip install feedparser textblob vaderSentiment nltk beautifulsoup4 lxml

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

### **⚡ Step 3: Quick Test (5 min)**

```bash
# Test 1: Data collection
python src/data_collector.py --symbols AAPL --period 1mo

# Test 2: News system
python trading-new/news_trading_cli.py cycle

# Test 3: RL Agent
python src/test_rl.py --quick

# Test 4: Web dashboard
python src/web_dashboard.py &
python trading-new/news_web_dashboard.py &
```

### **⚡ Step 4: First Trading Session (5 min)**

```bash
# Avvia trading automatico simulato
python src/main.py --mode simulation --duration 300  # 5 minuti

# Monitora in tempo reale
python src/cli_monitor.py
```

---

## 🎮 **Demo Mode - Prova Immediata**

### **🚀 Modalità Demo Completa**

```bash
# Avvia tutto in demo mode
./scripts/demo_start.sh

# O manualmente:
python src/main.py --demo --symbols AAPL,GOOGL,TSLA --duration 600
```

**Cosa include Demo Mode**:
- 📊 **Dati Live**: Prezzi reali da Yahoo Finance
- 🤖 **RL Agent**: Pre-trained model per decisioni immediate
- 📰 **News Analysis**: Sentiment analysis in tempo reale
- 💰 **Virtual Portfolio**: $10,000 iniziali
- 📈 **Live Dashboard**: Grafici e metriche real-time

### **👀 Cosa Vedere Durante Demo**

**Terminal Output**:
```
🤖 RL Agent initialized - Model loaded
📰 News collector started - 6/10 sources active
💰 Portfolio: $10,000 (100% cash)
📊 Monitoring: AAPL, GOOGL, TSLA

[12:34:56] 📈 AAPL: $175.30 (+0.5%) | Sentiment: +0.2 | Signal: BUY
[12:35:12] 🔥 Breaking: Apple earnings beat expectations (Sentiment: +0.7)
[12:35:15] 💰 TRADE: BUY AAPL 28 shares @ $175.30 ($4,908.40)
[12:35:16] 📊 Portfolio: $5,091.60 cash + $4,908.40 stocks = $10,000.00
```

**Web Dashboard**: 
- http://localhost:5000 - Main dashboard
- http://localhost:5001 - News dashboard

---

## 🎯 **Primi Comandi Essenziali**

### **📊 Monitoraggio Portfolio**

```bash
# Status portfolio corrente
python src/portfolio.py --status

# Performance history
python src/portfolio.py --history

# Risk analysis
python src/portfolio.py --risk
```

**Output Example**:
```
💰 PORTFOLIO STATUS
├── Total Value: $10,247.50 (+2.48%)
├── Cash: $2,150.30 (21.0%)
├── Positions: 3 active
│   ├── AAPL: 28 shares ($4,908.40, +1.2%)
│   ├── GOOGL: 15 shares ($2,189.85, +3.1%)
│   └── TSLA: 8 shares ($998.95, -0.8%)
└── P&L Today: +$97.35 (+0.98%)
```

### **📰 News Analysis**

```bash
# Latest news analysis
python trading-new/news_trading_cli.py news

# Current signals
python trading-new/news_trading_cli.py signals

# Breaking news alerts
python trading-new/news_trading_cli.py alerts
```

**Output Example**:
```
📰 NEWS ANALYSIS (Last Hour)
├── Articles: 47 collected from 6 sources
├── Breaking News: 3 items
├── Sentiment Score: +0.15 (Slightly Positive)
└── Trading Signals: 2 BUY, 1 SELL

🎯 ACTIVE SIGNALS
├── AAPL: BUY (Sentiment: +0.3, Confidence: 0.8)
├── TSLA: SELL (Sentiment: -0.2, Confidence: 0.7)
└── GOOGL: HOLD (Sentiment: +0.1, Confidence: 0.5)
```

### **🤖 RL Agent Control**

```bash
# Agent status
python src/rl_agent.py --status

# Force retrain (if needed)
python src/train_rl.py --episodes 100

# Model performance
python src/rl_agent.py --performance
```

---

## 🌐 **Dashboard Walkthrough**

### **📊 Main Dashboard (http://localhost:5000)**

**Sezioni Principali**:
1. **🏠 Overview**: Portfolio value, daily P&L, win rate
2. **📈 Charts**: Price charts con segnali RL
3. **💰 Portfolio**: Posizioni correnti e allocation
4. **📊 Performance**: Metriche storiche e benchmark
5. **⚙️ Settings**: Configurazione live

**Key Metrics da Monitorare**:
- **Total Portfolio Value**: Valore totale investimenti
- **Daily Return**: Performance giornaliera
- **Sharpe Ratio**: Rendimento aggiustato per rischio
- **Max Drawdown**: Massima perdita dal picco
- **Win Rate**: Percentuale trades profittevoli

### **📰 News Dashboard (http://localhost:5001)**

**Sezioni**:
1. **📰 Live Feed**: Stream notizie in tempo reale
2. **🎯 Signals**: Segnali trading basati su news
3. **📊 Sentiment**: Grafici sentiment per simbolo
4. **🚨 Alerts**: Breaking news e eventi critici
5. **📈 Impact**: Correlazione news-prezzi

**Funzionalità Interattive**:
- **Real-time Updates**: Aggiornamento automatico ogni 30s
- **Symbol Filtering**: Filtra per simboli specifici
- **Sentiment Timeline**: Storia sentiment per simbolo
- **News Source Toggle**: Abilita/disabilita fonti specifiche

---

## 🎮 **Modalità Operative**

### **🔒 Simulation Mode (Default)**

```bash
# Trading simulato - zero rischi
python src/main.py --mode simulation

# Caratteristiche:
# ✅ Portfolio virtuale ($10K)
# ✅ Prezzi reali di mercato
# ✅ Trades registrati ma non eseguiti
# ✅ Performance tracking completo
```

### **📊 Backtest Mode**

```bash
# Test su dati storici
python src/main.py --mode backtest --start 2023-01-01 --end 2023-12-31

# Risultati:
# ✅ Performance vs Buy & Hold
# ✅ Maximum Drawdown analysis
# ✅ Sharpe Ratio calculation
# ✅ Trade statistics
```

### **👁️ Watch Mode**

```bash
# Solo monitoraggio, no trading
python src/main.py --mode watch --symbols AAPL,GOOGL,MSFT

# Output:
# ✅ Prezzi live
# ✅ Segnali generati
# ✅ News sentiment
# ✅ Nessun trade eseguito
```

### **🎯 Paper Trading Mode**

```bash
# Trading realistico con denaro virtuale
python src/main.py --mode paper --cash 50000

# Simula:
# ✅ Latency di mercato
# ✅ Slippage dei prezzi
# ✅ Transaction costs
# ✅ Market hours restrictions
```

---

## 🛠️ **Personalizzazione Rapida**

### **🎯 Scegli i Tuoi Simboli**

```bash
# Edita config/settings.json
nano config/settings.json
```

```json
{
    "data_collector": {
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"],
        "period": "2y",
        "interval": "1d"
    }
}
```

### **💰 Personalizza Portfolio**

```json
{
    "portfolio": {
        "initial_cash": 50000,        // $50K invece di $10K
        "max_position_size": 0.15,    // Max 15% per posizione
        "transaction_cost": 0.0005,   // 0.05% transaction cost
        "stop_loss": 0.05             // Stop-loss a 5%
    }
}
```

### **📰 Configura News Sources**

```json
{
    "news": {
        "sources": {
            "yahoo_finance": true,
            "cnbc": true,
            "reuters": true,
            "bloomberg": false,    // Disabilita se non necessario
            "marketwatch": true
        },
        "update_interval": 300,    // Ogni 5 minuti
        "sentiment_threshold": 0.1  // Soglia per segnali
    }
}
```

---

## 📊 **Primi Risultati - Cosa Aspettarsi**

### **✅ Successo Indicators**

**Dopo 1 ora di trading**:
- 📊 **Portfolio Value**: Oscillazioni tra -2% e +3%
- 🤖 **RL Decisions**: 5-15 segnali generati
- 📰 **News Analysis**: 20-50 articoli processati
- 💰 **Trades**: 1-3 trades eseguiti
- 📈 **Performance**: Tracking accurato

**Log Output Tipico**:
```
[14:30:15] 📊 Market Open - Starting analysis
[14:30:45] 📰 Collected 23 news articles
[14:31:02] 🤖 RL Signal: AAPL BUY (confidence: 0.72)
[14:31:05] 📈 News Sentiment: AAPL +0.3 (positive)
[14:31:08] 💰 TRADE: BUY AAPL 15 shares @ $175.42
[14:31:10] 🎯 Portfolio: +0.15% today
```

### **⚠️ Warning Signs da Controllare**

- **RSS Errors**: >50% fonti fallite
- **Model Errors**: RL agent non risponde
- **Data Gaps**: Prezzi non aggiornati
- **Memory Issues**: Usage >80%
- **Performance**: Cycle time >30s

---

## 🎯 **Configurazioni Raccomandate**

### **🔰 Principiante**

```json
{
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "initial_cash": 10000,
    "max_position_size": 0.2,
    "mode": "simulation",
    "risk_tolerance": "low"
}
```

### **📈 Intermediate**

```json
{
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA"],
    "initial_cash": 25000,
    "max_position_size": 0.15,
    "mode": "paper",
    "risk_tolerance": "medium"
}
```

### **🚀 Advanced**

```json
{
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"],
    "initial_cash": 100000,
    "max_position_size": 0.1,
    "mode": "paper",
    "risk_tolerance": "high",
    "enable_shorting": true
}
```

---

## 🚀 **Prossimi Passi**

Dopo il Quick Start, esplora:

### **📚 Approfondimenti**
1. **[[RL Agent Overview|RL-Agent-Overview]]** - Capire l'AI trading
2. **[[News Trading Overview|News-Trading-Overview]]** - Sentiment analysis
3. **[[Configuration Files|Configuration-Files]]** - Setup avanzato
4. **[[Performance Analysis|Performance-Analysis]]** - Ottimizzare risultati

### **🛠️ Customizzazione**
1. **Nuove Strategie**: Sviluppa algoritmi custom
2. **Additional Data**: Integra più fonti dati
3. **Risk Management**: Implementa stop-loss avanzati
4. **Alert System**: Setup notifiche Discord/Slack

### **📊 Produzione**
1. **Live Trading**: Migrazione a broker reale
2. **Cloud Deployment**: Deploy su AWS/GCP
3. **Monitoring**: Setup alerting professionale
4. **Scaling**: Multiple accounts/strategies

---

## 🆘 **Quick Troubleshooting**

### **❌ Errori Comuni**

```bash
# Problema: ModuleNotFoundError
pip install -r requirements.txt

# Problema: Portfolio non si carica
rm data/current_portfolio.pkl
python src/portfolio.py --reset

# Problema: News feeds non funzionano
python trading-new/news_rss_collector.py --debug

# Problema: RL Agent errori
python src/train_rl.py --episodes 50 --force
```

### **🔧 Reset Completo**

```bash
# Reset tutto ai defaults
rm -rf data/cache/*
rm data/current_portfolio.pkl data/rl_model.pkl
cp config/settings.json.example config/settings.json
python src/main.py --init
```

---

## 🎉 **Congratulazioni!**

🚀 **Il tuo Stock AI Trading System è ora operativo!**

- ✅ Sistema funzionante in meno di 15 minuti
- ✅ Portfolio virtuale attivo
- ✅ News trading automatico
- ✅ Dashboard live accessibili
- ✅ Pronto per trading simulato

**Next**: Esplora le funzionalità avanzate e personalizza il sistema secondo le tue esigenze!

---

*Happy Trading! 📈💰*
