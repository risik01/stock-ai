#!/bin/bash

# 🚀 Stock AI - Log Reader con Filtri
# Script per leggere i log in modo più user-friendly

LOG_FILE="logs/trading_system_$(date +%Y%m%d).log"

# Colori
GREEN='\033[0;32m'
YELLOW='\033[1;33m' 
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

show_help() {
    echo "📖 Stock AI Log Reader"
    echo "Utilizzo: $0 [OPZIONE]"
    echo ""
    echo "Opzioni:"
    echo "  live      - Log live (default)"
    echo "  decisions - Solo decisioni AI"
    echo "  trades    - Solo operazioni"
    echo "  errors    - Solo errori"
    echo "  news      - Solo analisi news"
    echo "  summary   - Riassunto ultima sessione"
    echo "  --help    - Mostra questo help"
}

show_live() {
    echo -e "${BLUE}📊 Log Trading AI - Live Feed${NC}"
    echo -e "${YELLOW}Ctrl+C per uscire${NC}"
    echo "================================="
    
    tail -f "$LOG_FILE" 2>/dev/null | while read line; do
        # Colora i log in base al contenuto
        if [[ $line == *"=== ANALISI"* ]]; then
            echo -e "${PURPLE}$line${NC}"
        elif [[ $line == *"DECISIONE"* ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ $line == *"ERROR"* ]] || [[ $line == *"❌"* ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ $line == *"TRADE"* ]]; then
            echo -e "${YELLOW}$line${NC}"
        elif [[ $line == *"Breaking news"* ]] || [[ $line == *"🚨"* ]]; then
            echo -e "${RED}$line${NC}"
        else
            echo "$line"
        fi
    done
}

show_decisions() {
    echo -e "${GREEN}🎯 Decisioni AI di Trading${NC}"
    echo "=========================="
    
    if [[ -f "$LOG_FILE" ]]; then
        grep -E "(=== ANALISI|DECISIONE|Segnale|Score finale|Confidenza)" "$LOG_FILE" | tail -20
    else
        echo "❌ File log non trovato: $LOG_FILE"
    fi
}

show_trades() {
    echo -e "${YELLOW}💰 Operazioni di Trading${NC}"
    echo "======================="
    
    if [[ -f "$LOG_FILE" ]]; then
        grep -E "(TRADE|ACQUISTO|VENDITA|Portfolio|Cash)" "$LOG_FILE" | tail -15
    else
        echo "❌ File log non trovato: $LOG_FILE"
    fi
}

show_errors() {
    echo -e "${RED}❌ Errori di Sistema${NC}"
    echo "=================="
    
    if [[ -f "$LOG_FILE" ]]; then
        grep -E "(ERROR|❌|FAILED)" "$LOG_FILE" | tail -10
    else
        echo "❌ File log non trovato: $LOG_FILE"
    fi
}

show_news() {
    echo -e "${BLUE}📰 Analisi News${NC}"
    echo "==============="
    
    if [[ -f "$LOG_FILE" ]]; then
        grep -E "(news|News|sentiment|Sentiment|Breaking|articoli)" "$LOG_FILE" | tail -15
    else
        echo "❌ File log non trovato: $LOG_FILE"
    fi
}

show_summary() {
    echo -e "${PURPLE}📊 Riassunto Ultima Sessione${NC}"
    echo "============================"
    
    if [[ -f "$LOG_FILE" ]]; then
        # Sistema
        echo -e "${BLUE}🔧 Sistema:${NC}"
        grep "Automated Trading System inizializzato" "$LOG_FILE" | tail -1
        grep "Budget iniziale" "$LOG_FILE" | tail -1
        
        # Cicli
        echo -e "\n${BLUE}🔄 Cicli Trading:${NC}"
        cycles=$(grep -c "INIZIO CICLO TRADING" "$LOG_FILE")
        echo "Cicli completati: $cycles"
        
        # News
        echo -e "\n${BLUE}📰 News:${NC}"
        grep "Raccolti.*articoli" "$LOG_FILE" | tail -1
        grep "Sentiment mercato" "$LOG_FILE" | tail -1
        
        # Trades
        echo -e "\n${BLUE}💰 Trading:${NC}"
        trades=$(grep -c "TRADE ESEGUITO\|ACQUISTO ESEGUITO\|VENDITA ESEGUITA" "$LOG_FILE")
        echo "Trades eseguiti: $trades"
        
        # Performance
        echo -e "\n${BLUE}📈 Performance:${NC}"
        grep "PERFORMANCE:" "$LOG_FILE" | tail -1
        
        # Errori
        echo -e "\n${BLUE}❌ Errori:${NC}"
        error_count=$(grep -c "ERROR\|❌" "$LOG_FILE")
        echo "Errori totali: $error_count"
        
    else
        echo "❌ File log non trovato: $LOG_FILE"
    fi
}

# Menu principale
case "${1:-live}" in
    "live")
        show_live
        ;;
    "decisions")
        show_decisions
        ;;
    "trades")
        show_trades
        ;;
    "errors")
        show_errors
        ;;
    "news")
        show_news
        ;;
    "summary")
        show_summary
        ;;
    "--help"|"-h"|"help")
        show_help
        ;;
    *)
        echo "❌ Opzione non riconosciuta: $1"
        show_help
        exit 1
        ;;
esac
