# 🚀 Stock AI Trading System v2.1

Un sistema di trading automatizzato basato su Intelligenza Artificiale che utilizza un'architettura dual-AI per analizzare prezzi e sentiment delle notizie in tempo reale.

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

## 🌟 Caratteristiche Principali

### 🧠 **Dual AI Architecture**
- **Price AI**: Analisi tecnica dei prezzi ogni 10 secondi
- **News AI**: Analisi sentiment delle notizie ogni 10 minuti
- **Decisioni combinate**: Segnali di trading basati su entrambi gli AI

### 📊 **Trading Modes**
- **Trading Simulato**: Ambiente sicuro per test e apprendimento
- **Trading Live**: Trading reale con dati di mercato in tempo reale
- **Aggressive Trading**: Modalità ad alta frequenza per massimizzare opportunità

### 🎯 **AI Training System**
- **Background Learning**: Training continuo dell'AI durante il trading
- **Knowledge Base**: Persistenza delle conoscenze apprese
- **Pattern Recognition**: Riconoscimento automatico di pattern di mercato

### 📈 **Live Dashboard**
- **Real-time Monitoring**: Visualizzazione live del portfolio
- **Performance Charts**: Grafici di performance e P&L
- **Trading Signals**: Visualizzazione segnali AI in tempo reale
- **Auto-refresh**: Aggiornamento automatico ogni 3 secondi

## 🛠️ Installazione

### Prerequisiti
- Python 3.12+ 
- Ubuntu 20.04+ (testato su Ubuntu 24.04.2 LTS)
- Git

### 1. Clone del Repository
```bash
git clone https://github.com/risik01/stock-ai.git
cd stock-ai
```

### 2. Creazione Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installazione Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configurazione
Il sistema è preconfigurato con settings ottimali. Le configurazioni si trovano in:
- `config/settings.json` - Configurazioni generali
- `config/trading_config.json` - Parametri di trading

## 🚀 Utilizzo

### Launcher Unificato
Il sistema include un launcher unificato per tutti i comandi:

```bash
python launcher.py --help
```

### 📊 **Trading Simulato** (Raccomandato per iniziare)
```bash
# Trading simulato standard
python launcher.py trade

# Trading aggressivo simulato
python launcher.py trade --aggressive

# Trading con simboli specifici
python launcher.py trade --symbols AAPL TSLA GOOGL
```

### 💹 **Trading Live** (Dati reali)
```bash
# Trading live con dati reali
python launcher.py trade --live

# Trading live aggressivo
python launcher.py trade --live --aggressive
```

### 🧠 **AI Training**
```bash
# Training AI in background (1 giorno)
python launcher.py train

# Training esteso (7 giorni)
python launcher.py train --days 7

# Training su simboli specifici
python launcher.py train --symbols AAPL TSLA META
```

### 📈 **Dashboard Live**
```bash
# Avvia dashboard web
python launcher.py dashboard
```
Poi apri http://localhost:8501 nel browser

### 🔄 **Sistema Smart** (Training + Trading)
```bash
# Prima training poi trading automatico
python launcher.py smart

# Smart con modalità aggressiva
python launcher.py smart --aggressive
```

### 🧪 **Test del Sistema**
```bash
# Test dati real-time
python launcher.py test realtime

# Test API
python launcher.py test api

# Test dual AI
python launcher.py test dual-ai

# Test AI training
python launcher.py test training
```

### 📋 **Stato Sistema**
```bash
# Verifica stato completo
python launcher.py status
```

## 📊 Dashboard Features

### Metriche Principali
- **Portfolio Value**: Valore totale con P&L
- **Total Trades**: Numero di operazioni eseguite
- **Open Positions**: Posizioni attualmente aperte
- **Cash Available**: Liquidità disponibile

### Visualizzazioni
- **Posizioni Aperte**: Tabella con simboli e quantità
- **Trades Recenti**: Cronologia delle ultime operazioni
- **Prezzi e Segnali AI**: Prezzi attuali con segnali di trading
- **Performance Chart**: Grafico P&L cumulativo nel tempo

### Controlli
- **Auto-refresh**: Aggiornamento automatico (configurabile)
- **Manual Refresh**: Aggiornamento manuale
- **Debug Info**: Informazioni di sistema e debugging

## 🔧 Configurazione Avanzata

### Trading Parameters
Modifica `config/trading_config.json`:
```json
{
    "initial_balance": 1000.0,
    "max_position_size": 0.1,
    "risk_tolerance": 0.02,
    "trading_symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
}
```

### AI Settings
Modifica `config/settings.json`:
```json
{
    "price_ai_interval": 10,
    "news_ai_interval": 600,
    "market_hours": {
        "start": "09:30",
        "end": "16:00"
    }
}
```

## 📁 Struttura del Progetto

```
stock-ai/
├── 📊 dashboard/          # Dashboard web Streamlit
│   └── live_dashboard.py  # Dashboard principale
├── 📦 data/              # Dati e cache
│   ├── *.log            # Log di trading
│   ├── portfolio.json   # Stato portfolio
│   └── *.pkl           # Modelli AI salvati
├── ⚙️ config/            # Configurazioni
│   ├── settings.json
│   └── trading_config.json
├── 🐍 src/              # Codice sorgente principale
│   ├── main.py         # Entry point principale
│   ├── dual_ai_system.py
│   ├── realtime_data.py
│   ├── ai_background_trainer.py
│   └── ...
├── 🧪 tests/            # Test del sistema
├── 📝 logs/             # Log di sistema
└── 🚀 launcher.py       # Launcher unificato
```

## 🔒 Sicurezza e Risk Management

### Protezioni Integrate
- **Stop Loss**: Protezione automatica dalle perdite
- **Position Sizing**: Limitazione dimensioni posizioni
- **Risk Tolerance**: Controllo tolleranza al rischio
- **Simulazione First**: Test obbligatorio prima del live

### Gestione Errori
- **Graceful Shutdown**: Arresto sicuro con CTRL+C
- **Error Recovery**: Recupero automatico da errori
- **Data Persistence**: Salvataggio automatico dello stato
- **Logging Completo**: Tracciamento di tutte le operazioni

## 📈 Performance Monitoring

### Metriche Disponibili
- **P&L Real-time**: Profitti/perdite in tempo reale
- **Win Rate**: Percentuale di operazioni vincenti
- **Sharpe Ratio**: Rapporto rischio/rendimento
- **Maximum Drawdown**: Massima perdita consecutiva

### Log e Reporting
- **Trading Log**: `data/dual_ai_simple.log`
- **Performance History**: `data/performance_history.json`
- **System Log**: `logs/system.log`

## 🔄 Backup e Recovery

### Backup Automatico
Il sistema salva automaticamente:
- Stato portfolio
- Modelli AI addestrati
- Configurazioni personalizzate
- Cronologia performance

### Recovery
In caso di interruzione:
```bash
# Il sistema riprende automaticamente dall'ultimo stato salvato
python launcher.py trade
```

## 🚨 Troubleshooting

### Problemi Comuni

#### Dashboard non mostra dati
```bash
# Verifica log di trading
python launcher.py status

# Riavvia dashboard
python launcher.py dashboard
```

#### Errori API
```bash
# Test connessione API
python launcher.py test api

# Verifica configurazione di rete
```

#### Performance lente
```bash
# Pulisci cache
rm -rf data/cache/
rm -rf src/__pycache__/

# Riavvia sistema
python launcher.py trade
```

## 📞 Supporto

### Log di Debug
Per problemi, condividi:
- `logs/system.log`
- `data/dual_ai_simple.log`
- Output di `python launcher.py status`

### Issue Reporting
Apri un issue su GitHub con:
- Descrizione del problema
- Steps per riprodurre
- Log rilevanti
- Sistema operativo e versione Python

## 📋 Changelog

### v2.1 (Current)
- ✅ Dashboard live completamente funzionale
- ✅ Sistema di training AI in background
- ✅ Launcher unificato per tutti i comandi
- ✅ Gestione graceful shutdown (CTRL+C)
- ✅ Trading con dati real-time
- ✅ Architettura dual-AI ottimizzata
- ✅ Sistema di recovery e persistence migliorato

### v2.0
- 🔄 Dual AI architecture
- 🔄 Real-time data integration
- 🔄 Web dashboard introduction

## 📄 License

MIT License - Vedi [LICENSE](LICENSE) per dettagli.

## 🤝 Contributing

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

---

**⚠️ Disclaimer**: Questo software è fornito a scopo educativo. Il trading comporta rischi finanziari. Usa sempre la modalità simulata per test e formazione prima di procedere con trading reale.
