#!/bin/bash
MODEL_DIR="$HOME/mai-ui-models"
MODEL_FILE="MAI-UI-2B.Q4_K_M.gguf"
MMPROJ_FILE="MAI-UI-2B.mmproj-Q8_0.gguf"  # <-- ADAPTEZ au nom exact du fichier téléchargé
LLAMA_CPP_DIR="$HOME/MAI-UI-Setup/llama.cpp"

echo "🚀 Démarrage du serveur llama.cpp..."
echo "   Modèle: $MODEL_FILE"
echo "   Projecteur: $MMPROJ_FILE"
echo "   URL: http://localhost:8080"
echo ""

"$LLAMA_CPP_DIR/build/bin/llama-server" \
    --model "$MODEL_DIR/$MODEL_FILE" \
    --mmproj "$MODEL_DIR/$MMPROJ_FILE" \
    --host 0.0.0.0 \
    --port 8080 \
    --ctx-size 2048 \
    --threads 4 \
    --batch-size 512 \
    --chat-template chatml