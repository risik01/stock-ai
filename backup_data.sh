#!/bin/bash
# Script backup dati trading

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "💾 Backup dati trading in $BACKUP_DIR..."

# Backup configurazione
cp -r config "$BACKUP_DIR/"

# Backup logs
cp -r logs "$BACKUP_DIR/"

# Backup dati
cp -r data "$BACKUP_DIR/"

# Comprimi
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup completato: ${BACKUP_DIR}.tar.gz"

# Mantieni solo ultimi 7 backup
find backups -name "*.tar.gz" -mtime +7 -delete

echo "🗑️ Pulizia backup vecchi completata"
