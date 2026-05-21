#!/usr/bin/env python3
import gradio as gr
import requests
import base64
import os
import subprocess
from PIL import Image
import io
import re

API_BASE = "http://localhost:8080"
MODEL_ID = "MAI-UI-2B-Q4_K_M"

def capture_screen():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=10)
        if "device\n" not in result.stdout.replace("\t", " "):
            return None, "❌ Aucun appareil Android détecté. Branchez votre téléphone et activez le débogage USB."
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True, timeout=15)
        subprocess.run(["adb", "pull", "/sdcard/screen.png", "/tmp/screen_maiui.png"], check=True, timeout=15)
        return Image.open("/tmp/screen_maiui.png"), "✅ Capture réussie"
    except subprocess.TimeoutExpired:
        return None, "❌ Timeout ADB. Vérifiez la connexion USB."
    except Exception as e:
        return None, f"❌ Erreur ADB: {str(e)}"

def analyze_screen(image, instruction):
    if image is None:
        return "❌ Veuillez d'abord capturer l'écran du téléphone", ""
    if not instruction.strip():
        return "❌ Veuillez entrer une instruction", ""
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        messages = [
            {
                "role": "system",
                "content": "You are a GUI automation agent for Android. Analyze the screenshot and predict the next action. Respond ONLY with the action format: tap(x, y) or swipe(x1, y1, x2, y2) or text(\"string\") or back() or home()"
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text", "text": instruction}
                ]
            }
        ]
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            json={"model": MODEL_ID, "messages": messages, "temperature": 0.1, "max_tokens": 256},
            timeout=120
        )
        if response.status_code != 200:
            return f"❌ Erreur API {response.status_code}: {response.text}", ""
        return response.json()["choices"][0]["message"]["content"].strip(), "✅ Analyse terminée"
    except requests.exceptions.ConnectionError:
        return "❌ Serveur non accessible. Lancez d'abord ./start-server.sh", ""
    except Exception as e:
        return f"❌ Erreur: {str(e)}", ""

def execute_action(action_text):
    if not action_text or action_text.startswith("❌"):
        return "❌ Aucune action valide à exécuter"
    try:
        tap_match = re.search(r'tap\((\d+),\s*(\d+)\)', action_text, re.IGNORECASE)
        if tap_match:
            x, y = tap_match.groups()
            subprocess.run(["adb", "shell", "input", "tap", x, y], check=True, timeout=10)
            return f"✅ Tap exécuté à ({x}, {y})"
        swipe_match = re.search(r'swipe\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)', action_text, re.IGNORECASE)
        if swipe_match:
            x1, y1, x2, y2 = swipe_match.groups()
            subprocess.run(["adb", "shell", "input", "swipe", x1, y1, x2, y2], check=True, timeout=10)
            return f"✅ Swipe exécuté de ({x1},{y1}) à ({x2},{y2})"
        text_match = re.search(r'text\(["\'](.+?)["\']\)', action_text, re.IGNORECASE)
        if text_match:
            text = text_match.group(1)
            subprocess.run(["adb", "shell", "input", "text", text], check=True, timeout=10)
            return f"✅ Texte saisi: {text}"
        if "back()" in action_text.lower():
            subprocess.run(["adb", "shell", "input", "keyevent", "4"], check=True, timeout=10)
            return "✅ Bouton Retour pressé"
        if "home()" in action_text.lower():
            subprocess.run(["adb", "shell", "input", "keyevent", "3"], check=True, timeout=10)
            return "✅ Bouton Home pressé"
        return f"⚠️ Action non reconnue: {action_text}"
    except subprocess.TimeoutExpired:
        return "❌ Timeout ADB lors de l'exécution"
    except Exception as e:
        return f"❌ Erreur d'exécution: {str(e)}"

with gr.Blocks(title="MAI-UI Android Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 MAI-UI Android Automation Agent")
    gr.Markdown("### Contrôlez votre téléphone Android avec l'IA en langage naturel")
    with gr.Row():
        with gr.Column():
            gr.Markdown("#### 📱 Contrôles")
            screenshot = gr.Image(label="Capture d'écran", type="pil", height=400)
            capture_btn = gr.Button("📸 Capturer l'écran", variant="primary")
            status = gr.Textbox(label="Status", value="Prêt", interactive=False)
            instruction = gr.Textbox(
                label="📝 Votre instruction",
                placeholder="Ex: Clique sur le bouton bleu en haut à droite",
                lines=2
            )
            with gr.Row():
                analyze_btn = gr.Button("🔍 Analyser")
                execute_btn = gr.Button("▶️ Exécuter", variant="primary")
        with gr.Column():
            gr.Markdown("#### 🎯 Résultats")
            action_output = gr.Textbox(label="Action prédite par l'IA", lines=4)
            execution_log = gr.Textbox(label="Résultat d'exécution", lines=2)
    capture_btn.click(capture_screen, outputs=[screenshot, status])
    analyze_btn.click(analyze_screen, inputs=[screenshot, instruction], outputs=[action_output, status])
    execute_btn.click(execute_action, inputs=action_output, outputs=execution_log)

if __name__ == "__main__":
    print("🌐 Démarrage du Web UI...")
    print("   URL: http://localhost:7860")
    print("   Appuyez sur Ctrl+C pour arrêter")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
