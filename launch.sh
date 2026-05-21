#!/bin/bash
# Script principal: lance serveur + Web UI

INSTALL_DIR="$HOME/MAI-UI-Setup"

echo "=========================================="
echo "  MAI-UI Android Agent - Lancement"
echo "=========================================="
echo ""

# Vérifier si le serveur tourne déjà
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Serveur llama.cpp déjà actif sur le port 8080"
else
    echo "🚀 Démarrage du serveur llama.cpp..."
    gnome-terminal -- bash -c "$INSTALL_DIR/start-server.sh; read -p 'Appuyez sur Entrée pour fermer...'" 2>/dev/null ||     xterm -e "$INSTALL_DIR/start-server.sh" 2>/dev/null ||     (echo "   → Lancez manuellement dans un autre terminal: $INSTALL_DIR/start-server.sh" &)

    echo "⏳ Attente du démarrage du serveur (10s)..."
    sleep 10
fi

echo ""
echo "🌐 Démarrage du Web UI..."
bash "$INSTALL_DIR/start-webui.sh"
