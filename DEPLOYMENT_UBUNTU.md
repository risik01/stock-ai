# 🚀 DEPLOYMENT UBUNTU - Trading AI System v3.0

## 📋 ISTRUZIONI COMPLETE PER UBUNTU PULITO

### 🎯 OBIETTIVO
Installare e configurare il Trading AI System su Ubuntu pulito per trading multi-day con budget €1000.

---

## 🔧 PREREQUISITI UBUNTU

```bash
# 1. Aggiorna sistema
sudo apt update && sudo apt upgrade -y

# 2. Installa Git (se non presente)
sudo apt install git -y

# 3. Verifica Python (dovrebbe essere già installato)
python3 --version  # Minimo: Python 3.8+
```

---

## ⚡ INSTALLAZIONE AUTOMATICA (METODO CONSIGLIATO)

### Step 1: Download del repository
```bash
# Clona il repository in directory pulita
cd ~
git clone https://github.com/risik01/stock-ai.git
cd stock-ai
```

### Step 2: Installazione automatica
```bash
# Esegui setup automatico (tutto incluso)
./setup_ubuntu.sh
```

**⏱️ Tempo stimato: 5-10 minuti**

Il script installa automaticamente:
- ✅ Python e pip aggiornati
- ✅ Virtual environment con tutte le dipendenze
- ✅ Configurazioni di produzione (budget €1000)
- ✅ Script di controllo e monitoring
- ✅ Struttura directory corretta
- ✅ Test componenti sistema

---

## 🎮 CONFIGURAZIONE E AVVIO

### Step 3: Configurazione API Keys
```bash
# Crea file delle API keys
nano .env
```

Inserisci le tue API keys:
```env
# API Keys per trading (RICHIESTE)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# API Keys opzionali per news
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_token
```

### Step 4: Verifica configurazioni
```bash
# Controlla impostazioni di produzione
nano production_settings.json
```

**Configurazioni chiave:**
- 💰 Budget: €1000
- 🛡️ Max loss giornaliero: 5%
- 📊 Max posizione: 15%
- 🤖 IA Ensemble attiva

### Step 5: Avvio sistema
```bash
# Avvia il trading system
./trading_control.sh start

# Monitor in tempo reale (nuovo terminale)
./trading_control.sh logs
```

---

## 📊 COMANDI DI CONTROLLO

### Gestione Sistema
```bash
./trading_control.sh start      # 🚀 Avvia trading
./trading_control.sh stop       # 🛑 Ferma trading  
./trading_control.sh status     # ℹ️  Stato sistema
./trading_control.sh logs       # 📊 Log real-time
./trading_control.sh performance # 📈 Report performance
```

### Monitoring Avanzato
```bash
./monitor_system.sh             # 📊 Monitor completo
./backup_data.sh                # 💾 Backup dati
```

### Dashboard Web
```bash
# Avvia dashboard (opzionale)
python3 src/web_dashboard.py
# Accedi a: http://localhost:5000
```

---

## 🔐 SICUREZZA E RISK MANAGEMENT

### Protezioni Attive
- ✅ **Stop Loss**: 5% perdita giornaliera massima
- ✅ **Position Limit**: 15% del portfolio per trade
- ✅ **Trade Limit**: Massimo 10 trades/giorno
- ✅ **Emergency Stop**: Arresto automatico su anomalie
- ✅ **Health Checks**: Controlli ogni 30 minuti

### Monitoraggio Consigliato
```bash
# Controlla stato ogni ora
./trading_control.sh status

# Visualizza performance giornaliera
./trading_control.sh performance

# Backup quotidiano
./backup_data.sh
```

---

## 📈 SISTEMA IA ENSEMBLE

### Composizione Decisionale
- **40%** RL Agent (Reinforcement Learning)
- **35%** Technical Analysis (RSI, MACD, Bollinger)  
- **25%** News Sentiment (10 RSS feeds)

### Simboli Trading
- AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA

### Strategia Operativa
- 📊 Analisi real-time ogni minuto
- 🗞️ Sentiment news aggiornato ogni 5 minuti
- 🤖 Decisioni IA pesate per consenso
- ⚡ Esecuzione automatica trades

---

## 🆘 TROUBLESHOOTING

### Problemi Comuni

**1. Errore import moduli**
```bash
# Riattiva environment
source .venv/bin/activate
python3 -c "import pandas; print('OK')"
```

**2. Errore API keys**
```bash
# Verifica file .env
cat .env
# Assicurati che le keys siano valide
```

**3. Memoria insufficiente**
```bash
# Controlla risorse
free -h
# Ferma altri processi se necessario
```

**4. Trading non parte**
```bash
# Controlla log dettagliato
tail -f logs/system.log
# Verifica configurazioni
./trading_control.sh status
```

### Log Files Utili
- `logs/system.log` - Log principale
- `logs/performance_report_*.json` - Report performance
- `data/performance_history.json` - Storico completo

---

## 🎯 CHECKLIST DEPLOYMENT

### Prima del Trading Reale
- [ ] ✅ Sistema installato correttamente
- [ ] ✅ API keys configurate e testate
- [ ] ✅ Budget impostato su €1000
- [ ] ✅ Risk limits verificati (5% max loss)
- [ ] ✅ Test eseguito con ./trading_control.sh start
- [ ] ✅ Monitoring attivo
- [ ] ✅ Backup system configurato

### Durante il Trading
- [ ] 📊 Controlla performance 2-3 volte/giorno
- [ ] 🛡️ Verifica rispetto dei risk limits
- [ ] 💾 Backup quotidiano dati
- [ ] 📱 Monitor log per anomalie
- [ ] 🔄 Riavvia se necessario (./trading_control.sh stop/start)

---

## 🎉 SISTEMA PRONTO!

Il tuo Trading AI System è ora completamente configurato per:

🎯 **Trading automatico multi-day**  
💰 **Budget €1000 con risk management**  
🤖 **IA Ensemble per decisioni ottimali**  
📊 **Monitoring completo e real-time**  
🛡️ **Sicurezza e protezioni attive**

**✨ Buon Trading! ✨**

---

*Per supporto: leggi README.md e SETUP_GUIDE.md*
*Sistema testato su Ubuntu 20.04+ e Ubuntu 22.04+*
