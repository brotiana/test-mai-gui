#!/bin/bash
WEBUI_DIR="$HOME/MAI-UI-Setup/web-ui"

echo "🌐 Démarrage du Web UI Gradio..."
echo "   Installation des dépendances Python..."

# Créer un venv si nécessaire
if [ ! -d "$WEBUI_DIR/venv" ]; then
    python3 -m venv "$WEBUI_DIR/venv"
fi

source "$WEBUI_DIR/venv/bin/activate"
pip install -q gradio requests Pillow 2>/dev/null

echo "   Lancement de l'interface..."
echo "   URL: http://localhost:7860"
echo ""

cd "$WEBUI_DIR"
python3 app.py
