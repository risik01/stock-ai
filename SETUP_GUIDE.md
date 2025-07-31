# 🚀 Trading AI System - Guida Setup Ubuntu

## 📋 Installazione Rapida

### 1. **Preparazione Server Ubuntu**
```bash
# Su macchina Ubuntu pulita
sudo apt update && sudo apt upgrade -y
git clone https://github.com/risik01/stock-ai.git
cd stock-ai
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

### 2. **Avvio Sistema**
```bash
# Avvia trading automatico
./trading_control.sh start

# Monitor real-time (nuovo terminale)
./trading_control.sh logs
```

## 🎯 Configurazione Trading Reale

### **Budget e Risk Management**
- **Budget iniziale**: €1000
- **Max posizione**: 15% del portfolio
- **Stop loss**: 3%
- **Take profit**: 8%
- **Max loss giornaliero**: 5%
- **Max trades/giorno**: 8

### **AI Components Attivi**
- ✅ **RL Agent** (peso 40%): Analisi pattern e predizioni
- ✅ **Technical Analysis** (peso 35%): RSI, MACD, EMA, SMA
- ✅ **News Sentiment** (peso 25%): 10 RSS feeds finanziari
- ✅ **Ensemble Decision**: Combinazione intelligente dei segnali

### **Simboli Monitorati**
- AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA

## 🔧 Comandi Sistema

### **Controllo Base**
```bash
./trading_control.sh start     # Avvia sistema
./trading_control.sh stop      # Ferma sistema  
./trading_control.sh status    # Stato attuale
./trading_control.sh logs      # Log real-time
```

### **Monitoring Avanzato**
```bash
./monitor_system.sh           # Report completo sistema
./backup_data.sh              # Backup dati trading
```

### **Performance Tracking**
```bash
# Visualizza ultimi report
ls -la logs/performance_report_*.json | tail -5

# Report real-time
tail -f logs/trading_system_$(date +%Y%m%d).log
```

## 📊 Dashboard e Monitoring

### **Log Files Principali**
- `logs/trading_system_YYYYMMDD.log` - Log principale
- `logs/performance_report_*.json` - Report performance
- `data/` - Dati mercato e cache

### **Metriche Chiave da Monitorare**
1. **Portfolio Value** - Valore totale portfolio
2. **Total Return %** - Rendimento percentuale
3. **Total Trades** - Numero trade eseguiti
4. **AI Decisions** - Decisioni prese dall'AI
5. **News Based Trades** - Trade basati su news

### **Esempio Output Log**
```
2025-01-31 10:15:32 - INFO - 🚀 Automated Trading System inizializzato
2025-01-31 10:15:32 - INFO - 💰 Budget iniziale: €1000
2025-01-31 10:16:45 - INFO - 📊 Aggiornamento dati mercato...
2025-01-31 10:17:12 - INFO - 📰 Raccolta news...
2025-01-31 10:17:45 - INFO - 🤖 Elaborazione decisioni AI...
2025-01-31 10:18:03 - INFO - 🎯 Decisione AAPL: BUY (conf: 0.78)
2025-01-31 10:18:15 - INFO - ✅ TRADE ESEGUITO: BUY 6 AAPL @ €150.25 (conf: 0.78)
2025-01-31 10:18:16 - INFO - 📊 PERFORMANCE: €1045.67 (+4.57%)
```

## 🛡️ Sicurezza e Risk Management

### **Protezioni Automatiche**
- **Emergency Stop**: Ferma trading se loss > 10%
- **Daily Loss Limit**: Max 5% loss giornaliero
- **Position Sizing**: Max 15% per singola posizione
- **Trade Frequency**: Min 5 minuti tra trade dello stesso simbolo
- **Confidence Threshold**: Solo trade con confidence > 65%

### **Monitoring Continuo**
- Health check ogni 30 minuti
- Performance report ogni ora
- Backup automatico dati
- Log dettagliato di ogni operazione

## 🔄 Funzionamento AI Multi-Componente

### **1. Data Collection (ogni minuto)**
- Prezzi real-time via yfinance
- News RSS da 10 feeds principali
- Indicatori tecnici aggiornati

### **2. News Analysis**
- Sentiment analysis articoli
- Importanza per simbolo
- Impact score su decisioni

### **3. RL Agent Training**
- Apprendimento continuo
- Adattamento pattern mercato
- Memoria di 10.000 esperienze

### **4. Decision Making**
- Ensemble di 3 modelli AI
- Voto pesato per decisione finale
- Confidence scoring

### **5. Execution**
- Risk management pre-trade
- Position sizing dinamico
- Stop loss automatico

## 🚀 Test Multi-Giorno

### **Setup Test Esteso**
```bash
# 1. Avvia sistema
./trading_control.sh start

# 2. Setup monitoring automatico (crontab)
crontab -e
# Aggiungi:
# 0 */6 * * * cd /path/to/stock-ai && ./monitor_system.sh >> logs/monitoring.log
# 0 0 * * * cd /path/to/stock-ai && ./backup_data.sh

# 3. Monitoring continuo
screen -S trading-monitor
./trading_control.sh logs
# Ctrl+A, D per detach
```

### **Cosa Aspettarsi**
- **Prima settimana**: Sistema apprende pattern, 15-25 trade
- **Settimana 2-3**: RL agent migliora, decisioni più precise
- **Mese 1**: Sistema maturo, performance stabilizzate

### **Indicatori di Successo**
- Return > 2% mensile
- Drawdown < 8%
- Sharpe ratio > 1.2
- Win rate > 55%

## 🆘 Troubleshooting

### **Problemi Comuni**
```bash
# Sistema non si avvia
./trading_control.sh status
tail -50 logs/trading_system_$(date +%Y%m%d).log

# Errori di rete/API
grep "ERROR" logs/*.log | tail -10

# Performance degradata
./monitor_system.sh
cat logs/performance_report_*.json | tail -1 | python -m json.tool
```

### **Recovery Procedure**
```bash
# 1. Stop sistema
./trading_control.sh stop

# 2. Backup stato
./backup_data.sh

# 3. Reset cache
rm -rf data/cache/
rm -f data/*_cache.json

# 4. Restart
./trading_control.sh start
```

## 📈 Ottimizzazioni Avanzate

### **Tuning Performance**
- Modifica `config/settings.json`
- Ajusta pesi modelli AI
- Cambia thresholds confidence
- Personalizza simboli monitorati

### **Scaling Up**
- Aumenta budget in `initial_capital`
- Aggiungi più simboli in `symbols`
- Aumenta frequenza controlli
- Setup multiple strategie

## 🎯 Obiettivi Test

### **Metriche Target**
- **ROI mensile**: 3-8%
- **Max drawdown**: < 10%
- **Trades vincenti**: > 55%
- **Sharpe ratio**: > 1.0

### **Test Duration**
- **Minimo**: 2 settimane
- **Raccomandato**: 1 mese
- **Ottimale**: 3 mesi

---

## 🚨 **IMPORTANTE**: 
Questo è un sistema di trading automatico con capitale reale. 
Monitora costantemente le performance e interrompi se necessario.
Il trading comporta sempre rischi di perdite.

**Buon Trading! 🚀📈**
