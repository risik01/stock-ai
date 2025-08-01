#!/bin/bash

# Dual AI System Monitor & Control
# ===============================
# Path corretto dalla cartella bin/

cd "$(dirname "$0")/.." || exit 1  # Vai alla root del progetto

SYSTEM_PID=$(pgrep -f "src/simple_dual_ai.py")
LOG_FILE="data/dual_ai_simple.log"

print_status() {
    if [ -n "$SYSTEM_PID" ]; then
        echo "🟢 Sistema ATTIVO (PID: $SYSTEM_PID)"
        echo "📊 Log: $LOG_FILE"
        echo ""
    else
        echo "🔴 Sistema NON ATTIVO"
        return 1
    fi
}

show_live_decisions() {
    echo "🤖 DECISIONI AI LIVE"
    echo "==================="
    print_status || return 1
    
    echo "📊 Ultime decisioni AI:"
    tail -50 "$LOG_FILE" | grep "🧠" | tail -10
    echo ""
    
    echo "📰 News AI status:"
    tail -100 "$LOG_FILE" | grep -E "(News AI|📰|Sentiment)" | tail -3
    echo ""
    
    echo "💰 Trades eseguiti:"
    tail -100 "$LOG_FILE" | grep -E "(ACQUISTO|VENDITA|💰)" | tail -5 || echo "Nessun trade ancora"
    echo ""
    
    echo "📈 Portfolio status:"
    tail -20 "$LOG_FILE" | grep "📊 Portfolio:" | tail -1
}

show_real_time() {
    echo "🔄 MONITOR REAL-TIME"
    echo "=================="
    print_status || return 1
    
    echo "Premi Ctrl+C per uscire..."
    echo ""
    
    tail -f "$LOG_FILE" | grep --line-buffered -E "(🧠|📰|💰|🤖 === ANALISI|Portfolio:)" | while read line; do
        timestamp=$(echo "$line" | cut -d' ' -f1-2)
        if echo "$line" | grep -q "🧠"; then
            echo -e "\e[36m$line\e[0m"  # Cyan per decisioni
        elif echo "$line" | grep -q "📰"; then
            echo -e "\e[35m$line\e[0m"  # Magenta per news
        elif echo "$line" | grep -q "💰"; then
            echo -e "\e[32m$line\e[0m"  # Verde per trade
        elif echo "$line" | grep -q "🤖 === ANALISI"; then
            echo -e "\e[33m$line\e[0m"  # Giallo per analisi
        else
            echo -e "\e[37m$line\e[0m"  # Bianco per portfolio
        fi
    done
}

show_summary() {
    echo "📊 SUMMARY SISTEMA DUAL AI"
    echo "=========================="
    print_status || return 1
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "❌ Log file non trovato"
        return 1
    fi
    
    echo "🔄 Cicli Price AI (ultimo minuto):"
    tail -100 "$LOG_FILE" | grep "🤖 === ANALISI" | tail -5 | while read line; do
        timestamp=$(echo "$line" | cut -d' ' -f1-2)
        echo "  $timestamp"
    done
    echo ""
    
    echo "📰 Ultimo ciclo News AI:"
    tail -200 "$LOG_FILE" | grep -E "(News AI|📰.*Sentiment)" | tail -2
    echo ""
    
    echo "🎯 Segnali di trading generati:"
    signals=$(tail -100 "$LOG_FILE" | grep -c "🎯 SEGNALE TRADING" || echo "0")
    holds=$(tail -100 "$LOG_FILE" | grep -c "📋 Nessun segnale" || echo "0")
    echo "  Segnali attivi: $signals"
    echo "  Solo HOLD: $holds"
    echo ""
    
    echo "💰 Performance:"
    tail -50 "$LOG_FILE" | grep "📊 Portfolio:" | tail -1
    echo ""
    
    echo "📈 Variazioni prezzo recenti (ultimi 20 cicli):"
    tail -200 "$LOG_FILE" | grep "🧠" | tail -20 | while read line; do
        symbol=$(echo "$line" | grep -o "[A-Z]\+:" | head -1 | tr -d ':')
        delta=$(echo "$line" | grep -o "Δ[+-][0-9]\+\.[0-9]\+%")
        score=$(echo "$line" | grep -o "Score:[+-][0-9]\+\.[0-9]\+")
        action=$(echo "$line" | grep -o "→ [A-Z]\+" | cut -d' ' -f2)
        
        if [ -n "$symbol" ] && [ -n "$delta" ]; then
            echo "  $symbol: $delta $score → $action"
        fi
    done | sort | uniq -c | sort -nr | head -10
}

force_news_cycle() {
    echo "🔄 FORZATURA CICLO NEWS"
    echo "====================="
    print_status || return 1
    
    echo "Modifica temporanea per forzare news..."
    
    # Simula invio segnale al processo (non implementato nel sistema semplice)
    echo "⚠️ Funzione non implementata nel sistema attuale"
    echo "💡 Alternative:"
    echo "   1. Aspetta il ciclo naturale (ogni 10 min)"
    echo "   2. Riavvia il sistema: pkill -f simple_dual_ai.py && python3 simple_dual_ai.py &"
    echo "   3. Modifica la soglia di trading nel codice"
}

case "$1" in
    "status"|"")
        show_live_decisions
        ;;
    "live"|"monitor")
        show_real_time
        ;;
    "summary"|"stats")
        show_summary
        ;;
    "force-news")
        force_news_cycle
        ;;
    "help")
        echo "🤖 Dual AI System Monitor"
        echo "========================"
        echo ""
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandi:"
        echo "  status     - Mostra stato e ultime decisioni (default)"
        echo "  live       - Monitor in tempo reale"
        echo "  summary    - Statistiche complete"
        echo "  force-news - Forza ciclo news AI"
        echo "  help       - Questa guida"
        ;;
    *)
        echo "❌ Comando non riconosciuto: $1"
        echo "💡 Usa: $0 help"
        exit 1
        ;;
esac
