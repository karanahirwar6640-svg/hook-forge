import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# [TERE PURANE ENVIRONMENT VARIABLES YAHIN RAHENGE]
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

# ==========================================
# TERA ORIGINAL MASTER DESIGN (RESTORED)
# ==========================================
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hook Forge | Original</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background: #000; color: #fef3c7; font-family: 'Noto Sans JP', sans-serif; overflow-x: hidden; }
        .glass-panel { background: rgba(5, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px; }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">
    <div class="glass-panel w-full max-w-[450px] p-10">
        <div class="text-center mb-8">
            <h1 class="anime-title text-4xl font-black text-red-500 tracking-widest mb-2">HOOK FORGE</h1>
            <p class="text-[10px] tracking-[0.4em] text-red-300/80 uppercase font-bold">Original Render Engine</p>
        </div>
        <textarea id="raw-script" class="w-full crimson-input rounded-xl p-4 h-40 mb-4 focus:outline-none focus:border-red-500" placeholder="Paste your raw script here..."></textarea>
        <button onclick="forge()" class="w-full crimson-btn py-4 rounded-xl text-xs tracking-widest uppercase font-bold text-white shadow-lg shadow-red-900/50">Forge Master Script</button>
        <div id="result" class="mt-6 text-sm text-amber-50 leading-relaxed font-mono hidden"></div>
    </div>

    <script>
        async function forge() {
            const script = document.getElementById('raw-script').value;
            const res = await fetch('/forge', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({script})
            });
            const data = await res.json();
            const resDiv = document.getElementById('result');
            resDiv.innerText = data.master_script;
            resDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(MASTER_HTML)

@app.route('/forge', methods=['POST'])
def forge():
    prompt = f"Rewrite this script to be viral and retention-focused: {request.json.get('script')}"
    payload = {"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "user", "content": prompt}]}
    r = requests.post(SAMBANOVA_URL, json=payload, headers={"Authorization": f"Bearer {SAMBANOVA_API_KEY}"})
    return jsonify({"master_script": r.json()['choices'][0]['message']['content'].strip()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
