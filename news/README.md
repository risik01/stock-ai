# News Trading AI - Sistema di Trading basato su Notizie

Modulo avanzato per il trading automatico basato sull'analisi del sentiment delle notizie finanziarie in tempo reale.

## 🚀 Caratteristiche Principali

### 📰 Raccolta Notizie RSS
- **Fonti Multiple**: 10+ feed RSS da fonti finanziarie autorevoli
  - Yahoo Finance, CNBC, Reuters, Bloomberg, MarketWatch
  - Wall Street Journal, Financial Times, Seeking Alpha
  - The Motley Fool, Benzinga
- **Raccolta Parallela**: Threading per ottimizzare velocità
- **Filtraggio Intelligente**: Identificazione automatica simboli azionari
- **Breaking News**: Rilevamento notizie dell'ultima ora

### 🤖 Analisi Sentiment Avanzata
- **Metodi Multipli**: Combinazione di approcci per maggiore accuratezza
  - TextBlob: Analisi sentiment generale
  - VADER: Ottimizzato per testi social/finanziari
  - Dizionario Finanziario: 500+ termini specifici del settore
- **Scoring Ibrido**: Weighted average con confidence scoring
- **Context Awareness**: Comprensione del contesto finanziario

### 🎯 Trading AI Intelligente
- **Segnali Automatici**: Generazione automatica segnali BUY/SELL/HOLD
- **Portfolio Virtuale**: Simulazione sicura senza rischi reali
- **Risk Management**: Gestione posizioni e stop-loss
- **Alert System**: Notifiche per eventi critici

### 🌐 Interfacce Multiple
- **CLI Avanzata**: Controllo completo da riga di comando
- **Web Dashboard**: Interfaccia grafica moderna e responsive
- **API REST**: Endpoint per integrazione con altri sistemi

## 📁 Struttura del Progetto

```
trading-new/
├── news_rss_collector.py      # Raccolta notizie RSS
├── news_sentiment_analyzer.py # Analisi sentiment
├── news_based_trading_ai.py   # Sistema trading principale
├── news_trading_cli.py        # Interfaccia CLI
├── news_web_dashboard.py      # Server web dashboard
├── test_news_trading.py       # Test completi
└── README.md                  # Documentazione
```

## 🛠️ Installazione

### Dipendenze Python
```bash
pip install feedparser requests textblob vaderSentiment flask yfinance numpy pandas
```

### Download Dati NLTK
```python
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
```

## 🚀 Utilizzo

### 1. Interfaccia CLI

#### Analisi Notizie
```bash
# Mostra analisi notizie correnti
python news_trading_cli.py news

# Analizza simboli specifici
python news_trading_cli.py news --symbols AAPL GOOGL MSFT
```

#### Segnali di Trading
```bash
# Genera segnali di trading
python news_trading_cli.py signals

# Segnali per simboli specifici
python news_trading_cli.py signals --symbols TSLA AMZN
```

#### Trading Automatico
```bash
# Ciclo singolo
python news_trading_cli.py cycle

# Trading automatico (ogni 10 minuti)
python news_trading_cli.py auto

# Trading con intervallo personalizzato
python news_trading_cli.py auto --interval 15
```

#### Portfolio e Report
```bash
# Stato portfolio
python news_trading_cli.py portfolio

# Esporta report completo
python news_trading_cli.py export
```

### 2. Web Dashboard

#### Avvio Server
```bash
# Server locale (porta 5001)
python news_web_dashboard.py

# Server personalizzato
python news_web_dashboard.py --host 0.0.0.0 --port 8080 --debug
```

#### Funzionalità Dashboard
- **📊 Panoramica**: Statistiche in tempo reale
- **📰 Notizie**: Feed live con breaking news
- **🎯 Segnali**: Trading signals automatici
- **💰 Portfolio**: Gestione posizioni virtuali
- **📈 Grafici**: Visualizzazioni sentiment e performance
- **🚨 Alert**: Notifiche eventi critici
- **🔄 Controlli**: Start/stop trading automatico

### 3. Utilizzo Programmatico

#### Raccolta Notizie
```python
from news_rss_collector import NewsRSSCollector

collector = NewsRSSCollector()

# Raccoglie tutte le notizie
articles = collector.collect_all_news()

# Breaking news ultima ora
breaking = collector.get_breaking_news(minutes=60)

# Notizie per simbolo specifico
aapl_news = collector.get_news_for_symbol('AAPL')
```

#### Analisi Sentiment
```python
from news_sentiment_analyzer import NewsSentimentAnalyzer

analyzer = NewsSentimentAnalyzer()

# Analizza articolo singolo
sentiment = analyzer.analyze_article_sentiment(article)

# Overview mercato
overview = analyzer.get_market_sentiment_overview(articles, symbols)

# Genera segnali trading
signals = analyzer.generate_trading_signals(articles, symbols)
```

#### Trading AI
```python
from news_based_trading_ai import NewsBasedTradingAI

trading_ai = NewsBasedTradingAI()

# Esegue ciclo trading
result = trading_ai.run_trading_cycle()

# Avvia trading automatico
trading_ai.start_automated_trading(cycle_interval_minutes=10)

# Stato portfolio
portfolio = trading_ai.get_portfolio_status()
```

## 🧪 Testing

### Test Completo
```bash
python test_news_trading.py
```

I test coprono:
- ✅ Raccolta notizie da tutti i feed RSS
- ✅ Analisi sentiment con tutti i metodi
- ✅ Generazione segnali trading
- ✅ Esecuzione cicli trading
- ✅ Gestione portfolio virtuale
- ✅ Sistema alert e notifiche

## ⚙️ Configurazione

### Fonti RSS Disponibili
```python
RSS_FEEDS = {
    'yahoo_finance': 'https://finance.yahoo.com/rss/',
    'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'reuters': 'https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best',
    'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
    'marketwatch': 'http://feeds.marketwatch.com/marketwatch/marketpulse/',
    # ... altre fonti
}
```

### Parametri Trading
```python
# Portfolio virtuale iniziale
INITIAL_PORTFOLIO = {
    'cash': 100000,  # $100k cash iniziale
    'positions': {}
}

# Soglie decision-making
SENTIMENT_THRESHOLDS = {
    'strong_buy': 0.3,
    'buy': 0.1,
    'sell': -0.1,
    'strong_sell': -0.3
}

# Risk management
RISK_PARAMETERS = {
    'max_position_size': 0.1,  # 10% max per posizione
    'stop_loss': 0.05,         # 5% stop loss
    'take_profit': 0.15        # 15% take profit
}
```

## 📊 Metriche e KPI

### Sentiment Scoring
- **Range**: -1.0 (molto negativo) a +1.0 (molto positivo)
- **Confidence**: 0.0 a 1.0 based on agreement tra metodi
- **Mood Classification**: Bearish, Neutral, Bullish

### Trading Performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Win Rate**: Percentuale trades profittevoli
- **Max Drawdown**: Perdita massima
- **Portfolio Value**: Valore totale in tempo reale

## 🔧 API Endpoints

### News API
```
GET /api/news/latest          # Ultime notizie
GET /api/news/breaking        # Breaking news
```

### Sentiment API
```
GET /api/sentiment/overview   # Sentiment mercato
```

### Trading API
```
GET /api/trading/signals      # Segnali attivi
GET /api/trading/portfolio    # Stato portfolio
POST /api/trading/cycle       # Esegui ciclo
POST /api/trading/auto/start  # Avvia auto trading
POST /api/trading/auto/stop   # Ferma auto trading
```

### Utility API
```
GET /api/alerts/active        # Alert attivi
GET /api/stats/dashboard      # Stats dashboard
GET /api/export/report        # Esporta report
```

## ⚠️ Modalità Simulazione

**IMPORTANTE**: Questo sistema opera in modalità simulazione con portfolio virtuale. Nessuna operazione reale viene eseguita sui mercati.

### Caratteristiche Simulazione
- 💰 Portfolio virtuale con $100k iniziali
- 📊 Prezzi simulati basati su Yahoo Finance
- 🔄 Trades registrati ma non eseguiti
- 📈 Performance tracking accurato
- 🚨 Alert e notifiche realistiche

## 🔒 Sicurezza e Limitazioni

### Rate Limiting
- Feed RSS: Max 1 richiesta per fonte ogni 30 secondi
- Yahoo Finance: Max 1 richiesta per simbolo ogni 10 secondi
- Sentiment Analysis: Ottimizzata per velocità

### Gestione Errori
- Retry automatico per feed non disponibili
- Fallback su cache in caso di errori
- Logging completo per debug
- Graceful degradation delle funzionalità

## 📝 Logging

Il sistema genera log dettagliati in:
```
news_trading.log              # Log principale
portfolio_trades.json         # Storico trades
sentiment_analysis.log        # Log analisi sentiment
rss_collection.log           # Log raccolta notizie
```

## 🤝 Integrazione

### Con Sistema Principale
Il modulo può essere integrato con il sistema Stock AI principale:

```python
# Integrazione sentiment con RL agent
from trading_new.news_sentiment_analyzer import NewsSentimentAnalyzer

# Nel tuo RL environment
def get_market_sentiment():
    analyzer = NewsSentimentAnalyzer()
    # ... logica integrazione
```

### Con Altri Sistemi
- API REST per integrazione esterna
- Export JSON per data pipeline
- Webhook support per notifiche
- Database integration ready

## 📚 Documentazione Avanzata

### Algoritmi Sentiment
Il sistema utilizza un approccio ibrido per l'analisi del sentiment:

1. **TextBlob**: Sentiment polarity generale
2. **VADER**: Ottimizzato per social media e testi informali
3. **Financial Dictionary**: Termini specifici del settore finanziario
4. **Weighted Scoring**: Combinazione pesata basata su confidence

### Decision Logic
```python
if sentiment_score > 0.3 and confidence > 0.7:
    signal = "STRONG_BUY"
elif sentiment_score > 0.1 and confidence > 0.6:
    signal = "BUY"
elif sentiment_score < -0.1 and confidence > 0.6:
    signal = "SELL"
# ... altre condizioni
```

## 🔮 Roadmap Future

- [ ] Integrazione con più exchange
- [ ] Machine Learning per ottimizzazione parametri
- [ ] Sentiment analysis con modelli transformer
- [ ] Real-time alerts via email/SMS
- [ ] Mobile app companion
- [ ] Social media sentiment integration
- [ ] Options trading simulation

## 🐛 Troubleshooting

### Problemi Comuni

**Nessuna notizia raccolta**
```bash
# Verifica connessione internet
python -c "import requests; print(requests.get('https://finance.yahoo.com/rss/').status_code)"

# Test singolo feed
python news_rss_collector.py
```

**Errori sentiment analysis**
```bash
# Reinstalla dipendenze NLTK
python -c "import nltk; nltk.download('all')"
```

**Dashboard non carica**
```bash
# Verifica porta disponibile
python news_web_dashboard.py --port 5002
```

---

*News Trading AI - Sviluppato per il progetto Stock AI*
*⚠️ Solo per scopi educativi e di simulazione*
