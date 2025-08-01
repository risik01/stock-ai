#!/bin/bash

# Dual AI Trading System Controller
# ================================
# Path corretto dalla cartella bin/

cd "$(dirname "$0")/.." || exit 1  # Vai alla root del progetto

DUAL_AI_PID_FILE="data/dual_ai_system.pid"
DUAL_AI_LOG_FILE="data/dual_ai_trading.log"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🤖 DUAL AI TRADING SYSTEM${NC}"
    echo -e "${BLUE}=========================${NC}"
}

start_dual_ai() {
    print_header
    
    if [ -f "$DUAL_AI_PID_FILE" ] && kill -0 $(cat "$DUAL_AI_PID_FILE") 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Sistema già in esecuzione (PID: $(cat $DUAL_AI_PID_FILE))${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🚀 Avvio Dual AI Trading System...${NC}"
    echo -e "${CYAN}   📊 Price AI: Analisi tecnica ogni 10 secondi${NC}"
    echo -e "${CYAN}   📰 News AI: Analisi RSS ogni 10 minuti${NC}"
    echo -e "${CYAN}   🧠 Decision Maker: Decisioni ogni 30 secondi${NC}"
    echo ""
    
    # Avvia il sistema in background
    nohup python3 src/dual_ai_trading_system.py > "$DUAL_AI_LOG_FILE" 2>&1 &
    echo $! > "$DUAL_AI_PID_FILE"
    
    sleep 3
    
    if kill -0 $(cat "$DUAL_AI_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}✅ Sistema avviato (PID: $(cat $DUAL_AI_PID_FILE))${NC}"
        echo -e "${BLUE}📊 Log: tail -f $DUAL_AI_LOG_FILE${NC}"
        echo -e "${BLUE}🎮 Monitor: ./dual_ai_control.sh monitor${NC}"
    else
        echo -e "${RED}❌ Errore avvio sistema${NC}"
        rm -f "$DUAL_AI_PID_FILE"
        return 1
    fi
}

stop_dual_ai() {
    print_header
    
    if [ ! -f "$DUAL_AI_PID_FILE" ]; then
        echo -e "${RED}❌ Sistema non in esecuzione${NC}"
        return 1
    fi
    
    PID=$(cat "$DUAL_AI_PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        echo -e "${YELLOW}🛑 Fermando sistema (PID: $PID)...${NC}"
        kill -TERM "$PID"
        
        # Attende fino a 10 secondi
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${RED}⚠️  Forzo terminazione...${NC}"
            kill -KILL "$PID"
        fi
        
        echo -e "${GREEN}✅ Sistema fermato${NC}"
    else
        echo -e "${RED}❌ Processo non trovato${NC}"
    fi
    
    rm -f "$DUAL_AI_PID_FILE"
}

status_dual_ai() {
    print_header
    
    if [ -f "$DUAL_AI_PID_FILE" ] && kill -0 $(cat "$DUAL_AI_PID_FILE") 2>/dev/null; then
        PID=$(cat "$DUAL_AI_PID_FILE")
        UPTIME=$(ps -o etime= -p "$PID" 2>/dev/null | tr -d ' ')
        echo -e "${GREEN}✅ Sistema in esecuzione${NC}"
        echo -e "${BLUE}   PID: $PID${NC}"
        echo -e "${BLUE}   Uptime: $UPTIME${NC}"
        echo -e "${BLUE}   Log: $DUAL_AI_LOG_FILE${NC}"
        
        # Statistiche log
        if [ -f "$DUAL_AI_LOG_FILE" ]; then
            echo ""
            echo -e "${CYAN}📊 Statistiche Log (ultimi 100 righe):${NC}"
            tail -100 "$DUAL_AI_LOG_FILE" | grep -c "Price AI" | xargs echo -e "${BLUE}   Price AI cicli: ${NC}"
            tail -100 "$DUAL_AI_LOG_FILE" | grep -c "News AI" | xargs echo -e "${BLUE}   News AI cicli: ${NC}"
            tail -100 "$DUAL_AI_LOG_FILE" | grep -c "ACQUISTO\|VENDITA" | xargs echo -e "${GREEN}   Trades eseguiti: ${NC}"
            tail -100 "$DUAL_AI_LOG_FILE" | grep -c "ERROR" | xargs echo -e "${RED}   Errori: ${NC}"
        fi
    else
        echo -e "${RED}❌ Sistema non in esecuzione${NC}"
        if [ -f "$DUAL_AI_PID_FILE" ]; then
            rm -f "$DUAL_AI_PID_FILE"
        fi
    fi
}

monitor_dual_ai() {
    print_header
    echo -e "${CYAN}📊 Monitor Live - Premi Ctrl+C per uscire${NC}"
    echo -e "${CYAN}===========================================${NC}"
    echo ""
    
    if [ ! -f "$DUAL_AI_LOG_FILE" ]; then
        echo -e "${RED}❌ File di log non trovato${NC}"
        return 1
    fi
    
    # Segue il log con colori
    tail -f "$DUAL_AI_LOG_FILE" | while read line; do
        timestamp=$(echo "$line" | cut -d' ' -f1-2)
        level=$(echo "$line" | cut -d'-' -f3 | tr -d ' ')
        message=$(echo "$line" | cut -d'-' -f4-)
        
        case "$level" in
            "ERROR")
                echo -e "${RED}$timestamp - ERROR$message${NC}"
                ;;
            "WARNING")
                echo -e "${YELLOW}$timestamp - WARNING$message${NC}"
                ;;
            "INFO")
                if echo "$message" | grep -q "Price AI\|📊"; then
                    echo -e "${BLUE}$timestamp - INFO$message${NC}"
                elif echo "$message" | grep -q "News AI\|📰"; then
                    echo -e "${PURPLE}$timestamp - INFO$message${NC}"
                elif echo "$message" | grep -q "ACQUISTO\|VENDITA\|💰"; then
                    echo -e "${GREEN}$timestamp - INFO$message${NC}"
                else
                    echo -e "${CYAN}$timestamp - INFO$message${NC}"
                fi
                ;;
            *)
                echo "$line"
                ;;
        esac
    done
}

restart_dual_ai() {
    stop_dual_ai
    sleep 2
    start_dual_ai
}

logs_dual_ai() {
    print_header
    echo -e "${CYAN}📊 Ultimi 50 log entries${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    
    if [ -f "$DUAL_AI_LOG_FILE" ]; then
        tail -50 "$DUAL_AI_LOG_FILE"
    else
        echo -e "${RED}❌ File di log non trovato${NC}"
    fi
}

performance_dual_ai() {
    print_header
    echo -e "${CYAN}📈 Performance Report${NC}"
    echo -e "${CYAN}===================${NC}"
    echo ""
    
    if [ -f "$DUAL_AI_LOG_FILE" ]; then
        echo -e "${BLUE}🔄 Cicli Price AI (ultimi 100):${NC}"
        tail -100 "$DUAL_AI_LOG_FILE" | grep "Price AI ciclo completato" | tail -5
        echo ""
        
        echo -e "${PURPLE}📰 Cicli News AI (ultimi 10):${NC}"
        tail -100 "$DUAL_AI_LOG_FILE" | grep "News AI ciclo completato" | tail -3
        echo ""
        
        echo -e "${GREEN}💰 Trades recenti:${NC}"
        tail -100 "$DUAL_AI_LOG_FILE" | grep -E "ACQUISTO|VENDITA" | tail -5
        echo ""
        
        echo -e "${CYAN}📊 Portfolio Status:${NC}"
        tail -100 "$DUAL_AI_LOG_FILE" | grep "PORTFOLIO:" | tail -5
    else
        echo -e "${RED}❌ File di log non trovato${NC}"
    fi
}

show_help() {
    print_header
    echo -e "${CYAN}Uso: ./dual_ai_control.sh {start|stop|restart|status|monitor|logs|performance}${NC}"
    echo ""
    echo -e "${BLUE}Comandi:${NC}"
    echo -e "  ${GREEN}start${NC}       - Avvia il sistema Dual AI"
    echo -e "  ${RED}stop${NC}        - Ferma il sistema"
    echo -e "  ${YELLOW}restart${NC}     - Riavvia il sistema"
    echo -e "  ${CYAN}status${NC}      - Stato del sistema"
    echo -e "  ${PURPLE}monitor${NC}     - Monitor live dei log"
    echo -e "  ${BLUE}logs${NC}        - Mostra ultimi log"
    echo -e "  ${GREEN}performance${NC} - Report performance"
    echo ""
    echo -e "${CYAN}Sistema Dual AI:${NC}"
    echo -e "  📊 ${BLUE}Price AI${NC}: Analisi tecnica veloce (10s)"
    echo -e "  📰 ${PURPLE}News AI${NC}: Analisi RSS lenta (10min)"
    echo -e "  🧠 ${CYAN}Decision${NC}: Combine e decide (30s)"
}

# Menu principale
case "$1" in
    "start")
        start_dual_ai
        ;;
    "stop")
        stop_dual_ai
        ;;
    "restart")
        restart_dual_ai
        ;;
    "status")
        status_dual_ai
        ;;
    "monitor")
        monitor_dual_ai
        ;;
    "logs")
        logs_dual_ai
        ;;
    "performance")
        performance_dual_ai
        ;;
    *)
        show_help
        exit 1
        ;;
esac
