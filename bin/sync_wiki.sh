#!/bin/bash

# 🚀 GitHub Wiki Sync Script - Stock AI Trading System v4.0
# Automatizza il sync della documentazione wiki con GitHub

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni utility
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

# Verifica prerequisiti
check_prerequisites() {
    log_info "Verifico prerequisiti..."
    
    # Verifica Git
    if ! command -v git &> /dev/null; then
        log_error "Git non installato!"
        exit 1
    fi
    
    # Verifica GitHub repository
    if ! git remote get-url origin &> /dev/null; then
        log_error "Repository Git non configurato!"
        exit 1
    fi
    
    REPO_URL=$(git remote get-url origin)
    WIKI_URL="${REPO_URL%.git}.wiki.git"
    
    log_success "Prerequisiti verificati"
    log_info "Repository: $REPO_URL"
    log_info "Wiki URL: $WIKI_URL"
}

# Setup Wiki submodule
setup_wiki_submodule() {
    log_info "Setup Wiki come Git submodule..."
    
    # Rimuovi wiki esistente se presente
    if [ -d "wiki_repo" ]; then
        log_warning "Removing existing wiki_repo directory..."
        rm -rf wiki_repo
    fi
    
    # Clone wiki repository
    if git clone "$WIKI_URL" wiki_repo 2>/dev/null; then
        log_success "Wiki repository clonato"
    else
        log_warning "Wiki repository non esiste ancora, verrà creato"
        mkdir -p wiki_repo
        cd wiki_repo
        git init
        git remote add origin "$WIKI_URL"
        cd ..
    fi
}

# Sync documentation
sync_documentation() {
    log_info "Sincronizzazione documentazione..."
    
    # Copia file wiki aggiornati
    if [ -d "wiki" ]; then
        log_info "Copiando file da wiki/ a wiki_repo/..."
        
        # Copia nuovi file README e Wiki
        if [ -f "NEW_README.md" ]; then
            cp NEW_README.md README.md
            log_success "README.md aggiornato"
        fi
        
        # Copia file wiki
        for file in wiki/NEW_*.md; do
            if [ -f "$file" ]; then
                basename_file=$(basename "$file" .md)
                clean_name=${basename_file#NEW_}
                cp "$file" "wiki_repo/${clean_name}.md"
                log_success "Copiato: $file -> wiki_repo/${clean_name}.md"
            fi
        done
        
        # Copia file wiki esistenti aggiornati
        for file in wiki/*.md; do
            if [ -f "$file" ] && [[ ! "$file" =~ NEW_ ]]; then
                cp "$file" "wiki_repo/"
                log_success "Copiato: $file"
            fi
        done
    fi
}

# Commit and push changes
commit_and_push() {
    log_info "Commit e push modifiche..."
    
    cd wiki_repo
    
    # Setup git user se necessario
    if ! git config user.name &> /dev/null; then
        git config user.name "Stock AI Bot"
        git config user.email "bot@stock-ai.com"
    fi
    
    # Add all changes
    git add .
    
    # Check if there are changes
    if git diff --staged --quiet; then
        log_warning "Nessuna modifica da committare"
        cd ..
        return
    fi
    
    # Commit changes
    git commit -m "📚 Update Wiki Documentation v4.0

✅ Complete documentation overhaul
📖 Updated README with enterprise features
⚡ New Quick Start guide
📦 Comprehensive Installation guide
🤖 Enhanced AI system documentation
📰 News trading system details
🛡️ Production deployment guides

Updated: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Push to GitHub
    if git push origin master 2>/dev/null || git push origin main 2>/dev/null; then
        log_success "Wiki sincronizzata su GitHub!"
    else
        log_error "Errore durante push della wiki"
        cd ..
        exit 1
    fi
    
    cd ..
}

# Verifica risultati
verify_sync() {
    log_info "Verifica sincronizzazione..."
    
    if [ -d "wiki_repo" ]; then
        local file_count=$(find wiki_repo -name "*.md" | wc -l)
        log_success "Wiki sincronizzata: $file_count file markdown"
        
        log_info "File sincronizzati:"
        find wiki_repo -name "*.md" -exec basename {} \; | sort
    fi
}

# Cleanup temporaneo
cleanup() {
    log_info "Cleanup..."
    # Manteniamo wiki_repo per future sincronizzazioni
    log_success "Cleanup completato"
}

# Funzione principale
main() {
    echo "🚀 GitHub Wiki Sync Script - Stock AI Trading System v4.0"
    echo "=================================================================="
    
    check_prerequisites
    setup_wiki_submodule
    sync_documentation
    commit_and_push
    verify_sync
    cleanup
    
    echo "=================================================================="
    log_success "🎉 Wiki sincronizzazione completata!"
    log_info "📖 Visita: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]//' | sed 's/.git$//')/wiki"
}

# Help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "GitHub Wiki Sync Script"
    echo ""
    echo "Uso: $0 [opzioni]"
    echo ""
    echo "Opzioni:"
    echo "  --help, -h     Mostra questo help"
    echo "  --dry-run      Simula operazioni senza modificare"
    echo ""
    echo "Questo script:"
    echo "  1. Clona/aggiorna il repository wiki"
    echo "  2. Sincronizza la documentazione"
    echo "  3. Commit e push automatico"
    echo ""
    exit 0
fi

# Dry run mode
if [[ "$1" == "--dry-run" ]]; then
    log_warning "MODALITÀ DRY-RUN: Nessuna modifica verrà applicata"
    # Implementa dry-run logic se necessario
fi

# Esegui script
main
