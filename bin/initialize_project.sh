#!/bin/bash

# 🚀 Stock AI - Script di Inizializzazione Progetto
# Script per setup completo o reset del progetto Trading AI

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  ┌─────────────────────────────────────────┐"
echo "  │        🤖 STOCK AI v3.0                 │"
echo "  │    Trading System Initialization       │"
echo "  └─────────────────────────────────────────┘"
echo -e "${NC}"

# Funzioni helper
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Mostra help
show_help() {
    echo "Utilizzo: $0 [OPZIONE]"
    echo ""
    echo "Opzioni:"
    echo "  setup     - Setup completo nuovo progetto"
    echo "  reset     - Reset progetto esistente"
    echo "  clean     - Pulizia per upload GitHub"
    echo "  test      - Test sistema completo"
    echo "  --help    - Mostra questo help"
    echo ""
    echo "Esempi:"
    echo "  $0 setup         # Setup iniziale"
    echo "  $0 clean         # Pulizia per GitHub"
    echo "  $0 test          # Test completo"
}

# Setup completo
setup_project() {
    log_info "Avvio setup completo progetto..."
    
    # 1. Crea struttura directory
    log_info "Creazione struttura directory..."
    mkdir -p {data,logs,backups,config,src,news,templates}
    mkdir -p logs/{archived,performance}
    
    # 2. Crea .env da template se non esiste
    if [[ ! -f .env ]]; then
        log_info "Creazione file .env da template..."
        cp .env.example .env 2>/dev/null || {
            log_warning ".env.example non trovato, creazione .env base..."
            cat > .env << 'EOF'
# Trading AI System - API Keys Configuration
# IMPORTANTE: Configura le tue API keys prima dell'uso

# API Keys per trading (RICHIESTE per funzionalità complete)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# API Keys opzionali per news avanzate
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_token_here

# Configurazioni sistema
DEBUG_MODE=false
LOG_LEVEL=INFO
TRADING_MODE=simulation
INITIAL_CAPITAL=1000

# Database (opzionale)
DATABASE_URL=sqlite:///data/trading.db

# Notifiche (opzionali)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EOF
        }
        log_success "File .env creato - CONFIGURA LE API KEYS!"
    else
        log_success "File .env già esistente"
    fi
    
    # 3. Installa dipendenze Python
    log_info "Installazione dipendenze Python..."
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt --quiet
        log_success "Dipendenze Python installate"
    else
        log_error "pip3 non trovato - installa Python 3"
        exit 1
    fi
    
    # 4. Setup permessi script
    log_info "Setup permessi script..."
    chmod +x *.sh
    chmod +x src/*.py 2>/dev/null || true
    log_success "Permessi script configurati"
    
    # 5. Inizializza dati base
    log_info "Inizializzazione dati base..."
    python3 -c "
import json
import os

# Config base production
config = {
    'trading': {
        'initial_capital': 1000,
        'max_position_size': 0.15,
        'stop_loss': 0.03,
        'take_profit': 0.08,
        'live_trading': {
            'enabled': True,
            'check_interval': 180,
            'market_hours_only': True,
            'max_trades_per_day': 8,
            'min_trade_interval': 300,
            'risk_per_trade': 0.015,
            'max_daily_loss': 0.05
        }
    },
    'data': {
        'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA'],
        'timeframe': '1d',
        'history_days': 365
    },
    'ai_trading': {
        'enabled': True,
        'model_confidence_threshold': 0.65,
        'models': {
            'technical_analyzer': {'weight': 0.4, 'enabled': True},
            'rl_agent': {'weight': 0.35, 'enabled': True},
            'sentiment_analyzer': {'weight': 0.25, 'enabled': True}
        }
    },
    'safety': {
        'max_daily_trades': 8,
        'emergency_stop_loss': 0.10,
        'max_portfolio_risk': 0.20
    }
}

# Salva config
os.makedirs('config', exist_ok=True)
with open('config/production_settings.json', 'w') as f:
    json.dump(config, f, indent=2)

# Portfolio iniziale
portfolio = {
    'cash': 1000.0,
    'positions': {},
    'total_value': 1000.0,
    'created_at': '$(date -Iseconds)'
}

os.makedirs('data', exist_ok=True)
with open('data/portfolio.json', 'w') as f:
    json.dump(portfolio, f, indent=2)

print('✅ Configurazioni iniziali create')
" || log_error "Errore inizializzazione dati"
    
    log_success "Setup progetto completato!"
    log_warning "IMPORTANTE: Configura le API keys in .env prima dell'uso"
    echo ""
    echo -e "${YELLOW}Prossimi passi:${NC}"
    echo "1. Modifica .env con le tue API keys"
    echo "2. Esegui: ./trading_control.sh start"
    echo "3. Monitora: ./monitor_system.sh"
}

# Reset progetto
reset_project() {
    log_warning "Reset progetto in corso..."
    
    # Stop sistema se in esecuzione
    if ./trading_control.sh status &>/dev/null; then
        log_info "Stopping sistema in esecuzione..."
        ./trading_control.sh stop
    fi
    
    # Reset dati (mantiene config)
    log_info "Reset dati di trading..."
    rm -rf data/portfolio.json
    rm -rf data/performance_history.json
    rm -rf data/current_portfolio.pkl
    rm -rf logs/*.log
    rm -rf backups/*.tar.gz
    
    # Reinizializza
    python3 -c "
import json
portfolio = {
    'cash': 1000.0,
    'positions': {},
    'total_value': 1000.0,
    'created_at': '$(date -Iseconds)'
}
with open('data/portfolio.json', 'w') as f:
    json.dump(portfolio, f, indent=2)
print('Portfolio reset a €1000')
"
    
    log_success "Reset completato - Portfolio: €1000"
}

# Pulizia per GitHub
clean_for_github() {
    log_info "Pulizia progetto per upload GitHub..."
    
    # Stop sistema
    if ./trading_control.sh status &>/dev/null; then
        ./trading_control.sh stop
    fi
    
    # Backup .env
    if [[ -f .env ]]; then
        cp .env .env.backup
        log_info "Backup .env salvato in .env.backup"
    fi
    
    # Rimuovi dati sensibili
    log_info "Rimozione dati sensibili..."
    
    # Crea .env sicuro per GitHub
    cat > .env.example << 'EOF'
# Trading AI System - API Keys Configuration Template
# Copia questo file in .env e configura le tue API keys

# API Keys per trading (RICHIESTE per funzionalità complete)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FINNHUB_API_KEY=your_finnhub_key_here

# API Keys opzionali per news avanzate
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_token_here

# Configurazioni sistema
DEBUG_MODE=false
LOG_LEVEL=INFO
TRADING_MODE=simulation
INITIAL_CAPITAL=1000

# Database (opzionale)
DATABASE_URL=sqlite:///data/trading.db

# Notifiche (opzionali)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EOF
    
    # Rimuovi .env con API keys reali
    rm -f .env
    
    # Pulisci dati sensibili
    rm -rf data/*.pkl
    rm -rf logs/*.log
    rm -rf backups/*.tar.gz
    rm -rf __pycache__/
    rm -rf src/__pycache__/
    rm -rf news/__pycache__/
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Reset portfolio a valori di esempio
    cat > data/portfolio.json << 'EOF'
{
  "cash": 1000.0,
  "positions": {},
  "total_value": 1000.0,
  "created_at": "example_timestamp"
}
EOF
    
    log_success "Progetto pulito per GitHub"
    log_warning "Le API keys sono state rimosse da .env"
    log_info "Backup salvato in .env.backup"
    echo ""
    echo -e "${YELLOW}Prima del push su GitHub:${NC}"
    echo "1. Verifica che .env non sia presente"
    echo "2. Verifica che .env.example sia presente"
    echo "3. Aggiungi .env al .gitignore se non presente"
}

# Test sistema completo
test_system() {
    log_info "Test sistema completo..."
    
    # Test 1: Configurazione
    log_info "Test 1: Configurazione..."
    if [[ -f config/production_settings.json ]]; then
        python3 -c "import json; json.load(open('config/production_settings.json'))" && log_success "Config OK"
    else
        log_error "Configurazione mancante"
        return 1
    fi
    
    # Test 2: Dipendenze Python
    log_info "Test 2: Dipendenze Python..."
    python3 -c "
import sys
sys.path.append('src')
try:
    from data_collector import DataCollector
    from portfolio import Portfolio
    print('✅ Import moduli principali OK')
except Exception as e:
    print(f'❌ Errore import: {e}')
    sys.exit(1)
"
    
    # Test 3: API Yahoo Finance
    log_info "Test 3: Connessione Yahoo Finance..."
    python3 -c "
import sys
sys.path.append('src')
from yahoo_api_v8 import YahooFinanceV8
try:
    api = YahooFinanceV8()
    data = api.get_stock_data('AAPL', period='1d', interval='5m')
    if data is not None and not data.empty:
        print('✅ Yahoo Finance API OK')
    else:
        print('⚠️ Yahoo Finance: dati vuoti')
except Exception as e:
    print(f'❌ Yahoo Finance error: {e}')
"
    
    # Test 4: Script di controllo
    log_info "Test 4: Script di controllo..."
    if ./trading_control.sh status &>/dev/null; then
        log_success "Script controllo OK"
    else
        log_warning "Sistema non in esecuzione (normale se non avviato)"
    fi
    
    log_success "Test completati"
}

# Menu principale
main() {
    case "${1:-}" in
        "setup")
            setup_project
            ;;
        "reset")
            reset_project
            ;;
        "clean")
            clean_for_github
            ;;
        "test")
            test_system
            ;;
        "--help"|"-h"|"help")
            show_help
            ;;
        "")
            echo -e "${YELLOW}Seleziona un'opzione:${NC}"
            echo "1) Setup completo progetto"
            echo "2) Reset dati trading"
            echo "3) Pulizia per GitHub"
            echo "4) Test sistema"
            echo "5) Mostra help"
            echo ""
            read -p "Scelta [1-5]: " choice
            
            case $choice in
                1) setup_project ;;
                2) reset_project ;;
                3) clean_for_github ;;
                4) test_system ;;
                5) show_help ;;
                *) log_error "Scelta non valida" ;;
            esac
            ;;
        *)
            log_error "Opzione non riconosciuta: $1"
            show_help
            exit 1
            ;;
    esac
}

# Esegui funzione principale
main "$@"
