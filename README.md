# 🤖 Stock AI - Intelligent Trading System

Un sistema di trading intelligente che utilizza Reinforcement Learning per automatizzare le decisioni di investimento nel mercato azionario.

## 📋 Caratteristiche

- **Reinforcement Learning**: Agente RL che impara dalle esperienze di trading
- **Analisi Tecnica**: Indicatori e pattern di analisi tecnica
- **Gestione Portfolio**: Sistema automatico di gestione del portafoglio
- **Visualizzazioni**: Grafici interattivi e dashboard
- **Backtesting**: Test delle strategie su dati storici
- **API Integration**: Connessione con Yahoo Finance e altre API

## 🚀 Installazione su Ubuntu 22.04

### STEP 1: Accesso e aggiornamento iniziale

1. **Connettiti via SSH**
```bash
ssh root@IP_DEL_TUO_SERVER
```

2. **Aggiorna il sistema**
```bash
apt update && apt upgrade -y
```

### STEP 2: Installazione ambiente Python

1. **Installa Python 3 e pip**
```bash
apt install python3 python3-pip -y
```

2. **Installa venv (consigliato)**
```bash
apt install python3-venv -y
```

3. **Installa Git**
```bash
git -y
```

### STEP 3: Clona o carica il progetto

**Opzione A: Da repository GitHub**
```bash
git clone https://github.com/TUO_USERNAME/stock-ai.git
cd stock-ai
```

**Opzione B: Caricamento manuale**
```bash
# Dal tuo PC locale
scp -r stock-ai root@IP:/root/

# Sul server
cd /root/stock-ai
```

### STEP 4: Installazione dipendenze

1. **Crea ambiente virtuale (consigliato)**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Installa dipendenze di sistema**
```bash
# Installa setuptools prima
pip install --upgrade setuptools pip

# Installa le dipendenze principali
pip install -r requirements.txt
```

3. **Verifica installazione**
```bash
python3 -c "import yfinance, pandas, numpy, matplotlib; print('✅ Dipendenze installate correttamente')"
```

## 📁 Struttura del Progetto

```
stock-ai/
├── src/                    # Codice sorgente
│   ├── main.py            # Script principale
│   ├── rl_agent.py        # Agente Reinforcement Learning
│   ├── portfolio.py       # Gestione portafoglio
│   ├── data_collector.py  # Raccolta dati finanziari
│   └── visualizer.py      # Grafici e visualizzazioni
├── data/                  # Dati e modelli salvati
│   ├── stock_data.csv     # Dati storici titoli
│   ├── rl_model.pkl       # Modello RL salvato
│   └── portfolio.json     # Stato del portafoglio
├── config/                # File di configurazione
│   └── settings.json      # Impostazioni generali
├── logs/                  # File di log
├── requirements.txt       # Dipendenze Python
├── .gitignore            # File da escludere dal git
└── README.md             # Questo file
```

## ⚙️ Configurazione

### File di configurazione principale: `config/settings.json`

```json
{
  "trading": {
    "initial_capital": 10000,
    "max_position_size": 0.2,
    "stop_loss": 0.05,
    "take_profit": 0.1
  },
  "rl_agent": {
    "learning_rate": 0.1,
    "discount_factor": 0.95,
    "epsilon": 0.1,
    "batch_size": 32
  },
  "data": {
    "update_interval": 3600,
    "lookback_days": 365,
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"]
  },
  "risk_management": {
    "max_daily_loss": 0.02,
    "position_sizing": "kelly",
    "diversification_limit": 5
  }
}
```

### Variabili d'ambiente (opzionali)

Crea un file `.env` nella root del progetto:

```bash
# API Keys (se necessarie)
ALPHA_VANTAGE_KEY=your_api_key_here
QUANDL_KEY=your_quandl_key_here

# Trading settings
PAPER_TRADING=true
LOG_LEVEL=INFO
```

## 🎯 Comandi Disponibili

### Comando principale

```bash
python3 src/main.py [opzioni]
```

**NOTA**: Prima di eseguire qualsiasi comando, assicurati che le directory necessarie esistano:
```bash
# Le directory vengono create automaticamente al primo avvio
python3 src/main.py --version
```

### Opzioni disponibili:

#### **Modalità di Trading**
```bash
# Trading automatico (modalità live)
python3 src/main.py --mode live

# Modalità backtesting
python3 src/main.py --mode backtest --start-date 2023-01-01 --end-date 2024-01-01

# Training dell'agente RL
python3 src/main.py --mode train --episodes 1000
```

#### **Gestione Portafoglio**
```bash
# Visualizza stato del portafoglio
python3 src/main.py --portfolio status

# Reset del portafoglio
python3 src/main.py --portfolio reset

# Aggiorna dati di mercato
python3 src/main.py --update-data
```

#### **Analisi e Visualizzazioni**
```bash
# Genera report completo
python3 src/main.py --report

# Mostra performance dell'agente RL
python3 src/main.py --rl-stats

# Visualizza grafici
python3 src/main.py --plot AAPL

# Dashboard interattiva
python3 src/main.py --dashboard
```

#### **Configurazione**
```bash
# Aggiunge nuovo simbolo al portafoglio
python3 src/main.py --add-symbol NVDA

# Rimuove simbolo
python3 src/main.py --remove-symbol TSLA

# Modifica parametri RL
python3 src/main.py --set-param learning_rate 0.05

# Mostra configurazione attuale
python3 src/main.py --show-config
```

#### **Utilità**
```bash
# Test delle connessioni API
python3 src/main.py --test-api

# Pulizia dei file temporanei
python3 src/main.py --cleanup

# Backup dei dati
python3 src/main.py --backup

# Versione e informazioni
python3 src/main.py --version

# Mostra stato del sistema
python3 src/main.py --system-status

# Modalità debug
python3 src/main.py --debug --verbose
```

## 📊 Esempi di Utilizzo

### 1. Primo avvio e configurazione

```bash
# Verifica che tutto funzioni
python3 src/main.py --version

# Aggiorna dati di mercato
python3 src/main.py --update-data

# Visualizza stato iniziale
python3 src/main.py --portfolio status
```

### 2. Training dell'agente RL

```bash
# Training con 500 episodi
python3 src/main.py --mode train --episodes 500

# Visualizza statistiche apprendimento
python3 src/main.py --rl-stats
```

### 3. Backtesting di una strategia

```bash
# Test su periodo specifico
python3 src/main.py --mode backtest --start-date 2023-01-01 --end-date 2023-12-31

# Genera report dettagliato
python3 src/main.py --report --save-html
```

### 4. Trading automatico

```bash
# Modalità paper trading (simulazione)
PAPER_TRADING=true python3 src/main.py --mode live

# Trading reale (ATTENZIONE: usa denaro vero!)
python3 src/main.py --mode live --real-trading
```

## 📈 Monitoraggio e Log

### File di log

I log vengono salvati automaticamente in:
- `logs/trading.log` - Log delle operazioni di trading
- `logs/rl_agent.log` - Log dell'agente RL
- `logs/error.log` - Log degli errori

### Visualizzazione log in tempo reale

```bash
# Log trading
tail -f logs/trading.log

# Log agente RL
tail -f logs/rl_agent.log

# Tutti i log
tail -f logs/*.log
```

## 🔧 Risoluzione Problemi

### Problemi comuni

**1. Errore "No such file or directory" per logs**
```bash
# I log vengono creati automaticamente al primo avvio
python3 src/main.py --version
```

**2. Errore import moduli**
```bash
# Verifica ambiente virtuale attivo
which python3
pip list

# Reinstalla dipendenze
pip install --upgrade setuptools pip
pip install -r requirements.txt --force-reinstall
```

**3. Errore "gym" deprecato**
```bash
# Il progetto usa gymnasium invece di gym (già aggiornato)
python3 -c "import gymnasium; print('✅ Gymnasium OK')"
```

**4. Errore connessione API**
```bash
# Test connessione
python3 src/main.py --test-api

# Verifica firewall
ufw status
```

**5. Spazio insufficiente**
```bash
# Pulizia file temporanei
python3 src/main.py --cleanup

# Verifica spazio disco
df -h
```

**6. Performance lente**
```bash
# Riduce dimensione dati storici
python3 src/main.py --set-param lookback_days 90

# Ottimizza parametri RL
python3 src/main.py --set-param batch_size 16
```

### Debug avanzato

```bash
# Modalità verbose
python3 src/main.py --verbose --debug

# Profiling performance
python3 -m cProfile src/main.py --mode backtest

# Test specifico di un componente
python3 -c "from src.data_collector import DataCollector; print('✅ DataCollector OK')"
```

## 🚨 Avvertenze Importanti

⚠️ **DISCLAIMER**: Questo software è per scopi educativi e di ricerca. Il trading automatico comporta rischi finanziari significativi.

- **Mai investire più di quanto puoi permetterti di perdere**
- **Testa sempre in modalità paper trading prima del trading reale**
- **I risultati passati non garantiscono performance future**
- **Monitora costantemente le posizioni aperte**

## 📞 Supporto

Per problemi o domande:

1. Controlla i log in `logs/`
2. Verifica la configurazione in `config/settings.json`
3. Esegui i test: `python3 src/main.py --test-api`
4. Controlla lo stato del sistema: `python3 src/main.py --system-status`

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

---

**🚀 Buon Trading con l'IA! 📈**
