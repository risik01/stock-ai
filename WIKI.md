# 📚 Stock AI Trading System v2.1 - Wiki Completa

## 📖 Indice

1. [🏗️ Architettura del Sistema](#-architettura-del-sistema)
2. [🧠 Dual AI Architecture](#-dual-ai-architecture)
3. [📊 Moduli Principali](#-moduli-principali)
4. [🔧 Configurazione Dettagliata](#-configurazione-dettagliata)
5. [📈 Dashboard e Monitoring](#-dashboard-e-monitoring)
6. [🎯 Strategie di Trading](#-strategie-di-trading)
7. [🔒 Risk Management](#-risk-management)
8. [🧪 Testing e Debugging](#-testing-e-debugging)
9. [⚡ Performance e Ottimizzazioni](#-performance-e-ottimizzazioni)
10. [🔄 Deployment e Produzione](#-deployment-e-produzione)

---

## 🏗️ Architettura del Sistema

### Overview Generale
Il Stock AI Trading System v2.1 è costruito con un'architettura modulare che separa chiaramente le responsabilità:

```
┌─────────────────────────────────────────────────────────────┐
│                    🚀 LAUNCHER LAYER                        │
│              (launcher.py - Command Interface)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    🧠 AI LAYER                               │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│    │   Price AI  │  │   News AI   │  │ Training AI │       │
│    │   (10s)     │  │   (10min)   │  │ (Background)│       │
│    └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   📊 DATA LAYER                              │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐     │
│  │ Real-time     │ │ Market Data   │ │ News Data     │     │
│  │ Collector     │ │ API           │ │ Sentiment     │     │
│  └───────────────┘ └───────────────┘ └───────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  💼 TRADING LAYER                            │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐     │
│  │ Portfolio     │ │ Strategy      │ │ Risk          │     │
│  │ Manager       │ │ Engine        │ │ Manager       │     │
│  └───────────────┘ └───────────────┘ └───────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  📈 PRESENTATION LAYER                       │
│         ┌─────────────┐           ┌─────────────┐           │
│         │ Streamlit   │           │ Terminal    │           │
│         │ Dashboard   │           │ Interface   │           │
│         └─────────────┘           └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Flusso Dati Principale

1. **Data Collection**: `realtime_data.py` raccoglie dati da Yahoo Finance
2. **AI Processing**: Dual AI analizza prezzi e sentiment
3. **Decision Making**: `strategy_engine.py` combina segnali AI
4. **Trade Execution**: `portfolio.py` gestisce le operazioni
5. **Monitoring**: Dashboard visualizza risultati in tempo reale

---

## 🧠 Dual AI Architecture

### 🔥 Price AI (High-Frequency)
**Interval**: 10 secondi  
**Scope**: Analisi tecnica dei prezzi

#### Algoritmi Implementati:
- **Moving Averages**: SMA, EMA, MACD
- **Momentum Indicators**: RSI, Stochastic
- **Volatility Analysis**: Bollinger Bands, ATR
- **Pattern Recognition**: Support/Resistance, Breakouts

#### Input Features:
```python
price_features = {
    'current_price': float,
    'volume': int,
    'price_change': float,
    'price_change_pct': float,
    'volatility': float,
    'technical_indicators': {
        'rsi': float,
        'macd': float,
        'bollinger_position': float
    }
}
```

#### Output Signals:
- `BUY`: Segnale di acquisto (score > 0.3)
- `SELL`: Segnale di vendita (score < -0.3)
- `HOLD`: Nessuna azione (-0.3 ≤ score ≤ 0.3)

### 📰 News AI (Low-Frequency)
**Interval**: 10 minuti  
**Scope**: Analisi sentiment delle notizie

#### Data Sources:
- Financial news feeds
- Social media sentiment
- Market announcements
- Economic indicators

#### Processing Pipeline:
1. **News Collection**: Raccolta notizie per simbolo
2. **Text Processing**: Pulizia e preprocessing
3. **Sentiment Analysis**: NLP per sentiment score
4. **Impact Assessment**: Valutazione impatto su prezzo

#### Sentiment Scoring:
```python
sentiment_scores = {
    'very_positive': 0.8,    # Strong buy signal
    'positive': 0.4,         # Weak buy signal
    'neutral': 0.0,          # No influence
    'negative': -0.4,        # Weak sell signal
    'very_negative': -0.8    # Strong sell signal
}
```

### 🔄 Signal Combination
Il sistema combina i segnali usando una weighted average:

```python
def combine_signals(price_signal, news_signal, price_weight=0.7, news_weight=0.3):
    combined_score = (price_signal * price_weight) + (news_signal * news_weight)
    
    if combined_score > 0.3:
        return 'BUY'
    elif combined_score < -0.3:
        return 'SELL'
    else:
        return 'HOLD'
```

---

## 📊 Moduli Principali

### 1. `launcher.py` - Command Interface
**Responsabilità**: Entry point unificato per tutte le operazioni

#### Comandi Disponibili:
```bash
python launcher.py trade [--aggressive] [--live] [--symbols SYMBOL...]
python launcher.py train [--days N] [--symbols SYMBOL...]
python launcher.py dashboard
python launcher.py test [realtime|api|dual-ai|training]
python launcher.py status
python launcher.py smart [--aggressive]
```

#### Funzionalità:
- **Argument Parsing**: Gestione parametri command-line
- **Environment Setup**: Configurazione virtual environment
- **Process Management**: Avvio e gestione processi
- **Error Handling**: Gestione errori globali

### 2. `src/dual_ai_system.py` - Core AI Engine
**Responsabilità**: Implementazione dual AI e logica di trading

#### Classi Principali:
```python
class DualAITradingSystem:
    def __init__(self, config):
        self.price_ai = PriceAnalysisAI()
        self.news_ai = NewsAnalysisAI()
        self.strategy_engine = StrategyEngine()
        self.portfolio = Portfolio()
    
    async def run_trading_loop(self):
        # Main trading loop con dual AI
```

#### Features:
- **Async Processing**: Loop di trading asincrono
- **Signal Generation**: Generazione segnali combinati
- **Error Recovery**: Recupero automatico da errori
- **Graceful Shutdown**: Arresto sicuro con CTRL+C

### 3. `src/realtime_data.py` - Data Collection
**Responsabilità**: Raccolta dati real-time con fallback simulation

#### Data Sources:
- **Primary**: Yahoo Finance API
- **Fallback**: Realistic price simulation
- **Caching**: Local cache per performance

#### Implementazione:
```python
class RealTimeDataCollector:
    def __init__(self):
        self.yf_client = yfinance.Client()
        self.cache = PriceCache()
        self.simulator = PriceSimulator()
    
    def get_current_price(self, symbol):
        try:
            return self.yf_client.get_current_price(symbol)
        except:
            return self.simulator.simulate_price(symbol)
```

### 4. `src/ai_background_trainer.py` - Training System
**Responsabilità**: Training continuo dell'AI

#### Training Pipeline:
1. **Data Collection**: Raccolta dati storici
2. **Feature Engineering**: Creazione features per ML
3. **Model Training**: Training modelli AI
4. **Knowledge Persistence**: Salvataggio conoscenze apprese

#### Knowledge Base:
```python
class AIKnowledgeBase:
    def __init__(self):
        self.market_patterns = {}
        self.trading_performance = {}
        self.learned_correlations = {}
    
    def update_knowledge(self, market_observation):
        # Aggiorna conoscenze con nuove osservazioni
```

### 5. `dashboard/live_dashboard.py` - Web Interface
**Responsabilità**: Interfaccia web per monitoring

#### Components:
- **Real-time Metrics**: Portfolio value, P&L, trades
- **Data Visualization**: Charts, tables, graphs
- **Interactive Controls**: Refresh, filters, settings
- **Debug Information**: System status, logs

---

## 🔧 Configurazione Dettagliata

### `config/settings.json`
Configurazione generale del sistema:

```json
{
    "system": {
        "version": "2.1",
        "environment": "development",
        "logging_level": "INFO"
    },
    "ai": {
        "price_ai_interval": 10,
        "news_ai_interval": 600,
        "training_enabled": true,
        "model_persistence": true
    },
    "market": {
        "trading_hours": {
            "start": "09:30",
            "end": "16:00",
            "timezone": "US/Eastern"
        },
        "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"],
        "data_sources": {
            "primary": "yahoo_finance",
            "fallback": "simulation"
        }
    },
    "dashboard": {
        "auto_refresh": true,
        "refresh_interval": 3,
        "port": 8501
    }
}
```

### `config/trading_config.json`
Configurazione specifica per trading:

```json
{
    "portfolio": {
        "initial_balance": 1000.0,
        "currency": "USD",
        "commission_rate": 0.001
    },
    "risk_management": {
        "max_position_size": 0.1,
        "stop_loss_pct": 0.05,
        "take_profit_pct": 0.10,
        "max_daily_loss": 0.02,
        "risk_tolerance": "medium"
    },
    "trading_rules": {
        "min_trade_amount": 10.0,
        "max_trades_per_day": 50,
        "allow_short_selling": false,
        "require_confirmation": false
    },
    "ai_settings": {
        "price_weight": 0.7,
        "news_weight": 0.3,
        "confidence_threshold": 0.3,
        "learning_rate": 0.01
    }
}
```

### Environment Variables
```bash
# Opzionali per produzione
export STOCK_AI_ENV=production
export STOCK_AI_LOG_LEVEL=WARNING
export STOCK_AI_DATA_SOURCE=live
export STOCK_AI_DASHBOARD_PORT=8501
```

---

## 📈 Dashboard e Monitoring

### Live Dashboard Features

#### 1. **Main Metrics Panel**
- **Portfolio Value**: Valore totale real-time
- **P&L**: Profitti/perdite con percentuale
- **Total Trades**: Contatore operazioni
- **Open Positions**: Posizioni attualmente aperte
- **Cash Available**: Liquidità disponibile

#### 2. **Trading Activity**
- **Recent Trades Table**: Ultime 20 operazioni
- **Open Positions Table**: Posizioni correnti
- **Trading Signals**: Segnali AI in tempo reale

#### 3. **Performance Charts**
- **P&L Timeline**: Grafico profitti/perdite nel tempo
- **Price Charts**: Prezzi real-time con indicatori
- **Volume Analysis**: Analisi volumi di trading

#### 4. **System Monitoring**
- **AI Status**: Stato dei moduli AI
- **Data Source Status**: Stato connessioni dati
- **System Resources**: CPU, memoria, network

### Dashboard Architecture
```python
# dashboard/live_dashboard.py
def main():
    # Setup Streamlit
    st.set_page_config(...)
    
    # Data Collection
    data = parse_trading_log()
    
    # UI Components
    render_main_metrics(data)
    render_trading_activity(data)
    render_performance_charts(data)
    render_system_status(data)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(3)
        st.rerun()
```

### Custom Components

#### Real-time Price Chart
```python
def create_price_chart(symbol, data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['timestamps'],
        y=data['prices'],
        mode='lines+markers',
        name=f'{symbol} Price'
    ))
    return fig
```

#### P&L Performance Chart
```python
def create_pnl_chart(trades_data):
    cumulative_pnl = calculate_cumulative_pnl(trades_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cumulative_pnl['timestamps'],
        y=cumulative_pnl['values'],
        fill='tonexty',
        name='Cumulative P&L'
    ))
    return fig
```

---

## 🎯 Strategie di Trading

### 1. **Momentum Strategy**
Strategia basata su momentum dei prezzi:

```python
class MomentumStrategy:
    def __init__(self, lookback_period=20):
        self.lookback_period = lookback_period
    
    def generate_signal(self, price_data):
        momentum = calculate_momentum(price_data, self.lookback_period)
        
        if momentum > 0.02:  # 2% momentum positivo
            return 'BUY'
        elif momentum < -0.02:  # 2% momentum negativo
            return 'SELL'
        else:
            return 'HOLD'
```

### 2. **Mean Reversion Strategy**
Strategia di ritorno alla media:

```python
class MeanReversionStrategy:
    def __init__(self, window=50, threshold=2.0):
        self.window = window
        self.threshold = threshold
    
    def generate_signal(self, price_data):
        mean = price_data.rolling(self.window).mean()
        std = price_data.rolling(self.window).std()
        z_score = (price_data.iloc[-1] - mean.iloc[-1]) / std.iloc[-1]
        
        if z_score > self.threshold:
            return 'SELL'  # Prezzo troppo alto
        elif z_score < -self.threshold:
            return 'BUY'   # Prezzo troppo basso
        else:
            return 'HOLD'
```

### 3. **News Sentiment Strategy**
Strategia basata su sentiment delle notizie:

```python
class NewsSentimentStrategy:
    def __init__(self, sentiment_threshold=0.1):
        self.sentiment_threshold = sentiment_threshold
    
    def generate_signal(self, news_sentiment):
        if news_sentiment > self.sentiment_threshold:
            return 'BUY'
        elif news_sentiment < -self.sentiment_threshold:
            return 'SELL'
        else:
            return 'HOLD'
```

### 4. **Combined Strategy**
Strategia che combina multiple fonti:

```python
class CombinedStrategy:
    def __init__(self):
        self.momentum = MomentumStrategy()
        self.mean_reversion = MeanReversionStrategy()
        self.news_sentiment = NewsSentimentStrategy()
    
    def generate_signal(self, price_data, news_data):
        signals = {
            'momentum': self.momentum.generate_signal(price_data),
            'mean_reversion': self.mean_reversion.generate_signal(price_data),
            'news': self.news_sentiment.generate_signal(news_data)
        }
        
        return self.combine_signals(signals)
```

---

## 🔒 Risk Management

### 1. **Position Sizing**
Controllo dimensioni posizioni:

```python
class PositionSizer:
    def __init__(self, max_position_pct=0.1, risk_per_trade=0.02):
        self.max_position_pct = max_position_pct
        self.risk_per_trade = risk_per_trade
    
    def calculate_position_size(self, portfolio_value, entry_price, stop_loss):
        # Kelly Criterion based sizing
        risk_amount = portfolio_value * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        position_size = risk_amount / price_risk
        
        # Limit to max position percentage
        max_position_value = portfolio_value * self.max_position_pct
        max_shares = max_position_value / entry_price
        
        return min(position_size, max_shares)
```

### 2. **Stop Loss Management**
Gestione stop loss dinamici:

```python
class StopLossManager:
    def __init__(self, initial_stop_pct=0.05, trailing_stop_pct=0.03):
        self.initial_stop_pct = initial_stop_pct
        self.trailing_stop_pct = trailing_stop_pct
    
    def update_stop_loss(self, position, current_price):
        if position['type'] == 'LONG':
            # Trailing stop per posizioni long
            new_stop = current_price * (1 - self.trailing_stop_pct)
            position['stop_loss'] = max(position['stop_loss'], new_stop)
        else:
            # Trailing stop per posizioni short
            new_stop = current_price * (1 + self.trailing_stop_pct)
            position['stop_loss'] = min(position['stop_loss'], new_stop)
```

### 3. **Portfolio Risk Monitoring**
Monitoraggio rischio portfolio:

```python
class RiskMonitor:
    def __init__(self, max_drawdown=0.10, max_correlation=0.7):
        self.max_drawdown = max_drawdown
        self.max_correlation = max_correlation
    
    def check_portfolio_risk(self, portfolio):
        # Check drawdown
        current_drawdown = self.calculate_drawdown(portfolio)
        if current_drawdown > self.max_drawdown:
            return {'risk_level': 'HIGH', 'action': 'REDUCE_POSITIONS'}
        
        # Check correlation
        correlation = self.calculate_position_correlation(portfolio)
        if correlation > self.max_correlation:
            return {'risk_level': 'MEDIUM', 'action': 'DIVERSIFY'}
        
        return {'risk_level': 'LOW', 'action': 'CONTINUE'}
```

---

## 🧪 Testing e Debugging

### 1. **Unit Tests**
Test per singoli componenti:

```python
# tests/test_ai_system.py
import unittest
from src.dual_ai_system import DualAITradingSystem

class TestDualAISystem(unittest.TestCase):
    def setUp(self):
        self.ai_system = DualAITradingSystem()
    
    def test_price_analysis(self):
        # Test price AI
        price_data = self.generate_test_price_data()
        signal = self.ai_system.price_ai.analyze(price_data)
        self.assertIn(signal, ['BUY', 'SELL', 'HOLD'])
    
    def test_news_analysis(self):
        # Test news AI
        news_data = self.generate_test_news_data()
        sentiment = self.ai_system.news_ai.analyze(news_data)
        self.assertIsInstance(sentiment, float)
```

### 2. **Integration Tests**
Test per integrazione componenti:

```python
# tests/test_integration.py
def test_full_trading_cycle():
    """Test completo ciclo di trading"""
    # Setup
    system = DualAITradingSystem()
    
    # Simulate market data
    market_data = generate_market_data()
    
    # Run trading cycle
    result = system.process_market_data(market_data)
    
    # Verify results
    assert 'signal' in result
    assert 'confidence' in result
    assert result['signal'] in ['BUY', 'SELL', 'HOLD']
```

### 3. **Performance Tests**
Test per performance:

```python
# tests/test_performance.py
import time
import pytest

def test_ai_response_time():
    """Test tempo di risposta AI"""
    ai_system = DualAITradingSystem()
    
    start_time = time.time()
    signal = ai_system.generate_signal(test_data)
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 1.0  # Massimo 1 secondo
```

### 4. **Debugging Tools**

#### Log Analysis
```python
# tools/log_analyzer.py
def analyze_trading_logs(log_file):
    """Analizza log di trading per pattern e errori"""
    with open(log_file, 'r') as f:
        logs = f.readlines()
    
    # Analisi pattern
    trades = extract_trades(logs)
    errors = extract_errors(logs)
    performance = calculate_performance(trades)
    
    return {
        'total_trades': len(trades),
        'win_rate': performance['win_rate'],
        'avg_return': performance['avg_return'],
        'errors': errors
    }
```

#### Performance Profiler
```python
# tools/profiler.py
import cProfile
import pstats

def profile_trading_session():
    """Profila performance sessione trading"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run trading session
    run_trading_session()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 funzioni per tempo
```

---

## ⚡ Performance e Ottimizzazioni

### 1. **Caching Strategy**
Sistema di cache multi-livello:

```python
# src/cache_manager.py
class CacheManager:
    def __init__(self):
        self.memory_cache = {}  # Cache in memoria
        self.file_cache = FileCache('data/cache/')  # Cache su file
        self.redis_cache = RedisCache()  # Cache distribuita (opzionale)
    
    def get(self, key):
        # Try memory first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Try file cache
        data = self.file_cache.get(key)
        if data:
            self.memory_cache[key] = data
            return data
        
        return None
    
    def set(self, key, value, ttl=300):
        self.memory_cache[key] = value
        self.file_cache.set(key, value, ttl)
```

### 2. **Async Processing**
Elaborazione asincrona per performance:

```python
# src/async_processor.py
import asyncio
import aiohttp

class AsyncDataProcessor:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def fetch_multiple_symbols(self, symbols):
        tasks = []
        for symbol in symbols:
            task = self.fetch_symbol_data(symbol)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return dict(zip(symbols, results))
    
    async def fetch_symbol_data(self, symbol):
        url = f"https://api.example.com/data/{symbol}"
        async with self.session.get(url) as response:
            return await response.json()
```

### 3. **Memory Optimization**
Gestione efficiente della memoria:

```python
# src/memory_manager.py
import gc
import psutil

class MemoryManager:
    def __init__(self, max_memory_mb=512):
        self.max_memory_mb = max_memory_mb
    
    def check_memory_usage(self):
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb > self.max_memory_mb:
            self.cleanup_memory()
        
        return memory_mb
    
    def cleanup_memory(self):
        # Clear caches
        self.clear_data_caches()
        
        # Force garbage collection
        gc.collect()
        
        # Clear old model weights
        self.cleanup_ai_models()
```

### 4. **Database Optimization**
Ottimizzazioni per storage dati:

```python
# src/database_optimizer.py
import sqlite3
import json

class OptimizedDataStorage:
    def __init__(self, db_path='data/trading.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON trades(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol 
            ON trades(symbol)
        ''')
        
        conn.close()
    
    def batch_insert_trades(self, trades):
        """Inserimento batch per performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executemany('''
            INSERT INTO trades (timestamp, symbol, action, quantity, price)
            VALUES (?, ?, ?, ?, ?)
        ''', trades)
        
        conn.commit()
        conn.close()
```

---

## 🔄 Deployment e Produzione

### 1. **Environment Setup**
Setup per ambiente di produzione:

```bash
#!/bin/bash
# scripts/setup_production.sh

# System dependencies
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv git

# Create production user
sudo useradd -m -s /bin/bash stockai
sudo usermod -aG sudo stockai

# Setup application
cd /opt
sudo git clone https://github.com/risik01/stock-ai.git
sudo chown -R stockai:stockai stock-ai

# Setup virtual environment
sudo -u stockai python3.12 -m venv /opt/stock-ai/.venv
sudo -u stockai /opt/stock-ai/.venv/bin/pip install -r /opt/stock-ai/requirements.txt

# Setup systemd service
sudo cp /opt/stock-ai/scripts/stockai.service /etc/systemd/system/
sudo systemctl enable stockai
sudo systemctl start stockai
```

### 2. **Systemd Service**
Servizio per esecuzione automatica:

```ini
# scripts/stockai.service
[Unit]
Description=Stock AI Trading System
After=network.target

[Service]
Type=simple
User=stockai
WorkingDirectory=/opt/stock-ai
Environment=PATH=/opt/stock-ai/.venv/bin
ExecStart=/opt/stock-ai/.venv/bin/python launcher.py trade --live
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. **Monitoring e Alerting**
Sistema di monitoraggio:

```python
# src/monitoring.py
import smtplib
import requests
from email.mime.text import MIMEText

class MonitoringSystem:
    def __init__(self, config):
        self.config = config
        self.alerts_enabled = config.get('alerts_enabled', True)
    
    def check_system_health(self):
        """Controlla salute del sistema"""
        checks = {
            'ai_system': self.check_ai_system(),
            'data_feeds': self.check_data_feeds(),
            'portfolio': self.check_portfolio_health(),
            'memory': self.check_memory_usage(),
            'disk_space': self.check_disk_space()
        }
        
        failed_checks = [k for k, v in checks.items() if not v]
        
        if failed_checks and self.alerts_enabled:
            self.send_alert(f"System health check failed: {failed_checks}")
        
        return all(checks.values())
    
    def send_alert(self, message):
        """Invia alert via email/Slack"""
        if self.config.get('email_alerts'):
            self.send_email_alert(message)
        
        if self.config.get('slack_webhook'):
            self.send_slack_alert(message)
    
    def send_slack_alert(self, message):
        webhook_url = self.config['slack_webhook']
        payload = {'text': f"🚨 Stock AI Alert: {message}"}
        requests.post(webhook_url, json=payload)
```

### 4. **Backup Strategy**
Sistema di backup automatico:

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backup/stock-ai"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="stockai_backup_${DATE}.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application data
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    /opt/stock-ai/data/ \
    /opt/stock-ai/config/ \
    /opt/stock-ai/logs/

# Keep only last 30 backups
cd $BACKUP_DIR
ls -t stockai_backup_*.tar.gz | tail -n +31 | xargs -r rm

# Upload to cloud (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$AWS_S3_BUCKET/backups/"
fi
```

### 5. **Security Hardening**
Configurazioni di sicurezza:

```bash
#!/bin/bash
# scripts/security_hardening.sh

# Firewall setup
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8501  # Dashboard port

# File permissions
chmod 700 /opt/stock-ai/config/
chmod 600 /opt/stock-ai/config/*.json
chmod 755 /opt/stock-ai/scripts/*.sh

# Log rotation
sudo tee /etc/logrotate.d/stockai << EOF
/opt/stock-ai/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF
```

### 6. **Performance Monitoring**
Monitoraggio performance in produzione:

```python
# src/performance_monitor.py
import time
import psutil
import logging
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    network_io: dict
    trade_latency: float
    ai_processing_time: float

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.logger = logging.getLogger('performance')
    
    def collect_metrics(self):
        """Raccoglie metriche di performance"""
        process = psutil.Process()
        
        metrics = PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            network_io=psutil.net_io_counters()._asdict(),
            trade_latency=self.measure_trade_latency(),
            ai_processing_time=self.measure_ai_processing_time()
        )
        
        self.metrics_history.append(metrics)
        self.log_metrics(metrics)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    def get_performance_summary(self):
        """Genera summary delle performance"""
        if not self.metrics_history:
            return None
        
        recent_metrics = self.metrics_history[-100:]  # Ultime 100 metriche
        
        return {
            'avg_cpu': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_mb for m in recent_metrics) / len(recent_metrics),
            'avg_trade_latency': sum(m.trade_latency for m in recent_metrics) / len(recent_metrics),
            'avg_ai_processing': sum(m.ai_processing_time for m in recent_metrics) / len(recent_metrics)
        }
```

---

## 📝 Best Practices

### 1. **Code Quality**
- Seguire PEP 8 per style guide Python
- Usare type hints per migliore documentazione
- Implementare docstrings per tutte le funzioni pubbliche
- Utilizzare logging appropriato invece di print statements

### 2. **Error Handling**
- Implementare try/except specifici per diversi tipi di errore
- Utilizzare custom exceptions per errori applicazione-specifici
- Implementare retry logic per operazioni network
- Loggare errori con context appropriato

### 3. **Testing**
- Mantenere coverage > 80% per codice critico
- Utilizzare mock per external dependencies
- Implementare integration tests per flussi completi
- Eseguire performance tests regolarmente

### 4. **Security**
- Non committare mai credenziali in version control
- Utilizzare environment variables per configurazioni sensibili
- Implementare rate limiting per API calls
- Validare sempre input utente

### 5. **Performance**
- Profilare codice regolarmente per identificare bottlenecks
- Utilizzare appropriate data structures per ogni use case
- Implementare caching per operazioni costose
- Ottimizzare query database e API calls

---

## 🆘 Troubleshooting Avanzato

### Problemi Comuni e Soluzioni

#### 1. **High Memory Usage**
```python
# Diagnostic script
def diagnose_memory_issue():
    import tracemalloc
    tracemalloc.start()
    
    # Run problematic code
    run_trading_session()
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    
    tracemalloc.stop()
```

#### 2. **Slow AI Processing**
```python
# Performance optimization
def optimize_ai_processing():
    # Use batch processing
    def process_batch(data_batch):
        return [ai_model.predict(item) for item in data_batch]
    
    # Parallel processing
    from concurrent.futures import ThreadPoolExecutor
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_batch, batch) for batch in data_batches]
        results = [future.result() for future in futures]
```

#### 3. **Dashboard Connection Issues**
```bash
# Network diagnostic
netstat -tulpn | grep :8501
curl -v http://localhost:8501/healthz
ping -c 4 localhost
```

---

**📞 Support**: Per supporto aggiuntivo, aprire issue su GitHub con log dettagliati e descrizione del problema.

**🔗 Links**:
- [Repository GitHub](https://github.com/risik01/stock-ai)
- [Issue Tracker](https://github.com/risik01/stock-ai/issues)
- [Discussions](https://github.com/risik01/stock-ai/discussions)
