import os
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
# Yahan apne environment variables ensure kar lena
SAMBANOVA_API_KEY = os.environ.get("SAMBANOVA_API_KEY")
SAMBANOVA_URL = "https://api.sambanova.ai/v1/chat/completions"

# TERA ORIGINAL MASTER DESIGN - FULL POWER
MASTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hook Forge | Original Power</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background: #000; color: #fef3c7; font-family: 'Noto Sans JP', sans-serif; }
        .glass-panel { background: rgba(5, 0, 0, 0.4); backdrop-filter: blur(12px); border: 1px solid rgba(255, 50, 50, 0.4); border-radius: 24px; }
        .anime-title { font-family: 'Cinzel', serif; text-shadow: 0 0 30px rgba(255, 20, 20, 1); }
        .crimson-input { background: rgba(0, 0, 0, 0.7); border: 1px solid rgba(220, 38, 38, 0.35); color: #fef3c7; }
        .crimson-btn { background: linear-gradient(45deg, #7f1d1d, #dc2626); border: 1px solid #ef4444; }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen p-6">
    <div class="glass-panel w-full max-w-2xl p-12 shadow-2xl">
        <div class="text-center mb-10">
            <h1 class="anime-title text-5xl font-black text-red-500 tracking-[0.2em] mb-2">HOOK FORGE</h1>
            <p class="text-[12px] tracking-[0.5em] text-red-300 uppercase font-bold">Original Render Engine - Enterprise Mode</p>
        </div>
        <textarea id="raw-script" class="w-full crimson-input rounded-xl p-6 h-56 mb-6 focus:outline-none focus:border-red-500 text-lg" placeholder="Paste your raw script here..."></textarea>
        <button onclick="forge()" class="w-full crimson-btn py-5 rounded-xl text-sm tracking-[0.3em] uppercase font-bold text-white shadow-lg shadow-red-900/50 hover:scale-[1.01] transition-transform">Forge Master Script</button>
        <div id="result" class="mt-8 text-md text-amber-50 leading-relaxed font-mono hidden border-t border-red-900/30 pt-6 whitespace-pre-line"></div>
    </div>

    <script>
        async function forge() {
            const script = document.getElementById('raw-script').value;
            const resDiv = document.getElementById('result');
            resDiv.innerText = "Forging Master Script...";
            resDiv.style.display = 'block';
            
            const res = await fetch('/forge', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({script})
            });
            const data = await res.json();
            resDiv.innerText = data.master_script;
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
    # Yahan humne AI ko poora context aur aggressive training di hai
    prompt = f"""
    You are an elite, world-class retention expert and viral content architect.
    Your goal is to completely destroy the input script and rewrite it into a viral masterpiece.
    
    CRITICAL RULES:
    1. Hook the viewer in the first 3 seconds with a visceral, shocking, or contrarian statement.
    2. Zero fluff, zero boring introductions.
    3. Use deep psychological triggers (FOMO, Curiosity Gap, Status).
    4. Pacing must be intense and fast.
    
    INPUT: {request.json.get('script')}
    
    Return ONLY the highly optimized viral script.
    """
    payload = {"model": "Meta-Llama-3.3-70B-Instruct", "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {SAMBANOVA_API_KEY}"}
    r = requests.post(SAMBANOVA_URL, json=payload, headers=headers)
    return jsonify({"master_script": r.json()['choices'][0]['message']['content'].strip()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
