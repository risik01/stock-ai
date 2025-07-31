# 🔌 API Reference - Stock AI Trading System

Documentazione completa delle API REST, WebSocket e interfacce programmatiche del **Stock AI Trading System**.

---

## 📚 **Indice API**

1. [🌐 REST API Endpoints](#-rest-api-endpoints)
2. [📡 WebSocket Streams](#-websocket-streams)
3. [🐍 Python API](#-python-api)
4. [🔧 CLI Commands](#-cli-commands)
5. [📊 Data Formats](#-data-formats)
6. [🔐 Authentication](#-authentication)
7. [⚠️ Error Handling](#-error-handling)
8. [📈 Rate Limiting](#-rate-limiting)

---

## 🌐 **REST API Endpoints**

### **🏠 Main Dashboard API (Port 5000)**

Base URL: `http://localhost:5000/api/v1`

#### **📊 Portfolio Endpoints**

##### **GET /portfolio/status**
Ottieni status completo del portfolio.

```bash
curl -X GET http://localhost:5000/api/v1/portfolio/status
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "total_value": 10247.50,
        "initial_value": 10000.00,
        "total_return": 2.48,
        "daily_return": 0.98,
        "cash": 2150.30,
        "cash_percent": 21.0,
        "positions": [
            {
                "symbol": "AAPL",
                "shares": 28,
                "avg_price": 175.30,
                "current_price": 177.45,
                "market_value": 4968.60,
                "unrealized_pnl": 60.20,
                "pnl_percent": 1.23,
                "weight": 48.5
            }
        ],
        "timestamp": "2023-10-25T14:32:15Z"
    }
}
```

##### **GET /portfolio/positions**
Lista posizioni correnti.

**Parameters**:
- `symbol` (optional): Filtra per simbolo specifico
- `min_value` (optional): Valore minimo posizione

```bash
curl -X GET "http://localhost:5000/api/v1/portfolio/positions?symbol=AAPL"
```

##### **POST /portfolio/trade**
Esegui trade (solo in modalità simulation/paper).

**Request Body**:
```json
{
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "order_type": "MARKET",
    "price": null
}
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "trade_id": "trade_20231025_143215_001",
        "symbol": "AAPL",
        "action": "BUY",
        "quantity": 10,
        "executed_price": 177.45,
        "total_value": 1774.50,
        "transaction_cost": 1.77,
        "timestamp": "2023-10-25T14:32:15Z"
    }
}
```

#### **🤖 RL Agent Endpoints**

##### **GET /rl-agent/status**
Status dell'RL Agent.

```bash
curl -X GET http://localhost:5000/api/v1/rl-agent/status
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "model_loaded": true,
        "model_version": "v2.1",
        "last_update": "2023-10-24T10:30:00Z",
        "training_episodes": 1000,
        "performance_metrics": {
            "sharpe_ratio": 1.24,
            "win_rate": 0.685,
            "avg_return": 0.0034
        },
        "current_epsilon": 0.05,
        "memory_size": 8543,
        "is_training": false
    }
}
```

##### **GET /rl-agent/signals**
Segnali correnti dell'RL Agent.

**Parameters**:
- `symbol` (optional): Simbolo specifico
- `confidence_min` (optional): Confidenza minima (0-1)

```bash
curl -X GET "http://localhost:5000/api/v1/rl-agent/signals?confidence_min=0.7"
```

**Response**:
```json
{
    "status": "success",
    "data": [
        {
            "symbol": "AAPL",
            "signal": "BUY",
            "confidence": 0.78,
            "expected_return": 0.023,
            "risk_score": 0.34,
            "timestamp": "2023-10-25T14:32:15Z",
            "features_used": {
                "price_momentum": 0.12,
                "rsi": 45.6,
                "macd_signal": 0.08
            }
        }
    ]
}
```

##### **POST /rl-agent/retrain**
Avvia retraining del modello.

**Request Body**:
```json
{
    "episodes": 500,
    "symbols": ["AAPL", "GOOGL", "MSFT"],
    "force": false
}
```

#### **📊 Performance Endpoints**

##### **GET /performance/metrics**
Metriche performance dettagliate.

**Parameters**:
- `period`: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `all`
- `benchmark`: `SPY`, `QQQ`, `none`

```bash
curl -X GET "http://localhost:5000/api/v1/performance/metrics?period=1m&benchmark=SPY"
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "period": "1m",
        "portfolio_metrics": {
            "total_return": 5.47,
            "annualized_return": 71.1,
            "sharpe_ratio": 1.24,
            "sortino_ratio": 1.67,
            "max_drawdown": -3.2,
            "volatility": 11.2,
            "win_rate": 65.2
        },
        "benchmark_metrics": {
            "symbol": "SPY",
            "total_return": 2.1,
            "alpha": 3.37,
            "beta": 0.89,
            "correlation": 0.76
        },
        "trade_statistics": {
            "total_trades": 23,
            "profitable_trades": 15,
            "avg_win": 1.23,
            "avg_loss": -0.87,
            "profit_factor": 1.52
        }
    }
}
```

##### **GET /performance/equity-curve**
Dati per equity curve.

```bash
curl -X GET http://localhost:5000/api/v1/performance/equity-curve
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "timestamps": ["2023-09-25T00:00:00Z", "2023-09-26T00:00:00Z"],
        "portfolio_values": [10000.00, 10087.50],
        "benchmark_values": [10000.00, 10021.30],
        "drawdown": [0.0, -0.5],
        "daily_returns": [0.0, 0.875]
    }
}
```

### **📰 News Trading API (Port 5001)**

Base URL: `http://localhost:5001/api/v1`

#### **📡 News Endpoints**

##### **GET /news/latest**
Ultime notizie raccolte.

**Parameters**:
- `limit`: Numero massimo articoli (default: 50)
- `symbol`: Filtra per simbolo
- `source`: Filtra per fonte RSS
- `hours`: Ore passate (default: 24)

```bash
curl -X GET "http://localhost:5001/api/v1/news/latest?limit=10&symbol=AAPL"
```

**Response**:
```json
{
    "status": "success",
    "data": [
        {
            "id": "news_20231025_143200_001",
            "title": "Apple Reports Record Q4 Earnings",
            "summary": "Apple Inc. reported record fourth-quarter earnings...",
            "url": "https://finance.yahoo.com/news/apple-earnings-q4-2023",
            "source": "Yahoo Finance",
            "published": "2023-10-25T14:30:00Z",
            "symbols": ["AAPL"],
            "sentiment": {
                "score": 0.75,
                "confidence": 0.87,
                "methods": {
                    "textblob": 0.65,
                    "vader": 0.82,
                    "financial_dict": 0.78
                }
            },
            "is_breaking": true,
            "impact": "HIGH"
        }
    ],
    "total_count": 234,
    "sources_status": {
        "active": 6,
        "total": 10,
        "last_update": "2023-10-25T14:32:00Z"
    }
}
```

##### **GET /news/breaking**
Breaking news recenti.

```bash
curl -X GET http://localhost:5001/api/v1/news/breaking
```

##### **GET /news/sentiment/{symbol}**
Sentiment aggregato per simbolo.

```bash
curl -X GET http://localhost:5001/api/v1/news/sentiment/AAPL
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "symbol": "AAPL",
        "current_sentiment": {
            "score": 0.35,
            "confidence": 0.82,
            "classification": "POSITIVE",
            "last_update": "2023-10-25T14:32:15Z"
        },
        "sentiment_history": [
            {
                "timestamp": "2023-10-25T14:00:00Z",
                "score": 0.28,
                "article_count": 5
            }
        ],
        "contributing_articles": 12,
        "time_decay_factor": 0.95
    }
}
```

#### **🎯 Trading Signals Endpoints**

##### **GET /signals/current**
Segnali trading correnti basati su news.

```bash
curl -X GET http://localhost:5001/api/v1/signals/current
```

**Response**:
```json
{
    "status": "success",
    "data": [
        {
            "symbol": "AAPL",
            "signal": "STRONG_BUY",
            "confidence": 0.85,
            "sentiment_score": 0.75,
            "news_count": 12,
            "generated_at": "2023-10-25T14:32:15Z",
            "expires_at": "2023-10-25T15:32:15Z",
            "reasoning": [
                "Strong positive sentiment (0.75)",
                "High confidence (0.85)",
                "Multiple confirming articles (12)",
                "Breaking news impact"
            ]
        }
    ]
}
```

##### **POST /signals/webhook**
Webhook per ricevere segnali in tempo reale.

**Request Body** (da configurare nel sistema):
```json
{
    "webhook_url": "http://your-system.com/api/signals",
    "auth_token": "your_auth_token",
    "signal_types": ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL"],
    "min_confidence": 0.7
}
```

### **⚙️ System Endpoints**

##### **GET /system/health**
Health check sistema.

```bash
curl -X GET http://localhost:5000/api/v1/system/health
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "overall_status": "HEALTHY",
        "components": {
            "rl_agent": {"status": "HEALTHY", "response_time": 0.12},
            "news_system": {"status": "WARNING", "active_sources": 6},
            "portfolio": {"status": "HEALTHY", "last_update": "2023-10-25T14:32:15Z"},
            "database": {"status": "HEALTHY", "connection": true}
        },
        "system_metrics": {
            "memory_usage": 75.3,
            "cpu_usage": 23.4,
            "disk_usage": 45.6,
            "uptime": 86400
        }
    }
}
```

---

## 📡 **WebSocket Streams**

### **🔄 Real-time Data Streams**

#### **Portfolio Stream**
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/portfolio');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Portfolio Update:', data);
};

// Message format:
{
    "type": "portfolio_update",
    "data": {
        "total_value": 10247.50,
        "daily_pnl": 97.35,
        "positions": [...]
    },
    "timestamp": "2023-10-25T14:32:15Z"
}
```

#### **Trading Signals Stream**
```javascript
const ws = new WebSocket('ws://localhost:5000/ws/signals');

// Message format:
{
    "type": "new_signal",
    "data": {
        "symbol": "AAPL",
        "signal": "BUY",
        "confidence": 0.78,
        "source": "rl_agent"
    },
    "timestamp": "2023-10-25T14:32:15Z"
}
```

#### **News Stream**
```javascript
const ws = new WebSocket('ws://localhost:5001/ws/news');

// Message format:
{
    "type": "breaking_news",
    "data": {
        "title": "Apple Reports Record Earnings",
        "sentiment": 0.75,
        "symbols": ["AAPL"],
        "impact": "HIGH"
    },
    "timestamp": "2023-10-25T14:32:15Z"
}
```

---

## 🐍 **Python API**

### **📦 Core Classes**

#### **Portfolio Manager**

```python
from src.portfolio import Portfolio

# Initialize portfolio
portfolio = Portfolio(initial_cash=10000)

# Get current status
status = portfolio.get_status()
print(f"Total Value: ${status['total_value']:,.2f}")

# Execute trade
result = portfolio.buy('AAPL', quantity=10, price='market')
print(f"Trade executed: {result['trade_id']}")

# Get positions
positions = portfolio.get_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['shares']} shares")

# Performance metrics
metrics = portfolio.get_performance_metrics(period='1m')
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
```

#### **RL Agent**

```python
from src.rl_agent import RLAgent

# Initialize agent
agent = RLAgent()
agent.load_model('data/rl_model.pkl')

# Get trading signal
signal = agent.get_signal('AAPL')
print(f"Signal: {signal['action']} (confidence: {signal['confidence']:.2f})")

# Get action for current state
state = agent.get_current_state('AAPL')
action = agent.get_action(state)
print(f"Recommended action: {action}")

# Batch signals for multiple symbols
symbols = ['AAPL', 'GOOGL', 'MSFT']
signals = agent.get_batch_signals(symbols)
for symbol, signal in signals.items():
    print(f"{symbol}: {signal['action']}")
```

#### **News Trading System**

```python
from trading_new.news_based_trading_ai import NewsTradingAI

# Initialize news trader
news_trader = NewsTradingAI()

# Collect latest news
news_data = news_trader.collect_news()
print(f"Collected {len(news_data)} articles")

# Analyze sentiment for symbol
sentiment = news_trader.analyze_sentiment('AAPL')
print(f"AAPL Sentiment: {sentiment['score']:.2f}")

# Generate trading signals
signals = news_trader.generate_signals()
for signal in signals:
    print(f"{signal['symbol']}: {signal['action']}")

# Full trading cycle
cycle_result = news_trader.run_cycle()
print(f"Cycle completed in {cycle_result['duration']:.2f}s")
```

#### **Data Collector**

```python
from src.data_collector import DataCollector

# Initialize collector
collector = DataCollector()

# Download data for symbol
data = collector.get_data('AAPL', period='1y', interval='1d')
print(f"Downloaded {len(data)} data points")

# Bulk download
symbols = ['AAPL', 'GOOGL', 'MSFT']
bulk_data = collector.get_bulk_data(symbols, period='6m')

# Real-time price
current_price = collector.get_current_price('AAPL')
print(f"AAPL current price: ${current_price:.2f}")

# Technical indicators
indicators = collector.calculate_indicators('AAPL')
print(f"RSI: {indicators['rsi']:.2f}")
```

### **🔧 Utility Functions**

#### **Configuration Management**

```python
from src.config_manager import ConfigManager

# Load configuration
config = ConfigManager()

# Get specific setting
symbols = config.get('data_collector.symbols')
print(f"Monitored symbols: {symbols}")

# Update setting
config.set('portfolio.max_position_size', 0.15)
config.save()

# Validate configuration
validation_result = config.validate()
if not validation_result['valid']:
    print(f"Config errors: {validation_result['errors']}")
```

#### **Performance Analysis**

```python
from src.performance_analyzer import PerformanceAnalyzer

# Initialize analyzer
analyzer = PerformanceAnalyzer()

# Analyze portfolio performance
metrics = analyzer.analyze_portfolio(portfolio_data, benchmark='SPY')
print(f"Alpha: {metrics['alpha']:.2f}%")
print(f"Beta: {metrics['beta']:.2f}")

# Risk analysis
risk_metrics = analyzer.calculate_risk_metrics(returns_data)
print(f"VaR (95%): ${risk_metrics['var_95']:.2f}")

# Drawdown analysis
drawdown = analyzer.calculate_drawdown(equity_curve)
print(f"Max Drawdown: {drawdown['max_drawdown']:.2f}%")
```

---

## 🔧 **CLI Commands**

### **📊 Portfolio Commands**

```bash
# Portfolio status
python src/portfolio.py --status
python src/portfolio.py --status --json  # JSON output

# Portfolio history
python src/portfolio.py --history --period 1m
python src/portfolio.py --history --trades  # Trade history

# Risk analysis
python src/portfolio.py --risk --detailed

# Performance metrics
python src/portfolio.py --performance --benchmark SPY

# Reset portfolio
python src/portfolio.py --reset --confirm
```

### **🤖 RL Agent Commands**

```bash
# Agent status
python src/rl_agent.py --status
python src/rl_agent.py --status --detailed

# Generate signals
python src/rl_agent.py --signals
python src/rl_agent.py --signals --symbol AAPL

# Model management
python src/rl_agent.py --load_model data/rl_model_v2.pkl
python src/rl_agent.py --save_model data/rl_model_backup.pkl

# Performance evaluation
python src/rl_agent.py --evaluate --period 1y
python src/rl_agent.py --backtest --start 2023-01-01 --end 2023-10-25
```

### **🎓 Training Commands**

```bash
# Standard training
python src/train_rl.py

# Custom training
python src/train_rl.py --episodes 2000 --symbols AAPL,GOOGL,MSFT
python src/train_rl.py --learning_rate 0.0005 --batch_size 64

# Resume training
python src/train_rl.py --resume --episodes 500

# Quick training
python src/train_rl.py --quick --episodes 100
```

### **📰 News Trading Commands**

```bash
# News analysis
python trading-new/news_trading_cli.py news
python trading-new/news_trading_cli.py news --symbol AAPL
python trading-new/news_trading_cli.py news --hours 6

# Trading signals
python trading-new/news_trading_cli.py signals
python trading-new/news_trading_cli.py signals --min_confidence 0.8

# Full cycle
python trading-new/news_trading_cli.py cycle
python trading-new/news_trading_cli.py cycle --symbols AAPL,GOOGL

# Auto mode
python trading-new/news_trading_cli.py auto --interval 300
```

### **🔧 System Commands**

```bash
# System health
python src/system_health.py --check
python src/system_health.py --full_check

# Start/stop system
python src/main.py --start --mode simulation
python src/main.py --stop
python src/main.py --restart

# Backup/restore
python src/backup_manager.py --create --name manual_backup
python src/backup_manager.py --restore --name backup_20231025

# Performance profiling
python src/performance_profiler.py --duration 60s
```

---

## 📊 **Data Formats**

### **📈 Market Data Format**

```json
{
    "symbol": "AAPL",
    "timestamp": "2023-10-25T14:32:15Z",
    "ohlcv": {
        "open": 175.20,
        "high": 177.85,
        "low": 174.90,
        "close": 177.45,
        "volume": 2345678
    },
    "indicators": {
        "sma_20": 172.34,
        "ema_12": 175.67,
        "rsi_14": 45.6,
        "macd": {
            "macd": 0.12,
            "signal": 0.08,
            "histogram": 0.04
        },
        "bollinger_bands": {
            "upper": 180.25,
            "middle": 175.30,
            "lower": 170.35
        }
    }
}
```

### **📰 News Article Format**

```json
{
    "id": "news_20231025_143200_001",
    "title": "Apple Reports Record Q4 Earnings",
    "summary": "Apple Inc. reported record fourth-quarter earnings...",
    "content": "Full article content...",
    "url": "https://finance.yahoo.com/news/apple-earnings-q4-2023",
    "source": {
        "name": "Yahoo Finance",
        "url": "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "reliability": 0.95
    },
    "published": "2023-10-25T14:30:00Z",
    "collected": "2023-10-25T14:32:00Z",
    "symbols": ["AAPL"],
    "categories": ["earnings", "technology"],
    "sentiment": {
        "score": 0.75,
        "confidence": 0.87,
        "classification": "POSITIVE",
        "methods": {
            "textblob": 0.65,
            "vader": 0.82,
            "financial_dict": 0.78
        }
    },
    "is_breaking": true,
    "impact": "HIGH",
    "keywords": ["Apple", "earnings", "Q4", "record", "revenue"]
}
```

### **💰 Trade Format**

```json
{
    "trade_id": "trade_20231025_143215_001",
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "order_type": "MARKET",
    "requested_price": null,
    "executed_price": 177.45,
    "total_value": 1774.50,
    "transaction_cost": 1.77,
    "net_amount": 1776.27,
    "timestamp": "2023-10-25T14:32:15Z",
    "source": "rl_agent",
    "confidence": 0.78,
    "portfolio_impact": {
        "cash_before": 3926.77,
        "cash_after": 2150.50,
        "total_value_before": 10247.50,
        "total_value_after": 10247.50
    },
    "metadata": {
        "signal_timestamp": "2023-10-25T14:32:10Z",
        "processing_time": 0.15,
        "market_conditions": "NORMAL"
    }
}
```

### **📊 Performance Metrics Format**

```json
{
    "period": "1m",
    "start_date": "2023-09-25T00:00:00Z",
    "end_date": "2023-10-25T00:00:00Z",
    "portfolio_metrics": {
        "total_return": 5.47,
        "annualized_return": 71.1,
        "daily_return_mean": 0.18,
        "daily_return_std": 1.87,
        "sharpe_ratio": 1.24,
        "sortino_ratio": 1.67,
        "calmar_ratio": 8.65,
        "max_drawdown": -3.2,
        "max_drawdown_duration": 4,
        "volatility": 11.2,
        "win_rate": 65.2,
        "profit_factor": 1.52
    },
    "benchmark_comparison": {
        "benchmark_symbol": "SPY",
        "benchmark_return": 2.1,
        "alpha": 3.37,
        "beta": 0.89,
        "correlation": 0.76,
        "tracking_error": 4.2,
        "information_ratio": 0.80
    },
    "trade_statistics": {
        "total_trades": 23,
        "profitable_trades": 15,
        "losing_trades": 8,
        "avg_win": 1.23,
        "avg_loss": -0.87,
        "max_win": 3.45,
        "max_loss": -2.1,
        "avg_hold_time": 3.2,
        "avg_trade_return": 0.24
    }
}
```

---

## 🔐 **Authentication**

### **🔑 API Key Authentication**

Per production use, l'API supporta autenticazione via API key:

```bash
# Include API key nell'header
curl -X GET \
  -H "X-API-Key: your_api_key_here" \
  http://localhost:5000/api/v1/portfolio/status
```

### **🎫 JWT Authentication**

```bash
# Login per ottenere JWT token
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}' \
  http://localhost:5000/api/v1/auth/login

# Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
}

# Use token for authenticated requests
curl -X GET \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:5000/api/v1/portfolio/status
```

---

## ⚠️ **Error Handling**

### **📋 Standard Error Format**

```json
{
    "status": "error",
    "error": {
        "code": "INVALID_SYMBOL",
        "message": "Symbol 'INVALID' not found or not supported",
        "details": {
            "supported_symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
            "suggestion": "Check symbol spelling or add to monitored symbols"
        }
    },
    "timestamp": "2023-10-25T14:32:15Z"
}
```

### **🚨 Error Codes**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_SYMBOL` | 400 | Simbolo non valido o non supportato |
| `INSUFFICIENT_FUNDS` | 400 | Fondi insufficienti per trade |
| `INVALID_QUANTITY` | 400 | Quantità non valida |
| `MODEL_NOT_LOADED` | 500 | Modello RL non caricato |
| `DATA_UNAVAILABLE` | 503 | Dati di mercato non disponibili |
| `RATE_LIMITED` | 429 | Tropppe richieste |
| `UNAUTHORIZED` | 401 | Autenticazione richiesta |
| `FORBIDDEN` | 403 | Accesso negato |
| `NOT_FOUND` | 404 | Risorsa non trovata |
| `INTERNAL_ERROR` | 500 | Errore interno server |

### **🔧 Error Handling in Python**

```python
import requests
from requests.exceptions import RequestException

def safe_api_call(url, method='GET', **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API call failed: {e}")
        return None
    except ValueError as e:
        print(f"Invalid JSON response: {e}")
        return None

# Usage
result = safe_api_call('http://localhost:5000/api/v1/portfolio/status')
if result and result['status'] == 'success':
    print(f"Portfolio value: ${result['data']['total_value']:,.2f}")
else:
    print("Failed to get portfolio status")
```

---

## 📈 **Rate Limiting**

### **🚦 Default Limits**

| Endpoint Category | Requests per Minute | Burst Limit |
|------------------|-------------------|-------------|
| **Portfolio** | 60 | 10 |
| **RL Agent** | 120 | 20 |
| **News/Signals** | 180 | 30 |
| **Performance** | 30 | 5 |
| **System** | 30 | 5 |

### **📊 Rate Limit Headers**

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1635180735
X-RateLimit-Burst: 10
```

### **⚠️ Rate Limit Exceeded**

```json
{
    "status": "error",
    "error": {
        "code": "RATE_LIMITED",
        "message": "Rate limit exceeded",
        "details": {
            "limit": 60,
            "reset_time": "2023-10-25T14:45:00Z",
            "retry_after": 45
        }
    }
}
```

---

## 📚 **SDK Examples**

### **🐍 Python SDK Usage**

```python
from stock_ai_sdk import StockAIClient

# Initialize client
client = StockAIClient(
    base_url='http://localhost:5000',
    api_key='your_api_key'  # Optional
)

# Portfolio operations
portfolio = client.portfolio.get_status()
print(f"Total value: ${portfolio.total_value:,.2f}")

# Execute trade
trade_result = client.portfolio.trade(
    symbol='AAPL',
    action='BUY',
    quantity=10
)

# Get RL signals
signals = client.rl_agent.get_signals(min_confidence=0.7)
for signal in signals:
    print(f"{signal.symbol}: {signal.action}")

# News analysis
news = client.news.get_latest(symbol='AAPL', hours=6)
sentiment = client.news.get_sentiment('AAPL')
```

### **🟨 JavaScript SDK Usage**

```javascript
const { StockAIClient } = require('stock-ai-js-sdk');

// Initialize client
const client = new StockAIClient({
    baseUrl: 'http://localhost:5000',
    apiKey: 'your_api_key'
});

// Portfolio status
const portfolio = await client.portfolio.getStatus();
console.log(`Total value: $${portfolio.total_value.toLocaleString()}`);

// Real-time updates via WebSocket
client.portfolio.onUpdate((data) => {
    console.log('Portfolio updated:', data);
});

// Trading signals
const signals = await client.rlAgent.getSignals({ minConfidence: 0.7 });
signals.forEach(signal => {
    console.log(`${signal.symbol}: ${signal.action}`);
});
```

---

## 🔗 **Related Documentation**

- **[[Installation Guide|Installation-Guide]]** - Setup e configurazione
- **[[User Manual|User-Manual]]** - Guida utente completa
- **[[Configuration Files|Configuration-Files]]** - Riferimento configurazione
- **[[Quick Start|Quick-Start]]** - Avvio rapido

---

*Questa documentazione API fornisce tutti gli strumenti necessari per integrare e interagire con il Stock AI Trading System programmaticamente.*
