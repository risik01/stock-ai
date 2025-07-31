# 📁 File di Configurazione - Guida Completa

Il sistema Stock AI utilizza diversi file di configurazione per personalizzare il comportamento. Questa guida spiega tutti i parametri disponibili.

## 📂 **Struttura File di Configurazione**

```
config/
├── settings.json          # Configurazione principale
└── trading_config.json    # Configurazione trading specifica
```

---

## ⚙️ **config/settings.json - Configurazione Principale**

### **📊 Sezione `data_collection`**

```json
{
  "data_collection": {
    "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
    "period": "1y",
    "interval": "1d",
    "max_retries": 3,
    "delay_between_requests": 1.0,
    "data_source": "yfinance",
    "cache_enabled": true,
    "cache_duration": 3600
  }
}
```

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `symbols` | Array | `["AAPL", "GOOGL", ...]` | **Simboli azionari da monitorare**. Lista dei ticker da analizzare e tradare |
| `period` | String | `"1y"` | **Periodo dati storici**. Valori: `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max` |
| `interval` | String | `"1d"` | **Intervallo temporale**. Valori: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo` |
| `max_retries` | Integer | `3` | **Tentativi massimi** per richieste fallite |
| `delay_between_requests` | Float | `1.0` | **Delay tra richieste** (secondi) per rispettare rate limits |
| `data_source` | String | `"yfinance"` | **Fonte dati**. Attualmente supporta: `yfinance` |
| `cache_enabled` | Boolean | `true` | **Abilita cache** per ridurre richieste API |
| `cache_duration` | Integer | `3600` | **Durata cache** in secondi (3600 = 1 ora) |

### **💰 Sezione `trading`**

```json
{
  "trading": {
    "initial_balance": 100000.0,
    "max_position_size": 0.1,
    "transaction_cost": 0.001,
    "risk_tolerance": 0.02,
    "live_trading": {
      "enabled": false,
      "check_interval": 300,
      "market_hours_only": true,
      "max_trades_per_day": 20,
      "min_trade_interval": 60,
      "risk_per_trade": 0.02
    }
  }
}
```

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `initial_balance` | Float | `100000.0` | **Capitale iniziale** in dollari per simulazione |
| `max_position_size` | Float | `0.1` | **Dimensione massima posizione** (10% del portfolio) |
| `transaction_cost` | Float | `0.001` | **Costo transazione** (0.1% per trade) |
| `risk_tolerance` | Float | `0.02` | **Tolleranza rischio** globale (2% del portfolio) |

#### **🔴 Sottosezione `live_trading`**

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `enabled` | Boolean | `false` | **⚠️ TRADING REALE ABILITATO**. Cambiare solo se si vuole trading reale! |
| `check_interval` | Integer | `300` | **Intervallo controlli** (secondi) per monitoring continuo |
| `market_hours_only` | Boolean | `true` | **Solo orari mercato**. Trading limitato agli orari di apertura |
| `max_trades_per_day` | Integer | `20` | **Limite trades giornalieri** per controllo rischio |
| `min_trade_interval` | Integer | `60` | **Intervallo minimo tra trades** (secondi) |
| `risk_per_trade` | Float | `0.02` | **Rischio per singolo trade** (2% del portfolio) |

### **🤖 Sezione `ml` (Machine Learning)**

```json
{
  "ml": {
    "training_episodes": 1000,
    "batch_size": 64,
    "learning_rate": 0.0003,
    "algorithms": ["PPO", "SAC", "TD3", "A2C"],
    "ensemble_enabled": true,
    "hyperparameter_optimization": {
      "enabled": true,
      "n_trials": 100,
      "timeout": 3600
    },
    "model_selection": {
      "validation_split": 0.2,
      "cross_validation": true,
      "metric": "sharpe_ratio"
    }
  }
}
```

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `training_episodes` | Integer | `1000` | **Episodi training** per algoritmi RL |
| `batch_size` | Integer | `64` | **Dimensione batch** per training |
| `learning_rate` | Float | `0.0003` | **Learning rate** per ottimizzatori |
| `algorithms` | Array | `["PPO", "SAC", "TD3", "A2C"]` | **Algoritmi RL attivi** |
| `ensemble_enabled` | Boolean | `true` | **Abilita ensemble** di modelli |

#### **🔧 Sottosezione `hyperparameter_optimization`**

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `enabled` | Boolean | `true` | **Ottimizzazione hyperparameter** con Optuna |
| `n_trials` | Integer | `100` | **Numero tentativi** ottimizzazione |
| `timeout` | Integer | `3600` | **Timeout ottimizzazione** (secondi) |

### **📊 Sezione `monitoring`**

```json
{
  "monitoring": {
    "price_alerts": true,
    "volume_alerts": true,
    "technical_indicators": ["RSI", "MACD", "BB"],
    "alert_thresholds": {
      "rsi_oversold": 30,
      "rsi_overbought": 70,
      "volume_spike": 2.0,
      "price_change": 0.05
    },
    "notifications": {
      "email_enabled": false,
      "webhook_enabled": false,
      "console_enabled": true
    }
  }
}
```

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `price_alerts` | Boolean | `true` | **Alert variazioni prezzo** significative |
| `volume_alerts` | Boolean | `true` | **Alert spike volume** anomali |
| `technical_indicators` | Array | `["RSI", "MACD", "BB"]` | **Indicatori tecnici** da monitorare |

#### **📈 Sottosezione `alert_thresholds`**

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `rsi_oversold` | Float | `30` | **RSI oversold** (segnale possibile acquisto) |
| `rsi_overbought` | Float | `70` | **RSI overbought** (segnale possibile vendita) |
| `volume_spike` | Float | `2.0` | **Moltiplicatore volume** per spike detection |
| `price_change` | Float | `0.05` | **Variazione prezzo** (5%) per alert |

---

## 🎯 **config/trading_config.json - Configurazione Trading**

### **📋 Sezione `strategies`**

```json
{
  "strategies": {
    "default": {
      "name": "RL_Ensemble",
      "type": "reinforcement_learning",
      "risk_level": "medium",
      "rebalance_frequency": "daily",
      "enabled": true,
      "weight": 0.7
    },
    "news_sentiment": {
      "name": "News_Sentiment",
      "type": "sentiment_analysis",
      "risk_level": "medium",
      "rebalance_frequency": "hourly",
      "enabled": true,
      "weight": 0.3
    }
  }
}
```

| Parametro | Tipo | Valori | Descrizione |
|-----------|------|--------|-------------|
| `name` | String | Custom | **Nome strategia** identificativo |
| `type` | String | `reinforcement_learning`, `sentiment_analysis`, `technical_analysis` | **Tipo strategia** |
| `risk_level` | String | `low`, `medium`, `high` | **Livello rischio** strategia |
| `rebalance_frequency` | String | `minute`, `hourly`, `daily`, `weekly` | **Frequenza ribilanciamento** |
| `enabled` | Boolean | `true`/`false` | **Strategia attiva** |
| `weight` | Float | `0.0-1.0` | **Peso strategia** in ensemble (totale deve = 1.0) |

### **🛡️ Sezione `risk_management`**

```json
{
  "risk_management": {
    "max_drawdown": 0.15,
    "stop_loss": 0.05,
    "take_profit": 0.15,
    "var_confidence": 0.95,
    "position_sizing": {
      "method": "kelly_criterion",
      "max_leverage": 1.0,
      "concentration_limit": 0.25
    },
    "portfolio_protection": {
      "circuit_breaker": true,
      "max_daily_loss": 0.03,
      "correlation_limit": 0.8
    }
  }
}
```

| Parametro | Tipo | Default | Descrizione |
|-----------|------|---------|-------------|
| `max_drawdown` | Float | `0.15` | **Drawdown massimo** (15%) prima di stop trading |
| `stop_loss` | Float | `0.05` | **Stop loss** globale (5% perdita) |
| `take_profit` | Float | `0.15` | **Take profit** globale (15% guadagno) |
| `var_confidence` | Float | `0.95` | **Confidence level** per Value at Risk |

#### **📏 Sottosezione `position_sizing`**

| Parametro | Tipo | Valori | Descrizione |
|-----------|------|--------|-------------|
| `method` | String | `kelly_criterion`, `fixed_percent`, `volatility_based` | **Metodo sizing** posizioni |
| `max_leverage` | Float | `1.0` | **Leva massima** (1.0 = no leverage) |
| `concentration_limit` | Float | `0.25` | **Limite concentrazione** (25% max per singolo asset) |

---

## 📰 **Configurazione News Trading AI**

### **File `trading-new/config.json` (creato automaticamente)**

```json
{
  "rss_feeds": {
    "update_interval": 300,
    "max_articles_per_feed": 50,
    "breaking_news_threshold": 60,
    "sources": {
      "yahoo_finance": {
        "enabled": true,
        "url": "https://feeds.finance.yahoo.com/rss/2.0/headline",
        "priority": "high"
      },
      "cnbc": {
        "enabled": true,
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "priority": "high"
      }
    }
  },
  "sentiment_analysis": {
    "methods": {
      "textblob": {"weight": 0.3, "enabled": true},
      "vader": {"weight": 0.4, "enabled": true},
      "financial_dict": {"weight": 0.3, "enabled": true}
    },
    "confidence_threshold": 0.6,
    "sentiment_thresholds": {
      "strong_buy": 0.3,
      "buy": 0.1,
      "sell": -0.1,
      "strong_sell": -0.3
    }
  },
  "news_trading": {
    "virtual_portfolio": {
      "initial_balance": 10000,
      "max_position": 0.2
    },
    "signal_generation": {
      "min_confidence": 0.7,
      "min_news_count": 3,
      "time_decay": 0.1
    }
  }
}
```

---

## 🔧 **Esempi di Configurazione**

### **Configurazione Conservativa**

```json
{
  "trading": {
    "initial_balance": 50000.0,
    "max_position_size": 0.05,
    "risk_tolerance": 0.01
  },
  "risk_management": {
    "max_drawdown": 0.10,
    "stop_loss": 0.03,
    "take_profit": 0.10
  }
}
```

### **Configurazione Aggressiva**

```json
{
  "trading": {
    "initial_balance": 200000.0,
    "max_position_size": 0.15,
    "risk_tolerance": 0.05
  },
  "risk_management": {
    "max_drawdown": 0.25,
    "stop_loss": 0.08,
    "take_profit": 0.20
  }
}
```

---

## 🚨 **Parametri Critici - ATTENZIONE**

### **⚠️ Parametri che influenzano denaro reale:**

1. **`trading.live_trading.enabled`**: 
   - `false` = **SIMULAZIONE** (sicuro)
   - `true` = **TRADING REALE** (rischio!)

2. **`initial_balance`**: 
   - Importo del capitale (reale se live_trading=true)

3. **`max_position_size`** e **`risk_per_trade`**: 
   - Controllano l'esposizione massima

### **🛡️ Controlli di Sicurezza:**

- Sistema default in modalità simulazione
- Warnings espliciti per trading reale
- Limits automatici su drawdown
- Circuit breaker per perdite eccessive

---

## 📖 **Validazione Configurazione**

### **Comandi per verificare configurazione:**

```bash
# Mostra configurazione corrente
python src/main.py show-config

# Valida file configurazione
python src/main.py validate-config

# Test configurazione News Trading
python trading-new/news_trading_cli.py --help
```

---

## 🔄 **Aggiornamenti Runtime**

Alcuni parametri possono essere modificati senza restart:

- **Simboli monitorati** (richiede restart data collection)
- **Soglie alert** (aggiornamento immediato)
- **Intervalli monitoring** (effetto al prossimo ciclo)
- **Risk parameters** (applicati ai nuovi trades)

---

*Ultima modifica: 31 Luglio 2025*
*Per domande specifiche: [GitHub Issues](https://github.com/risik01/stock-ai/issues)*
