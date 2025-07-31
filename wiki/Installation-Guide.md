# 🚀 Guida Installazione - Stock AI Trading System

Questa guida ti accompagnerà passo-passo nell'installazione e configurazione completa del **Stock AI Trading System**.

---

## 📋 **Prerequisiti Sistema**

### **🖥️ Sistema Operativo Supportati**
- ✅ **Ubuntu 20.04+** (Raccomandato)
- ✅ **macOS 10.15+**
- ✅ **Windows 10+** (con WSL2 raccomandato)
- ✅ **Docker** (Qualsiasi OS)

### **🐍 Python Requirements**
- **Python 3.8+** (3.10+ raccomandato)
- **pip** package manager
- **venv** o **conda** per virtual environments

### **💾 Requisiti Hardware**
- **RAM**: Minimo 4GB, raccomandato 8GB+
- **Storage**: 2GB spazio libero
- **CPU**: Multi-core raccomandato per training RL
- **GPU**: Opzionale (NVIDIA CUDA per training accelerato)

---

## 📥 **Step 1: Clone Repository**

```bash
# Clone del repository principale
git clone https://github.com/risik01/stock-ai.git
cd stock-ai

# Verifica struttura files
ls -la
```

**Struttura Expected**:
```
stock-ai/
├── src/                    # Codice sorgente principale
├── trading-new/           # News Trading AI module
├── config/                # File configurazione
├── data/                  # Dati e models
├── templates/             # Web templates
├── requirements.txt       # Dependencies Python
├── README.md             # Documentazione
└── wiki/                 # Documentazione estesa
```

---

## 🐍 **Step 2: Setup Python Environment**

### **🔧 Opzione A: Virtual Environment (venv)**

```bash
# Crea virtual environment
python3 -m venv stock-ai-env

# Attiva environment
# Su Linux/macOS:
source stock-ai-env/bin/activate
# Su Windows:
# stock-ai-env\Scripts\activate

# Verifica attivazione
which python
# Output: /path/to/stock-ai-env/bin/python
```

### **🔧 Opzione B: Conda Environment**

```bash
# Crea conda environment
conda create -n stock-ai python=3.10
conda activate stock-ai

# Verifica installazione
python --version
# Output: Python 3.10.x
```

---

## 📦 **Step 3: Installazione Dependencies**

### **📋 Install Core Dependencies**

```bash
# Aggiorna pip
pip install --upgrade pip

# Installa requirements principali
pip install -r requirements.txt

# Verifica installazioni chiave
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import yfinance; print('YFinance: OK')"
```

### **📰 Install News Trading Dependencies**

```bash
# Dependencies specifiche per News Trading AI
pip install feedparser==6.0.10
pip install textblob==0.18.0
pip install vaderSentiment==3.3.2
pip install nltk==3.8.1
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

### **🔍 Verifica Installazione**

```bash
# Test importazioni principali
python -c "
import torch
import pandas as pd
import numpy as np
import yfinance as yf
import feedparser
import textblob
import vaderSentiment
print('✅ Tutte le dependencies installate correttamente!')
"
```

---

## ⚙️ **Step 4: Configurazione Sistema**

### **🗂️ Crea Directory Mancanti**

```bash
# Crea directories necessarie
mkdir -p data/models
mkdir -p data/cache
mkdir -p logs
mkdir -p config/backup

# Imposta permessi
chmod 755 data/ logs/ config/
```

### **📄 Setup File Configurazione**

#### **config/settings.json**
```bash
# Copia template configurazione
cp config/settings.json.example config/settings.json

# Edita configurazione base
nano config/settings.json
```

```json
{
    "data_collector": {
        "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
        "period": "1y",
        "interval": "1d",
        "auto_update": true,
        "cache_enabled": true
    },
    "rl_agent": {
        "model_path": "data/rl_model.pkl",
        "training_episodes": 1000,
        "learning_rate": 0.001,
        "epsilon_start": 1.0,
        "epsilon_end": 0.05,
        "epsilon_decay": 0.995
    },
    "portfolio": {
        "initial_cash": 10000,
        "transaction_cost": 0.001,
        "max_position_size": 0.2
    }
}
```

#### **config/trading_config.json**
```json
{
    "trading": {
        "mode": "simulation",
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "max_positions": 5,
        "risk_tolerance": "medium"
    },
    "alerts": {
        "enabled": true,
        "methods": ["console", "file"],
        "thresholds": {
            "portfolio_loss": -0.05,
            "daily_loss": -0.03
        }
    }
}
```

---

## 🧪 **Step 5: Test Installazione**

### **🔬 Test Componenti Principali**

```bash
# Test 1: Data Collector
python src/data_collector.py --test

# Test 2: RL Agent (quick test)
python src/test_rl.py

# Test 3: Portfolio System
python src/portfolio.py --test

# Test 4: Strategy Engine
python src/strategy_engine.py --test
```

### **📰 Test News Trading System**

```bash
# Test News RSS Collector
python trading-new/news_rss_collector.py --test

# Test Sentiment Analysis
python trading-new/news_sentiment_analyzer.py --test

# Test News Trading AI
python trading-new/news_based_trading_ai.py --test
```

**Output Expected**:
```
✅ RSS Collection: 60+ articles from 6+ sources
✅ Sentiment Analysis: Processing in <0.1s per article  
✅ Trading AI: Signal generation in <0.2s
✅ Complete Cycle: <10s for full analysis
```

---

## 🌐 **Step 6: Verifica Web Interfaces**

### **🖥️ Dashboard Principale**

```bash
# Avvia dashboard principale
python src/web_dashboard.py

# Test accesso
curl http://localhost:5000
# O apri browser: http://localhost:5000
```

### **📰 News Trading Dashboard**

```bash
# Avvia news dashboard
python trading-new/news_web_dashboard.py

# Test accesso
curl http://localhost:5001
# O apri browser: http://localhost:5001
```

### **💻 CLI Interface**

```bash
# Test CLI principale
python src/cli_monitor.py --help

# Test CLI news trading  
python trading-new/news_trading_cli.py --help
```

---

## 📊 **Step 7: Setup Database (Opzionale)**

### **🗄️ SQLite Setup (Default)**

```bash
# Crea database SQLite
python -c "
import sqlite3
conn = sqlite3.connect('data/trading.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY,
        symbol TEXT,
        action TEXT,
        quantity INTEGER,
        price REAL,
        timestamp DATETIME
    )
''')
conn.commit()
conn.close()
print('✅ Database SQLite creato')
"
```

### **🐘 PostgreSQL Setup (Avanzato)**

```bash
# Installa PostgreSQL (Ubuntu)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Crea database
sudo -u postgres createdb stockai
sudo -u postgres psql -c "CREATE USER stockai WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stockai TO stockai;"

# Aggiorna config/settings.json
# "database": {
#     "type": "postgresql",
#     "host": "localhost",
#     "port": 5432,
#     "name": "stockai",
#     "user": "stockai",
#     "password": "your_password"
# }
```

---

## 🔐 **Step 8: Setup API Keys (Opzionale)**

### **📈 Financial Data APIs**

```bash
# Crea file per API keys
touch config/.env

# Edita file .env
nano config/.env
```

```bash
# Alpha Vantage (per dati estesi)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# News APIs
NEWS_API_KEY=your_news_api_key
POLYGON_API_KEY=your_polygon_key

# Discord/Slack (per notifiche)
DISCORD_WEBHOOK_URL=your_discord_webhook
SLACK_WEBHOOK_URL=your_slack_webhook
```

### **🔒 Sicurezza API Keys**

```bash
# Imposta permessi restrittivi
chmod 600 config/.env

# Aggiungi al .gitignore
echo "config/.env" >> .gitignore
echo "config/secrets/" >> .gitignore
```

---

## 🎯 **Step 9: Prima Esecuzione**

### **🚀 Quick Start Test**

```bash
# 1. Raccolta dati iniziale
python src/data_collector.py --symbols AAPL,GOOGL --period 1y

# 2. Training rapido RL Agent
python src/train_rl.py --episodes 100 --quick

# 3. Test ciclo trading completo
python src/main.py --mode test --duration 60

# 4. Test News Trading
python trading-new/news_trading_cli.py cycle
```

### **📊 Verifica Output**

**Logs da controllare**:
```bash
# Log sistema principale
tail -f logs/trading.log

# Log news trading
tail -f data/aggressive_trader.log

# Log performance
tail -f data/performance_history.json
```

**Metriche di successo**:
- ✅ **Data Collection**: Simboli scaricati senza errori
- ✅ **RL Training**: Convergenza loss function
- ✅ **Portfolio**: Valore iniziale corretto
- ✅ **News System**: Articoli raccolti e analizzati
- ✅ **Web Dashboard**: Accessibile e responsive

---

## 🛠️ **Troubleshooting Comune**

### **🐛 Errori Dependencies**

```bash
# Errore: No module named 'torch'
pip install torch torchvision torchaudio

# Errore: SSL certificate error
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>

# Errore: Permission denied
sudo chown -R $USER:$USER /path/to/stock-ai
```

### **📡 Errori Network**

```bash
# Test connettività Yahoo Finance
python -c "import yfinance as yf; print(yf.download('AAPL', period='1d'))"

# Test RSS feeds
python -c "import feedparser; print(len(feedparser.parse('https://feeds.finance.yahoo.com/rss/2.0/headline').entries))"
```

### **🔧 Errori Configurazione**

```bash
# Verifica sintassi JSON
python -c "import json; json.load(open('config/settings.json'))"

# Reset configurazione
cp config/settings.json.example config/settings.json
```

### **💾 Errori Spazio Disco**

```bash
# Pulizia cache
rm -rf data/cache/*
rm -rf logs/*.log

# Verifica spazio
df -h
du -sh data/
```

---

## 🎉 **Step 10: Configurazione Avanzata**

### **🐳 Docker Deployment (Opzionale)**

```bash
# Build Docker image
docker build -t stock-ai .

# Run container
docker run -d -p 5000:5000 -p 5001:5001 --name stock-ai-container stock-ai

# Verifica
docker ps
docker logs stock-ai-container
```

### **🔄 Setup Autostart (Linux)**

```bash
# Crea service systemd
sudo nano /etc/systemd/system/stock-ai.service
```

```ini
[Unit]
Description=Stock AI Trading System
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/stock-ai
ExecStart=/path/to/stock-ai-env/bin/python src/main.py --mode auto
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Abilita e avvia service
sudo systemctl enable stock-ai.service
sudo systemctl start stock-ai.service
sudo systemctl status stock-ai.service
```

### **📊 Monitoring Setup**

```bash
# Installa monitoring tools
pip install psutil prometheus_client

# Setup log rotation
sudo nano /etc/logrotate.d/stock-ai
```

```
/path/to/stock-ai/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 your_username your_username
}
```

---

## ✅ **Checklist Finale**

Verifica che tutti i componenti siano funzionanti:

- [ ] **Environment Python**: Attivato e dependencies installate
- [ ] **Configurazione**: File JSON validati e personalizzati
- [ ] **Data Collection**: Dati storici scaricati per simboli test
- [ ] **RL Agent**: Training completato o model caricato
- [ ] **Portfolio System**: Portfolio virtuale inizializzato
- [ ] **News Trading**: RSS feeds collegati e sentiment funzionante
- [ ] **Web Dashboard**: Entrambe le dashboard accessibili
- [ ] **CLI Tools**: Comandi principali testati
- [ ] **Logging**: Log files creati e accessibili
- [ ] **API Keys**: Configurate se necessarie

---

## 📚 **Next Steps**

Dopo l'installazione, consulta:

1. **[[Quick Start Guide|Quick-Start]]** - Primi passi operativi
2. **[[Configuration Guide|Configuration-Files]]** - Configurazione avanzata
3. **[[User Manual|User-Manual]]** - Guida utente completa
4. **[[API Reference|API-Reference]]** - Documentazione API

---

## 🆘 **Supporto**

In caso di problemi:

1. **Check Logs**: Controlla sempre i file di log
2. **GitHub Issues**: Apri issue sul repository
3. **Wiki Troubleshooting**: Consulta sezione troubleshooting
4. **Community**: Partecipa alle discussioni GitHub

---

*Congratulazioni! 🎉 Il tuo Stock AI Trading System è ora pronto per l'uso!*
